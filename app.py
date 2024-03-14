from pdf_reader import read_data_from_pdf
from text_processing import get_text_chunks, get_embedding
from qdrant_connect import create_qdrant_collection, insert_data_into_qdrant
from lib import st, QdrantClient,time
from gen import generate_image_with_dalle,generate_answer_with_context,client,generate_prompt_from_video


#model_id = "all-MiniLM-L6-v2"

model_id = "all-mpnet-base-v2"
    
st.title("Ứng dụng Xử lý PDF và Sinh Ảnh")

# Upload PDF
pdf_files = st.file_uploader("Chọn file PDF để tải lên:", type=['pdf'], accept_multiple_files=True)
if pdf_files is not None and len(pdf_files) > 0:
    for pdf_file in pdf_files:
        raw_text = read_data_from_pdf(pdf_file)  
        st.write("Văn bản được trích xuất từ PDF:")
        st.text(raw_text[:10])  # show a little bit 

        text_chunks = get_text_chunks(raw_text)
        embeddings_points = get_embedding(text_chunks,model_id)

        create_qdrant_collection(client,"chatbot_with_qdrant")

        insert_data_into_qdrant(client, "chatbot_with_qdrant", embeddings_points)
#up video
video_file = st.file_uploader("Chọn file video để tải lên:", type=['mp4', 'avi', 'mov'])


user_question = st.text_input("Nhập câu hỏi của bạn:")

if user_question and st.button("Nhận Câu Trả Lời"):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    if video_file is not None:
        # Sử dụng hàm generate_prompt_from_video để tạo prompt từ video
        video_prompt = generate_prompt_from_video(video_file)
        
    
    # Tiếp tục sinh câu trả lời dựa vào chat_history và user_question
    answer = generate_answer_with_context(user_question + video_prompt, st.session_state['chat_history'])
    st.text_area("Câu trả lời:", value=answer, height=200)
    st.session_state['chat_history'].append(f"Bạn: {user_question}")
    st.session_state['chat_history'].append(f"Bot: {answer}")
    st.text_area("Lịch Sử Trò Chuyện", value="\n".join(st.session_state['chat_history']), height=300)


# Input text from user
user_input_text = st.text_input("Nhập mô tả văn bản:")
if user_input_text and st.button("Sinh Ảnh"):
    
    if 'image_history' not in st.session_state:
        st.session_state['image_history'] = []
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Sử dụng chat_history để tinh chỉnh prompt cho việc sinh ảnh mới
    image_url, timestamp = generate_image_with_dalle(user_input_text, st.session_state['chat_history'])
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

    

# Upload img (in the future)
