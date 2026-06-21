import image_service
import groq_service

def detect_ingredients_from_image(uploaded_file) -> list[str]:
    """
    Orchestrate the ingredient detection workflow:
    1. Validate the uploaded file
    2. Convert file to base64
    3. Send base64 data to Groq Vision API
    4. Return detected list of ingredients
    """
    # 1. Validate
    is_valid, err_msg = image_service.validate_image(uploaded_file)
    if not is_valid:
        raise ValueError(err_msg)
        
    # 2. Convert to Base64
    base64_str = image_service.get_image_base64(uploaded_file)
    
    # 3. Analyze image
    detected_ingredients = groq_service.analyze_image_ingredients(base64_str)
    
    return detected_ingredients

def get_recipe_suggestions(ingredients: list[str], diet: str) -> list[dict]:
    """
    Fetch recipe suggestions based on a list of ingredients and dietary preferences.
    """
    if not ingredients:
        raise ValueError("Please provide at least one ingredient to get suggestions.")
    return groq_service.get_recipe_suggestions(ingredients, diet)

def generate_recipe(ingredients: list[str], diet: str, recipe_title: str = None) -> dict:
    """
    Generate a full recipe based on a list of ingredients, dietary preferences, and optional title.
    """
    if not ingredients:
        raise ValueError("Please provide at least one ingredient to generate a recipe.")
    return groq_service.generate_full_recipe(ingredients, diet, recipe_title)
