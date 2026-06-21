import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize Groq client
# In Streamlit or local environments, GROQ_API_KEY is read from environment variables.
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key":
        raise ValueError("GROQ_API_KEY is not configured. Please set your Groq API Key in the settings or .env file.")
    return Groq(api_key=api_key)

def clean_json_response(response_text: str) -> str:
    """
    Cleans the model's text response to ensure it contains only a JSON string.
    Removes markdown code blocks (e.g., ```json ... ```) and any leading/trailing whitespace.
    """
    cleaned = response_text.strip()
    
    # Remove markdown code blocks
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()
    
    # Try to extract content between first [ and last ] or first { and last } if still invalid
    if not (cleaned.startswith("[") or cleaned.startswith("{")):
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
            
    return cleaned

def analyze_image_ingredients(base64_image: str) -> list[str]:
    """
    Analyze the base64 encoded food image and detect ingredients.
    Uses Groq Vision model: meta-llama/llama-4-scout-17b-16e-instruct
    """
    client = get_groq_client()
    
    prompt = """Analyze this food image carefully.
Identify all visible ingredients,
food items,
or dishes.
Return ONLY a JSON array.
Example:
["tomato","onion","rice","egg"]
If image contains prepared dish,
identify dish name and likely ingredients."""

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1
        )
        
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_json_response(raw_response)
        ingredients = json.loads(cleaned_response)
        
        if not isinstance(ingredients, list):
            raise ValueError("Vision API did not return a JSON array.")
            
        return [str(item).strip().lower() for item in ingredients if item]
        
    except json.JSONDecodeError as je:
        print(f"JSON Decode Error parsing ingredients: {je}. Raw: {raw_response}")
        # Return fallback ingredients or re-raise
        raise ValueError("Failed to parse detected ingredients. The AI output format was incorrect. Please try again.")
    except Exception as e:
        print(f"Error in analyze_image_ingredients: {e}")
        raise e

def get_recipe_suggestions(ingredients: list[str], diet: str) -> list[dict]:
    """
    Get 3 compact recipe suggestions based on ingredients and dietary preferences.
    Uses Groq Text model: llama-3.3-70b-versatile
    """
    client = get_groq_client()
    
    ingredients_str = ", ".join(ingredients)
    
    prompt = f"""You are a professional chef.
Ingredients:
{ingredients_str}
Diet:
{diet}
Suggest 3 different recipes.
Return ONLY valid JSON.
Format:
[
{{
"title":"",
"description":"",
"difficulty":"",
"cookTime":"",
"dietaryTags":[]
}}
]"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional chef. You respond only with valid JSON as requested, with no other text, conversational prefix, or markdown tags outside code formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_json_response(raw_response)
        suggestions = json.loads(cleaned_response)
        
        if not isinstance(suggestions, list):
            raise ValueError("Suggestions response is not a list.")
            
        return suggestions[:3] # Ensure at most 3
        
    except Exception as e:
        print(f"Error in get_recipe_suggestions: {e}")
        # Raise clear exception
        raise ValueError(f"Failed to generate recipe suggestions. Error: {str(e)}")

def generate_full_recipe(ingredients: list[str], diet: str, recipe_title: str = None) -> dict:
    """
    Generate a complete detailed recipe based on ingredients, dietary preferences, and optionally a specific title.
    Uses Groq Text model: llama-3.3-70b-versatile
    """
    client = get_groq_client()
    
    ingredients_str = ", ".join(ingredients)
    title_context = f"Specifically build a recipe for '{recipe_title}' using these ingredients." if recipe_title else "Create a recipe based on these ingredients."
    
    prompt = f"""You are a professional chef.
Create a complete recipe.
{title_context}
Ingredients:
{ingredients_str}
Dietary Preference:
{diet}
Return ONLY valid JSON.
Format:
{{
"title":"",
"ingredients":[
{{
"name":"",
"quantity":""
}}
],
"instructions":[
{{
"step":1,
"description":""
}}
],
"nutrition":
{{
"calories":"",
"protein":"",
"carbs":"",
"fat":"",
"fiber":""
}},
"servings":"",
"prepTime":"",
"cookTime":"",
"difficulty":"",
"dietaryTags":[],
"servingSuggestions":[]
}}"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional chef. You respond only with valid JSON matching the exact structure requested, with no additional conversational text or markdown blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        raw_response = completion.choices[0].message.content
        cleaned_response = clean_json_response(raw_response)
        recipe = json.loads(cleaned_response)
        
        # Verify structure keys exist
        required_keys = ["title", "ingredients", "instructions", "nutrition", "servings", "prepTime", "cookTime", "difficulty", "dietaryTags", "servingSuggestions"]
        for key in required_keys:
            if key not in recipe:
                # Add default empty or fallback value
                if key in ["ingredients", "instructions", "dietaryTags", "servingSuggestions"]:
                    recipe[key] = []
                elif key == "nutrition":
                    recipe[key] = {"calories": "N/A", "protein": "N/A", "carbs": "N/A", "fat": "N/A", "fiber": "N/A"}
                else:
                    recipe[key] = ""
                    
        return recipe
        
    except Exception as e:
        print(f"Error in generate_full_recipe: {e}")
        raise ValueError(f"Failed to generate full recipe. Error: {str(e)}")
