import requests
import os
import ast
import uuid
import json
from PIL import Image
from openai import OpenAI
import soundfile as sf
import numpy as np
from .database import keywords_table
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
STATIC_DIR = os.environ.get('STATIC_DIR')


def get_title_keywords(blog_content):
    """Generates titles, keywords, and categories for a blog content."""

    categories = list(keywords_table.find({}, {'_id': 0}).limit(1)[0].keys())

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_message = """Follow these steps to answer the user queries. Only give output for the Step 9.\n

    \nStep 1 - Analyze the blog given by the user.\n

    \nStep 2 - Give 3 Titles that best suite the blog.\n

    \nStep 3 - Extract 3 keywords that define the genre of the blog.\n

    \nStep 4 - Analyze the genre of keywords\n

    \nStep 5 - Analyze the genre of catogoreis given below: 
    {input_catorgory}.\n
    
    \nStep 6 - Matchup the keywords with their catogoreis according to their genre.\n
    
    \nStep 7 - Make a JSON object of titles, keywords.Follow this format:
    "titles":["title1","title2","title3"]\n
    "keywords":["keyword1","keyword2","keyword3"]\n
    
    \nStep 8 - Make a JSON object with the category as the key and keyword as the values.
    Try to match the keywords with atleast one of the given categories.
    If then also none of the category match with the keywords then make the value of categories {{}} \n

    \nStep 9 - Addup both the JSON objects and show them as one. Follow this format:
    {{"titles":["title1","title2","title3"],\n
    "keywords":["keyword1","keyword2","keyword3"],\n
    "categories":{{"category":"keyword"}}}}\n
    """

    user_message = """Blog:{input_blog}"""
    error_count = 0
    while True:
        try:
            prompt = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                                "content": system_message.format(input_catorgory=categories)
                    },
                    {
                        "role": "user",
                                "content": user_message.format(input_blog=blog_content)
                    }
                ]
            )
            data = prompt.choices[0].message.content
            data = ast.literal_eval(data)
            break
        except Exception as e:
            error_count += 1
            print(f"An error occurred in get_title_keywords: {e}")
            if error_count > 3:
                return None

    return data


def generate_image(title, keywords):
    """Generates a DALL-E-2 image based on a title and keywords."""

    instruction_template = """Follow these steps to answer the user queries. 
    Only give output for the Step 3.

    Step 1 - Analyse Title: {title} and Tags: {keywords}.

    Step 2 - Generate a detailed description of a realistic image suiting the title 
    and tags. The description should not contain any Person or Text.

    Step 3 - Generate a prompt in 1000 words or less such that it directs DALL-E-2 
    to create an image according to the description. Make sure the generated prompt 
    is safe for DALL-E-2.
    """

    # Format the instruction message
    system_message = instruction_template.format(
        title=title, keywords=keywords)

    # Use OpenAI chat completion for prompt generation
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    # try:
    error_count = 0
    while True:
        try:
            prompt_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_message}],
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            image_prompt = prompt_response.choices[0].message.content

            # Use OpenAI image generation for image creation
            image_response = openai_client.images.generate(
                model="dall-e-2",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = image_response.data[0].url
            break
        except Exception as e:
            error_count += 1
            print(f"An error occurred in generate_image: {e}")
            if error_count > 3:
                return None

    # Download and save image
    response = requests.get(image_url)
    if response.status_code == 200:
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(STATIC_DIR, 'images', filename)
        with open(filepath, "wb") as file:
            file.write(response.content)

        image = Image.open(filepath)
        image.thumbnail((100, 100))
        image.save(os.path.join(STATIC_DIR, 'thumbs', filename))

        return filename
    else:
        return None


def generate_audio(content):
    """Generates an audio file from a given content."""

    if len(content) < 3800:
        error_count = 0
        while True:
            # ADD TRY EXCEPT
            try:
                audio_file_name = f"audio/{uuid.uuid4()}.mp3"
                audio_file_path = os.path.join(STATIC_DIR, audio_file_name)
                openai_client = OpenAI(api_key=OPENAI_API_KEY)

                response = openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=content
                )

                with open(audio_file_path, "wb") as file:
                    file.write(response.content)
                return audio_file_name
            except Exception as e:
                error_count += 1
                print(f"An error occurred in generate_audio: {e}")
                if error_count > 3:
                    return None
    

    system_template = """Follow these steps to answer the user queries. Only give output for the Step 3.
    Step - 1 User will provide a blog content.
    Step - 2 Sliceup the content into lists of 4000 words or less. Do not slice in the middle of a sentence. Do not slice in the middle of a word. Do not slice in the middle of a paragraph. Do not alter or add any new content just remove the links and images.
    Step - 3 Generate an JSON object with the sliced content. Follow this format:
    ["sliced_content1","sliced_content2","sliced_content3",...]
    """
    user_template = f"Blog Content:{content}"
    audio_client = OpenAI(api_key=OPENAI_API_KEY)

    # ADD TRY EXCEPT
    error_count = 0
    while True:
        try:
            prompt_response = audio_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role': 'system', 'content': system_template},
                    {'role': 'user', 'content': user_template}
                ],
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            audio_prompt = prompt_response.choices[0].message.content
            audio_prompt = json.loads(audio_prompt)
            audio_segments = []

            for i in range(len(audio_prompt)):
                audio_file_name = f"audio/temp{i}.mp3"
                audio_file_path = os.path.join(STATIC_DIR, audio_file_name)
                openai_client = OpenAI(api_key=OPENAI_API_KEY)

                response = openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=audio_prompt[i]
                )

                with open(audio_file_path, "wb") as file:
                    file.write(response.content)
                # audio_files.append(audio_file_name)
                tmp_audio, sr = sf.read(audio_file_path)
                audio_segments.append(tmp_audio)
                os.remove(audio_file_path)
            break
        except Exception as e:
            error_count += 1
            print(f"An error occurred in generate_audio: {e}")
            if error_count > 3:
                return None


    merged_audio = np.concatenate(audio_segments)
    audio_file_name = f"audio/{uuid.uuid4()}.mp3"
    audio_file_path = os.path.join(STATIC_DIR, audio_file_name)
    sf.write(audio_file_path, merged_audio, sr)
        
    return audio_file_name