import os

VECTOR_STORE_DIR = "vector_db"
TEMP_DIR = os.path.join(os.getcwd(), "audio_temp")
os.makedirs(TEMP_DIR, exist_ok = True)

MODEL_PATH = r"models/DeepSeek-R1-Distill-Qwen-1.5B"
EMBEDDING_PATH = "models/bge-base-zh-v1.5"




