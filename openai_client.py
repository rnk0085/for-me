from openai import OpenAI
from config import OPENAI_API_KEY

class OpenAIClient:
    openai_model = "gpt-4o-mini"

    def __init__(self):
        self.openAiClient = OpenAI(api_key=OPENAI_API_KEY)

    def get_response(
            self,
            prompt,
            user_message,
            model = openai_model,
    ):
        try:
            # ref: https://platform.openai.com/docs/guides/text-generation
            completion = self.openAiClient.chat.completions.create(
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
    
