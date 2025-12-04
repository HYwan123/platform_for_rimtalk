from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam
import asyncio

class OpenaiClient:

    _instance = None
    conn = AsyncOpenAI(
        base_url='https://apis.iflow.cn/v1',
        timeout=999999999,
        api_key='sk-d5a9b4f92ce356963a48f06322867811'
        )

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def test(cls):
        return await cls.conn.chat.completions.create(
            model='Qwen3-Max',
            messages=[
                ChatCompletionSystemMessageParam(role="system", content="test")
                
                ]
            
            )
        

async def main() -> None:
    client = OpenaiClient()
    result = await client.test()
    print(result)

if __name__ == '__main__':
    asyncio.run(main())