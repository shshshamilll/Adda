from PIL import Image
import base64
import io
import os

def get_last_post_id(vk_session, group_id):
    """
    Retrieves the ID of the second most recent post.

    Parameters:
        vk_session: VK API session.
        group_id: VK group ID with a minus sign.

    Returns:
        The ID of the second most recent post.
    """
    vk = vk_session.get_api()
    response = vk.wall.get(
        owner_id=group_id
    )
    return response["items"][1]["id"]

def get_comments(vk_session, group_id, last_post_id):
    """
    Retrieves comments from a specific post.

    Parameters:
        vk_session: VK API session.
        group_id: VK group ID with a minus sign.
        last_post_id: The ID of the post for which to retrieve comments (last post).

    Returns:
        A dictionary of comments.
    """
    vk = vk_session.get_api()
    comments = vk.wall.getComments(
        owner_id=group_id,
        post_id=last_post_id,
        count=100,
        extended=0,
        thread_items_count=10
    )
    return comments

def get_attachment(vk_session, group_id):
    """
    Uploads an image and retrieves the attachment ID.

    Parameters:
        vk_session: VK API session.
        group_id: VK group ID with a minus sign.

    Returns:
        The attachment ID.
    """
    vk = vk_session.get_api()
    upload_url = vk.photos.getWallUploadServer(group_id=group_id[1:])["upload_url"]
    with open("Content/combined_image.png", "rb") as file:
        response = vk_session.http.post(upload_url, files={"photo": file}).json()
    photo = vk.photos.saveWallPhoto(
        group_id=group_id[1:],
        photo=response["photo"],
        server=response["server"],
        hash=response["hash"]
    )[0]
    attachment = f"photo{photo['owner_id']}_{photo['id']}"
    return attachment

def publish_comment(vk_session, group_id, post_id, comment_id, attachment):
    """
    Publishes a reply to a specific comment with an attachment.

    Parameters:
        vk_session: VK API session.
        group_id: VK group ID with a minus sign.
        post_id: The ID of the post to which the comment is added.
        comment_id: The ID of the comment to reply to.
        attachment: The attachment ID.
    """
    vk = vk_session.get_api()
    vk.wall.createComment(
        owner_id=group_id,
        post_id=post_id,
        reply_to_comment=comment_id,
        attachments=attachment,
        from_group=1
    )

def decode_image(image_in_base64_format):
    """
    Decodes an image from a base64 format.

    Parameters:
        image_in_base64_format: The image in base64 format.

    Returns:
        A PIL Image object.
    """
    return Image.open(io.BytesIO(base64.b64decode(image_in_base64_format)))

def clear_table_and_close_connection(connection, table_name):
    """
    Deletes all data from the specified table and closes the database connection.

    Parameters:
        connection: The database connection.
        table_name: The name of the table to delete data from.
    """
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name};")
    connection.close()

def clear_Content_folder():
    """
    Clears the images from the 'Content' folder by removing the specified image files.
    """
    images = ["Content/remote_generated_image.png", "Content/combined_image.png"]
    for image in images:
        try:
            os.remove(image)
        except Exception as error:
            pass
