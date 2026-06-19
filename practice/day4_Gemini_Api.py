from dotenv import load_dotenv
from google import genai
import os

# Load the .env file
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Ask Gemini something
response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Say hello in one sentence."
)
print(response.text)
