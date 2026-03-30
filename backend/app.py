from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import cv2
import pytesseract

# 🔥 SET YOUR TESSERACT PATH (VERY IMPORTANT)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app)

# -------- LOAD MODEL --------
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------- PREDICTION FUNCTION --------
def predict_text(text):
    vec = vectorizer.transform([text])

    prob = model.predict_proba(vec)[0]
    confidence = max(prob)

    result = model.predict(vec)[0]
    label = "Cyberbullying" if result == 1 else "Safe"

    return label, round(confidence * 100, 2)


# -------- HOME ROUTE --------
@app.route("/")
def home():
    return "Cyberbullying Detection API is Running!"


# -------- MAIN API --------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        text = request.form.get("text")

        # ================= FILE CASE =================
        if 'file' in request.files:
            file = request.files['file']

            if file and file.filename != "":
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)

                print("File received:", file.filename)

                # -------- IMAGE OCR --------
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):

                    img = cv2.imread(filepath)

                    if img is None:
                        return jsonify({
                            "result": "Image not read properly",
                            "confidence": 0
                        })

                    # preprocess image
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, None, fx=2, fy=2)

                    _, thresh = cv2.threshold(
                        gray, 150, 255, cv2.THRESH_BINARY
                    )

                    extracted_text = pytesseract.image_to_string(
                        thresh, config='--oem 3 --psm 6'
                    )

                else:
                    # TEXT FILE
                    extracted_text = file.read().decode("utf-8", errors="ignore")

                print("OCR TEXT:", extracted_text)

                # -------- EMPTY TEXT --------
                if extracted_text.strip() == "":
                    return jsonify({
                        "result": "No text detected",
                        "confidence": 0
                    })

                label, confidence = predict_text(extracted_text)

                print("FINAL RESULT:", label, confidence)

                return jsonify({
                    "result": label,
                    "confidence": confidence
                })

        # ================= TEXT CASE =================
        if text and text.strip() != "":
            label, confidence = predict_text(text)

            return jsonify({
                "result": label,
                "confidence": confidence
            })

        return jsonify({
            "result": "No input provided",
            "confidence": 0
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "result": "Error occurred",
            "confidence": 0
        })


# -------- RUN SERVER --------
if __name__ == "__main__":
    app.run(debug=True)