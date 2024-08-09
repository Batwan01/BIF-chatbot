import requests
import json
import base64
import openai
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO  

# OpenAI API 키 설정
openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key

# Google Vision API 키 설정
google_api_key = ''

# Vision API를 호출하여 이미지에서 텍스트를 추출하는 함수
def extract_text_using_google_vision(image):
    # 이미지를 바이너리로 변환
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_content = buffered.getvalue()

    # 이미지를 base64로 인코딩
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

    # 응답 처리
    if response.status_code == 200:
        response_data = response.json()
        texts = response_data['responses'][0].get('textAnnotations', [])
        return texts[0]['description'] if texts else ""
    else:
        raise Exception(f"Vision API 호출 실패: {response.status_code} - {response.text}")

# GPT API를 사용하여 텍스트를 쉽게 바꾸는 함수
def simplify_text_with_gpt(original_text):
    prompt = f"Please rewrite the following text in Korean, using language that even elementary school students can easily understand. Use polite and formal language. While maintaining the original content and structure, please add any additional explanations that may help clarify the meaning: {original_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    return response['choices'][0]['message']['content'].strip()

def save_text_to_jpeg(text, output_path, width=900, initial_height=600, font_size=15, margin=10, line_spacing=5):
    # 텍스트를 줄바꿈하여 이미지에 맞추기 위해 준비
    font_path = r"c:\Windows\Fonts\MALGUNSL.TTF"  # 이 경로는 사용자의 시스템에 맞게 조정해야 합니다.
    font = ImageFont.truetype(font_path, font_size)
    
    # 흰색 배경의 임시 이미지 생성
    temp_image = Image.new('RGB', (width, initial_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(temp_image)

    # 텍스트 줄바꿈 및 총 높이 계산
    lines = []
    max_width = width - 2 * margin
    for line in text.splitlines():
        words = line.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if draw.textlength(test_line, font=font) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

    # 전체 텍스트의 높이를 계산
    total_height = len(lines) * (font.getbbox('A')[3] + line_spacing) + 2 * margin

    # 최종 이미지 생성
    final_height = max(total_height, initial_height)  # 최소 높이는 initial_height로 설정
    image = Image.new('RGB', (width, final_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 텍스트를 이미지에 그리기
    y_offset = margin
    for line in lines:
        draw.text((margin, y_offset), line, font=font, fill=(0, 0, 0))
        y_offset += font.getbbox(line)[3] + line_spacing

    # 이미지 저장
    image.save(output_path, format='JPEG')
