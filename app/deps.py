from transformers import AutoTokenizer, AutoModelForCausalLM
import whisper
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import MODEL_PATH, EMBEDDING_PATH
import torch

# 语音识别模型
asr_model = whisper.load_model("base")
print(f"[INFO]: Whisper ASR模型加载完成")

# 确保tokenizer有正确的pad_token
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
print(f"[INFO]: Tokenizer加载完成")

# 加载模型并移动到GPU
llm_model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, 
    trust_remote_code=True,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

# 确定设备并移动模型
device = "cuda" if torch.cuda.is_available() else "cpu"
llm_model = llm_model.to(device).eval()
print(f"[INFO]: DeepSeek模型加载完成，运行在 {device.upper()} 设备上")

# 嵌入模型
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_PATH,
    model_kwargs={"device": "cuda"} if torch.cuda.is_available() else {"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)
print(f"[INFO]: Embedding模型加载完成")



