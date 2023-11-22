from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import io
import keras
import tensorflow.compat.v2 as tf
from flask_cors import CORS
model = keras.models.load_model('VGG_model.h5')

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    if not request.files:
        return "No file upload", 400

    for file_name in request.files:
        file = request.files[file_name]

        if file and allowed_file(file.filename):
            image = Image.open(io.BytesIO(file.read()))
            processed_image = preprocess_image(image)
            res = model.predict_on_batch(processed_image)
            classification = np.where(res == np.amax(res))[1][0]

            result = {
                "filename": file.filename,
                "probability": str(res[0][classification] * 100) + '%',
                "conclusion": names(classification),
                "other": str(np.round(res, 3)),
            }

            return jsonify(result)
    return "No valid image files found", 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


def preprocess_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    x = np.array(image.resize((224, 224)))
    x = x.reshape(1 ,224, 224, 3)

    return x

def names(classification):
    tumor_types = ['glioma', 'meningioma', 'notumor', 'pituitary']

    if classification >= 0 and classification < len(tumor_types):
        return tumor_types[classification]
    else:
        return 'notumor'




if __name__ == '__main__':
    app.run(debug=True)