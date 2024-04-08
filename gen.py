from lib import *

model_id = "all-mpnet-base-v2"
client = QdrantClient(
    url="https://785dad3b-d933-4697-87ad-93ccebc059d8.us-east4-0.gcp.cloud.qdrant.io:6333",
    api_key="O8iHYXhv7fuR1IW5vA8OLGeFEpQmr6W2lqPfQbUC5iglpcPAgyuG1A",
)
import cv2
import os
import tempfile



def save_temp_video(video_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmpfile:
        shutil.copyfileobj(video_file, tmpfile)
        return tmpfile.name
    
def generate_prompt_from_video(video_file):
    temp_video_path = save_temp_video(video_file)
    video = cv2.VideoCapture(temp_video_path)
    base64_frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
    video.release()

    # Chỉ lấy một số frame cụ thể để tạo prompt (ví dụ: mỗi 60 frames)
    selected_frames = base64_frames[0::90]

    prompt_messages = [
        {
            "role": "user",
            "content": [
                "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video.",
                *map(lambda x: {"image": x, "resize": 384}, selected_frames),
            ],
        },
    ]

    # Gửi yêu cầu đến OpenAI API
    params = {
        "model": "gpt-4-vision-preview",
        "messages": prompt_messages,
        "max_tokens": 300,
    }
    result = openai.ChatCompletion.create(**params)
    os.remove(temp_video_path)
    return result.choices[0].message['content']

def generate_with_text_prompt(query, text, chat_history):
    messages = [
        {"role": "system", "content": "This is a conversation with an AI."},
    ]
    for msg in chat_history:
        messages.append({"role" : "user", "content" : str(msg)})
        
    messages.append({"role" : "user", "content" : text})
    messages.append({"role" : "user", "content" : query})

    completion = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=messages,
        max_tokens=1000,
        temperature=0.75,
        top_p=1,
    )

    return completion.choices[0].message['content'].strip()

def generate_image_with_dalle(text, chat_history):
    # Gộp chat_history vào prompt
    # Lấy mô tả mới nhất từ chat_history để tinh chỉnh prompt, bạn có thể điều chỉnh logic này
    # để lựa chọn các phần mô tả phù hợp từ chat_history
    if chat_history:
        history_prompt = ". ".join([msg for msg in chat_history[-3:]])  # Lấy 3 mô tả cuối cùng
        combined_prompt = f"{history_prompt}. {text}"
    else:
        combined_prompt = text

    # Sinh ảnh từ DALL-E 3 sử dụng mô tả kết hợp
    response = openai.Image.create(
        model="dall-e-3",
        prompt=combined_prompt,
        n=1,  # Số lượng ảnh
        size="1024x1024"
    )
    image_url = response.data[0].url

    # Bạn cũng có thể thêm timestamp như đã đề cập trước đó nếu cần
    timestamp = int(time.time())

    return image_url, timestamp
