from dataclasses import dataclass

@dataclass
class Bot:
    mbti_type: str # token で使用
    mbti_file_name: str # プロンプトの取得で使用
    interests: list[str] # 雑談で使用するテーマリスト

all_bots = [
    Bot(
        mbti_type="ENTP",
        mbti_file_name="entp-kosho",
        interests=[
            "未来のテクノロジー",
            "哲学的な議論",
            "社会のルールや仕組み",
            "起業・ビジネスアイデア",
            "陰謀論やSF的な発想",
            "変わったゲームや心理戦",
        ],
    ),
    Bot(
        mbti_type="INTP",
        mbti_file_name="intp-nagi",
        interests=[
            "数学・物理・宇宙論",
            "AI・プログラミング・最新技術",
            "哲学・認知科学",
            "論理パズル・知的ゲーム",
            "SF小説や映画",
            "ミニマリズム",
        ],
    ),
    Bot(
        mbti_type="INFJ",
        mbti_file_name="infj-tohru",
        interests=[
            "心理学・カウンセリング",
            "社会問題・哲学的な問い",
            "未来予測・歴史",
            "文学・詩・芸術",
            "人間関係の分析",
            "瞑想やマインドフルネス",
        ],
    ),
    Bot(
        mbti_type="ENFP",
        mbti_file_name="enfp-haru",
        interests=[
            "旅行・新しい体験",
            "人との交流",
            "社会変革・ユートピア論",
            "ファッション・アート・音楽",
            "即興の遊びや企画",
            "ミームやバズるネタ",
        ],
    ),
]