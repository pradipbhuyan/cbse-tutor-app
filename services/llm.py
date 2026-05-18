import os
import asyncio
import edge_tts

from openai import OpenAI
from dotenv import load_dotenv

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


async def _generate_edge_tts(text, output_file, voice):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(output_file)


def generate_speech(
    text,
    output_file="lesson.mp3",
    voice="en-IN-NeerjaNeural"
):

    asyncio.run(
        _generate_edge_tts(
            text,
            output_file,
            voice
        )
    )

    return output_file
