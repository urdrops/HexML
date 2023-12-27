import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
Openai_Token = os.getenv("OPENAI_TOKEN", "openai token doesnt exist")

client = OpenAI(api_key=Openai_Token)

i = 0
while True:
    speech_file_path = f"./audio/generated_{i}.mp3"
    text = input("\nEnter text:")

    start_time = time.time()
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
    )
    response.stream_to_file(speech_file_path)
    print("\nspent time: ", time.time() - start_time)
    i += 1
