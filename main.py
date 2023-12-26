import os
import random
import time

import pygame
import asyncio
from playsound import playsound
import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
from funcs import get_weather_name, light_control_name, control_soft_name, control_soft, light_control
import pvporcupine
from pvrecorder import PvRecorder

# ==============================================================================
# load token and set up client Openai API
# ==============================================================================
load_dotenv()
Openai_Token = os.getenv("OPENAI_TOKEN", "openai token doesnt exist")
Pvporcopine_Token = os.getenv("PVPOR_TOKEN", "pvporcopine token doesnt exist")

client = OpenAI(api_key=Openai_Token)

# setup think audio
pygame.mixer.init()
pygame.mixer.music.load("./audio/think.mp3")

# setup wake word
porcupine = pvporcupine.create(
    access_key=Pvporcopine_Token, keyword_paths=['ww.ppn'])
recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)


# ==============================================================================
# Voice to text.
# ==============================================================================
async def stt_func():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("\033[92mPlease, feel free to speak your mind...\033[0m")
            audio = recognizer.listen(source, timeout=3)
        print("Saving data as .wav file...")
        tstart = time.time()
        pygame.mixer.music.play()
        # Convert the audio to wav format
        with open("./audio/input.wav", "wb") as wav_file:
            wav_file.write(audio.get_wav_data())
        print("Speech recognition in progress...")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=open("./audio/input.wav", "rb")
        )
        text = transcript.text
        print(f"\033[94mYou said: \033[0m{text}")
        print("STT model time:", time.time() - tstart)
        return text

    except sr.exceptions.UnknownValueError:
        print("Speech not recognized.")
        return ""
    except sr.exceptions.RequestError as e:
        print(f"Error while querying the recognition service: {e}")
        return ""
    except sr.exceptions.WaitTimeoutError as w:
        print(f"Timeout error: {w}")
        return ""


# ==============================================================================
# Chatting with the HexML assistant.
# ==============================================================================
async def conversation_loop(HexML, conversation, input_text):
    # Represents a message within a thread.
    message = client.beta.threads.messages.create(
        thread_id=conversation.id,
        role="user",
        content=input_text,
    )
    print("Message has been created...")
    # print("Message: ", message)
    tstart = time.time()
    # Represents an execution run on a thread.
    run = client.beta.threads.runs.create(
        thread_id=conversation.id,
        assistant_id=HexML.id,
    )

    i = 0
    while run.status not in ["completed", "requires_action", "failed"]:
        if i > 0:
            await asyncio.sleep(0.5)
        i += 1
        run = client.beta.threads.runs.retrieve(thread_id=conversation.id, run_id=run.id)
    if run.status == "requires_action":
        tools_to_call = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for each_tool in tools_to_call:
            tool_call_id = each_tool.id
            func_name = each_tool.function.name
            func_args = each_tool.function.arguments
            print("Function Name: ", func_name)
            print("Function Args:", func_args)
            print("Data extraction complete...")
            print("Calling functions...")
            output = "The function does not exist."
            # =========================================================
            dict_func_args = eval(func_args)  # str to dict
            match func_name:
                case "get_current_weather":
                    output = "Tashkent 9 degree"
                case "light_control":
                    output = light_control(dict_func_args["light_mode"])
                case "control_soft":
                    output = control_soft(dict_func_args["app_name"])

            # =========================================================
            tool_outputs.append({"tool_call_id": tool_call_id, "output": output})

        # To submit tool outputs.
        # print(tool_outputs)
        print("Submitting tool outputs...")
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=conversation.id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )

    # check status and connection
    i = 0
    while run.status not in ["completed", "requires_action", "failed"]:
        if i > 0:
            await asyncio.sleep(0.5)
        i += 1
        run = client.beta.threads.runs.retrieve(thread_id=conversation.id, run_id=run.id)
    # print(run)

    messages = client.beta.threads.messages.list(thread_id=conversation.id)
    new_message = messages.data[0].content[0].text.value
    print("\033[94mHexML: \033[0m", new_message)
    print("ChatGPT model time:", time.time() - tstart)

    return new_message


# ==============================================================================
# Text to Speech.
# ==============================================================================
async def tts_func(output_text):
    tstart = time.time()
    speech_file_path = "./audio/output.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=output_text, speed=1.1
    )

    response.stream_to_file(speech_file_path)
    pygame.mixer.music.stop()
    print("TTS model time:", time.time() - tstart)
    playsound("./audio/output.mp3")


# ==============================================================================
# Main async function
# ==============================================================================

async def main():
    # Build assistants that can call models and use tools to perform tasks.
    HexML = client.beta.assistants.retrieve("asst_zCn8mg381R9TCJaxSOAKQxMK")

    # Modify assistant and Tools.
    client.beta.assistants.update(
        assistant_id="asst_zCn8mg381R9TCJaxSOAKQxMK",
        tools=[
            {
                "type": "function",
                "function": get_weather_name,
            },
            {
                "type": "function",
                "function": light_control_name,
            },
            {
                "type": "function",
                "function": control_soft_name,
            }

        ]
    )

    # create a thread
    make_smalltalk = client.beta.threads.create()
    conversation = client.beta.threads.retrieve(make_smalltalk.id)
    try:
        recoder.start()
        while True:
            keyword_index = porcupine.process(recoder.read())
            if keyword_index >= 0:
                print("detected HexML")
                playsound(f"./audio/wakewords_{random.randint(a=0, b=4)}.mp3")
                while True:
                    input_text = await stt_func()
                    if input_text == "":
                        print("sleep mode")
                        break
                    output_text = await conversation_loop(HexML, conversation, input_text)
                    await tts_func(output_text)
    except KeyboardInterrupt:
        recoder.stop()
        print("Recoder has been stopped.")
    finally:
        client.beta.threads.delete(conversation.id)
        print("Conversation has been deleted.")
        porcupine.delete()
        recoder.delete()


# ==============================================================================
# Start point.
# ==============================================================================

if __name__ == "__main__":
    asyncio.run(main())
