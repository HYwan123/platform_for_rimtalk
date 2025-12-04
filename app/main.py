from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import uvicorn
from typing import List, Optional, Literal, Union

# --- 1. OpenaiClient 保持不变 ---
class OpenaiClient:
    """
    单例模式的 OpenAI 异步客户端，用于连接您的 iflow API 服务。
    """
    _instance = None
    conn = AsyncOpenAI(
        base_url='https://apis.iflow.cn/v1',
        timeout=999999999,
        # 注意: 实际部署时，API Key 应该从环境变量或安全配置中获取
        api_key='sk-d5a9b4f92ce356963a48f06322867811' 
    )

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_client(cls):
        return cls.conn

# --- 2. Pydantic 请求模型 (兼容 OpenAI API) ---
class Message(BaseModel):
    """定义消息结构"""
    role: Literal["system", "user", "assistant", "tool"]
    content: str

class ChatRequest(BaseModel):
    """定义聊天完成请求体"""
    model: str = Field(..., description="要使用的模型名称，如 'Qwen3-Max'")
    messages: List[Message] = Field(..., description="对话历史消息列表")
    stream: bool = Field(False, description="是否以流式方式返回响应")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    # 还可以添加 max_tokens, stop 等其他参数

# --- 3. FastAPI 应用和路由 ---
app = FastAPI(title="Ollama/OpenAI API Emulator")

# 实例化客户端（单例）
openai_client = OpenaiClient()


from fastapi import FastAPI, HTTPException
from fastapi.responses import Response # 使用 Response 替代 JSONResponse
import json # 需要导入内置的 json 库
# ... (其他导入保持不变) ...



@app.post('/api/chat')
async def chat_completions(request: ChatRequest):
    conn = await openai_client.get_client()

    messages_param = [m.model_dump(exclude_none=True) for m in request.messages]

    async def event_generator():
        stream = await conn.chat.completions.create(
            model=request.model,
            messages=messages_param, # type: ignore
            stream=True
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
