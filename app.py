import os
import base64
from flask import Flask, request, jsonify, render_template
from utils.image_processing import classify_image
from utils.chatbot_response import generate_response, create_prompt, extract_text_from_image, summarize_text_with_gpt
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
    if "설명해줘" in prompt:
        text = extract_text_from_image(image)
        summary = summarize_text_with_gpt(text)
        return f"설명서 내용: {summary}"

    if "장례식장" in prompt:
        result = classify_image(image, event='funeral')
        if result['funeral'] == 'Appropriate':
            return "장례식장에 적합한 옷차림입니다! (고인에 대한 언급 자제 등 예의 설명)"
        else:
            return "장례식장에 적합한 옷차림이 아닙니다! 검정색에 가까운 옷을 선택해야 하고, 노출이 심한 옷은 장례식에 적합하지 않아요!"

    if "결혼식장" in prompt:
        result = classify_image(image, event='wedding')
        if result['wedding'] == 'Appropriate':
            return "결혼식장에 적합한 옷차림입니다! (결혼식에 대한 예의 설명)"
        else:
            return "결혼식장에 적합한 옷차림이 아닙니다! 흰색 옷과 노출이 심한 옷은 결혼식에 적합하지 않아요!"
    return None

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
        print(prompt)
        response = generate_response(prompt)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
