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
import tempfile
import shutil
import cv2
openai.api_key = "sk-proj-D0bqBJNuu5C6Lu7tQ7tRT3BlbkFJCdJk6bIpuXag34onwDNf"
