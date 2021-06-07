import pytest
from galaxy.api.errors import UnknownBackendResponse
from galaxy.api.types import SubscriptionGame

from parsers import PSNGamesParser


@pytest.mark.asyncio
@pytest.mark.parametrize("http_response, expected_result", [
    pytest.param("<div class=ems-sdk-strand-paginator><a></a></div>", [], id="'a' tag without 'ems-sdk-strand-paginator' class"),
    pytest.param("<div class=ems-sdk-strand-paginator><a class=ems-sdk-product-tile-link></a></div>", [], id="'a' tag without 'data-telemetry-meta' attr"),
    pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            '<a class=ems-sdk-product-tile-link data-telemetry-meta=""></a>'
        '</div>',
        [],
        id="empty 'data-telemetry-meta' attr"
    ),
    pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"name\":\"Firewall Zero Hour™\",\"titleId\":\"CUSA09831_00\"}'>"
            "</a>"
        '</div>',
        [SubscriptionGame(game_id="CUSA09831_00", game_title="Firewall Zero Hour™")],
        id="One correct game"
    ),
    pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"titleId\":\"CUSA09831_00\"}'>"
            "</a>"
        '</div>',
        [],
        id="Incorrect game - without name"
    ),
    pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"name\":\"Firewall Zero Hour™\"}'>"
            "</a>"
        '</div>',
        [],
        id="Incorrect game - without titleID"
    ),
    pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"name\":\"Firewall Zero Hour™\",\"titleId\":\"CUSA09831_00\"}'>"
            "</a>"
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"name\":\"Firewall Zero Hour 2™\",\"titleId\":\"CUSA09831_01\"}'>"
            "</a>"
        '</div>',
        [SubscriptionGame(game_id="CUSA09831_00", game_title="Firewall Zero Hour™"),
         SubscriptionGame(game_id="CUSA09831_01", game_title="Firewall Zero Hour 2™")],
        id="Two correct games"
    ),
    pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"name\":\"Firewall Zero Hour™\",\"titleId\":\"CUSA09831_00\"}'>"
            "</a>"
            "<a class=ems-sdk-product-tile-link data-telemetry-meta="
            "'{\"id\":\"SOME_ID\",\"index\":3,\"titleId\":\"CUSA09831_01\"}'>"
            "</a>"
        '</div>',
        [SubscriptionGame(game_id="CUSA09831_00", game_title="Firewall Zero Hour™")],
        id="Two games - one incorrect, without name"
    ),
   pytest.param(
        '<div class=ems-sdk-strand-paginator>'
            "<a class=\"ems-sdk-product-tile-link\" href=\"/ja-jp/product/JP0507-PPSA01954_00-CONTROLUEPS50001\" "
            "data-track-content=\"web:store:product-tile\" data-track-click=\"web:store:product-tile\" "
            "data-telemetry-meta=\"{&quot;id&quot;:&quot;JP0507-PPSA01954_00-CONTROLUEPS50001&quot;,&quot;index&quot;:1,&quot;name&quot;:&quot;『CONTROL』アルティメットエディション&quot;,&quot;price&quot;:&quot;定額サービス対象&quot;,&quot;titleId&quot;:&quot;PPSA01954_00&quot;}\" "
            "title=\"『CONTROL』アルティメットエディション\">"
        '</div>',
        [SubscriptionGame(game_id="PPSA01954_00", game_title="『CONTROL』アルティメットエディション")],
        id="Japanese version"
    ),
])
async def test_parse_subscription_games(http_response, expected_result):
    parser = PSNGamesParser().parse(http_response)

    assert parser == expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize("http_response", [
    pytest.param(""),
    pytest.param("ems-sdk-strand-paginator-WRONG_TAG"),
    pytest.param("<div class=ems-sdk-strand-paginator-WRONG_TAG></div>"),
    ])
async def test_parse_subscription_games_raise_lack_paginator_tag(http_response):
    with pytest.raises(UnknownBackendResponse):
        PSNGamesParser().parse(http_response)
