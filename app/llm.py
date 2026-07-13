from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, ValidationError

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_model(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Call Gemini and validate the JSON response against a Pydantic schema."""

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
            print("Validation failed. Retrying...")

        except Exception as exc:
            print(f"Attempt {attempt + 1} failed: {exc}")

        if attempt == 2:
            raise

        time.sleep(5 * (attempt + 1))

    raise RuntimeError("Unexpected failure in call_model()")
