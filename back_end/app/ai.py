from dotenv import load_dotenv
from openai import OpenAI
import re
import os

load_dotenv()
client = OpenAI()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def send_messages(messages):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": messages
            }
        ],
        temperature=1,
        max_tokens=725,
        top_p=0.7,
        frequency_penalty=2,
        presence_penalty=1,
        stream=True
    )

    return response

def detect_chinese_punctuation(text):
    """
    Detects Chinese punctuation marks in the given text.

    Args:
    - text (str): The input text to search for Chinese punctuation marks.

    Returns:
    - list: A list of Chinese punctuation marks found in the text.
    """
    # Regular expression pattern for Chinese punctuation marks
    # chinese_punctuation_pattern = r'[，。、；：？！“”‘’（）【】《》「」『』【】〔〕﹁﹂〈〉《》〖〗…—～·﹏]'
    chinese_punctuation_pattern = r'[，。、；：？！]'
    
    # Find all occurrences of Chinese punctuation marks in the text
    chinese_punctuation_marks = re.findall(chinese_punctuation_pattern, text)
    
    return chinese_punctuation_marks