from PIL import ImageDraw, ImageFont

class Combiner():
    """
    This class is used to add formatted text to an image within a specified bounding box.

    Attributes:
        offset: Offset for text positioning.
        font: Font used to render the text.

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
            image: The image to which the text will be added.
            text: The text to be added.
            bbox: Coordinates of the bounding box coordinates in the format
                  [x_min, y_min, x_max, y_max], where (x_min, y_min) is the top-left
                  corner and (x_max, y_max) is the bottom-right corner.
        """
        draw = ImageDraw.Draw(image)
        formatted_text = text[0]
        for i in range(1, len(text)):
            text_bbox = draw.textbbox(
                (int(bbox[0] + self.offset), int(bbox[1] + self.offset / 2)),
                formatted_text + text[i],
                font=self.font
            )
            if text_bbox[2] > int(bbox[2] - self.offset) and text[i] != " ":
                formatted_text += "\n" + text[i]
            elif text_bbox[2] > int(bbox[2] - self.offset) and text[i] == " ":
                formatted_text += "\n"
            else:
                formatted_text += text[i]
        draw.text((int(bbox[0] + self.offset), int(bbox[1] + self.offset / 2)), formatted_text, fill=(0, 0, 0), font=self.font)
        image.save("Content/combined_image.png")

