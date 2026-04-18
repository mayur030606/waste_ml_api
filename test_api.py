import requests

url = "http://127.0.0.1:5000/compare-images"


files = {
    "before": open("C:/Users/mayur/OneDrive/Desktop/Project/del_img1.jpeg", "rb"),
    "after": open("C:/Users/mayur/OneDrive/Desktop/Project/del_img2.jpeg", "rb")
    }


response = requests.post(url, files=files)

print(response.json())