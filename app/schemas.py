from pydantic import BaseModel


class GeneratedDocument(BaseModel):
    title: str
    content: str
