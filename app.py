from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # IMPORTANT for frontend connection


def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        return 0.0, 0.0

    # Resize
    img1 = cv2.resize(img1, (500, 500))
    img2 = cv2.resize(img2, (500, 500))

    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Blur (reduce noise)
    gray1 = cv2.GaussianBlur(gray1, (7, 7), 0)
    gray2 = cv2.GaussianBlur(gray2, (7, 7), 0)

    # ---------------------------
    # 1. SSIM (Cleaning Detection)
    # ---------------------------
    score, _ = ssim(gray1, gray2, full=True)
    difference = 1 - score   # higher = more change

    # ---------------------------
    # 2. ORB Feature Matching
    # ---------------------------
    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    match_score = 0.0

    if des1 is not None and des2 is not None and len(kp1) > 0 and len(kp2) > 0:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        match_score = len(matches) / max(len(kp1), len(kp2))

    return float(difference), float(match_score)


@app.route('/')
def home():
    return "ML API Running"


@app.route('/compare-images', methods=['POST'])
def compare():
    try:
        file1 = request.files.get('before')
        file2 = request.files.get('after')

        if not file1 or not file2:
            return jsonify({"error": "Missing files"}), 400

        file1.save("before.jpg")
        file2.save("after.jpg")

        # ✅ Correct unpacking
        difference, match_score = compare_images("before.jpg", "after.jpg")

        # Cleanup
        os.remove("before.jpg")
        os.remove("after.jpg")

        return jsonify({
            "difference": difference,
            "match_score": match_score
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
