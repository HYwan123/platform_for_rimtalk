from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.utils.openai_client import OpenaiClient
import uvicorn
from app.model.chat import *
from app.utils.to_chunk import *


# --- 3. FastAPI 应用和路由 ---
app = FastAPI(title="Ollama/OpenAI API Emulator")

# 实例化客户端（单例） 
openai_client = OpenaiClient()




@app.post('/api/chat')
async def chat_completions(request: ChatRequest):
    conn = await openai_client.get_client()

    messages_param = [m.model_dump(exclude_none=True) for m in request.messages]


    response = await conn.chat.completions.create(
        model=request.model,
        messages=messages_param, # type: ignore
        stream=False,
        response_format=
        {
            "type": "json_schema",
            "schema": OutputMessage.model_json_schema()
        } # type: ignore
    ) # type: ignore
    choice = response.choices[0]

    if hasattr(choice, "message") and hasattr(choice.message, "content"):
        print(choice.message.content)
    else:
        print(response)

    return StreamingResponse(event_generator(response) ,media_type="text/event-stream")

"""


"""

# --- 4. 启动函数 ---
def run_server() -> None:
    """启动 uvicorn 服务器"""
    print("🚀 API 模拟服务正在启动...")
    uvicorn.run(app, host="0.0.0.0", port=15432)

if __name__ == '__main__':
    run_server()
