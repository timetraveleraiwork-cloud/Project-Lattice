from pydantic import BaseModel
from typing import Optional
#1st example
'''
class Person(BaseModel):
    title: str
    name: str
    department: str
person = Person(title=123, name="Alice Smith", department="Research")
print(person)
'''
#2nd example
'''
class Person(BaseModel):
    title: str
    name: str
    department: Optional[str] = None
person = Person(title="Dr.", name="Alice Smith")
print(person)
'''
#3rd example
class Student(BaseModel):
    name: str
    age: int
    branch: str
    hostel: Optional[str] = None
student = Student(name="John Doe", age=20, branch="Computer Science")
print(student)