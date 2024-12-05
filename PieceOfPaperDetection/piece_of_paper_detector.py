import numpy as np
import requests

class PieceOfPaperDetector():
    """
    A class for detecting a piece of paper in an image using the Roboflow API.

    Attributes:
        api_key (str): The API key for accessing Roboflow.
        project_id (str): The project ID.
        version_number (str): The version number.

    Methods:
        get_piece_of_paper_bbox(): Returns the bounding box coordinates for the piece of paper in the image.
    """

    def __init__(self, api_key, project_id, version_number):
        """
        Initializes the PieceOfPaperDetector object.

        Parameters:
            api_key (str): The API key for accessing Roboflow.
            project_id (str): The project ID.
            version_number (str): The version number.
        """
        self.api_key = api_key
        self.project_id = project_id
        self.version_number = version_number

    def get_piece_of_paper_bbox(self):
        """
        Retrieves the bounding box coordinates for the piece of paper in the image.

        The image "remote_generated_image.png" is expected to be in the "Content" folder.

        Returns:
            np.ndarray: An array containing the bounding box coordinates in the format
                        [x_min, y_min, x_max, y_max], where (x_min, y_min) is the top-left
                        corner and (x_max, y_max) is the bottom-right corner.
        """
        with open("Content/remote_generated_image.png", "rb") as file:
            predictions = requests.post(f"https://detect.roboflow.com/{self.project_id}/{self.version_number}?api_key={self.api_key}", files={"file": ("remote_generated_image.png", file, "image/png")}).json()["predictions"][0]
        piece_of_paper_bbox = np.array([predictions["x"] - predictions["width"] / 2, predictions["y"] - predictions["height"] / 2, predictions["x"] + predictions["width"] / 2, predictions["y"] + predictions["height"] / 2])
        return piece_of_paper_bbox
