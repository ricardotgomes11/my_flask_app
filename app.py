import openai
import asyncio
import ssl
import certifi
import os
from aiohttp import ClientSession, TCPConnector, ClientConnectionError, ClientPayloadError
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

async def generate_response(prompt):
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = TCPConnector(ssl=ssl_context)

        async with ClientSession(connector=connector) as session:
            headers = {
                "Authorization": f"Bearer {openai.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
            async with session.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    logger.error(f"Request failed with status code {response.status}")
                    return f"Request failed with status code {response.status}"
    except openai.error.OpenAIError as e:
        logger.error(f"An OpenAI error occurred: {e}")
        return f"An OpenAI error occurred: {e}"
    except asyncio.TimeoutError:
        logger.error("The request timed out. Please try again.")
        return "The request timed out. Please try again."
    except ClientConnectionError as e:
        logger.error(f"A connection error occurred: {e}")
        return f"A connection error occurred: {e}"
    except ClientPayloadError as e:
        logger.error(f"A payload error occurred: {e}")
        return f"A payload error occurred: {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.json.get('prompt')
    response = asyncio.run(generate_response(prompt))
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(port=5002, debug=True)

