from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
import os

load_dotenv()


class Student(BaseModel):
    name: str
    age: int
    branch: str


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Generate a random student.",
    config={
        "response_mime_type": "application/json",
        "response_schema": Student,
    },
)

student = Student.model_validate_json(response.text)

print(student)
print(student.name)
print(student.age)
print(student.branch)