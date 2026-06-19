from dotenv import load_dotenv
from google import genai
import os
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
Give information about a student in JSON.

Fields:
- name
- age
- branch

Return ONLY JSON.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

print(response.text)

# Convert JSON string into Python dictionary
student = json.loads(response.text)

print(student)
print(student["name"])
