from dataclasses import dataclass

@dataclass
class Bot:
    mebti_type: str # token で使用
    mbti_file_name: str # プロンプトの取得で使用

allBots = [
    Bot(
        mebti_type="ENTP",
        mbti_file_name="entp-kosho",
    ),
    Bot(
        mebti_type="INTP",
        mbti_file_name="intp-nagi",
    )
]