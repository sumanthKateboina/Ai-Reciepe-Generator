import os
import base64
from PIL import Image
import io

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

def ensure_upload_dir():
    """Ensure the uploads directory exists."""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

def validate_image(uploaded_file) -> tuple[bool, str]:
    """
    Validate the uploaded file:
    - Checks file extension (.jpg, .jpeg, .png, .webp)
    - Checks file size (Max 10 MB)
    Returns (is_valid, error_message).
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    # Validate file extension
    file_name = uploaded_file.name.lower()
    valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
    if not file_name.endswith(valid_extensions):
        return False, f"Invalid file format. Allowed formats: {', '.join(valid_extensions)}"

    # Validate size (10 MB = 10 * 1024 * 1024 bytes)
    max_size_bytes = 10 * 1024 * 1024
    # In Streamlit, uploaded_file is a BytesIO-like object which has a size attribute
    file_size = getattr(uploaded_file, 'size', 0)
    if file_size > max_size_bytes:
        return False, f"File size exceeds the 10 MB limit. Your file is {file_size / (1024 * 1024):.2f} MB."

    # Verify if it can be opened as an image by PIL
    try:
        # Reset pointer just in case
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        img.verify()
        # Reset pointer after verify() as it closes the file or advances the pointer
        uploaded_file.seek(0)
    except Exception as e:
        return False, f"Uploaded file is not a valid image. Error: {str(e)}"

    return True, ""

def save_temp_image(uploaded_file) -> str:
    """
    Save the uploaded file temporarily inside the uploads directory.
    Returns the absolute path to the saved file.
    """
    ensure_upload_dir()
    
    # Save the file with its original name or a safe name
    safe_name = f"temp_{uploaded_file.name}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    
    uploaded_file.seek(0)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return file_path

def get_image_base64(file_path_or_buffer) -> str:
    """
    Convert an image file path or BytesIO buffer into a base64 string.
    """
    if isinstance(file_path_or_buffer, str):
        # It's a file path
        with open(file_path_or_buffer, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    else:
        # It's a file buffer
        file_path_or_buffer.seek(0)
        return base64.b64encode(file_path_or_buffer.read()).decode('utf-8')

def cleanup_temp_files():
    """Delete all files inside the uploads directory."""
    if os.path.exists(UPLOAD_DIR):
        for file_name in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting temp file {file_path}: {e}")
