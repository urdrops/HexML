import playsound
from openai import OpenAI
import os
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf

load_dotenv()
Openai_Token = os.getenv("OPENAI_TOKEN", "value doesnt exist")
client = OpenAI(api_key=Openai_Token)

"output.mp3"


def stt_func(client: OpenAI, file: str):
    audio_file = open(file, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )
    return transcript.text


def text_generation_func(client: OpenAI, text: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a HexML robot assistant, skilled to help"},
            {"role": "user", "content": text}
        ],
        max_tokens=50,
    )
    return completion.choices[0].message.content


def tts(client: OpenAI, output_text: str, file_name: str):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=output_text,
    )
    response.stream_to_file(file_name)



#______________________________________________
import playsound
from openai import OpenAI
import os
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf
import speech_recognition






load_dotenv()
Openai_Token = os.getenv("OPENAI_TOKEN", "value doesnt exist")

client = OpenAI(api_key=Openai_Token)

audio_file = open("output.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
)
print(transcript.text)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a HexML robot assistant, skilled to help"},
    {"role": "user", "content": input("\nEnter prompt: ")}
  ],
  max_tokens=50,
)
response = client.audio.speech.create(
    model="tts-1",
    voice="onyx",
    input=completion.choices[0].message.content,
)

response.stream_to_file("output.mp3")
playsound.playsound("output.mp3", True)

#---------------------------------------


import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)
# recognize speech using whisper
try:
    print("Whisper thinks you said " + r.recognize_whisper(audio, language="english"))
except sr.UnknownValueError:
    print("Whisper could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Whisper")