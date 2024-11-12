from segment_anything import SamPredictor
from segment_anything import sam_model_registry
from PIL import Image
import numpy as np

class SAM():
    def __init__(self):
        self.mask_predictor = SamPredictor(sam_model_registry["vit_h"](checkpoint="SAM/weights/sam_vit_h_4b8939.pth"))

    def get_mask(self, image_for_sam, box):
        self.mask_predictor.set_image(image_for_sam)
        masks, _, _ = self.mask_predictor.predict(
            box=box,
            multimask_output=False
        )
        return Image.fromarray(np.concatenate([masks[0][:, :, np.newaxis]] * 3, axis=2).astype(np.uint8) * 255)
