from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
Openai_Token = os.getenv("OPENAI_TOKEN", "openai token doesnt exist")
Pvporcopine_Token = os.getenv("PVPOR_TOKEN", "pvporcopine token doesnt exist")

client = OpenAI(api_key=Openai_Token)

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "explain Nlp as a poem"}],
    stream=True,
)
frame = ""
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        frame += chunk.choices[0].delta.content
        if frame.find(".") >= 0:
            print(frame[:frame.find(".") + 1])
            frame = ""
