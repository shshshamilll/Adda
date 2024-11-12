from roboflow import Roboflow
import numpy as np

class SheetDetectionModel():
    def __init__(self, roboflow_api_key, project_id, version_number):
        self.rf = Roboflow(api_key=roboflow_api_key)
        self.project = self.rf.workspace().project(project_id)
        self.model = self.project.version(version_number).model

    def get_sheet_coordinates(self):
        predictions = self.model.predict("Content/Adda.png", confidence=40, overlap=30).json()["predictions"][0]
        box = np.array([predictions["x"], predictions["y"], predictions["x"] + predictions["width"], predictions["y"] + predictions["height"]])
        return box
