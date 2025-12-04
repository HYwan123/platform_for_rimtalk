from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.utils.openai_client import OpenaiClient
import uvicorn
from app.model.chat import *



# --- 3. FastAPI 应用和路由 ---
app = FastAPI(title="Ollama/OpenAI API Emulator")

# 实例化客户端（单例）
openai_client = OpenaiClient()




@app.post('/api/chat')
async def chat_completions(request: ChatRequest):
    conn = await openai_client.get_client()

    messages_param = [m.model_dump(exclude_none=True) for m in request.messages]

    async def event_generator():
        stream = await conn.chat.completions.create(
            model=request.model,
            messages=messages_param, # type: ignore
            stream=True,
            response_format=
            {
                "type": "json_schema",
                "schema": OutputMessage.model_json_schema()
            } # type: ignore
        ) # type: ignore
        async for chunk in stream:
            json_str = chunk.model_dump_json()
            # 替换中文引号
            json_str = json_str.replace('“', '"').replace('”', '"')
            yield f"data: {json_str}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")



# --- 4. 启动函数 ---
def run_server() -> None:
    """启动 uvicorn 服务器"""
    print("🚀 API 模拟服务正在启动...")
    uvicorn.run(app, host="0.0.0.0", port=15432)

if __name__ == '__main__':
    run_server()
