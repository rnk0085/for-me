from openai import OpenAI
from src.services.config_service import ConfigService

class OpenAIClient:
    openai_model = "gpt-4o-mini"

    def __init__(self, config_service: ConfigService):
        self.openAiClient = OpenAI(api_key=config_service.get_openai_api_key())

    async def get_response(
            self,
            prompt: str,
            user_message: str,
            model: str = openai_model,
    ) -> str:
        """OpenAIからの返答を返す"""
        print(f"OpenAIClient > get_response started")
        try:
            # ref: https://platform.openai.com/docs/guides/text-generation
            completion = await self.openAiClient.chat.completions.create(
                model = model,
                messages = [
                    {"role": "developer", "content": prompt},
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ]
            )

            print(f'completion = {completion}')

            # 生成された返答を返す
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error during OpenAI request: {e}")
            return "OpenAIでエラーが起きました"
    
