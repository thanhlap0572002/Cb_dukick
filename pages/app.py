from pdf_reader import read_data_from_pdf, get_text_chunks, get_embedding
from qdrant_connect import create_qdrant_collection, insert_data_into_qdrant, search_data_into_qdrant
from lib import st, QdrantClient,time
from gen import generate_image_with_dalle,generate_with_text_prompt,generate_prompt_from_video
from image_handler import generate_prompt_from_images
from utils import get_timestamp
from data_operations import load_messages, delete_chat_history, get_mysql_cursor, save_text_message, save_image_message, create_mysql_connection, get_all_chat_history_ids
from streamlit_chat import message
from get_data_mongo import get_files_content, get_categories,get_database

model_id = "all-mpnet-base-v2"

from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://785dad3b-d933-4697-87ad-93ccebc059d8.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="9GNe65ku1CMzizKksXJTM1Q_qqCfwjFgA-lv8-TpX4QwtWcGX2MHKQ",
)
@st.cache_resource

def toggle_pdf_chat():
    st.session_state.pdf_chat = True
    clear_cache()

def get_session_key():
    if st.session_state.session_key == "new_session":
        st.session_state.new_session_key = get_timestamp()
        return st.session_state.new_session_key
    return st.session_state.session_key

def delete_chat_session_history():
    delete_chat_history(st.session_state.session_key)
    st.session_state.session_index_tracker = "new_session"

def clear_cache():
    st.cache_resource.clear()

st.title("Ứng dụng Xử lý PDF và Sinh Ảnh")

if 'session_key' not in st.session_state:
    st.session_state['session_key'] = "new_session"

if "db_conn" not in st.session_state:
    st.session_state.session_key = "new_session"
    st.session_state.new_session_key = None
    st.session_state.session_index_tracker = "new_session"
    # Tạo kết nối MySQL 
    st.session_state.db_conn = create_mysql_connection()
    st.session_state.db_cursor = get_mysql_cursor(st.session_state.db_conn)

if st.session_state.session_key == "new_session" and st.session_state.new_session_key is not None:
    st.session_state.session_index_tracker = st.session_state.new_session_key
    st.session_state.new_session_key = None

st.sidebar.title("Chat Sessions")
chat_sessions = ["new_session"] + get_all_chat_history_ids()[::-1]

index = chat_sessions.index(st.session_state.session_index_tracker)
st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index)
delete_chat_col, clear_cache_col = st.sidebar.columns(2)
delete_chat_col.button("Delete Chat Session", on_click=delete_chat_session_history)
clear_cache_col.button("Clear Cache", on_click=clear_cache)

    
if 'upload_sessions' not in st.session_state:
    st.session_state['upload_sessions'] = {}

user_question = st.chat_input("Nhập câu hỏi của bạn:", key = 'user_question')
# Upload PDF
pdf_files = st.sidebar.file_uploader("Chọn file PDF để tải lên:", type=['pdf'], accept_multiple_files=True)
#up video
video_file = st.sidebar.file_uploader("Chọn file video để tải lên:", type=['mp4', 'avi', 'mov'])
################################################################################################ \/
# Giao diện
# st.sidebar.title('Lựa chọn bối cảnh')
# import random

# # Lựa chọn cho ba collections khác nhau
# collections = ['field', 'mood', 'type', 'thông tin khác']

# context = {}
# for collection in collections:
#     categories = get_categories(collection)
#     selected_category = st.sidebar.selectbox(f'Chọn category cho {collection}:', categories, key=f'category_select_{collection}')
#     files_content = get_files_content(collection, selected_category)
#     if files_content:
#         # Chọn ngẫu nhiên 3 nội dung file (hoặc ít hơn nếu không đủ 3)
#         selected_files = random.sample(files_content, min(3, len(files_content)))
#         for file in selected_files:
#             context[f"{collection}/{file['file_name']}"] = file['content']
st.sidebar.title('Lựa chọn bối cảnh')
import random

# Lựa chọn cho ba collections khác nhau
collections = ['field', 'mood', 'type', 'thông tin khác']

context = {}
for collection in collections:
    categories = get_categories(collection)
    
    # Đảm bảo rằng 'None' luôn có trong danh sách và là lựa chọn mặc định
    if 'None' not in categories:
        categories.insert(0, 'None')
        
    # Set 'None' là lựa chọn mặc định khi mới chạy chương trình
    default_index = categories.index('None')
    selected_category = st.sidebar.selectbox(f'Chọn category cho {collection}:', categories, index=default_index, key=f'category_select_{collection}')
    
    # Xử lý nội dung file nếu selected_category không phải là 'None'
    if selected_category != 'None':
        files_content = get_files_content(collection, selected_category)
        if files_content:
            # Chọn ngẫu nhiên 3 nội dung file (hoặc ít hơn nếu không đủ 3)
            selected_files = random.sample(files_content, min(3, len(files_content)))
            for file in selected_files:
                context[f"{collection}/{file['file_name']}"] = file['content']

################################################################################################# /\

image_files = st.sidebar.file_uploader("Chọn file ảnh để tải lên:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if pdf_files is not None and len(pdf_files) > 0:
    for pdf_file in pdf_files:
        raw_text = read_data_from_pdf(pdf_file)  
        text_chunks = get_text_chunks(raw_text)
        embeddings_points = get_embedding(text_chunks,model_id)
        print(embeddings_points)
        create_qdrant_collection(client,"chatbot_with_qdrant")
        insert_data_into_qdrant(client, "chatbot_with_qdrant", embeddings_points)

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if user_question :
    result = search_data_into_qdrant(client, "chatbot_with_qdrant", user_question, model_id)
    save_text_message(get_session_key(), "human", user_question)
    st.write(user_question)
    
    
    combined_prompt = "\n".join([message['content'] for message in load_messages(get_session_key())])
    if video_file:      
        
        combined_prompt += "\n\nMô tả video:"
        combined_prompt += generate_prompt_from_video(video_file)
        
    if pdf_files:
        combined_prompt = f" phân tích kịch bản chính của các mô tả và từ đó sáng tạo cho kịch bản mới : {context}"
        combined_prompt +=  str(result)
        # for pdf_file in pdf_files:
        #     raw_text = read_data_from_pdf(pdf_file)
        #     #save_text_message(get_session_key(), "human", raw_text)
        #     combined_prompt += raw_text
    if image_files:
        save_text_message(get_session_key(), "human", user_question)
        for image in image_files:
            save_image_message(get_session_key(), "human", image.getvalue())
        combined_prompt += "\n\n mô tả hình ảnh:"
        combined_prompt += generate_prompt_from_images(image_files)
            
    answer = generate_with_text_prompt(user_question, combined_prompt, st.session_state['chat_history'])
    save_text_message(get_session_key(), "bot", answer)

# Input text from user
user_input_text = st.text_input("Nhập mô tả văn bản sinh ảnh:")
if user_input_text and st.button("Sinh Ảnh"):
    save_text_message(get_session_key(),'human', user_input_text)
    
    if 'image_history' not in st.session_state:
        st.session_state['image_history'] = []
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Sử dụng chat_history để tinh chỉnh prompt cho việc sinh ảnh mới
    image_url, timestamp = generate_image_with_dalle(user_input_text, st.session_state['chat_history'])
    save_image_message(get_session_key(),"bot",  image_url)
    st.image(image_url, caption="Ảnh được sinh ra từ mô tả")
    
    # Cập nhật image_history với thông tin mới, bao gồm cả timestamp
    st.session_state['image_history'].append({"url": image_url, "timestamp": timestamp})
    # Cập nhật chat_history với mô tả mới
    st.session_state['chat_history'].append(user_input_text)

# Hiển thị lịch sử hình ảnh
if 'image_history' in st.session_state and st.session_state['image_history']:
    st.write("Lịch Sử Hình Ảnh:")
    for image_info in st.session_state['image_history']:
        image_url = image_info["url"]  # Truy cập URL từ thông tin hình ảnh
        # Bạn có thể format caption để bao gồm timestamp nếu muốn
        caption = f"Ảnh được sinh ra từ mô tả, tạo lúc {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(image_info['timestamp']))}"
        st.image(image_url, caption=caption, use_column_width=True)


#show chat session

if (st.session_state.session_key != "new_session") != (st.session_state.new_session_key != None):

    chat_history_messages = load_messages(get_session_key())

    for message in chat_history_messages:
        with st.chat_message(name=message["sender_type"]):
                if message["message_type"] == "text":
                    st.write(message["content"])
                if message["message_type"] == "image":
                    st.image(message["content"])

    if (st.session_state.session_key == "new_session") and (st.session_state.new_session_key != None):
        st.rerun()
