from PIL import ImageDraw, ImageFont

class Combiner():
    """
    The Combiner class is used to add formatted text to an image within a specified bounding box.

    Attributes:
        offset (int): Offset for text positioning.
        font (ImageFont.FreeTypeFont): Font used to render the text.

    Methods:
        combine(): Saves the combined image.
    """

    def __init__(self):
        """
        Initializes the Combiner object.
        """
        self.offset = 40
        self.font = ImageFont.truetype("TextOnPieceOfPaper/Fonts/arial.ttf", 20)

    def combine(self, image, text, bbox):
        """
        Adds text to the image within the specified bounding box, handling line breaks.

        Parameters:
            image (PIL.Image.Image): The image to which the text will be added.
            text (str): The text to be added.
            bbox (np.ndarray): Coordinates of the bounding box coordinates in the format
                               [x_min, y_min, x_max, y_max], where (x_min, y_min) is the top-left
                               corner and (x_max, y_max) is the bottom-right corner.
        """
        draw = ImageDraw.Draw(image)
        formatted_text = text[0]
        for i in range(1, len(text)):
            bbox = draw.textbbox(
                (int(bbox[0] + self.offset), int(bbox[1] + self.offset / 2)),
                formatted_text + text[i],
                font=self.font
            )
            if bbox[2] > int(bbox[2] - self.offset) and text[i] != " ":
                formatted_text += "\n" + text[i]
            elif bbox[2] > int(bbox[2] - self.offset) and text[i] == " ":
                formatted_text += "\n"
            else:
                formatted_text += text[i]
        draw.text((int(bbox[0] + self.offset), int(bbox[1] + self.offset / 2)), formatted_text, fill=(0, 0, 0), font=self.font)
        image.save("Content/combined_image.png")

