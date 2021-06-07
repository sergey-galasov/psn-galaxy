__version__ = "0.33"

__changelog__ = {
    "0.33": """
        - Add game time feature 
    """,
    "0.32": """
        - Fix showing correct PS Plus monthly games in Galaxy Subscription tab
    """,
    "0.31": """
        - Fix losing authentication as side effect of shutdown while refreshing credentials
        - Add cache invalidation for title-communication_ids map every 7 days; fixes not showing updated games without reconnection
        - Provide fallback game name using trophy titles; fixes not showing some games (Cyberpunk 2077, Mafia: Definitive Edition, ...)
    """,
    "0.30": """
        - Only allow one token refresh at a time
    """,
    "0.29": """
        - Fix broken authentication due to change on psn side
    """,
    "0.28": """
        - Implements `get_subscription_games` to report current free games from PSPlus
    """
}
