import math
import pytest
from galaxy.api.errors import UnknownBackendResponse


GAMES = [
    {"id": "CUSA15900_00", "name": "Persona 5: Dancing in Starlight"},
    {"id": "CUSA16532_00", "name": "KINGDOM HEARTS III"},
    {"id": "CUSA15608_00", "name": "Persona 4 Dancing All Night"},
    {"id": "CUSA15899_00", "name": "Persona 3: Dancing in Moonlight"},
    {"id": "CUSA11036_00", "name": "ACE COMBAT™ 7: SKIES UNKNOWN"},
    {"id": "CUSA03852_00", "name": "Dragon's Crown"},
    {"id": "CUSA16122_00", "name": "Fist of the North Star: Lost Paradise"},
    {"id": "CUSA16634_00", "name": "ACE COMBAT™ SQUADRON LEADER"},
    {"id": "CUSA16410_00", "name": "Castlevania Requiem: Symphony Of The Night & Rondo Of Blood"},
    {"id": "CUSA13243_00", "name": "SNK HEROINES Tag Team Frenzy"},
    {"id": "CUSA09167_00", "name": "Marvel's Spider-Man"},
    {"id": "CUSA15315_00", "name": "DRAGON QUEST XI: Echoes of an Elusive Age"},
    {"id": "CUSA13281_00", "name": "DARK SOULS™: REMASTERED"},
    {"id": "CUSA12990_00", "name": "Street Fighter 30th Anniversary Collection\n"},
    {"id": "CUSA14092_00", "name": "SEGA Mega Drive & Genesis Classics"},
    {"id": "CUSA13872_00", "name": "DETROIT: BECOME HUMAN"},
    {"id": "CUSA10879_00", "name": "Paladins"},
    {"id": "CUSA09886_00", "name": "School Girl/Zombie Hunter"},
    {"id": "CUSA12223_00", "name": "Tokyo Xanadu eX+"},
    {"id": "CUSA12961_00", "name": "WARRIORS ALL-STARS"},
    {"id": "CUSA12518_00", "name": "God of War"},
    {"id": "CUSA10979_00", "name": "Brawlhalla"},
    {"id": "CUSA11885_00", "name": "TERA"},
    {"id": "CUSA14858_00", "name": "Ni no Kuni™ II: Revenant Kingdom"},
    {"id": "CUSA08053_00", "name": "War of the Monsters™"},
    {"id": "CUSA11401_00", "name": "South Park™: The Fractured But Whole™"},
    {"id": "CUSA10890_00", "name": "Sniper Ghost Warrior 3"},
    {"id": "CUSA13550_00", "name": "SWORD ART ONLINE: FATAL BULLET"},
    {"id": "CUSA11735_00", "name": "METAL GEAR SURVIVE"},
    {"id": "CUSA11209_00", "name": "Hand of Fate 2"},
    {"id": "CUSA12176_00", "name": "88 Heroes"},
    {"id": "CUSA14240_00", "name": "DYNASTY WARRIORS 9"},
    {"id": "CUSA10035_00", "name": "Sky Force Anniversary"},
    {"id": "CUSA10673_00", "name": "Downwell"},
    {"id": "CUSA10126_00", "name": "Guilty Gear Xrd -Revelator- Trophy"},
    {"id": "CUSA06535_00", "name": "Blue Estate"},
    {"id": "CUSA07552_00", "name": "Rollers of the Realm"},
    {"id": "CUSA13920_00", "name": "Morphite"},
    {"id": "CUSA10039_00", "name": "Joe Dever's Lone Wolf Console Edition"},
    {"id": "CUSA11631_00", "name": "Monster Hunter: World"},
    {"id": "CUSA11350_00", "name": "Night In The Woods"},
    {"id": "CUSA14140_00", "name": "Iconoclasts"},
    {"id": "CUSA12541_00", "name": "The Silver Case HD"},
    {"id": "CUSA10787_00", "name": "Exist Archive"},
    {"id": "CUSA13363_00", "name": "Pyre"},
    {"id": "CUSA14333_00", "name": "STAR OCEAN™ - THE LAST HOPE -™ 4K & Full HD Remaster"},
    {"id": "CUSA07518_00", "name": "STREET FIGHTER V"},
    {"id": "CUSA09921_00", "name": "Gran Turismo Sport"},
    {"id": "CUSA11338_00", "name": "Injustice 2 Trophies"},
    {"id": "CUSA11619_00", "name": "Need for Speed™ Payback"},
    {"id": "CUSA12510_00", "name": "Wolfenstein® II: The New Colossus"},
    {"id": "CUSA12420_00", "name": ".hack//G.U. Last Recode"},
    {"id": "CUSA11424_00", "name": "Assassin's Creed® Origins"},
    {"id": "CUSA12568_00", "name": "ELEX"},
    {"id": "CUSA13161_00", "name": "Cyberdimension Neptunia: 4 Goddesses Online"},
    {"id": "CUSA11756_00", "name": "The Evil Within® 2"},
    {"id": "CUSA12586_00", "name": "_>OBSERVER_"},
    {"id": "CUSA10569_00", "name": "Middle-earth™: Shadow of War™"},
    {"id": "CUSA13858_00", "name": "Battle Chasers: Nightwar"},
    {"id": "CUSA12435_00", "name": "Dragon's Dogma: Dark Arisen"},
    {"id": "CUSA13202_00", "name": "Ruiner"},
    {"id": "CUSA10344_00", "name": "Hard Reset Redux"},
    {"id": "CUSA12704_00", "name": "Yonder: The Cloud Catcher Chronicles"},
    {"id": "CUSA11056_00", "name": "Destiny 2"},
    {"id": "CUSA11920_00", "name": "BLUE REFLECTION　"},
    {"id": "CUSA13133_00", "name": "Spacelords"},
    {"id": "CUSA09395_00", "name": "Tom Clancy’s Ghost Recon® Wildlands"},
    {"id": "CUSA13712_00", "name": "Ys VIII -Lacrimosa of DANA-"},
    {"id": "CUSA11690_00", "name": "Senran Kagura\nPEACH BEACH SPLASH"},
    {"id": "CUSA10362_00", "name": "Project CARS 2"},
    {"id": "CUSA11874_00", "name": "MARVEL VS. CAPCOM: INFINITE"},
    {"id": "CUSA12219_00", "name": "Pillars of Eternity: Complete Edition"},
    {"id": "CUSA13354_00", "name": "Life is Strange: Before the Storm"},
    {"id": "CUSA08922_00", "name": "LEGO® MARVEL's Avengers"},
    {"id": "CUSA11777_00", "name": "Resident Evil Revelations"},
    {"id": "CUSA09497_00", "name": "Agents of Mayhem"},
    {"id": "CUSA13408_00", "name": "Uncharted™: The Lost Legacy"},
    {"id": "CUSA06510_00", "name": "LEGO® Batman™ 3"},
    {"id": "CUSA11243_00", "name": "Batman"},
    {"id": "CUSA11474_00", "name": "RiME"},
    {"id": "CUSA12591_00", "name": "Hellblade: Senua's Sacrifice"},
    {"id": "CUSA08516_00", "name": "Overwatch: Origins Edition"},
    {"id": "CUSA10320_00", "name": "Sniper Elite 4"},
    {"id": "CUSA08661_00", "name": "DOOM®"},
    {"id": "CUSA12756_00", "name": "Shadow Tactics"},
    {"id": "CUSA12411_00", "name": "Bulletstorm: Full Clip Edition"},
    {"id": "CUSA12196_00", "name": "Stardew Valley"},
    {"id": "CUSA06600_00", "name": "Assassin's Creed® Unity"},
    {"id": "CUSA11261_00", "name": "Alone With You"},
    {"id": "CUSA12540_00", "name": "Kona"},
    {"id": "CUSA12765_00", "name": "Late Shift"},
    {"id": "CUSA13412_00", "name": "Fortnite"},
    {"id": "CUSA13022_00", "name": "Cosmic Star Heroine"},
    {"id": "CUSA07942_00", "name": "Ratchet & Clank™"},
    {"id": "CUSA12115_00", "name": "Full Throttle Remastered"},
    {"id": "CUSA08193_00", "name": "Mirror's Edge™ Catalyst"},
    {"id": "CUSA08609_00", "name": "Bastion"},
    {"id": "CUSA10066_00", "name": "Enter The Gungeon"},
    {"id": "CUSA09096_00", "name": "Curses 'n Chaos"},
    {"id": "CUSA11367_00", "name": "FINAL FANTASY Ⅻ THE ZODIAC AGE"}
]

GAMES_PAGE = "https://url.com/get-games" \
             "?operationName=getGames" \
             '&variables={{"start":{start},"size":{size}}}'


def create_backend_response_generator(size=len(GAMES)):
    def gen_range(start, stop, step):
        return ((n, min((n + step), stop)) for n in range(start, stop, step))

    def response_generator():
        for start, stop in gen_range(0, len(GAMES), size):
            yield {
                "data": {
                    "getGames": {
                        "games": GAMES[start:stop],
                        "pageInfo":  {
                            "totalCount": len(GAMES),
                            "offset": start,
                            "size": size,
                            "isLast": True if GAMES[-1] in GAMES[start:stop] else False
                        }
                    }
                }
            }
    return response_generator


def create_backend_response_all_trophies():
    response = create_backend_response_generator()()
    return [_ for _ in response][0]


def parser(data):
    return [{g["id"]: g["name"]} for g in data["data"]["getGames"]["games"]] if data else []


def assert_all_games_fetched(games):
    assert games == [{g["id"]: g["name"]} for g in GAMES]


@pytest.mark.asyncio
async def test_simple_fetch(
    http_get,
    authenticated_psn_client,
):
    http_get.side_effect = create_backend_response_generator()()
    assert_all_games_fetched(await authenticated_psn_client.fetch_data(parser, GAMES_PAGE))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_pagination(
    http_get,
    authenticated_psn_client,
):
    limit = 13

    http_get.side_effect = create_backend_response_generator(limit)()
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, GAMES_PAGE, "getGames", "totalCount", limit))
    http_get.assert_called()
    assert math.ceil(len(GAMES) / limit) == http_get.call_count


@pytest.mark.asyncio
async def test_single_fetch(
    http_get,
    authenticated_psn_client,
):
    http_get.side_effect = create_backend_response_generator()()
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, GAMES_PAGE, "getGames", "totalCount", len(GAMES)))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_less_than_expected(
    http_get,
    authenticated_psn_client,
):
    http_get.side_effect = create_backend_response_generator()()
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, GAMES_PAGE, "getGames", "totalCount", len(GAMES) + 50))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_no_total_results(
    http_get,
    authenticated_psn_client,
):
    response = create_backend_response_all_trophies()
    del response["data"]["getGames"]["pageInfo"]["totalCount"]
    http_get.return_value = response
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, GAMES_PAGE, "getGames", "totalCount", len(GAMES)))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_total_results(
    http_get,
    authenticated_psn_client,
):
    response = create_backend_response_all_trophies()
    response["data"]["getGames"]["pageInfo"]["totalCount"] = "bad_number"
    http_get.return_value = response

    with pytest.raises(UnknownBackendResponse):
        await authenticated_psn_client.fetch_paginated_data(parser, GAMES_PAGE, "getGames", "totalCount", len(GAMES))
    http_get.assert_called_once()
