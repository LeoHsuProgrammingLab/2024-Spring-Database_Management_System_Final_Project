import google.generativeai as genai
import os
from dotenv import load_dotenv

# Set the API key
def set_api_key(prompt = 'Hello World'):
    load_dotenv()
    api_key = os.getenv('GENAI_API_KEY')
    if api_key is None:
        print('Please set the environment variable')
    
    genai.configure(api_key = api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    print("'''\n", response, "\n'''")

if __name__ == '__main__':
    prompt = 'Help me find all the related topic with distributed system'
    set_api_key(prompt)