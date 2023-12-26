import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
Openai_Token = os.getenv("OPENAI_TOKEN", "openai token doesnt exist")

client = OpenAI(api_key=Openai_Token)

while True:
    text = int(input("Enter file name:"))
    if text == 0:
        break
    speech_file_path = f"./audio/generated_{text}.mp3"
    response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=input("Enter text:"),
        )
    response.stream_to_file(speech_file_path)