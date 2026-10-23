from pydantic import BaseModel, Field

class LearningExplanation(BaseModel):
    topic: str = Field(description="The concept being explained")
    difficulty: str = Field(description="beginner, intermediate, or advanced")
    key_points: list[str] = Field(
        description="Important points about the concept"
    )
    suggested_next_step: str = Field(
        description="A practical next step for learning"
    )