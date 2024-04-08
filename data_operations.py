import mysql.connector

def create_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="thanhlap2002",
        database="chatbotdukick"
    )
def get_mysql_cursor(connection):
    return connection.cursor()

def delete_chat_history(chat_history_id):
    conn = create_mysql_connection()  # Tạo kết nối mới
    cursor = conn.cursor()  # Tạo cursor từ kết nối
    query = "DELETE FROM messages WHERE chat_history_id = %s"
    cursor.execute(query, (chat_history_id,))  # Sử dụng %s như placeholder cho MySQL
    conn.commit()  # Gọi commit() trên đối tượng kết nối
    cursor.close()  # Đóng cursor khi hoàn thành
    conn.close()  # Đóng kết nối khi hoàn thành
    print(f"đã xóa {chat_history_id} thành công")

def get_all_chat_history_ids():
    conn = create_mysql_connection()  # Tạo kết nối mới
    cursor = conn.cursor()  # Tạo cursor từ kết nối
    query = "SELECT DISTINCT chat_history_id FROM messages ORDER BY chat_history_id ASC"
    cursor.execute(query)
    chat_history_ids = cursor.fetchall()
    chat_history_id_list = [item[0] for item in chat_history_ids]
    cursor.close()  # Đóng cursor sau khi sử dụng
    conn.close()  # Đóng kết nối sau khi sử dụng
    return chat_history_id_list

def save_text_message(chat_history_id, sender_type, text):
    conn = create_mysql_connection()
    cursor = conn.cursor()

    # Sử dụng %s thay cho ? trong câu lệnh SQL để phù hợp với MySQL
    cursor.execute('INSERT INTO messages (chat_history_id, sender_type, message_type, text_content) VALUES (%s, %s, %s, %s)',
                    (chat_history_id, sender_type, 'text', text))

    conn.commit()
    cursor.close()
    conn.close()

def save_image_message(chat_history_id, sender_type, image_bytes):
    conn = create_mysql_connection()
    cursor = conn.cursor()

    # Sử dụng %s như placeholder và không cần phải sử dụng sqlite3.Binary với MySQL
    cursor.execute('INSERT INTO messages (chat_history_id, sender_type, message_type, blob_content) VALUES (%s, %s, %s, %s)',
                    (chat_history_id, sender_type, 'image', image_bytes))

    conn.commit()
    cursor.close()
    conn.close()

def load_messages(chat_history_id):
    conn = create_mysql_connection()
    cursor = conn.cursor()

    # Cập nhật câu truy vấn SQL cho MySQL, sử dụng %s thay cho ? như placeholder
    query = "SELECT message_id, sender_type, message_type, text_content, blob_content FROM messages WHERE chat_history_id = %s"
    cursor.execute(query, (chat_history_id,))

    messages = cursor.fetchall()
    chat_history = []
    for message in messages:
        message_id, sender_type, message_type, text_content, blob_content = message

        # Dựa trên loại tin nhắn, thêm nội dung phù hợp vào lịch sử chat
        if message_type == 'text':
            chat_history.append({
                'message_id': message_id, 
                'sender_type': sender_type, 
                'message_type': message_type, 
                'content': text_content
            })
        else:
            # Đối với MySQL, không cần chuyển đổi blob_content khi trả về
            chat_history.append({
                'message_id': message_id, 
                'sender_type': sender_type, 
                'message_type': message_type, 
                'content': blob_content
            })

    cursor.close()
    conn.close()

    return chat_history


def init_db():
    conn = create_mysql_connection()
    cursor = conn.cursor()

    # Sửa đổi cú pháp tạo bảng cho MySQL
    create_messages_table = """
    CREATE TABLE IF NOT EXISTS messages (
        message_id INT AUTO_INCREMENT PRIMARY KEY,
        chat_history_id VARCHAR(255) NOT NULL,
        sender_type VARCHAR(255) NOT NULL,
        message_type VARCHAR(255) NOT NULL,
        text_content TEXT,
        blob_content LONGBLOB
    );
    """
    create_pdf_table = """ CREATE TABLE IF NOT EXISTS pdf_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    chat_history_id VARCHAR(255) NOT NULL,
    sender_type VARCHAR(255) NOT NULL,
    pdf_content LONGBLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

    cursor.execute(create_messages_table)
    cursor.execute(create_pdf_table)
    conn.commit()
    cursor.close()
    conn.close()
    
if __name__ == "__main__":
    init_db()