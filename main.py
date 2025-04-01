from flask import Flask, request, render_template, jsonify
from deepface import DeepFace
from PIL import Image
import os
from uuid import uuid4

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_uploaded_file(file, filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath

def convert_image_to_jpg(input_path, output_path):
    with Image.open(input_path) as img:
        img.convert('RGB').save(output_path, 'JPEG')

def delete_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath) 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({"error": "Both image files are required."}), 400
        
        image1 = request.files['image1']
        image2 = request.files['image2']
        
        if image1.filename == '' or image2.filename == '':
            return jsonify({"error": "Both image files must be selected."}), 400
        
        chosen_uuid = str(uuid4())
        
        # Save the original files
        path1 = save_uploaded_file(image1, f"{chosen_uuid}-image1{os.path.splitext(image1.filename)[1]}")
        path2 = save_uploaded_file(image2, f"{chosen_uuid}-image2{os.path.splitext(image2.filename)[1]}")

        # Convert the images to JPG format
        converted_path1 = f"{chosen_uuid}-image1-converted.jpg"
        converted_path2 = f"{chosen_uuid}-image2-converted.jpg"
        

        convert_image_to_jpg(path1, os.path.join(app.config['UPLOAD_FOLDER'], converted_path1))
        convert_image_to_jpg(path2, os.path.join(app.config['UPLOAD_FOLDER'], converted_path2))
        
        try:
            result = DeepFace.verify(img1_path=os.path.join(app.config['UPLOAD_FOLDER'], converted_path1), 
                                      img2_path=os.path.join(app.config['UPLOAD_FOLDER'], converted_path2))
            match = result['verified']
        except Exception as e:
            print(str(e))
            match = None
            result = {"error": str(e)}

        # Delete the original and converted files after processing
        delete_file(path1)
        delete_file(path2)
        delete_file(os.path.join(app.config['UPLOAD_FOLDER'], converted_path1))
        delete_file(os.path.join(app.config['UPLOAD_FOLDER'], converted_path2))

        return render_template("result.html", match=match, details=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=os.environ.get('PORT', 8080), debug=True)
