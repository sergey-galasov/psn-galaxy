from galaxy.api.consts import LicenseType
from galaxy.api.types import Achievement, FriendInfo, Game, LicenseInfo
from plugin import COMM_ID_NOT_AVAILABLE

COMMUNICATION_ID = "NPWR12784_00"

DEFAULT_LICENSE = LicenseInfo(LicenseType.SinglePurchase, None)

GAMES = [
    Game("CUSA07917_00", "Tooth and Tail", [], DEFAULT_LICENSE),
    Game("CUSA02000_00", "Batman: Return to Arkham - Arkham City", [], DEFAULT_LICENSE),
    Game("CUSA05603_00", "Batman", [], DEFAULT_LICENSE),
    Game("CUSA01427_00", "Game of Thrones", [], DEFAULT_LICENSE),
    Game("CUSA01858_00", "Grim Fandango Remastered", [], DEFAULT_LICENSE),
    Game("CUSA04607_00", "Batman: Return to Arkham - Arkham Asylum", [], DEFAULT_LICENSE),
    Game("CUSA00860_00", "Tales from the Borderlands", [], DEFAULT_LICENSE),
    Game("CUSA07320_00", "Horizon Zero Dawn™", [], DEFAULT_LICENSE),
    Game("CUSA07140_00", "Dreamfall Chapters", [], DEFAULT_LICENSE),
    Game("CUSA08487_00", "Life is Strange: Before the Storm", [], DEFAULT_LICENSE)
]

DLCS = [
    Game("CUSA07719_00", "Dreamfall Chapters (Original Soundtrack)", [], DEFAULT_LICENSE)
]

TITLES = GAMES + DLCS

BACKEND_GAME_TITLES_WITHOUT_DLC = {
    "start": 0,
    "size": 10,
    "totalResults": 10,
    "titles": [
        {"titleId": "CUSA07917_00", "name": "Tooth and Tail"},
        {"titleId": "CUSA02000_00", "name": "Batman: Return to Arkham - Arkham City"},
        {"titleId": "CUSA05603_00", "name": "Batman"},
        {"titleId": "CUSA01427_00", "name": "Game of Thrones"},
        {"titleId": "CUSA01858_00", "name": "Grim Fandango Remastered"},
        {"titleId": "CUSA04607_00", "name": "Batman: Return to Arkham - Arkham Asylum"},
        {"titleId": "CUSA00860_00", "name": "Tales from the Borderlands"},
        {"titleId": "CUSA07320_00", "name": "Horizon Zero Dawn™"},
        {"titleId": "CUSA07140_00", "name": "Dreamfall Chapters"},
        {"titleId": "CUSA08487_00", "name": "Life is Strange: Before the Storm"}
    ]
}

BACKEND_GAME_TITLES_WITH_DLC = {
    "start": 0,
    "size": 11,
    "totalResults": 11,
    "titles": [
        {"titleId": "CUSA07917_00", "name": "Tooth and Tail"},
        {"titleId": "CUSA02000_00", "name": "Batman: Return to Arkham - Arkham City"},
        {"titleId": "CUSA05603_00", "name": "Batman"},
        {"titleId": "CUSA01427_00", "name": "Game of Thrones"},
        {"titleId": "CUSA01858_00", "name": "Grim Fandango Remastered"},
        {"titleId": "CUSA04607_00", "name": "Batman: Return to Arkham - Arkham Asylum"},
        {"titleId": "CUSA00860_00", "name": "Tales from the Borderlands"},
        {"titleId": "CUSA07320_00", "name": "Horizon Zero Dawn™"},
        {"titleId": "CUSA07719_00", "name": "Dreamfall Chapters (Original Soundtrack)"},
        {"titleId": "CUSA07140_00", "name": "Dreamfall Chapters"},
        {"titleId": "CUSA08487_00", "name": "Life is Strange: Before the Storm"}
    ]
}

TITLE_TO_COMMUNICATION_ID = {
    "CUSA07917_00": "NPWR12784_00",
    "CUSA02000_00": "NPWR10584_00",
    "CUSA05603_00": "NPWR11243_00",
    "CUSA01427_00": "NPWR07882_00",
    "CUSA01858_00": "NPWR07722_00",
    "CUSA04607_00": "NPWR10793_00",
    "CUSA00860_00": "NPWR07228_00",
    "CUSA07320_00": "NPWR11556_00",
    "CUSA07719_00": COMM_ID_NOT_AVAILABLE,
    "CUSA07140_00": "NPWR12456_00",
    "CUSA08487_00": "NPWR13354_00"
}

BACKEND_TROPHIES = {
    "trophies": [
        {
            "trophyId": 0,
            "fromUser": {"onlineId": "user-id", "earned": False},
            "trophyName": "achievement 0",
            "groupId": "default"
        },
        {
            "trophyId": 1,
            "fromUser": {"onlineId": "user-id", "earned": True, "earnedDate": "1987-01-22T09:01:33Z"},
            "trophyName": "achievement 1",
            "groupId": "default"
        },
        {
            "trophyId": 2,
            "fromUser": {"onlineId": "user-id", "earned": True, "earnedDate": "2011-10-16T16:33:18Z"},
            "trophyName": "achievement 2",
            "groupId": "default"
        },
        {
            "trophyId": 3,
            "fromUser": {"onlineId": "user-id", "earned": True, "earnedDate": "2013-12-29T09:18:33Z"},
            "trophyName": "achievement 3",
            "groupId": "001"
        },
        {
            "trophyId": 4,
            "fromUser": {"onlineId": "user-id", "earned": False},
            "trophyName": "achievement 4",
            "groupId": "001"
        },
        {
            "trophyId": 5,
            "fromUser": {"onlineId": "user-id", "earned": True, "earnedDate": "1987-02-07T10:14:42Z"},
            "trophyName": "achievement 5",
            "groupId": "022"
        },
    ]
}

UNLOCKED_ACHIEVEMENTS = [
    Achievement(achievement_id="1", achievement_name="achievement 1", unlock_time=538304493),
    Achievement(achievement_id="2", achievement_name="achievement 2", unlock_time=1318782798),
    Achievement(achievement_id="3", achievement_name="achievement 3", unlock_time=1388308713),
    Achievement(achievement_id="5", achievement_name="achievement 5", unlock_time=539691282),
]

BACKEND_USER_PROFILES = {
    "start": 0,
    "size": 7,
    "totalResults": 7,
    "profiles": [{
        "accountId": 1,
        "onlineId": "veryopenperson",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/DefaultAvatar_m.png"}],
        "primaryOnlineStatus": "online",
        "presences": [{
            "onlineStatus": "online",
            "platform": "PS4"
        }],
        "friendRelation": "friend"
    }, {
        "accountId": 2,
        "onlineId": "ImTestingSth1",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/DefaultAvatar_m.png"}],
        "primaryOnlineStatus": "offline",
        "presences": [{
            "onlineStatus": "offline",
            "lastOnlineDate": "2019-03-04T09:15:19Z"
        }],
        "friendRelation": "friend",
    }, {
        "accountId": 3,
        "onlineId": "venom6683",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/WWS_E/E0007_m.png"}],
        "primaryOnlineStatus": "online",
        "presences": [{
            "onlineStatus": "online",
            "platform": "PS4"
        }],
        "friendRelation": "friend"
    }, {
        "accountId": 4,
        "onlineId": "l_Touwa_l",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/DefaultAvatar_m.png"}],
        "primaryOnlineStatus": "offline",
        "presences": [{
            "onlineStatus": "offline",
            "lastOnlineDate": "2018-03-22T18:50:58Z"
        }],
        "friendRelation": "friend"
    }, {
        "accountId": 5,
        "onlineId": "Resilb",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/DefaultAvatar_m.png"}],
        "primaryOnlineStatus": "offline",
        "presences": [{
            "onlineStatus": "offline",
            "lastOnlineDate": "2019-02-22T23:31:16Z"
        }],
        "friendRelation": "friend"
    }, {
        "accountId": 6,
        "onlineId": "Di_PL",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/DefaultAvatar_m.png"}],
        "primaryOnlineStatus": "offline",
        "presences": [{
            "onlineStatus": "offline"
        }],
        "friendRelation": "friend"
    }, {
        "accountId": 7,
        "onlineId": "nyash",
        "avatarUrls": [{"avatarUrl": "http://playstation.net/avatar/3RD/E9A0BB8BC40BBF9B_M.png"}],
        "primaryOnlineStatus": "offline",
        "presences": [{
            "onlineStatus": "offline",
            "lastOnlineDate": "2019-02-25T01:52:44Z"
        }],
        "friendRelation": "friend"
    }]
}

FRIEND_INFO_LIST = [
    FriendInfo(user_id="1", user_name="veryopenperson"),
    FriendInfo(user_id="2", user_name="ImTestingSth1"),
    FriendInfo(user_id="3", user_name="venom6683"),
    FriendInfo(user_id="4", user_name="l_Touwa_l"),
    FriendInfo(user_id="5", user_name="Resilb"),
    FriendInfo(user_id="6", user_name="Di_PL"),
    FriendInfo(user_id="7", user_name="nyash")
]
