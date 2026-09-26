import os

from dotenv import load_dotenv
from openai import OpenAI


# Load variables from .env
load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")


if not api_key:
    print("ERROR: OPENAI_API_KEY was not found in .env")
    raise SystemExit


client = OpenAI(
    api_key=api_key
)


print("Connecting Raremotion Analytics to OpenAI...")


try:
    response = client.responses.create(
        model="gpt-5.6-luna",
        input=(
            "You are the AI assistant for Raremotion Analytics. "
            "Reply with exactly this sentence: "
            "Raremotion AI connection successful."
        ),
    )

    print()
    print(response.output_text)

except Exception as error:
    print()
    print("OpenAI connection failed:")
    print(error)