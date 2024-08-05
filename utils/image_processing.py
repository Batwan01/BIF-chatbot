import tensorflow as tf
import numpy as np
from PIL import Image

# 모델 경로
FUNERAL_MODEL_PATH = './models/funeral_model.keras'
WEDDING_MODEL_PATH = './models/wedding_model.keras'

# 모델 로드
funeral_model = tf.keras.models.load_model(FUNERAL_MODEL_PATH)
wedding_model = tf.keras.models.load_model(WEDDING_MODEL_PATH)

# 모델의 입력 크기 확인
funeral_input_shape = funeral_model.input_shape[1:]  # (224, 224, 3) 등의 형태
wedding_input_shape = wedding_model.input_shape[1:]

# 이미지 전처리 함수
def preprocess_image(image, input_shape):
    img = image.resize((input_shape[1], input_shape[0]))
    img = np.array(img) / 255.0  # 정규화
    img = np.expand_dims(img, axis=0)  # 배치 차원 추가
    return img

# 이미지 분류 함수
def classify_image(image, event):
    if event == 'funeral':
        img = preprocess_image(image, funeral_input_shape)
        prediction = funeral_model.predict(img)[0][0]
        result = 'Appropriate' if prediction > 0.5 else 'Inappropriate'
        return {'funeral': result}
    
    elif event == 'wedding':
        img = preprocess_image(image, wedding_input_shape)
        prediction = wedding_model.predict(img)[0][0]
        result = 'Appropriate' if prediction > 0.5 else 'Inappropriate'
        return {'wedding': result}
