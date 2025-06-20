from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔗 客户端已连接")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📥 收到消息: {data}")
            await websocket.send_text(f"你发送了：{data}")
    except:
        print("❌ 客户端断开连接")

if __name__ == "__main__":
    uvicorn.run("ws_server:app", host="127.0.0.1", port=6006)
