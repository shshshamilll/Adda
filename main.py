from Utils.utils import get_last_post_id, get_comments, get_attachment, publish_comment, decode_image, clear_table_and_close_connection, clear_Content_folder
from PieceOfPaperDetection.piece_of_paper_detector import PieceOfPaperDetector
from ResponseGeneration.response_generator import ResponseGenerator
from langchain_core.messages import AIMessage, HumanMessage
from langchain_postgres import PostgresChatMessageHistory
from TextOnPieceOfPaper.combiner import Combiner
from dotenv import load_dotenv
import traceback
import argparse
import requests
import psycopg
import vk_api
import emoji
import uuid
import time
import os

load_dotenv()

group_token = os.getenv("GROUP_TOKEN")
user_token = os.getenv("USER_TOKEN")
group_id = os.getenv("GROUP_ID")

openai_api_key = os.getenv("OPENAI_API_KEY")
llm_model = os.getenv("LLM_MODEL")

roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")

user = os.getenv("USER")
database_name = os.getenv("DATABASE_NAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
table_name = os.getenv("TABLE_NAME")

vk_user_session = vk_api.VkApi(token=user_token)
vk_group_session = vk_api.VkApi(token=group_token)

connection = psycopg.connect(
    user=user,
    dbname=database_name,
    password=password,
    host=host
)
connection.autocommit = True

response_generator = ResponseGenerator(
    openai_api_key,
    llm_model
)

piece_of_paper_detector = PieceOfPaperDetector(
    roboflow_api_key
)

combiner = Combiner()

def create_comment_and_get_caption(input, messages=None):
    """
    Creates a comment image by generating an image, and combining it with the response text, and also returns the caption.

    Parameters:
        input: The input text to generate a response from.
        messages: A messages that make up the history of the chat.

    Returns:
        The caption.
    """
    session_id = str(uuid.uuid4())
    chat_history = PostgresChatMessageHistory(
        table_name,
        session_id,
        sync_connection=connection
    )
    if messages is not None:
        chat_history.add_messages(messages)
    response = response_generator.get_response(input, chat_history.messages)
    response += " | neutral" if "|" not in response else ""
    image_generation_requests_result = requests.post(args.url + "/get_remote_generated_image", json={"prompt": f"Image of {response.split('|', 1)[1].strip()} sks anime girl on white background, she holds a white piece of paper in her hands"})
    remote_generated_image = decode_image(image_generation_requests_result.json().get("remote_generated_image_in_base64_format"))
    remote_generated_image.save("Content/remote_generated_image.png")
    piece_of_paper_bbox = piece_of_paper_detector.get_piece_of_paper_bbox()
    combiner.combine(remote_generated_image, response.split('|', 1)[0].strip(), piece_of_paper_bbox)
    return response.split('|', 1)[0].strip()

def main(args):
    if args.url is not None:
        while True:
            try:
                with open("stop_or_continue.txt", "r") as file:
                    file_content = file.read().strip()
                    stop = int(file_content) if file_content else 0
                if stop:
                    clear_table_and_close_connection(connection, table_name)
                    clear_Content_folder()
                    break
                else:
                    last_post_id = get_last_post_id(vk_user_session, group_id)
                    comments = get_comments(vk_user_session, group_id, last_post_id)
                    for i in comments["items"]:
                        if not i["thread"]["items"]:
                            if i["text"] and not any([emoji.is_emoji(k) for k in i["text"]]):
                                caption = create_comment_and_get_caption(i["text"])
                                attachment = get_attachment(vk_user_session, group_id, caption)
                                publish_comment(vk_group_session, group_id, last_post_id, i["id"], attachment)
                                clear_Content_folder()
                        else:
                            messages = [HumanMessage(content=i["text"])]
                            for j in i["thread"]["items"]:
                                if j["from_id"] == int(group_id):
                                    messages.append(AIMessage(content=j["attachments"][0]["photo"]["text"]))
                                elif j["from_id"] == i["from_id"] and j["reply_to_user"] == int(group_id) and j["text"] and not any([emoji.is_emoji(k) for k in j["text"]]):
                                    messages.append(HumanMessage(content=j["text"]))
                            if len(messages) % 2 != 0:
                                caption = create_comment_and_get_caption(messages[-1].content, messages[:-1])
                                attachment = get_attachment(vk_user_session, group_id, caption)
                                publish_comment(vk_group_session, group_id, last_post_id, i["id"], attachment)
                                clear_Content_folder()
            except Exception as error:
                print(error)
                traceback.print_exc()
            time.sleep(1 * 5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, help="Define the server URL")
    args = parser.parse_args()
    main(args)
