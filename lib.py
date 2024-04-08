from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient,models
from qdrant_client.http.models import PointStruct
import os
import openai
import uuid
from qdrant_client import QdrantClient,models
from qdrant_client.http.models import PointStruct
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import time 
import base64
import cv2
import tempfile
import shutil
openai.api_key = "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"