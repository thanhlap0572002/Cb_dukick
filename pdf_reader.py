from lib import *

def read_data_from_pdf(file_buffer):
    text = ""  # for storing the extracted text
    pdf_reader = PdfReader(file_buffer)

    for page in pdf_reader.pages:
        text += page.extract_text() if page.extract_text() else ''

    return text