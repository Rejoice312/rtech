
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


GEMINI_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-3.5-flash',
    'gemini-3.1-flash-lite',
]

load_dotenv()
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']

class Gemini:
    def __init__(self, api_key = GEMINI_API_KEY, model = 'gemini-2.5-flash'):
        self.client = genai.Client(api_key = api_key)
        self.model = model

    def reply(self, prompt, web_search = False):
        if not web_search:
            response = self.client.models.generate_content(
            model=self.model,
            contents= prompt,
            )
        else:
            response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
            )
        return response.text