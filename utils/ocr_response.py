import requests
import json
import base64
import openai
from PIL import Image, ImageDraw, ImageFont
import os

# API 키 설정
google_api_key = os.getenv('GOOGLE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
# 이미지 파일 경로 설정
image_path = 'images\\menu.jpeg'

# 이미지 파일을 바이너리로 읽기
with open(image_path, 'rb') as image_file:
    image_content = image_file.read()

# 이미지 파일을 base64로 인코딩
image_base64 = base64.b64encode(image_content).decode('utf-8')

# Vision API 요청 본문 생성
request_payload = {
    "requests": [
        {
            "image": {
                "content": image_base64
            },
            "features": [
                {
                    "type": "TEXT_DETECTION"
                }
            ]
        }
    ]
}

# Vision API 엔드포인트 URL
url = f'https://vision.googleapis.com/v1/images:annotate?key={google_api_key}'

# Vision API 호출
response = requests.post(url, data=json.dumps(request_payload), headers={'Content-Type': 'application/json'})

# 응답 확인
if response.status_code == 200:
    response_data = response.json()
    texts = response_data['responses'][0].get('textAnnotations', [])
    extracted_text = texts[0]['description'] if texts else ""
    print("추출된 텍스트: ", extracted_text)
else:
    print("Error: ", response.status_code, response.text)

# OpenAI API 키 설정
openai.api_key = openai_api_key

# GPT API를 사용하여 텍스트 쉽게 바꾸기
def simplify_text_with_gpt(original_text):
    prompt = f"다음 텍스트를 더 쉽게 바꿔줘: {original_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message['content'].strip()

simplified_text = simplify_text_with_gpt(extracted_text)
print("쉽게 바꾼 텍스트: ", simplified_text)

# 이미지 열기
image = Image.open(image_path)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("arial.ttf", 15)  # 폰트와 크기 설정

# 기존 텍스트의 위치에 새 텍스트 그리기 (위치를 하드코딩하지 않기 위해 좌표 계산 필요)
draw.text((10, 10), simplified_text, fill="black", font=font)

# 수정된 이미지 저장
modified_image_path = 'C:/Users/박지완/Desktop/test/modified_image.jpeg'  # 올바른 확장자 사용
image.save(modified_image_path, format='JPEG')

print("수정된 이미지를 저장했습니다: ", modified_image_path)
