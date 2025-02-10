import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを環境変数から取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openAiClient = OpenAI(api_key=OPENAI_API_KEY)

# ジャンルと対応する絵文字のマッピング
reaction_genre_map = {
    "良い": "👍",
    "面白い": "😂",
    "悲しい": "😢",
    "怒り": "😡",
    "愛": "❤️",
    "驚き": "😲",
    "感謝": "🙏",
    "モチベーション": "💪",
    "お祝い": "🎊",
    "眠い": "💤",
    "仕事": "💼",
    "旅行": "✈️",
    "運動": "🏋️",
    "勉強": "📚",
}

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

            with open(f'prompt/reaction.txt', 'r', encoding='utf-8') as file:
                reaction_prompt = file.read()
                print(f"reaction_prompt = {reaction_prompt}")

            # OpenAI 使う
            prompt = f"「{message_content} 」{reaction_prompt}" 
            print(f"prompt = {prompt}")
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
            genre_response = response.choices[0].message.content
            print(f"genre_response: {genre_response}")

            recommend_reactions = []
            
            # OpenAIの返答を基にリアクションを選定
            try:
                recommend_reactions.append("👀")

                # 定義されたジャンルに当てはまれば、絵文字を追加する
                for genre in reaction_genre_map:
                    if genre in genre_response:
                        recommend_reactions.append(reaction_genre_map[genre])
            except Exception as e:
                print(e)
            
            print(f"recommend_reactions = {recommend_reactions}")

            self.message_reactions[message_id] = recommend_reactions
            self.fetching_message_ids.remove(message_id)

    def getReactions(self, messageId):
        return self.message_reactions[messageId]
