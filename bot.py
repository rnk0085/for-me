from dataclasses import dataclass

@dataclass
class Bot:
    mbti_type: str # token で使用
    mbti_file_name: str # プロンプトの取得で使用

allBots = [
    Bot(
        mbti_type="ENTP",
        mbti_file_name="entp-kosho",
    ),
    Bot(
        mbti_type="INTP",
        mbti_file_name="intp-nagi",
    ),
    Bot(
        mbti_type="INFJ",
        mbti_file_name="infj-tohru",
    )
]