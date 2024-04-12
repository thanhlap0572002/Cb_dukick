import streamlit as st
from pymongo import MongoClient
from datetime import datetime
from gen import generate_with_text_prompt_Customers
from lib import *

# Tạo tiêu đề cho sidebar trong Streamlit
st.sidebar.title("Create Second Brain")

def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    return client['Custom_brain']

def get_collection_names():
    db = get_database()
    return db.list_collection_names()

def create_collection(collection_name):
    db = get_database()
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        st.sidebar.success(f"Collection '{collection_name}' đã được tạo.")
    else:
        st.sidebar.error("Collection này đã tồn tại.")

existing_collections = get_collection_names()
collection_choice = st.sidebar.selectbox("Chọn Collection có sẵn hoặc nhập mới bên dưới:", [""] + existing_collections)
collection_name = st.sidebar.text_input("Hoặc nhập tên Collection mới", key="new_collection")
target_collection = collection_name if collection_name else collection_choice

def add_file_to_category(collection_name, category, file_name, content):
    db = get_database()
    if db[collection_name].find_one({"category": category}) is None:
        db[collection_name].insert_one({"category": category, "files_content": []})
    db[collection_name].update_one({"category": category}, {"$push": {"files_content": {"file_name": file_name, "content": content}}})

def get_categories(collection_name):
    db = get_database()
    if collection_name:
        return db[collection_name].distinct("category")
    return []

def get_files_in_category(collection_name, category):
    db = get_database()
    result = db[collection_name].find_one({"category": category})
    if result:
        return result["files_content"]
    return []

uploaded_file = st.sidebar.file_uploader("Chọn file để upload", type=['txt', 'pdf', 'png', 'jpg', 'jpeg'])
if uploaded_file is not None:
    existing_categories = get_categories(target_collection)
    current_time = datetime.now().strftime("%Y-%m-%d")
    category_choice = st.sidebar.selectbox("Chọn Category hoặc nhập mới bên dưới:", [""] + existing_categories, index=0, format_func=lambda x: x if x else "Nhập mới")
    category_name = st.sidebar.text_input("Hoặc nhập tên Category mới", value=current_time if not category_choice else "")
    file_name = uploaded_file.name
    file_extension = file_name.split('.')[-1].lower()  # Get the file extension

    if st.sidebar.button("Upload File"):
        if file_extension in ['png', 'jpg', 'jpeg']:
            file_content = uploaded_file.getvalue()  # For images, keep as binary
            add_file_to_category(target_collection, category_name if category_name else category_choice, file_name, file_content)
            st.sidebar.success("Hình ảnh đã được upload thành công.")
        elif file_extension in ['txt', 'pdf']:
            file_content = uploaded_file.getvalue().decode("utf-8")  # For text, read as string (UTF-8)
            add_file_to_category(target_collection, category_name if category_name else category_choice, file_name, file_content)
            st.sidebar.success("Tài liệu đã được upload thành công.")
        else:
            st.sidebar.error("Định dạng file không được hỗ trợ.")

selected_category = st.sidebar.selectbox("Chọn Category để xem nội dung:", [""] + get_categories(target_collection), format_func=lambda x: x if x else "Chọn một category")

# giao diện chính 
st.title("thông tin truy xuất")
box_chat = st.container(height=700)
# Khởi tạo session state để giữ nội dung chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        

if  st.sidebar.button("Hiển thị nội dung"):
    if selected_category:
        file_contents = get_files_in_category(target_collection, selected_category)
        with box_chat:
            for file in file_contents:
                st.write(f"Tên file: {file['file_name']}")
                if file['file_name'].endswith((".png", ".jpg", ".jpeg")):
                    st.image(file['content'], caption=file['file_name'])
                else:
                    st.write("Nội dung:")
                    st.code(file['content'])
  
                    
    else:
        st.error("Vui lòng chọn một category để hiển thị.")

# Phản ứng với người dùng nhập liệu
if prompt := st.chat_input("What is up?"):
    # Hiển thị tin nhắn người dùng
    st.chat_message("user").markdown(prompt)
    # Thêm tin nhắn người dùng vào lịch sử trò chuyện
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Lấy nội dung file theo danh mục đã chọn
    file_contents = get_files_in_category(target_collection, selected_category) 

    # Gọi hàm generate_with_text_prompt để tạo phản hồi
    response = generate_with_text_prompt_Customers(prompt, file_contents, st.session_state['messages'])
    
    # Hiển thị phản hồi của trợ lý
    with st.chat_message("assistant"):
        st.markdown(response)
    # Thêm phản hồi trợ lý vào lịch sử trò chuyện
    st.session_state.messages.append({"role": "assistant", "content": response})

