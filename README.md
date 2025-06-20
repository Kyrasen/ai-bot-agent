# 简介
    这是一个在小学教育领域提供问答服务的智能机器人，只需要客户上传知识库，便可快速回答相关问题，不同的智能体有着不一样的功能，现在还仅有语文和数学智能体，未来还会加以完善。

# 如何使用
1. 前端：
   界面如下图所示：
<div align=center>
    <image src="imgs/image1.png" width=700>
    <image src="imgs/image2.png" width=700>
    <image src="imgs/image3.png" width=700>

</div>
- 先上传PDF文件，待文件入库之后，便可点击开始录音按钮，说出你的问题，说完之后便可点击停止录音，稍等1秒之后便可听到你想要的答案。
- 启动index1.html即可

2. 后端：
    只需在terminal输入命令：python app/run.py


# 依赖
## 下载deepseek模型：
- sudo apt update
- sudo apt install git-lfs
- git lfs install
- git clone https://www.modelscope.cn/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B.git
- git clone https://www.modelscope.cn/BAAI/bge-base-zh-v1.5.git

## 创建新环境
- conda create -n aiBot python=3.11 -y
- conda activate aiBot

## 下载依赖，有些是用conda，有些是用pip
- conda install -c conda-forge faiss-cpu pypdf uvicorn python-multipart -y
- pip install fastapi langchain sentence-transformers openai-whisper langchain_community edge_tts pydub soundfile

## 安装ffmpeg
- sudo apt update
- sudo apt install ffmpeg