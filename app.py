from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import json
# --------------------------- #
app = Flask(__name__)
# --------------------------- #
# Load Model
model = load_model("brain_tumor_model.keras")
# --------------------------- #
# Load Class Indices
with open("class_indices.json", "r") as file:
    class_indices = json.load(file)
# --------------------------- #
# Reverse dictionary
class_names = {
    value: key
    for key, value in class_indices.items()
}
# --------------------------- #
# Prediction Function
def predict_image(image):
    # --------------------------- #
    # Resize image
    image = image.resize((224, 224))
    # Convert image to NumPy
    image = np.array(image)
    # Grayscale → RGB
    if image.ndim == 2:
        image = np.stack((image,) * 3, axis=-1)
    # RGBA → RGB
    if image.shape[-1] == 4:
        image = image[:, :, :3]
    # Add batch dimension
    image = np.expand_dims(image, axis=0)
    # Normalize
    image = image / 255.0
    # --------------------------- #
    # Model prediction#
    predictions = model.predict(image, verbose=0)[0]
    predicted_index = np.argmax(predictions)
    # Get class name #
    predicted_class = class_names[predicted_index]
    # Confidence #
    confidence = float(predictions[predicted_index] * 100)
    # All class probabilities #
    probabilities = {
        class_names[i]: round(float(predictions[i] * 100), 2)
        for i in range(len(predictions))
    }
    # Return Values #
    return predicted_class, confidence, probabilities

# ---------------------------------------------------------------------------------- #
# Home Route
@app.route("/", methods=["GET", "POST"])
def home():
    # --------------------------- #
    result = None
    confidence = None
    probabilities = None
    error = None
    # --------------------------- #
    if request.method == "POST":
        # Check uploaded file
        if "mri_image" not in request.files:
            error = "Please select an MRI image."
        else:
            file = request.files["mri_image"]
            # Check filename
            if file.filename == "":
                error = "Please select an MRI image."
            else:
                try:
                    # Open image
                    image = Image.open(file)
                    # Predict
                    result, confidence, probabilities = predict_image(image)
                except Exception as e:
                    error = f"Error: {str(e)}"
    # --------------------------- #
    return render_template(
        "index.html",
        result=result,
        confidence=confidence,
        probabilities=probabilities
    )
    # --------------------------- #

