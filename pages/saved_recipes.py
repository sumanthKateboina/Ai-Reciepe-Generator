import os
import streamlit as st
import database

# Initialize database
database.init_db()

# --- Page Configuration ---
st.set_page_config(
    page_title="Saved Recipes Library",
    page_icon="📚",
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
    
    .library-title {
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .library-subtitle {
        font-size: 1.15rem !important;
        color: #6B7280;
        margin-bottom: 2.5rem;
    }
    
    /* Saved Recipe Card */
    .recipe-card {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .recipe-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -8px rgba(16, 185, 129, 0.15);
        border-color: #A7F3D0;
        background-color: #F0FDF4;
    }
    
    /* Tags */
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

# --- Main Page Content ---
st.markdown('<h1 class="library-title">📚 Saved Recipes Library</h1>', unsafe_allow_html=True)
st.markdown('<p class="library-subtitle">Browse, search, filter, and manage your collection of custom generated recipes.</p>', unsafe_allow_html=True)

# Filters Row
st.markdown("### 🔍 Search & Filters")
col_search, col_diet, col_diff, col_sort = st.columns([2, 1, 1, 1])

with col_search:
    search_q = st.text_input("Search by Recipe Name", placeholder="e.g., pasta, chicken...", key="saved_search")
with col_diet:
    diet_pref = st.selectbox(
        "Dietary Filter",
        options=["All", "No Preference", "Vegan", "Vegetarian", "Keto", "Gluten Free", "Dairy Free", "Low Carb", "High Protein", "Paleo"],
        key="saved_diet"
    )
with col_diff:
    diff_pref = st.selectbox(
        "Difficulty Filter",
        options=["All", "Easy", "Medium", "Hard"],
        key="saved_diff"
    )
with col_sort:
    sort_newest = st.selectbox(
        "Sort Order",
        options=["Newest First", "Oldest First"],
        key="saved_sort"
    )

# Query Database
sort_bool = (sort_newest == "Newest First")
recipes = database.get_all_recipes(
    search_query=search_q if search_q.strip() else None,
    dietary_preference=diet_pref,
    difficulty=diff_pref,
    sort_newest=sort_bool
)

st.markdown("---")

if not recipes:
    st.info("No saved recipes found matching your filters. Create a new recipe on the home page and save it!")
else:
    # Grid of saved recipes (3 columns)
    cols = st.columns(3)
    for idx, r in enumerate(recipes):
        col_idx = idx % 3
        with cols[col_idx]:
            st.markdown(f"""
            <div class="recipe-card">
                <div>
                    <h3 style="color:#059669; margin-top:0; font-size:1.35rem;">{r.title}</h3>
                    <div style="margin-bottom:12px;">
                        <span class="info-tag">📊 {r.difficulty or 'N/A'}</span>
                        <span class="info-tag">⏰ Prep: {r.prep_time or 'N/A'}</span>
                        <span class="info-tag">🍳 Cook: {r.cook_time or 'N/A'}</span>
                        <span class="info-tag">👥 Serves: {r.servings or 'N/A'}</span>
                    </div>
                    <div style="margin-bottom:16px;">
            """, unsafe_allow_html=True)
            
            # Draw dietary tags
            tags = r.dietary_tags or []
            for tag in tags:
                st.markdown(f'<span class="diet-tag">{tag}</span>', unsafe_allow_html=True)
                
            st.markdown("""
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Actions Row
            c_view, c_del = st.columns([1, 1])
            with c_view:
                if st.button("👁️ View Details", key=f"view_rec_{r.id}", use_container_width=True):
                    # Set selected recipe ID in session state and query parameters, then switch page
                    st.session_state.selected_recipe_id = r.id
                    st.query_params["id"] = str(r.id)
                    st.switch_page("pages/recipe_details.py")
            with c_del:
                if st.button("🗑️ Delete", key=f"del_rec_{r.id}", type="secondary", use_container_width=True):
                    if database.delete_recipe(r.id):
                        st.toast(f"Deleted '{r.title}'")
                        st.rerun()
                    else:
                        st.error("Failed to delete recipe.")
