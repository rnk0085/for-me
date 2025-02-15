def get_prompt(file_path: str) -> str:
    """指定されたファイルからプロンプトを読み込む"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"プロンプト読み込みエラー: {e}")
        return ""