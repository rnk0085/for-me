import pytest
from unittest.mock import Mock
from src.utils.role_mention_checker import check_role_mention

def test_check_role_mention():
    """ロールメンションのチェックテスト"""
    ### Given
    message = Mock()
    client = Mock()

    # client.user をモック
    client.user = Mock()

    # ロールメンションがある場合
    role_mock = Mock()
    role_mock.members = [client.user]  # client.user をロールのメンバーに設定
    message.role_mentions = [role_mock]

    # テスト実行
    assert check_role_mention(message, client) is True  # ロールメンションがあるのでTrue

    # ロールメンションがない場合
    role_mock.members = []  # メンバーがいない場合
    message.role_mentions = [role_mock]

    # テスト実行
    assert check_role_mention(message, client) is False  # メンバーがいないのでFalse
