import os
import streamlit as st
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

# Import database and services
import database
import recipe_service

# Load environment variables and initialize database tables
load_dotenv()
database.init_db()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Powered Recipe Generator",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme and Custom CSS ---
st.markdown("""
<style>
    /* Premium CSS styling */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hero Title styling */
    .hero-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem !important;
        color: #6B7280;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Custom Card Design */
    .suggestion-card {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .suggestion-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -8px rgba(16, 185, 129, 0.15);
        border-color: #A7F3D0;
        background-color: #F0FDF4;
    }
    
    /* Tag styles */
    .diet-tag {
        display: inline-block;
        background-color: #D1FAE5;
        color: #065F46;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 12px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .info-tag {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0369A1;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 12px;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    /* Nutrition Card design */
    .nutrition-box {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .nutrition-val {
        font-size: 1.5rem;
        font-weight: 700;
        color: #059669;
    }
    .nutrition-label {
        font-size: 0.85rem;
        color: #6B7280;
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "ingredients" not in st.session_state:
    st.session_state.ingredients = []
if "suggestions" not in st.session_state:
    st.session_state.suggestions = None
if "full_recipe" not in st.session_state:
    st.session_state.full_recipe = None
if "last_analyzed_image" not in st.session_state:
    st.session_state.last_analyzed_image = None
if "selected_recipe_id" not in st.session_state:
    st.session_state.selected_recipe_id = None

# Sidebar - API Key override and metadata
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/cooking-book.png", width=120)
    st.title("Settings")
    
    # Enable entering Groq API key directly via Streamlit interface
    api_key_env = os.getenv("GROQ_API_KEY", "")
    if api_key_env == "your_key":
        api_key_env = ""
        
    user_api_key = st.text_input(
        "Groq API Key", 
        value=st.session_state.get("groq_api_key", api_key_env),
        type="password",
        help="Paste your Groq API key here. It will override the one in your .env file."
    )
    if user_api_key:
        st.session_state.groq_api_key = user_api_key
        os.environ["GROQ_API_KEY"] = user_api_key
        
    st.markdown("---")
    st.markdown("### Navigation")
    
    # We display simple navigation buttons
    # Since saved_recipes.py is in the pages/ directory, Streamlit handles loading it automatically.
    # However, to help guide the user, we put direct links here.
    st.page_link("app.py", label="🍳 Recipe Generator", icon="🏠")
    st.page_link("pages/saved_recipes.py", label="📚 Saved Recipes Library", icon="💾")
    
    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.8rem; color: gray; text-align: center;'>"
        "Powered by Groq Cloud<br>"
        "Llama 4 Scout (Vision) & Llama 3.3 (Text)"
        "</div>", 
        unsafe_allow_html=True
    )

# --- Main Page Layout ---

# Hero Section
st.markdown('<h1 class="hero-title">What\'s in Your Fridge?</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Upload an image of ingredients and let AI create delicious custom recipes instantly.</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### 1. Upload Ingredients Image")
    
    # File Uploader
    uploaded_image = st.file_uploader(
        "Drag & Drop or Browse File (Max 10MB)",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload an image containing visible food ingredients, items, or a prepared dish."
    )
    
    if uploaded_image is not None:
        # Size and type validations are done by image_service, but we check size here visually too
        file_size_mb = uploaded_image.size / (1024 * 1024)
        
        # Display image preview
        st.image(uploaded_image, caption="Uploaded Image Preview", use_container_width=True)
        
        # We only run the analysis if the image has changed or hasn't been analyzed yet
        image_identifier = f"{uploaded_image.name}_{uploaded_image.size}"
        if st.session_state.last_analyzed_image != image_identifier:
            if st.button("🔍 Detect Ingredients with AI", type="primary", use_container_width=True):
                with st.spinner("Analyzing image using Groq Vision (Llama-4 Scout)..."):
                    try:
                        detected = recipe_service.detect_ingredients_from_image(uploaded_image)
                        st.session_state.ingredients = list(set(st.session_state.ingredients + detected))
                        st.session_state.last_analyzed_image = image_identifier
                        st.success(f"Successfully detected {len(detected)} ingredients!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Image analysis failed: {str(e)}")

with col_right:
    st.markdown("### 2. Detected / Editable Ingredients")
    
    # Render Ingredients in standard list with edit and remove options
    if st.session_state.ingredients:
        # Display items
        st.write("Edit, remove, or add new ingredients below to perfect the list:")
        
        # Render dynamic ingredient list
        updated_ings = []
        for idx, ing in enumerate(st.session_state.ingredients):
            c_input, c_del = st.columns([5, 1])
            with c_input:
                new_val = st.text_input(
                    f"Ingredient #{idx+1}", 
                    value=ing, 
                    key=f"ing_edit_{idx}", 
                    label_visibility="collapsed"
                )
                if new_val.strip():
                    updated_ings.append(new_val.strip())
            with c_del:
                if st.button("❌", key=f"ing_del_btn_{idx}", help=f"Remove {ing}"):
                    # Remove it immediately and rerun
                    st.session_state.ingredients.pop(idx)
                    st.rerun()
        
        st.session_state.ingredients = updated_ings
    else:
        st.info("No ingredients detected or added yet. Upload an image or add one manually below.")
        
    # Add new ingredient manually
    c_add_input, c_add_btn = st.columns([4, 1.2])
    with c_add_input:
        new_ing = st.text_input("New ingredient name", key="manual_add_input", placeholder="e.g., egg, milk, cheese", label_visibility="collapsed")
    with c_add_btn:
        if st.button("➕ Add Ingredient", use_container_width=True) and new_ing.strip():
            # Avoid duplicates
            clean_new_ing = new_ing.strip().lower()
            if clean_new_ing not in st.session_state.ingredients:
                st.session_state.ingredients.append(clean_new_ing)
                st.success(f"Added '{clean_new_ing}'!")
                st.rerun()
                
    st.markdown("---")
    
    # Dietary preference selection
    st.markdown("### 3. Dietary Preferences")
    dietary_options = [
        "No Preference", "Vegan", "Vegetarian", "Keto", 
        "Gluten Free", "Dairy Free", "Low Carb", "High Protein", "Paleo"
    ]
    
    # Fallback to horizontal radio buttons for Streamlit versions that lack pills
    selected_diet = st.radio("Select Diet Tag:", options=dietary_options, horizontal=True)
    
    st.markdown("---")
    
    # Generation Buttons
    st.markdown("### 4. Create Recipes")
    c_btn1, c_btn2 = st.columns([1, 1])
    
    with c_btn1:
        if st.button("🤖 Generate Full Recipe Direct", type="primary", use_container_width=True):
            if not st.session_state.ingredients:
                st.error("Please add or detect at least one ingredient first.")
            else:
                with st.spinner("Generating custom recipe (Llama-3.3-70b)..."):
                    try:
                        recipe = recipe_service.generate_recipe(st.session_state.ingredients, selected_diet)
                        st.session_state.full_recipe = recipe
                        st.session_state.suggestions = None # Clear suggestions
                        st.success("Recipe generated successfully!")
                    except Exception as e:
                        st.error(str(e))
                        
    with c_btn2:
        if st.button("💡 Get 3 Recipe Suggestions", use_container_width=True):
            if not st.session_state.ingredients:
                st.error("Please add or detect at least one ingredient first.")
            else:
                with st.spinner("Finding recipe ideas..."):
                    try:
                        suggestions = recipe_service.get_recipe_suggestions(st.session_state.ingredients, selected_diet)
                        st.session_state.suggestions = suggestions
                        st.session_state.full_recipe = None # Clear direct recipe
                        st.success("Fetched 3 recommendations!")
                    except Exception as e:
                        st.error(str(e))

st.markdown("---")

# --- Suggestions Section ---
if st.session_state.suggestions:
    st.markdown("## 💡 Suggested Dishes")
    st.write("Click on any recipe below to generate its full cooking recipe:")
    
    cols = st.columns(3)
    for idx, sug in enumerate(st.session_state.suggestions):
        with cols[idx]:
            # Custom card rendering using markdown/HTML with a standard Streamlit button inside
            st.markdown(f"""
            <div class="suggestion-card">
                <h4 style="color:#059669; margin-top:0;">{sug.get('title')}</h4>
                <p style="font-size:0.9rem; color:#4B5563; min-height: 80px;">{sug.get('description')}</p>
                <div style="margin-bottom:12px;">
                    <span class="info-tag">⏰ {sug.get('cookTime', 'N/A')}</span>
                    <span class="info-tag">📊 {sug.get('difficulty', 'N/A')}</span>
                </div>
                <div>
            """, unsafe_allow_html=True)
            
            # Show tags
            tags = sug.get('dietaryTags', [])
            for t in tags:
                st.markdown(f'<span class="diet-tag">{t}</span>', unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Action button inside the column to select this card
            if st.button(f"Generate '{sug.get('title')}'", key=f"select_sug_{idx}", type="secondary", use_container_width=True):
                with st.spinner(f"Preparing complete recipe for {sug.get('title')}..."):
                    try:
                        recipe = recipe_service.generate_recipe(
                            st.session_state.ingredients, 
                            selected_diet, 
                            recipe_title=sug.get('title')
                        )
                        st.session_state.full_recipe = recipe
                        st.session_state.suggestions = None
                        st.success(f"Full recipe for {recipe.get('title')} is ready!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

# --- Full Recipe Display Section ---
if st.session_state.full_recipe:
    recipe = st.session_state.full_recipe
    
    # Title & Metadata
    st.markdown(f"# 🍽️ {recipe.get('title')}")
    
    col_info1, col_info2, col_info3, col_info4 = st.columns(4)
    with col_info1:
        st.metric("Difficulty", recipe.get('difficulty', 'N/A'))
    with col_info2:
        st.metric("Prep Time", recipe.get('prepTime', 'N/A'))
    with col_info3:
        st.metric("Cook Time", recipe.get('cookTime', 'N/A'))
    with col_info4:
        st.metric("Servings", recipe.get('servings', 'N/A'))
        
    st.markdown("### Dietary Tags")
    for tag in recipe.get('dietaryTags', []):
        st.markdown(f'<span class="diet-tag" style="font-size:0.9rem; padding:6px 14px;">{tag}</span>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Ingredients & Instructions
    col_ing, col_inst = st.columns([1, 1.5], gap="large")
    
    with col_ing:
        st.markdown("### 🛒 Ingredients Required")
        ings = recipe.get('ingredients', [])
        if ings:
            for item in ings:
                if isinstance(item, dict):
                    st.markdown(f"- **{item.get('quantity', '')}** {item.get('name', '')}")
                else:
                    st.markdown(f"- {item}")
        else:
            st.write("No specific ingredients listed.")
            
    with col_inst:
        st.markdown("### 🍳 Instructions")
        instructions = recipe.get('instructions', [])
        for step in instructions:
            if isinstance(step, dict):
                st.markdown(f"**Step {step.get('step', '')}**")
                st.write(step.get('description', ''))
            else:
                st.write(step)
                
    st.markdown("---")
    
    # Nutrition Details
    st.markdown("### 📊 Nutrition Facts")
    nutrition = recipe.get('nutrition', {})
    
    col_nut1, col_nut2, col_nut3, col_nut4, col_nut5 = st.columns(5)
    with col_nut1:
        st.markdown(f"""
        <div class="nutrition-box">
            <div class="nutrition-val">{nutrition.get('calories', 'N/A')}</div>
            <div class="nutrition-label">Calories</div>
        </div>
        """, unsafe_allow_html=True)
    with col_nut2:
        st.markdown(f"""
        <div class="nutrition-box">
            <div class="nutrition-val">{nutrition.get('protein', 'N/A')}</div>
            <div class="nutrition-label">Protein</div>
        </div>
        """, unsafe_allow_html=True)
    with col_nut3:
        st.markdown(f"""
        <div class="nutrition-box">
            <div class="nutrition-val">{nutrition.get('carbs', 'N/A')}</div>
            <div class="nutrition-label">Carbs</div>
        </div>
        """, unsafe_allow_html=True)
    with col_nut4:
        st.markdown(f"""
        <div class="nutrition-box">
            <div class="nutrition-val">{nutrition.get('fat', 'N/A')}</div>
            <div class="nutrition-label">Fat</div>
        </div>
        """, unsafe_allow_html=True)
    with col_nut5:
        st.markdown(f"""
        <div class="nutrition-box">
            <div class="nutrition-val">{nutrition.get('fiber', 'N/A')}</div>
            <div class="nutrition-label">Fiber</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Serving Suggestions
    st.markdown("### 💡 Serving Suggestions")
    suggestions = recipe.get('servingSuggestions', [])
    for sugg in suggestions:
        st.markdown(f"- {sugg}")
        
    # Save Recipe Section
    st.markdown("---")
    if st.button("💾 Save Recipe to DB", type="primary", use_container_width=True):
        try:
            # Map structural field name differences from API output to model column names if any
            db_recipe_data = {
                "title": recipe.get("title"),
                "ingredients": recipe.get("ingredients"),
                "instructions": recipe.get("instructions"),
                "nutrition": recipe.get("nutrition"),
                "servings": recipe.get("servings"),
                "prep_time": recipe.get("prepTime"),
                "cook_time": recipe.get("cookTime"),
                "difficulty": recipe.get("difficulty"),
                "dietary_tags": recipe.get("dietaryTags"),
                "serving_suggestions": recipe.get("servingSuggestions")
            }
            saved_recipe = database.save_recipe(db_recipe_data)
            st.success(f"Recipe '{saved_recipe.title}' saved successfully to your library!")
        except Exception as e:
            st.error(f"Failed to save recipe: {str(e)}")
