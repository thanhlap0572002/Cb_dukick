import streamlit as st
from pymongo import MongoClient

# Khởi tạo MongoDB
def get_database():
    client = MongoClient('mongodb://localhost:27017/')
    return client['dukickData']

# Lấy danh sách các categories từ collection
def get_categories(collection_name):
    db = get_database()
    categories = db[collection_name].distinct("category")
    return categories

# Lấy nội dung files từ một category cụ thể
def get_files_content(collection_name, category):
    db = get_database()
    files_content = []
    documents = db[collection_name].find({"category": category})
    for doc in documents:
        if 'files_content' in doc:
            files_content.extend(doc['files_content'])
    return files_content
