from flask import Flask, request, jsonify
from flask_cors import CORS
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np
import os
import uuid

app = Flask(__name__)
CORS(app)


def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        return 0.0, 0.0

    # Resize
    img1 = cv2.resize(img1, (500, 500))
    img2 = cv2.resize(img2, (500, 500))

    # Grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Blur
    gray1 = cv2.GaussianBlur(gray1, (7, 7), 0)
    gray2 = cv2.GaussianBlur(gray2, (7, 7), 0)

    # SSIM
    score, _ = ssim(gray1, gray2, full=True)
    difference = 1 - score

    # ORB
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
    before_path = f"before_{uuid.uuid4().hex}.jpg"
    after_path = f"after_{uuid.uuid4().hex}.jpg"

    try:
        file1 = request.files.get('before')
        file2 = request.files.get('after')

        if not file1 or not file2:
            return jsonify({"error": "Missing files"}), 400

        # Save unique files (IMPORTANT FIX)
        file1.save(before_path)
        file2.save(after_path)

        difference, match_score = compare_images(before_path, after_path)

        return jsonify({
            "difference": difference,
            "match_score": match_score
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        # Always delete files (even if error)
        if os.path.exists(before_path):
            os.remove(before_path)
        if os.path.exists(after_path):
            os.remove(after_path)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
