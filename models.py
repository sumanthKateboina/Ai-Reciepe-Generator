from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    
    # SQLite supports JSON type, which SQLAlchemy stores as text under the hood
    ingredients = Column(JSON, nullable=False)          # list of dicts: [{"name": str, "quantity": str}]
    instructions = Column(JSON, nullable=False)         # list of dicts: [{"step": int, "description": str}]
    nutrition = Column(JSON, nullable=False)            # dict: {"calories": str, "protein": str, "carbs": str, "fat": str, "fiber": str}
    
    servings = Column(String(50), nullable=True)
    prep_time = Column(String(50), nullable=True)
    cook_time = Column(String(50), nullable=True)
    difficulty = Column(String(50), nullable=True)
    
    dietary_tags = Column(JSON, nullable=True)          # list of strings
    serving_suggestions = Column(JSON, nullable=True)   # list of strings
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Helper to convert recipe model to dictionary format"""
        return {
            "id": self.id,
            "title": self.title,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "nutrition": self.nutrition,
            "servings": self.servings,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "difficulty": self.difficulty,
            "dietary_tags": self.dietary_tags,
            "serving_suggestions": self.serving_suggestions,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
