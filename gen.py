from lib import *

model_id = "all-mpnet-base-v2"
client = QdrantClient(
    url="https://785dad3b-d933-4697-87ad-93ccebc059d8.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="9GNe65ku1CMzizKksXJTM1Q_qqCfwjFgA-lv8-TpX4QwtWcGX2MHKQ",
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
    selected_frames = base64_frames[0::30]

    prompt_messages = [
        {
            "role": "user",
            "content": [
                "These are frames from a video that I want to upload. Generate a compelling description that I can upload along with the video.",
                *map(lambda x: {"image": x, "resize": 768}, selected_frames),
            ],
        },
    ]

    # Gửi yêu cầu đến OpenAI API
    params = {
        "model": "gpt-4-turbo",
        "messages": prompt_messages,
        "max_tokens": 300,
    }
    result = openai.ChatCompletion.create(**params)
    os.remove(temp_video_path)
    return result.choices[0].message['content']

def generate_with_text_prompt(query, text, chat_history):
    messages = [{
        "role": "user",
        "content": [{
            "type": "text",
            "text": "Xin chào, tôi có thể giúp gì cho bạn?"
        }]
    }]

    for msg in chat_history:
        messages.append({"role" : "user", "content" : str(msg)})
        
    messages.append({"role" : "user", "content" : text})
    messages.append({"role" : "user", "content" : query})

    completion = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=4096,
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

def generate_with_text_prompt_Customers(prompt, file_contents, chat_history):
    messages = []

    messages.append({
        "role": "system",
        "content": "Xin chào, tôi có thể giúp gì cho bạn?"
    })

    for msg in chat_history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    if file_contents:
        for file in file_contents:
            file_info = f"Tên file: {file['file_name']}, Nội dung mô tả: {file['content']}"
            messages.append({"role": "system", "content": file_info})


    print("Final messages list:", messages)  # In danh sách messages trước khi gọi API

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.75,
        top_p=1,
    )

    return response['choices'][0]['message']['content'].strip()