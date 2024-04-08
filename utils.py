import json
from langchain.schema.messages import HumanMessage, AIMessage
from datetime import datetime
import yaml

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
