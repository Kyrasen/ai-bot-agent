import os, uuid
from fastapi import WebSocket
from audio_utils import convert_webm_to_wav, synthesize_speech
from config import TEMP_DIR, VECTOR_STORE_DIR
from deps import asr_model, tokenizer, llm_model, embedding_model
from langchain_community.vectorstores import FAISS
import torch
import edge_tts
from edge_tts import Communicate

# 确保模型在正确的设备上
if torch.cuda.is_available():
    device = "cuda"
    llm_model = llm_model.to(device)  # 将语言模型移到GPU
else:
    device = "cpu"
    print("警告：未检测到GPU，将在CPU上运行")

async def handle_ws(websocket: WebSocket):
    await websocket.accept()
    audio_chunks = []  # 存储接收到的音频数据块
    audio_buffer = bytearray()  # 用于临时存储音频数据
    end_marker = b"<END>"  # 结束标记的字节表示
    end_marker_length = len(end_marker)

    try:
        while True:
            data = await websocket.receive()
            
            # 处理二进制数据
            if "bytes" in data:
                audio_buffer.extend(data["bytes"])
                
                # 检查缓冲区中是否有结束标记
                if end_marker in audio_buffer:
                    # 分离音频数据和结束标记
                    end_index = audio_buffer.index(end_marker)
                    audio_data = bytes(audio_buffer[:end_index])
                    audio_buffer = audio_buffer[end_index + end_marker_length:]
                    
                    if not audio_data:
                        continue
                    
                    # 保存音频数据到临时文件
                    webm_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.webm")
                    with open(webm_path, "wb") as f:
                        f.write(audio_data)
                    
                    # 将WebM转换为WAV
                    wav_path = convert_webm_to_wav(webm_path)
                    if not wav_path or not os.path.exists(wav_path):
                        print(f"[ERROR]: 音频转换失败: {webm_path}")
                        await websocket.send_text("音频转换失败")
                        continue
                    
                    # 语音识别
                    result = asr_model.transcribe(wav_path, language="zh")
                    user_text = result.get("text", "")
                    print(f"[INFO]: 语音识别完成：{user_text}")
                    
                    # 知识库检索
                    try:
                        db = FAISS.load_local(VECTOR_STORE_DIR, embedding_model, allow_dangerous_deserialization=True)
                        docs = db.similarity_search(user_text, k=3)
                        content = "\n\n".join([doc.page_content for doc in docs])
                        print(f"[INFO]: RAG召回完成：{content}")
                    except Exception as e:
                        print(f"[ERROR]: 知识库检索失败: {e}")
                        content = "无法获取相关信息"
                    
                    # 构建提示
                    prompt = f"""你是专业助手，请基于以下参考资料回答用户问题。
                    不能编造，若无资料请说“对不起，资料中没有提到”。不要说那么多废话，直接告诉答案就好了
                    【资料】：{content}
                    【问题】：{user_text}
                    【回答】：
                    """
                    
                    # 生成回答
                    try:
                        messages = [{"role": "user", "content": prompt}]
                        prompt_text = tokenizer.apply_chat_template(
                            messages, tokenize=False, add_generation_prompt=True
                        )
                        inputs = tokenizer(prompt_text, return_tensors="pt")
                        
                        # 关键修复：确保输入在正确的设备上
                        inputs = {k: v.to(llm_model.device) for k, v in inputs.items()}
                        
                        # 生成参数调整
                        generation_config = {
                            "max_new_tokens": 256,
                            "do_sample": True,
                            "temperature": 0.7,
                            "pad_token_id": tokenizer.pad_token_id or tokenizer.eos_token_id
                        }
                        
                        output = llm_model.generate(**inputs, **generation_config)
                        answer = tokenizer.decode(
                            output[0][inputs["input_ids"].shape[-1]:],  # ✅ 修复这里, 
                            skip_special_tokens=True
                        )
                        # 提取</think>后的内容作为最终回答
                        think_end = "</think>"
                        think_index = answer.find(think_end)
                        
                        if think_index != -1:
                            final_answer = answer[think_index + len(think_end):].strip()
                        else:
                            final_answer = answer  # 如果没有找到标签，返回完整内容

                        print(f"[INFO]: 模型生成答案完成：{answer}")
                    except Exception as e:
                        print(f"[ERROR]: 模型生成失败: {e}")
                        final_answer = "抱歉，我无法回答这个问题"
                    
                    # 语音合成
                    try:
                        communicate = Communicate(final_answer, voice="zh-CN-XiaoxiaoNeural")
                        audio_chunks = []
                        
                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                audio_chunks.append(chunk["data"])
                        
                        # 发送合并后的音频
                        if audio_chunks:
                            combined_audio = b"".join(audio_chunks)
                            await websocket.send_bytes(combined_audio)
                        
                        await websocket.send_text("<AUDIO_END>")
                    except Exception as e:
                        print(f"[ERROR]: 语音合成失败: {e}")
                        await websocket.send_text("语音合成失败")
                    
                    # # 清理临时文件
                    # for path in [webm_path, wav_path, speech_path]:
                    #     if path and os.path.exists(path):
                    #         try:
                    #             os.remove(path)
                    #         except:
                    #             pass
                
            # 处理文本消息
            elif "text" in data:
                if data["text"] == "<END>":
                    # 处理显式结束标记
                    if audio_buffer:
                        audio_data = bytes(audio_buffer)
                        audio_buffer = bytearray()
                        # 处理音频数据（同上）
    
    except Exception as e:
        print(f"WebSocket 错误：{e}")
    finally:
        # # 清理资源
        # if os.path.exists(TEMP_DIR):
        #     for file in os.listdir(TEMP_DIR):
        #         try:
        #             os.remove(os.path.join(TEMP_DIR, file))
        #         except:
        #             pass
        pass

# async def handle_ws(websocket: WebSocket):
#     await websocket.accept()
#     audio_chunks = []

#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             if data == b"<END>":
#                 if not audio_chunks:
#                     continue
#                 # 将音频数据转化为 wav 格式并获取 wav 格式的音频数据
#                 wav_path = combine_webm_segments(b"".join(audio_chunks))
#                 # wav_data = convert_webm_to_wav_with_denoise(b"".join(audio_chunks))
#                 if not wav_data:
#                     continue
                
#                 # 将获取的音频数据写下来
#                 path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.wav")
#                 with open(path, "wb") as f:
#                     f.write(wav_data)

#                 # 对 wav 文件进行语音识别
#                 result = asr_model.transcribe(path, language="zh")
#                 user_text = result["text"]
#                 print(f"[INFO]: 语音识别完成：{user_text}")

#                 # 对用户上传的文件进行召回
#                 db = FAISS.load_local(VECTOR_STORE_DIR, embedding_model, allow_dangerous_deserialization=True)
#                 docs = db.similarity_search(user_text, k = 3)
#                 content = "\n\n".join([doc.page_content for doc in docs])
#                 print(f"[INFO]: RAG召回完成完成：{content}")

#                 # 将用户的问题、上传的相似知识组合形成prompt
#                 prompt = f"""你是专业助手，请基于以下参考资料回答用户问题。
#                 不能编造，若无资料请说“对不起，资料中没有提到”。
#                 【资料】：{content}
#                 【问题】：{user_text}
#                 【回答】：
#                 """

#                 messages = [{"role": "user", "content": prompt}]
#                 prompt_text = tokenizer.apply_chat_template(messages, tokenize = False, add_generation_prompt=True)
#                 inputs = tokenizer(prompt_text, return_tensors="pt")
#                 output = llm_model.generate(**inputs, max_new_tokens=128, do_sample=True, temperature=0.7)
#                 answer = tokenizer.decode(output[0][inputs.input_ids.shape[-1]:], skip_special_tokens = True)
#                 print(f"[INFO]: 模型生成答案完成：{answer}")


#                 # 将模型生成的答案用语音生成出来
#                 speech_path = await synthesize_speech(answer)
#                 with open(speech_path, "rb") as f:
#                     await websocket.send_bytes(f.read())

#             else:
#                 audio_chunks.append(data)
#     except Exception as e:
#         print(f"WebSocker 错误：{e}")




