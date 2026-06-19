from dotenv import load_dotenv
from google import genai
from pydantic import ValidationError
import os
import time

# Load environment variables
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_model(prompt, schema):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                },
            )

            return schema.model_validate_json(response.text)

        except ValidationError:
            print("Validation error occurred. Invalid Json returned. Retrying...")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

        if attempt == 2:
            raise

        time.sleep(1)
