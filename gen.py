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

    # Chỉ lấy một số frame cụ thể để tạo prompt (ví dụ: mỗi 50 frames)
    selected_frames = base64_frames[0::50]

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
        "model": "gpt-4-vision-preview",
        "messages": prompt_messages,
        "max_tokens": 500,
    }
    result = openai.ChatCompletion.create(**params)
    os.remove(temp_video_path)
    return result.choices[0].message['content']

def generate_answer_with_context(query, chat_history ):
    model = SentenceTransformer(model_id)
    # embed query 
    query_embeddings = model.encode(query).tolist()

    # compare search query emb 
    search_result = client.search(
        collection_name="chatbot_with_qdrant",
        query_vector=query_embeddings,  #  embeddings type list
        limit=1  # most results
    )
    
    # Kiểm tra nếu có kết quả tìm kiếm
    if search_result and 'hits' in search_result[0]:  # Giả sử search_result là một danh sách và bạn quan tâm đến phần tử đầu tiên
        hits = search_result[0]['hits']
    # Xử lý hits ở đây
    else:
        context_text = "Không tìm thấy thông tin liên quan trong tài liệu."

    messages = [
        {"role": "system", "content": "This is a conversation with an AI."},
    ]
    for msg in chat_history:
        messages.append({"role" : "user", "content" : msg})
        
    messages.append({"role" : "user", "content" : query})

    # Sử dụng OpenAI API để sinh văn bản từ prompt
    completion = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        max_tokens=2000,
        temperature=1.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return completion.choices[0].message['content'].strip()


# def generate_image_with_dalle(text,chat_history):
    
#     # Sinh ảnh từ DALL-E 3 sử dụng mô tả kết hợp
#     response = openai.Image.create(
#         model = "dall-e-3",
#         prompt=text,
#         n=1,  # Số lượng ảnh
#         size="1024x1024"
#     )
#     image_url = response.data[0].url

#     return image_url
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


# def generate_image_with_image(image_emb,text_emb):
#     model = SentenceTransformer(model_id)
#     # embed query 
#     query_embeddings = model.encode(text_emb)
    
    
    
