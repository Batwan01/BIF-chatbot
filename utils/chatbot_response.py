import openai
import os
from PIL import Image
import pytesseract

# OpenAI API 키 설정
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
openai.api_key = api_key

def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=1.0
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"오류 발생: {e}"

def extract_text_from_image(image):
    try:
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text
    except Exception as e:
        return f"텍스트 추출 중 오류 발생: {e}"

def summarize_text_with_gpt(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"요약해줘 한국어로:\n\n{text}"}
            ],
            max_tokens=500,
            temperature=1.0
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"요약 중 오류 발생: {e}"

def create_prompt(user_input):
    return f"사용자의 입력: {user_input}. 이 사용자는 초등학교 5학년 수준의 이해력을 가지고 있으므로, 어려운 말은 이해하지 못합니다. 쉽게 설명해 주세요. 초등학교 5학년 수준의 이해력은 언급하지 않았으면 좋겠습니다."