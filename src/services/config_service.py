import os
from dotenv import load_dotenv

class ConfigService:
    def __init__(self):
        load_dotenv()
    
    def get_openai_api_key(self) -> str:
        return os.getenv('OPENAI_API_KEY')
    
    def get_discord_token(self, mbti_type: str) -> str:
        return os.getenv(f'DISCORD_{mbti_type}_TOKEN')
    
    def get_channel_id(self, channel_name: str) -> int:
        try:
            return int(os.getenv(f'{channel_name}_CHANNEL_ID'))
        except Exception as e:
            print(f"Error = {e}: チャンネルIDの取得に失敗しました")
            return 0
    
    def get_reaction_rate(self) -> float:
        return float(os.getenv('REACTION_RATE', 0.5)) 
    
    def get_auto_reply_rate(self) -> float:
        return float(os.getenv('AUTO_REPLY_RATE', 0.75))
    
    def get_auto_reply_in_free_talk_rate(self) -> float:
        return float(os.getenv('AUTO_REPLY_IN_FREE_TALK_RATE', 0.1))
