from openai import OpenAI
import os
from dotenv import load_dotenv
import speech_recognition as sr
import playsound


# Record voice via mic
def microphone_rec_func():
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


# openai whisper speech to text
def stt_func(client: OpenAI, audio_file_path: str):
    audio_file = open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )
    return transcript.text


# chatgpt to get ai answer
def conversation_func(client: OpenAI, input_text: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a HexML robot assistant, skilled to help"},
            {"role": "user", "content": input_text}
        ],
        max_tokens=50,
    )
    return completion.choices[0].message


# openai tts to generate voice onyx (deep man voice)
def tts_func(client: OpenAI, text: str):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
    )
    response.stream_to_file("./audio/output.mp3")
    playsound.playsound(sound="./audio/output.mp3", block=True)


def main():
    load_dotenv()
    Openai_Token = os.getenv("OPENAI_TOKEN", "value doesnt exist")
    client = OpenAI(api_key=Openai_Token)

    my_assistant = client.beta.assistants.create(
        instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
        name="Hexdecimal ML",
        tools=[{"type": "code_interpreter"}],
        model="gpt-3.5-turbo-16k",
    )
    print(my_assistant, "\n")

    message_thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Hello, what is AI?",
                "file_ids": ["file-abc123"],
            },
            {
                "role": "user",
                "content": "How does AI work? Explain it in simple terms."
            },
        ]
    )
    print(message_thread, "\n")

    thread_message = client.beta.threads.messages.create(
        "thread_abc123",
        role="user",
        content="How does AI work? Explain it in simple terms.",
    )
    print(thread_message, "\n")

    run = client.beta.threads.runs.create(
        thread_id="thread_abc123",
        assistant_id="asst_abc123"
    )
    print(run, "\n")

    #input_text: str = stt_func(client, audio_file_path="./audio/input.mp3")
    #output_text: str = conversation_func(client, input_text)
    #tts_func(client, output_text)


if __name__ == "__main__":
    main()
