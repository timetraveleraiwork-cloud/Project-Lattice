from pydantic import BaseModel, field_validator
from typing import Optional

#1st example [Base model class]
'''
class Person(BaseModel):
    title: str
    name: str
    department: str
person = Person(title=123, name="Alice Smith", department="Research")
print(person)
'''
#2nd example [Validation]
'''
class Person(BaseModel):
    title: str
    name: str
    department: Optional[str] = None
person = Person(title="Dr.", name="Alice Smith")
print(person)
'''
#3rd example
'''
class Student(BaseModel):
    name: str
    age: int
    branch: str
    hostel: Optional[str] = None
student = Student(name="John Doe", age=20, branch="Computer Science")
print(student)
'''
#4th Example [Field Types Custom validator]
class Student(BaseModel):
    name: str
    age: int
    @field_validator("age")
    @classmethod
    def check_age(cls, value):
        if value < 18:
            raise ValueError("Age must  be atleast 18")
        return value
student = Student(name = "Bhuvan", age = 17)
print(student)