import google.generativeai as genai
from django.conf import settings
from PIL import Image
import io
import json

def analyze_product_image_with_ai(image_file):
    """
    Takes an uploaded Django InMemoryUploadedFile, passes it to Gemini 1.5 Flash Vision,
    and returns a structured JSON dictionary with title, description, and keywords.
    """
    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings.py")
            
        genai.configure(api_key=api_key)
        
        # Open the image using PIL so Gemini can read it
        img = Image.open(image_file)
        
        # Use the universally stable multimodal Vision model available to all keys
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = '''
        You are an expert luxury fashion copywriter and catalog manager.
        Look at this product image.
        Respond ONLY with a raw JSON block (do not add ```json markdown formatting).
        
        The JSON MUST have exactly these keys:
        - "title": A catchy, professional, e-commerce ready product name (max 5 words).
        - "description": A highly engaging, persuasive, and detailed 3-sentence e-commerce description highlighting the style, materials, and vibe of the product.
        - "category_suggestion": A single word summarizing the type (e.g. "Shoes", "Shirt", "Dress", "Accessories", "Kids").
        '''
        
        response = model.generate_content([prompt, img])
        text_response = response.text.strip()
        
        # Clean markdown formatting if the LLM adds it
        if text_response.startswith('```json'):
            text_response = text_response[7:]
        if text_response.endswith('```'):
            text_response = text_response[:-3]
            
        return json.loads(text_response.strip())
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {
            "title": "",
            "description": f"AI Generation Failed: {str(e)}",
            "category_suggestion": ""
        }
