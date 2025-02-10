import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを環境変数から取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openAiClient = OpenAI(api_key=OPENAI_API_KEY)

class Reactions:
    def __init__(self):
        self.message_reactions = {}
        self.fetching_message_ids = []
    
    async def fetchReaction(self, message_id, message_content):
        print("fetchReaction start")

        # 他のが呼び出していないか。同じIDで呼び出していれば、待って欲しい。
        if message_id in self.fetching_message_ids:
            print("同じIDで呼び出し中")
            await asyncio.sleep(1)
            return

        print(f"self.message_reactions[message_id] = {self.message_reactions}")
        if message_id not in self.message_reactions:
            print("OpenAIでリアクションを決める処理")
            self.fetching_message_ids.append(message_id)

            # OpenAI 使う
            prompt=f"Analyze the sentiment and content of this message: '{message_content}' and suggest an emoji reaction."
            response = openAiClient.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "developer", "content": prompt},
                    {
                        "role": "user",
                        "content": message_content,
                    }
                ]
            )
            
            # OpenAIからのレスポンス
            sentiment_analysis = response.choices[0].message.content
            print(f"Sentiment analysis result: {sentiment_analysis}")

            recommend_reactions = []
            
            # OpenAIの返答を基にリアクションを選定
            try:
                if "happy" in sentiment_analysis or "good" in sentiment_analysis:
                    recommend_reactions.append("👍")  # ポジティブなメッセージに反応
                elif "funny" in sentiment_analysis or "laugh" in sentiment_analysis:
                    recommend_reactions.append("😂")  # 面白いメッセージに反応
                elif "sad" in sentiment_analysis or "bad" in sentiment_analysis:
                    recommend_reactions.append("👋")  # 悲しいメッセージに反応
                elif "angry" in sentiment_analysis:
                    recommend_reactions.append("👋")  # 怒っているメッセージに反応
                else:
                    recommend_reactions.append("👋")  # その他のメッセージにはお祝いのリアクションを追加
            except Exception as e:
                print(e)
            
            print(f"recommend_reactions = {recommend_reactions}")

            self.message_reactions[message_id] = recommend_reactions
            self.fetching_message_ids.remove(message_id)

    def getReactions(self, messageId):
        return self.message_reactions[messageId]
