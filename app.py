import os
import base64
from flask import Flask, request, jsonify, render_template
from utils.image_processing import classify_image
from utils.chatbot_response import generate_response, create_prompt, summarize_text_with_gpt #extract_text_from_image, 
from utils.ocr_response import extract_text_using_google_vision, simplify_text_with_gpt, save_text_to_jpeg  # 추가된 부분
from PIL import Image
from io import BytesIO
import openai

app = Flask(__name__)

# OpenAI API 키 설정
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
openai.api_key = api_key

@app.route('/')
def index():
    return render_template('index.html')

def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def handle_image_prompt(prompt, image):
    if "요약해줘" in prompt:
        summary = summarize_text_with_gpt(simplified_text)
        return f"요약 내용: {summary}"

    if "장례식장" in prompt:
        result = classify_image(image, event='funeral')
        if result['funeral'] == 'Appropriate':
            response = generate_response("대한민국 장례식장에 대한 예의에 대해 짧게 설명해줘, 대답은 안 해도 돼")
            return "장례식장에 적합한 옷차림입니다!<br>", response
        else:
            response = generate_response("대한민국 장례식장 복장에 대해 짧게 설명해줘, 대답은 안 해도 돼")
            return "장례식장에 적합하지 않은 옷차림입니다!<br>", response
        
    if "결혼식장" in prompt:
        result = classify_image(image, event='wedding')
        if result['wedding'] == 'Appropriate':
            response = generate_response("대한민국 결혼식장에 대한 예의에 대해 짧게 설명해줘, 관계에 따른 축의금도 말해줘, 대답은 안 해도 돼")
            return "결혼식장에 적합한 옷차림입니다!<br>", response
        else:
            response = generate_response("대한민국 결혼식장에 복장에 대해 짧게 설명해줘, 대답은 안 해도 돼")
            return "결혼식장에 적합한 옷차림이 아닙니다!<br>", response
        
    if "설명해줘" in prompt:
        try:
            # Google Vision API를 통해 텍스트 추출
            extracted_text = extract_text_using_google_vision(image)
            # GPT를 통해 텍스트를 쉽게 변환
            simplified_text = simplify_text_with_gpt(extracted_text)
            jpeg_path = 'image/simplified_text.jpeg'
            save_text_to_jpeg(simplified_text, jpeg_path)
            # 결과를 JPEG로 저장
            simplified_text = simplified_text.replace("\n", "<br>")
            return "쉽게 설명해 드릴게요!.", simplified_text
        except Exception as e:
            return f"텍스트 변환 및 이미지 생성 중 오류 발생: {e}", None


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.form
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "메시지를 입력해주세요."})

        if 'file' in request.files and request.files['file'].filename != '':
            image_file = request.files['file']
            image = Image.open(image_file.stream)
            response_text = handle_image_prompt(prompt, image)
            if response_text:
                image_base64 = encode_image(image)
                return jsonify({"response": response_text, "image": image_base64})

        if any(keyword in prompt for keyword in ["설명해줘", "장례식장", "결혼식장"]):
            return jsonify({"response": "이미지를 업로드 해주세요."})

        prompt = create_prompt(prompt)
        response = generate_response(prompt)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
