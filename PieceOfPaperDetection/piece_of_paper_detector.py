import numpy as np
import requests

class PieceOfPaperDetector():
    def __init__(self, api_key, project_id, version_number):
        self.api_key = api_key
        self.project_id = project_id
        self.version_number = version_number

    def get_piece_of_paper_bbox(self):
        with open("Content/remote_generated_image.png", "rb") as file:
            predictions = requests.post(f"https://detect.roboflow.com/{self.project_id}/{self.version_number}?api_key={self.api_key}", files={"file": ("remote_generated_image.png", file, "image/png")}).json()["predictions"][0]
        piece_of_paper_bbox = np.array([predictions["x"] - predictions["width"] / 2, predictions["y"] - predictions["height"] / 2, predictions["x"] + predictions["width"] / 2, predictions["y"] + predictions["height"] / 2])
        return piece_of_paper_bbox
