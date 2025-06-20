import uuid, os, subprocess
import edge_tts
from config import TEMP_DIR
from gtts import gTTS

'''
    将模型回复的文本 “说” 出来
'''
async def synthesize_speech(text: str) -> str:
    try:
        output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.mp3")
        communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        print(f"语音合成失败: {e}")
        return None

def convert_webm_to_wav(webm_path: str) -> str:
    """转换WebM为WAV格式，解决回声问题"""
    if not os.path.exists(webm_path):
        print(f"文件不存在: {webm_path}")
        return None
    
    wav_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.wav")
    
    try:
        result = subprocess.run([
            "ffmpeg",
            "-y",  # 覆盖输出文件
            "-fflags", "+genpts",      # 生成缺失的PTS
            "-avoid_negative_ts", "make_zero",
            "-i", webm_path,
            "-ac", "1",                # 单声道
            "-ar", "16000",            # 16kHz采样率
            "-acodec", "pcm_s16le",    # PCM 16位小端编码
            wav_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg转换错误: {result.stderr}")
            return None
        
        return wav_path
    except Exception as e:
        print(f"音频转换异常: {e}")
        return None
import pyttsx3

# async def synthesize_speech(text: str) -> str:
#     try:
#         engine = pyttsx3.init()
#         output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.wav")
#         engine.save_to_file(text, output_path)
#         engine.runAndWait()
#         return output_path
#     except Exception as e:
#         print(f"语音合成失败: {e}")
#         return None

# 方案2：使用gTTS（在线）
# async def synthesize_speech(text: str) -> str:
#     try:
#         tts = gTTS(text=text, lang='zh')
#         output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.mp3")
#         tts.save(output_path)
#         return output_path
#     except Exception as e:
#         print(f"语音合成失败: {e}")
#         return None

# 语音合成函数（需要实现）
# async def synthesize_speech(text: str) -> str:
#     """将文本合成为语音文件，返回文件路径"""
#     # 这里应该是您的TTS实现
#     # 例如使用pyttsx3、gTTS或其他TTS服务
#     # 返回生成的音频文件路径
#     try:
#         # 示例：保存为临时WAV文件
#         output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.wav")
        
#         # 这里应该是实际的TTS合成代码
#         # 暂时创建一个空文件代替
#         with open(output_path, "wb") as f:
#             pass
            
#         return output_path
#     except Exception as e:
#         print(f"语音合成失败: {e}")
#         return None


'''
    将前端返回的音频文件转化为wav格式，这样后端好识别
'''
# def convert_webm_to_wav(webm_data: bytes) -> bytes | None:
#     try:
#         if not webm_data or len(webm_data) < 100:
#             print("webm_data is empty or too short")
#             return None

#         webm_path = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4().hex}.webm")
#         with open(webm_path, "wb") as f:
#             f.write(webm_data)

#         wav_path = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4().hex}.wav")
#         result = subprocess.run(
#             [
#                 "ffmpeg", 
#                 "-fflags", "+genpts",
#                 "-avoid_negative_ts", "make_zero",
#                 "-i", 
#                 webm_path, 
#                 "-ac", 
#                 "1", 
#                 "-ar", 
#                 "16000", 
#                 "-acodec", 
#                 "pcm_s16le", 
#                 wav_path
                
#             ],
#             stdout=subprocess.PIPE, 
#             stderr=subprocess.PIPE,
#             text=True
#         )

#         if result.returncode != 0:
#             print(f"ffmpeg error:\n{result.stderr}")
#             return None

#         with open(wav_path, "rb") as f:
#             data = f.read()

#         return data
#     except Exception as e:
#         print(f"音频转换失败：{e}")
#         return None

# # 正确做法：使用concat协议
# def combine_webm_segments(segments: list[bytes]) -> bytes:
#     """ 使用FFmpeg拼接WebM片段 """
#     concat_file = os.path.join(TEMP_DIR, f"concat_{uuid.uuid4().hex}.txt")
    
#     # 生成包含所有片段的列表
#     with open(concat_file, "w") as f:
#         for seg in segments:
#             path = os.path.join(TEMP_DIR, f"seg_{uuid.uuid4().hex}.webm")
#             with open(path, "wb") as seg_file:
#                 seg_file.write(seg)
#             f.write(f"file '{path}'\n")
    
#     # 使用concat协议合并
#     output_path = os.path.join(TEMP_DIR, f"combined_{uuid.uuid4().hex}.webm")
#     subprocess.run([
#         "ffmpeg",
#         "-f", "concat",
#         "-safe", "0",
#         "-i", concat_file,
#         "-c", "copy",
#         output_path
#     ], check=True)
    
#     return output_path

    




