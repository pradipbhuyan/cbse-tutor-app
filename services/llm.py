import os
from openai import OpenAI, APIConnectionError, APIStatusError, AuthenticationError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )
        return response.output_text

    except AuthenticationError:
        return "Authentication failed. Please check your OPENAI_API_KEY in the .env file."

    except APIConnectionError:
        return """
Connection error while contacting OpenAI API.

Please check:
1. Internet connection
2. VPN/proxy/firewall
3. Whether https://api.openai.com is accessible
4. Try using a mobile hotspot
"""

    except APIStatusError as e:
        return f"OpenAI API returned an error: {e.status_code} - {e.response}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"
