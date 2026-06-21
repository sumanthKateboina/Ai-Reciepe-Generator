import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine, or_, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Recipe

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///recipes.db")

# Create engine. SQLite needs check_same_thread=False for Streamlit's multi-threaded model.
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def save_recipe(recipe_data: dict) -> Recipe:
    """
    Save a new recipe to the database.
    Accepts recipe_data dictionary and returns the database Recipe object.
    """
    with get_db_session() as db:
        # Create Recipe instance
        recipe = Recipe(
            title=recipe_data.get("title"),
            ingredients=recipe_data.get("ingredients", []),
            instructions=recipe_data.get("instructions", []),
            nutrition=recipe_data.get("nutrition", {}),
            servings=str(recipe_data.get("servings", "")),
            prep_time=recipe_data.get("prep_time"),
            cook_time=recipe_data.get("cook_time"),
            difficulty=recipe_data.get("difficulty"),
            dietary_tags=recipe_data.get("dietary_tags", []),
            serving_suggestions=recipe_data.get("serving_suggestions", [])
        )
        db.add(recipe)
        # Flush to populate the id field before committing/returning
        db.flush()
        # Create a transient copy of the recipe properties so we can read it outside the session
        db.expunge(recipe)
        return recipe

def get_recipe_by_id(recipe_id: int) -> Recipe:
    """Retrieve a single recipe by its ID."""
    with get_db_session() as db:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            db.expunge(recipe)
        return recipe

def get_all_recipes(
    search_query: str = None,
    dietary_preference: str = None,
    difficulty: str = None,
    sort_newest: bool = True
) -> list:
    """
    Retrieve all recipes with optional search, filtering, and sorting.
    """
    with get_db_session() as db:
        query = db.query(Recipe)
        
        # Apply search filter (case-insensitive title search)
        if search_query:
            query = query.filter(Recipe.title.ilike(f"%{search_query}%"))
            
        # Apply difficulty filter
        if difficulty and difficulty != "All":
            query = query.filter(Recipe.difficulty == difficulty)
            
        # Apply dietary preference filter
        # Since dietary_tags is stored as JSON, we'll check it in python or use ilike on the serialized text
        # If it's a specific diet (other than 'No Preference' or 'All'), we check if the tags contain it.
        # SQLite stores JSON as string, e.g., '["Vegan", "Keto"]'. We can do an ilike filter on the JSON column.
        if dietary_preference and dietary_preference != "No Preference" and dietary_preference != "All":
            query = query.filter(Recipe.dietary_tags.ilike(f"%{dietary_preference}%"))

        # Apply sorting
        if sort_newest:
            query = query.order_by(desc(Recipe.created_at))
        else:
            query = query.order_by(Recipe.created_at)
            
        recipes = query.all()
        # Expunge all objects from session to access them after session closes
        for recipe in recipes:
            db.expunge(recipe)
        return recipes

def delete_recipe(recipe_id: int) -> bool:
    """Delete a recipe by ID. Returns True if deleted, False otherwise."""
    with get_db_session() as db:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe:
            db.delete(recipe)
            return True
        return False
