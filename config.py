import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_KEY")

gemini_client = genai.Client()
