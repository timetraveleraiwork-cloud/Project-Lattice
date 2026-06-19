from app.schemas import Student
from app.llm import call_model

student = call_model(
    prompt="Generate a random student.",
    schema=Student,
)
print(student)
