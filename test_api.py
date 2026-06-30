import os
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
print("API key loaded:", api_key is not None)

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Say hello.")

print(response.text)