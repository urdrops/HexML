import os
import pygame
import random
import time
import pvporcupine
import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI
from playsound import playsound
from pvrecorder import PvRecorder
import funcs as f

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

# colors logging
ANSI_RESET = "\u001B[0m"
ANSI_BLACK = "\u001B[30m"
ANSI_RED = "\u001B[31m"
ANSI_GREEN = "\u001B[32m"
ANSI_YELLOW = "\u001B[33m"
ANSI_BLUE = "\u001B[34m"
ANSI_PURPLE = "\u001B[35m"
ANSI_CYAN = "\u001B[36m"
ANSI_WHITE = "\u001B[37m"


# ==============================================================================
# Voice to text.
# ==============================================================================
def stt_func():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print(ANSI_GREEN + "Please, feel free to speak your mind..." + ANSI_RESET)
            audio = recognizer.listen(source, timeout=4)
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

        print(ANSI_BLUE + "You said:" + ANSI_RESET, transcript.text)
        print(ANSI_CYAN + "STT model time:", ANSI_RED, time.time() - tstart, ANSI_RESET)

        return transcript.text

    except sr.exceptions.UnknownValueError as un:
        print(f"Speech not recognized. Error: {un}")
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
def conversation_loop(HexML, conversation, input_text):
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
            time.sleep(0.5)
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
                case "light_control":
                    output = f.light_control(dict_func_args["light_mode"])
                case "control_soft":
                    output = f.control_soft(dict_func_args["app_name"])

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
            time.sleep(0.5)
        i += 1
        run = client.beta.threads.runs.retrieve(thread_id=conversation.id, run_id=run.id)

    # ===========================================================================
    messages = client.beta.threads.messages.list(thread_id=conversation.id)
    extracted_message = messages.data[0].content[0].text.value

    print(ANSI_CYAN + "ChatGPT model time:", ANSI_RED, time.time() - tstart, ANSI_RESET)
    print(ANSI_BLUE + "HexML: " + ANSI_RESET, extracted_message)

    return extracted_message


# ==============================================================================
# Text to Speech.
# ==============================================================================
def tts_func(output_text):
    tstart = time.time()
    speech_file_path = "./audio/output.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=output_text,
        speed=1.1,
    )

    response.stream_to_file(speech_file_path)

    pygame.mixer.music.stop()

    print(ANSI_CYAN + "TTS model time:", ANSI_RED, time.time() - tstart, ANSI_RESET)
    playsound("./audio/output.mp3")


# ==============================================================================
# Main async function
# ==============================================================================

def main():
    # Build assistants that can call models and use tools to perform tasks.
    HexML = client.beta.assistants.retrieve("asst_zCn8mg381R9TCJaxSOAKQxMK")

    # Modify assistant and Tools.

    # client.beta.assistants.update(
    #     assistant_id="asst_zCn8mg381R9TCJaxSOAKQxMK",
    #     tools=[
    #         {
    #             "type": "function",
    #             "function": f.light_control_name,
    #         },
    #         {
    #             "type": "function",
    #             "function": f.control_soft_name,
    #         },
    #     ]
    # )

    # Create a thread
    make_smalltalk = client.beta.threads.create()
    conversation = client.beta.threads.retrieve(make_smalltalk.id)
    try:
        recoder.start()
        while True:
            keyword_index = porcupine.process(recoder.read())
            if keyword_index >= 0:
                print(ANSI_YELLOW + "detected wake word HexML" + ANSI_RESET)
                playsound(f"./audio/wakewords_{random.randint(a=0, b=4)}.mp3")
                while True:
                    input_text = stt_func()
                    if input_text == "":
                        print(ANSI_PURPLE + "sleep mode" + ANSI_RESET)
                        break
                    output_text = conversation_loop(HexML, conversation, input_text)
                    tts_func(output_text)
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
    main()
