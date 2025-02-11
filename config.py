import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIのAPIキーを環境変数から取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_discord_token(mbti_type):
    return os.getenv(f'DISCORD_{mbti_type}_TOKEN')
