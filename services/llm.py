import os
import asyncio
import edge_tts

from openai import OpenAI
from dotenv import load_dotenv

import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_llm(system_prompt: str, user_prompt: str) -> str:

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    return response.output_text


async def _generate_edge_tts(text, output_file, voice, rate="+0%", pitch="+0Hz"):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )

    await communicate.save(output_file)

def clean_text_for_tts(text: str) -> str:

    import re

    # Remove markdown headers
    text = re.sub(r'#+\s*', '', text)

    # Remove markdown bold/italic
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Remove bullets
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)

    # Remove code ticks
    text = re.sub(r'`+', '', text)

    # Remove markdown separators
    text = re.sub(r'---+', ' ', text)

    # Remove LaTeX backslashes
    text = text.replace("\\", "")

    # Remove brackets
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace("{", "")
    text = text.replace("}", "")

    # Math readability improvements
    text = text.replace("Rightarrow", " therefore ")

    # Replace powers
    text = text.replace("^2", " square")
    text = text.replace("^3", " cube")

    # Replace equations carefully
    text = re.sub(r'\s=\s', ' equals ', text)
    text = re.sub(r'\s\+\s', ' plus ', text)

    # ONLY replace minus between numbers/variables
    text = re.sub(r'(\w)-(\w)', r'\1 minus \2', text)

    # Remove repeated spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def generate_speech(
    text,
    output_file="lesson.mp3",
    voice="en-IN-NeerjaNeural",
    rate="+0%",
    pitch="+0Hz"
):
    cleaned_text = clean_text_for_tts(text)

    asyncio.run(
        _generate_edge_tts(
            cleaned_text,
            output_file,
            voice,
            rate,
            pitch
        )
    )

    return output_file
