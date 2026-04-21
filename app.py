from skimage.metrics import structural_similarity as ssim
from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

import cv2

def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        return 0

    # Resize (important)
    img1 = cv2.resize(img1, (500, 500))
    img2 = cv2.resize(img2, (500, 500))

    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    gray1 = cv2.GaussianBlur(gray1, (7,7), 0)
    gray2 = cv2.GaussianBlur(gray2, (7,7), 0)

    # SSIM comparison
    score, _ = ssim(gray1, gray2, full=True)

    # Convert similarity → difference
    difference = 1 - score

    return float(difference)
@app.route('/')
def home():
    return "ML API Running"


@app.route('/compare-images', methods=['POST'])
def compare():
    try:
        file1 = request.files['before']
        file2 = request.files['after']

        file1.save("before.jpg")
        file2.save("after.jpg")

        similarity = compare_images("before.jpg", "after.jpg")

        os.remove("before.jpg")
        os.remove("after.jpg")

        return jsonify({
            "similarity": float(similarity)
        })

    except Exception as e:
        return jsonify({
    "difference": difference
})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
