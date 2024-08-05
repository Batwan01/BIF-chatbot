import openai
import os
from PIL import Image
import pytesseract

# OpenAI API 키 설정
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"오류 발생: {e}"

def extract_text_from_image(image):
    try:
        text = pytesseract.image_to_string(image, lang='kor')
        return text
    except Exception as e:
        return f"텍스트 추출 중 오류 발생: {e}"

def summarize_text_with_gpt(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

def create_prompt(user_input):
    return f"사용자의 입력: {user_input}. 경계성 지능장애를 고려하여 쉽게 이해할 수 있는 답변을 생성합니다."
