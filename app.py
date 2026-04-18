from flask import Flask, request, jsonify
import cv2
import numpy as np
import os

app = Flask(__name__)

def compare_images(img1_path, img2_path):
    import cv2
    import numpy as np

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        return 0

    # Resize
    img1 = cv2.resize(img1, (500, 500))
    img2 = cv2.resize(img2, (500, 500))

    # ---------- ORB ----------
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    orb_score = 0
    if des1 is not None and des2 is not None:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        orb_score = len(matches) / max(len(kp1), len(kp2))

    # ---------- Histogram ----------
    hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

    hist1 = cv2.calcHist([hsv1], [0,1], None, [50,60], [0,180,0,256])
    hist2 = cv2.calcHist([hsv2], [0,1], None, [50,60], [0,180,0,256])

    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)

    hist_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    # ---------- Final ----------
    similarity = (orb_score + hist_score) / 2
    return float(similarity)

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
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)