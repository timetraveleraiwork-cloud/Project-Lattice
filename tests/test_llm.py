from app.schemas import Student


def test_create_student():
    student = Student(
        name="Alice",
        age=20,
        branch="Computer Science",
    )

    assert student.name == "Alice"
    assert student.age == 20
    assert student.branch == "Computer Science"
