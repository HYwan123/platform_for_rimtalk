import time
import json
import uuid
import asyncio

async def event_generator(response, chunk_size=12):
    text = response.choices[0].message.content
    base_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    model = response.model

    # 这里把内容按你想要的大小分块
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    for part in chunks:
        chunk = {
            "id": base_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": part,
                        "function_call": None,
                        "refusal": None,
                        "role": None,
                        "tool_calls": None
                    },
                    "finish_reason": None,
                    "logprobs": None
                }
            ],
            "service_tier": None,
            "system_fingerprint": "fpv0_fake",
            "usage": None,
            "extend_fields": {
                "traceId": uuid.uuid4().hex,
                "requestId": uuid.uuid4().hex
            }
        }

        # yield SSE 字符串
        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0)

    # 最终的 stop chunk
    finish_chunk = {
        "id": base_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop",
                "logprobs": None
            }
        ],
        "extend_fields": {},
        "usage": None
    }

    yield f"data: {json.dumps(finish_chunk, ensure_ascii=False)}\n\n"
