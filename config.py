import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを環境変数から取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_discord_token(mbti_type):
    """Discordのトークンを取得"""
    return os.getenv(f'DISCORD_{mbti_type}_TOKEN')

def get_channel_id(channel_name: str) -> int:
    """チャンネルIDを取得"""
    try:
        return int(os.getenv(f'{channel_name}_CHANNEL_ID'))
    except Exception as e:
        print(f"Error {e}: チャンネルIDをintに変換できませんでした")

# リアクションを付ける割合
REACTION_RATE = 0.5  # 50%

# 自動返信をする割合
AUTO_REPLY_RATE = 0.75 # 75%
AUTO_REPLY_IN_FREE_TALK_RATE = 0.1 # 10%
