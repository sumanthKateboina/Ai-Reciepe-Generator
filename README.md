# 🍳 AI Powered Recipe Generator

An elegant, fully featured AI-powered recipe generator application built with **Python**, **Streamlit**, **SQLite**, and **Groq Cloud APIs**. 

Never open your fridge and wonder what to cook again. Simply snap or upload a photo of your available ingredients, and let the AI instantly suggest or generate complete recipes tailored to your dietary preferences.

---

## 🚀 Key Features

* **AI Image Ingredient Detection**: Upload images in `.jpg`, `.jpeg`, `.png`, or `.webp` format (up to 10MB). Powered by Groq's Vision model `meta-llama/llama-4-scout-17b-16e-instruct`.
* **Editable Ingredient Dashboard**: Dynamically edit, add, or delete detected ingredients in real-time before generating recipes.
* **Dietary Preferences Filtering**: Select from 9 dietary tags including *Vegan, Vegetarian, Keto, Gluten-Free, Dairy-Free, Low-Carb, High-Protein, Paleo, or No Preference*.
* **Compact Recipe Recommendations**: Request 3 different tailored recipe suggestions with preparation time, difficulty level, and tags.
* **Full Detailed Recipe Generator**: Generate step-by-step cooking instructions, exact ingredient quantities, serving counts, preparation/cook time, and professional serving suggestions.
* **Granular Nutrition Analysis**: Provides beautiful visual dashboards showing *Calories, Protein, Carbs, Fat, and Fiber*.
* **Permanent Library Database**: Save generated recipes to an SQLite database managed with **SQLAlchemy ORM**.
* **Saved Recipes Library**: View, delete, sort (newest/oldest), search, and filter saved recipes by diet and difficulty in a searchable grid dashboard.

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python 3.12+
* **Database**: SQLite (SQLAlchemy ORM)
* **AI Model Engine**: Groq Cloud API
  * **Vision (Ingredient Detection)**: `meta-llama/llama-4-scout-17b-16e-instruct`
  * **Text Generation (Recipes & Ideas)**: `llama-3.3-70b-versatile`
* **Image Processing**: Pillow
* **Data Handling**: Pandas

---

## 📁 Project Directory Structure

```text
ai_recipe_generator/
├── app.py                  # Main Streamlit entrance and Home dashboard
├── database.py             # SQLite connection initialization and SQLAlchemy CRUD operations
├── models.py               # SQLAlchemy ORM Model schemas for table mappings
├── groq_service.py         # Groq API vision/text integration and JSON sanitizers
├── recipe_service.py       # Orchestration layer connecting services together
├── image_service.py        # File validation and Base64 encoder helper
├── requirements.txt        # Project packages dependencies definition
├── .gitignore              # Ignored local databases, settings, and credential folders
├── .env                    # Environment local configurations (Groq key, DB paths)
├── assets/                 # App assets and static designs
├── uploads/                # Temporary directory for uploaded image previews
└── pages/                  # Streamlit Multi-page pages
    ├── saved_recipes.py    # List, search, filter, and delete saved recipes dashboard
    └── recipe_details.py   # Full detailed recipe display panel
```

---

## ⚙️ Local Installation & Setup

Follow these steps to run the application locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/sumanthKateboina/Ai-Reciepe-Generator.git
cd Ai-Reciepe-Generator
```

### 2. Configure Environment Variables
Create a file named `.env` in the root folder (or rename the existing placeholder template) and insert your Groq API Key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
DATABASE_URL=sqlite:///recipes.db
```

### 3. Install Dependencies
It is recommended to use a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 4. Run the Application
Start the local Streamlit server:
```bash
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser to start generating delicious recipes!

---

## 🐳 Running with Docker

You can run the application in a self-contained container using the provided `Dockerfile` and `docker-compose.yml`.

### Docker Compose (Recommended)
1. Build and start the container:
   ```bash
   docker-compose up --build -d
   ```
2. The application will be running at [http://localhost:8501](http://localhost:8501).

### Standalone Docker Build
1. Build the image:
   ```bash
   docker build -t ai-recipe-generator .
   ```
2. Run the container, passing your Groq API Key:
   ```bash
   docker run -p 8501:8501 -e GROQ_API_KEY="your_api_key_here" ai-recipe-generator
   ```

---

## ☁️ Cloud Deployment Guides

### 1. Render or Railway (Docker Container)
These platforms can read the `Dockerfile` automatically:
1. Connect your GitHub repository to [Render](https://render.com) or [Railway](https://railway.app).
2. Create a new **Web Service** (Render) or **Service** (Railway).
3. Set the build/runtime environment to **Docker**.
4. Define the Environment Variable in their panel:
   - `GROQ_API_KEY`: `<Your Groq API Key>`
5. Deploy! The container will build and expose port `8501` automatically.

---

## 🔒 Security Notice
The `.env` file containing your private **Groq API Key** and your local database (`recipes.db`) are automatically excluded from version control by the `.gitignore` configuration. Never commit these files to public repositories.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
