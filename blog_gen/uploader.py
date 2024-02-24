import os
from .database import s3
STATIC_DIR = os.environ.get('STATIC_DIR')

def upload_audio(audio_name):
    """Uploads an audio file to S3."""

    local_audio = os.path.join(STATIC_DIR, audio_name)
    s3_audio = f'{audio_name}'
    s3.Bucket(os.environ.get('AWS_BUCKET_NAME')
              ).upload_file(local_audio, s3_audio)
    os.remove(local_audio)
    return s3_audio


def upload_image(image_name):
    """Uploads an image to S3."""

    local_image = os.path.join(STATIC_DIR, 'images',image_name)
    local_image_thumb = os.path.join(STATIC_DIR, 'thumbs',image_name)
    s3_image = f'images/{image_name}'
    s3_image_thumb = f'thumbs/{image_name}'

    # Upload the original image
    s3.Bucket(os.environ.get('AWS_BUCKET_NAME')
              ).upload_file(local_image, s3_image)
    
    # Upload the thumbnail
    s3.Bucket(os.environ.get('AWS_BUCKET_NAME')
              ).upload_file(local_image_thumb, s3_image_thumb)
    
    # Remove the local files
    os.remove(local_image)
    os.remove(local_image_thumb)
    return image_name