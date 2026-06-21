import streamlit as st
import database

# Initialize database
database.init_db()

# --- Page Configuration ---
st.set_page_config(
    page_title="Recipe Details",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme and Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .diet-tag {
        display: inline-block;
        background-color: #D1FAE5;
        color: #065F46;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 12px;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
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

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/cooking-book.png", width=120)
    st.title("Navigation")
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

# --- Retrieve Recipe ID ---
# Fetch from query params first (allows bookmarks/reloads) or session state fallback
recipe_id_str = st.query_params.get("id")
recipe_id = None

if recipe_id_str:
    try:
        recipe_id = int(recipe_id_str)
    except ValueError:
        pass

if not recipe_id and st.session_state.selected_recipe_id:
    recipe_id = st.session_state.selected_recipe_id

# --- Display Recipe Details ---
if not recipe_id:
    st.warning("No recipe selected. Please go back to the Saved Recipes Library to choose a recipe.")
    if st.button("⬅️ Go to Saved Recipes", type="primary"):
        st.switch_page("pages/saved_recipes.py")
else:
    recipe = database.get_recipe_by_id(recipe_id)
    
    if not recipe:
        st.error(f"Recipe with ID {recipe_id} not found.")
        if st.button("⬅️ Go to Saved Recipes", type="primary"):
            st.switch_page("pages/saved_recipes.py")
    else:
        # Title and Header
        st.markdown(f"# 🍽️ {recipe.title}")
        
        # Actions row
        col_back, col_del = st.columns([4, 1])
        with col_back:
            if st.button("⬅️ Back to Saved Recipes Library", type="secondary"):
                st.switch_page("pages/saved_recipes.py")
        with col_del:
            if st.button("🗑️ Delete This Recipe", type="secondary", use_container_width=True):
                if database.delete_recipe(recipe.id):
                    st.toast(f"Deleted '{recipe.title}'")
                    st.switch_page("pages/saved_recipes.py")
                else:
                    st.error("Failed to delete recipe.")
                    
        st.markdown("---")
        
        # Metadata Metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Difficulty", recipe.difficulty or "N/A")
        with col_m2:
            st.metric("Prep Time", recipe.prep_time or "N/A")
        with col_m3:
            st.metric("Cook Time", recipe.cook_time or "N/A")
        with col_m4:
            st.metric("Servings", recipe.servings or "N/A")
            
        # Dietary tags
        tags = recipe.dietary_tags or []
        if tags:
            st.markdown("### Dietary Tags")
            for tag in tags:
                st.markdown(f'<span class="diet-tag">{tag}</span>', unsafe_allow_html=True)
            st.markdown("---")
            
        # Ingredients and Instructions
        col_left_side, col_right_side = st.columns([1, 1.5], gap="large")
        
        with col_left_side:
            st.markdown("### 🛒 Ingredients Required")
            ings = recipe.ingredients or []
            if ings:
                for item in ings:
                    if isinstance(item, dict):
                        st.markdown(f"- **{item.get('quantity', '')}** {item.get('name', '')}")
                    else:
                        st.markdown(f"- {item}")
            else:
                st.write("No ingredients listed.")
                
        with col_right_side:
            st.markdown("### 🍳 Instructions")
            instructions = recipe.instructions or []
            if instructions:
                for step in instructions:
                    if isinstance(step, dict):
                        st.markdown(f"**Step {step.get('step', '')}**")
                        st.write(step.get('description', ''))
                    else:
                        st.write(step)
            else:
                st.write("No instructions listed.")
                
        st.markdown("---")
        
        # Nutrition
        nutrition = recipe.nutrition or {}
        if nutrition:
            st.markdown("### 📊 Nutrition Facts")
            col_n1, col_n2, col_n3, col_n4, col_n5 = st.columns(5)
            with col_n1:
                st.markdown(f"""
                <div class="nutrition-box">
                    <div class="nutrition-val">{nutrition.get('calories', 'N/A')}</div>
                    <div class="nutrition-label">Calories</div>
                </div>
                """, unsafe_allow_html=True)
            with col_n2:
                st.markdown(f"""
                <div class="nutrition-box">
                    <div class="nutrition-val">{nutrition.get('protein', 'N/A')}</div>
                    <div class="nutrition-label">Protein</div>
                </div>
                """, unsafe_allow_html=True)
            with col_n3:
                st.markdown(f"""
                <div class="nutrition-box">
                    <div class="nutrition-val">{nutrition.get('carbs', 'N/A')}</div>
                    <div class="nutrition-label">Carbs</div>
                </div>
                """, unsafe_allow_html=True)
            with col_n4:
                st.markdown(f"""
                <div class="nutrition-box">
                    <div class="nutrition-val">{nutrition.get('fat', 'N/A')}</div>
                    <div class="nutrition-label">Fat</div>
                </div>
                """, unsafe_allow_html=True)
            with col_n5:
                st.markdown(f"""
                <div class="nutrition-box">
                    <div class="nutrition-val">{nutrition.get('fiber', 'N/A')}</div>
                    <div class="nutrition-label">Fiber</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            
        # Serving Suggestions
        suggestions = recipe.serving_suggestions or []
        if suggestions:
            st.markdown("### 💡 Serving Suggestions")
            for sugg in suggestions:
                st.markdown(f"- {sugg}")
