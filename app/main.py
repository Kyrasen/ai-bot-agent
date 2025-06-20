from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ws, pdf
import os, subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws.router)
app.include_router(pdf.router)

@app.on_event("startup")
def on_startup():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True)
        print("✅ FFmpeg 可用")
    except FileNotFoundError:
        print("❌ FFmpeg 未找到，请检查是否已安装并配置到 PATH 中")
    except subprocess.CalledProcessError:
        print("❌ FFmpeg 执行失败，请检查命令或环境")



