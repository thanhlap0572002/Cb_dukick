import base64
import cv2
import numpy as np
from lib import *

def generate_prompt_from_images(image_files):
    base64_images = []
    for uploaded_file in image_files:
        # Đọc nội dung file dưới dạng bytes
        file_bytes = uploaded_file.read()

        # Mã hóa nội dung file sang base64
        encoded_image = base64.b64encode(file_bytes).decode("utf-8")
        base64_images.append(encoded_image)

    # Tạo prompt với danh sách ảnh đã mã hóa
    prompt_messages = [
        {
            "role": "user",
            "content": [
                "These are images that I want to upload. Generate a compelling description that I can upload along with the images.",
                *map(lambda x: {"image": x, "resize": 384}, base64_images),
            ],
        },
    ]

    # Gửi yêu cầu đến OpenAI API (giả định bạn đã thiết lập môi trường cho openai)
    params = {
        "model": "gpt-4-vision-preview",
        "messages": prompt_messages,
        "max_tokens": 500,
    }
    result = openai.ChatCompletion.create(**params)
    
    return result.choices[0].message['content']
