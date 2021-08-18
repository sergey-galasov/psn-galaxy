import math
import pytest
from galaxy.api.errors import UnknownBackendResponse


TROPHIES = [
    {"id": "NPWR15900_00", "name": "Persona 5: Dancing in Starlight"},
    {"id": "NPWR16532_00", "name": "KINGDOM HEARTS III"},
    {"id": "NPWR15608_00", "name": "Persona 4 Dancing All Night"},
    {"id": "NPWR15899_00", "name": "Persona 3: Dancing in Moonlight"},
    {"id": "NPWR11036_00", "name": "ACE COMBAT™ 7: SKIES UNKNOWN"},
    {"id": "NPWR03852_00", "name": "Dragon's Crown"},
    {"id": "NPWR16122_00", "name": "Fist of the North Star: Lost Paradise"},
    {"id": "NPWR16634_00", "name": "ACE COMBAT™ SQUADRON LEADER"},
    {"id": "NPWR16410_00", "name": "Castlevania Requiem: Symphony Of The Night & Rondo Of Blood"},
    {"id": "NPWR13243_00", "name": "SNK HEROINES Tag Team Frenzy"},
    {"id": "NPWR09167_00", "name": "Marvel's Spider-Man"},
    {"id": "NPWR15315_00", "name": "DRAGON QUEST XI: Echoes of an Elusive Age"},
    {"id": "NPWR13281_00", "name": "DARK SOULS™: REMASTERED"},
    {"id": "NPWR12990_00", "name": "Street Fighter 30th Anniversary Collection\n"},
    {"id": "NPWR14092_00", "name": "SEGA Mega Drive & Genesis Classics"},
    {"id": "NPWR13872_00", "name": "DETROIT: BECOME HUMAN"},
    {"id": "NPWR10879_00", "name": "Paladins"},
    {"id": "NPWR09886_00", "name": "School Girl/Zombie Hunter"},
    {"id": "NPWR12223_00", "name": "Tokyo Xanadu eX+"},
    {"id": "NPWR12961_00", "name": "WARRIORS ALL-STARS"},
    {"id": "NPWR12518_00", "name": "God of War"},
    {"id": "NPWR10979_00", "name": "Brawlhalla"},
    {"id": "NPWR11885_00", "name": "TERA"},
    {"id": "NPWR14858_00", "name": "Ni no Kuni™ II: Revenant Kingdom"},
    {"id": "NPWR08053_00", "name": "War of the Monsters™"},
    {"id": "NPWR11401_00", "name": "South Park™: The Fractured But Whole™"},
    {"id": "NPWR10890_00", "name": "Sniper Ghost Warrior 3"},
    {"id": "NPWR13550_00", "name": "SWORD ART ONLINE: FATAL BULLET"},
    {"id": "NPWR11735_00", "name": "METAL GEAR SURVIVE"},
    {"id": "NPWR11209_00", "name": "Hand of Fate 2"},
    {"id": "NPWR12176_00", "name": "88 Heroes"},
    {"id": "NPWR14240_00", "name": "DYNASTY WARRIORS 9"},
    {"id": "NPWR10035_00", "name": "Sky Force Anniversary"},
    {"id": "NPWR10673_00", "name": "Downwell"},
    {"id": "NPWR10126_00", "name": "Guilty Gear Xrd -Revelator- Trophy"},
    {"id": "NPWR06535_00", "name": "Blue Estate"},
    {"id": "NPWR07552_00", "name": "Rollers of the Realm"},
    {"id": "NPWR13920_00", "name": "Morphite"},
    {"id": "NPWR10039_00", "name": "Joe Dever's Lone Wolf Console Edition"},
    {"id": "NPWR11631_00", "name": "Monster Hunter: World"},
    {"id": "NPWR11350_00", "name": "Night In The Woods"},
    {"id": "NPWR14140_00", "name": "Iconoclasts"},
    {"id": "NPWR12541_00", "name": "The Silver Case HD"},
    {"id": "NPWR10787_00", "name": "Exist Archive"},
    {"id": "NPWR13363_00", "name": "Pyre"},
    {"id": "NPWR14333_00", "name": "STAR OCEAN™ - THE LAST HOPE -™ 4K & Full HD Remaster"},
    {"id": "NPWR07518_00", "name": "STREET FIGHTER V"},
    {"id": "NPWR09921_00", "name": "Gran Turismo Sport"},
    {"id": "NPWR11338_00", "name": "Injustice 2 Trophies"},
    {"id": "NPWR11619_00", "name": "Need for Speed™ Payback"},
    {"id": "NPWR12510_00", "name": "Wolfenstein® II: The New Colossus"},
    {"id": "NPWR12420_00", "name": ".hack//G.U. Last Recode"},
    {"id": "NPWR11424_00", "name": "Assassin's Creed® Origins"},
    {"id": "NPWR12568_00", "name": "ELEX"},
    {"id": "NPWR13161_00", "name": "Cyberdimension Neptunia: 4 Goddesses Online"},
    {"id": "NPWR11756_00", "name": "The Evil Within® 2"},
    {"id": "NPWR12586_00", "name": "_>OBSERVER_"},
    {"id": "NPWR10569_00", "name": "Middle-earth™: Shadow of War™"},
    {"id": "NPWR13858_00", "name": "Battle Chasers: Nightwar"},
    {"id": "NPWR12435_00", "name": "Dragon's Dogma: Dark Arisen"},
    {"id": "NPWR13202_00", "name": "Ruiner"},
    {"id": "NPWR10344_00", "name": "Hard Reset Redux"},
    {"id": "NPWR12704_00", "name": "Yonder: The Cloud Catcher Chronicles"},
    {"id": "NPWR11056_00", "name": "Destiny 2"},
    {"id": "NPWR11920_00", "name": "BLUE REFLECTION　"},
    {"id": "NPWR13133_00", "name": "Spacelords"},
    {"id": "NPWR09395_00", "name": "Tom Clancy’s Ghost Recon® Wildlands"},
    {"id": "NPWR13712_00", "name": "Ys VIII -Lacrimosa of DANA-"},
    {"id": "NPWR11690_00", "name": "Senran Kagura\nPEACH BEACH SPLASH"},
    {"id": "NPWR10362_00", "name": "Project CARS 2"},
    {"id": "NPWR11874_00", "name": "MARVEL VS. CAPCOM: INFINITE"},
    {"id": "NPWR12219_00", "name": "Pillars of Eternity: Complete Edition"},
    {"id": "NPWR13354_00", "name": "Life is Strange: Before the Storm"},
    {"id": "NPWR08922_00", "name": "LEGO® MARVEL's Avengers"},
    {"id": "NPWR11777_00", "name": "Resident Evil Revelations"},
    {"id": "NPWR09497_00", "name": "Agents of Mayhem"},
    {"id": "NPWR13408_00", "name": "Uncharted™: The Lost Legacy"},
    {"id": "NPWR06510_00", "name": "LEGO® Batman™ 3"},
    {"id": "NPWR11243_00", "name": "Batman"},
    {"id": "NPWR11474_00", "name": "RiME"},
    {"id": "NPWR12591_00", "name": "Hellblade: Senua's Sacrifice"},
    {"id": "NPWR08516_00", "name": "Overwatch: Origins Edition"},
    {"id": "NPWR10320_00", "name": "Sniper Elite 4"},
    {"id": "NPWR08661_00", "name": "DOOM®"},
    {"id": "NPWR12756_00", "name": "Shadow Tactics"},
    {"id": "NPWR12411_00", "name": "Bulletstorm: Full Clip Edition"},
    {"id": "NPWR12196_00", "name": "Stardew Valley"},
    {"id": "NPWR06600_00", "name": "Assassin's Creed® Unity"},
    {"id": "NPWR11261_00", "name": "Alone With You"},
    {"id": "NPWR12540_00", "name": "Kona"},
    {"id": "NPWR12765_00", "name": "Late Shift"},
    {"id": "NPWR13412_00", "name": "Fortnite"},
    {"id": "NPWR13022_00", "name": "Cosmic Star Heroine"},
    {"id": "NPWR07942_00", "name": "Ratchet & Clank™"},
    {"id": "NPWR12115_00", "name": "Full Throttle Remastered"},
    {"id": "NPWR08193_00", "name": "Mirror's Edge™ Catalyst"},
    {"id": "NPWR08609_00", "name": "Bastion"},
    {"id": "NPWR10066_00", "name": "Enter The Gungeon"},
    {"id": "NPWR09096_00", "name": "Curses 'n Chaos"},
    {"id": "NPWR11367_00", "name": "FINAL FANTASY Ⅻ THE ZODIAC AGE"}
]

TROPHIES_PAGE = "https://url.com/get-prophies?limit={limit}&offset={offset}"


def create_backend_response_generator(limit=len(TROPHIES)):
    def gen_range(start, stop, step):
        return ((n, min((n + step), stop)) for n in range(start, stop, step))

    def response_generator():
        for start, stop in gen_range(0, len(TROPHIES), limit):
            yield {
                "totalResults": len(TROPHIES),
                "offset": start,
                "limit": limit,
                "trophyTitles": TROPHIES[start:stop]
            }

    return response_generator


def create_backend_response_all_trophies():
    return {"totalResults": len(TROPHIES), "offset": 0, "limit": len(TROPHIES), "trophyTitles": TROPHIES}


def parser(data):
    return [{g["id"]: g["name"]} for g in data["trophyTitles"]] if data else []


def assert_all_games_fetched(games):
    assert games == [{g["id"]: g["name"]} for g in TROPHIES]


@pytest.mark.asyncio
async def test_simple_fetch(
    http_get,
    authenticated_psn_client,
):
    http_get.side_effect = create_backend_response_generator()()
    assert_all_games_fetched(await authenticated_psn_client.fetch_data(parser, TROPHIES_PAGE))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_pagination(
    http_get,
    authenticated_psn_client,
):
    limit = 13

    http_get.side_effect = create_backend_response_generator(limit)()
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, TROPHIES_PAGE, "totalResults", limit))
    http_get.assert_called()
    assert math.ceil(len(TROPHIES) / limit) == http_get.call_count


@pytest.mark.asyncio
async def test_single_fetch(
    http_get,
    authenticated_psn_client,
):
    http_get.side_effect = create_backend_response_generator()()
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, TROPHIES_PAGE, "totalResults", len(TROPHIES)))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_less_than_expected(
    http_get,
    authenticated_psn_client,
):
    http_get.side_effect = create_backend_response_generator()()
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, TROPHIES_PAGE, "totalResults", len(TROPHIES) + 50))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_no_total_results(
    http_get,
    authenticated_psn_client,
):
    response = create_backend_response_all_trophies()
    del response["totalResults"]
    http_get.return_value = response
    assert_all_games_fetched(await authenticated_psn_client.fetch_paginated_data(
        parser, TROPHIES_PAGE, "totalResults", len(TROPHIES)))
    http_get.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_total_results(
    http_get,
    authenticated_psn_client,
):
    response = create_backend_response_all_trophies()
    response["totalResults"] = "bad_number"
    http_get.return_value = response

    with pytest.raises(UnknownBackendResponse):
        await authenticated_psn_client.fetch_paginated_data(parser, TROPHIES_PAGE, "totalResults", len(TROPHIES))
    http_get.assert_called_once()
