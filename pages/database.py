import streamlit as st
from pymongo import MongoClient
import time

def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    return client['dukickData']

def add_file_to_category(collection_name, category, file_name, content):
    db = get_database()
    # Trước khi thêm file, kiểm tra xem category đã tồn tại chưa
    if db[collection_name].find_one({"category": category}) is None:
        # Nếu category mới, tạo một document mới với category đó
        db[collection_name].insert_one({"category": category, "files_content": []})
    # Thêm file vào category
    db[collection_name].update_one({"category": category}, {"$push": {"files_content": {"file_name": file_name, "content": content}}})

def get_categories(collection_name):
    db = get_database()
    categories = db[collection_name].distinct("category")
    return categories

st.title('Upload File và Cập Nhật Data')

collection_name = st.selectbox('Chọn collection:', ('field','mood', 'type','thông tin khác'), key='selected_collection')

# Lấy danh sách categories dựa trên collection được chọn
categories = get_categories(collection_name)

# Cho phép người dùng chọn category hiện có hoặc nhập mới
existing_category = st.selectbox('Chọn category hiện có:', ('', *categories))
new_category = st.text_input('Hoặc nhập tên category mới:', key="new_category")

# Upload file
uploaded_file = st.file_uploader("Chọn file để upload:", type=['txt'], key="file_uploader")

# Nhập tên file (tùy chọn)
file_name_input = st.text_input('Nhập tên file (để trống để sử dụng tên file gốc):', key="file_name_input")

# Khi người dùng nhấn nút "Thêm vào MongoDB"
if st.button('Thêm vào MongoDB') and uploaded_file is not None:
    # Đọc nội dung file
    content = uploaded_file.getvalue().decode("utf-8")
    
    # Xác định tên file
    file_name = file_name_input if file_name_input else uploaded_file.name
    
    # Xác định category
    category = new_category if new_category else existing_category
    
    if category:  # Kiểm tra xem có category được chọn hoặc nhập mới không
        # Thêm vào MongoDB
        add_file_to_category(collection_name, category, file_name, content)
        st.success(f'File "{file_name}" đã được thêm vào category "{category}" trong collection "{collection_name}".')
        time.sleep(2)
        # Làm mới ứng dụng để upload file tiếp theo
        st.experimental_rerun()
    else:
        st.error('Vui lòng chọn hoặc nhập tên category.')
else:
    if st.session_state.get("file_uploader", None) is not None:
        # Nếu không có file nào được chọn nhưng uploader không rỗng (do rerun), reset uploader
        del st.session_state["file_uploader"]
