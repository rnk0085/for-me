def check_role_mention(message, client) -> bool:
    """ロールメンションされたかどうか"""
    roles = message.role_mentions
    is_role_mentioned = False

    for role in roles:
        if client.user in role.members:
            is_role_mentioned = True

    return is_role_mentioned
