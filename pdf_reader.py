from lib import *

def read_data_from_pdf(file_buffer):
    text = ""  # for storing the extracted text
    pdf_reader = PdfReader(file_buffer)

    for page in pdf_reader.pages:
        text += page.extract_text() if page.extract_text() else ''

    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

def get_embedding(text_chunks, model_id):
    model = SentenceTransformer(model_id)
    points = []

    for chunk in text_chunks:
        embeddings = model.encode(chunk)
        point_id = str(uuid.uuid4())
        points.append({"id": point_id, "vector": embeddings.tolist(), "payload": {"text": chunk}})
    return points
