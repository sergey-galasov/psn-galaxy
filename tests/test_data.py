from galaxy.api.consts import LicenseType
from galaxy.api.types import Game, LicenseInfo, SubscriptionGame

COMMUNICATION_ID = "NPWR11556_00"

DEFAULT_LICENSE = LicenseInfo(LicenseType.SinglePurchase, None)

GAMES = [
    Game("CUSA07917_00", "Tooth and Tail", [], DEFAULT_LICENSE),
    Game("CUSA02000_00", "Batman: Return to Arkham - Arkham City", [], DEFAULT_LICENSE),
    Game("CUSA05603_00", "Batman", [], DEFAULT_LICENSE),
    Game("CUSA01427_00", "Game of Thrones", [], DEFAULT_LICENSE),
    Game("CUSA01858_00", "Grim Fandango Remastered", [], DEFAULT_LICENSE),
    Game("CUSA06291_00", "NARUTO SHIPPUDEN: Ultimate Ninja STORM TRILOGY", [], DEFAULT_LICENSE),
    Game("CUSA00860_00", "Tales from the Borderlands", [], DEFAULT_LICENSE),
    Game("CUSA07320_00", "Horizon Zero Dawnâ„¢", [], DEFAULT_LICENSE),
    Game("CUSA07140_00", "Dreamfall Chapters", [], DEFAULT_LICENSE),
    Game("CUSA08487_00", "Life is Strange: Before the Storm", [], DEFAULT_LICENSE),
]

DLCS = [
    Game("CUSA07719_00", "Dreamfall Chapters (Original Soundtrack)", [], DEFAULT_LICENSE)
]

TITLES = GAMES + DLCS

PARSED_GAME_TITLES = [
    {"titleId": "CUSA07917_00", "name": "Tooth and Tail"},
    {"titleId": "CUSA02000_00", "name": "Batman: Return to Arkham - Arkham City"},
    {"titleId": "CUSA05603_00", "name": "Batman"},
    {"titleId": "CUSA01427_00", "name": "Game of Thrones"},
    {"titleId": "CUSA01858_00", "name": "Grim Fandango Remastered"},
    {"titleId": "CUSA06291_00", "name": "NARUTO SHIPPUDEN: Ultimate Ninja STORM TRILOGY"},
    # shown as single item in the console
    {"titleId": "CUSA00860_00", "name": "Tales from the Borderlands"},
    {"titleId": "CUSA07320_00", "name": "Horizon Zero Dawnâ„¢"},
    {"titleId": "CUSA07140_00", "name": "Dreamfall Chapters"},
    {"titleId": "CUSA08487_00", "name": "Life is Strange: Before the Storm"},
]

BACKEND_GAME_TITLES = {
    "data": {
        "purchasedTitlesRetrieve": {
            "games": PARSED_GAME_TITLES,
            "pageInfo": {
                "start": 0,
                "size": 11,
                "totalCount": 11,
            }
        }
    }
}

SUBSCRIPTION_GAMES = [
    SubscriptionGame(game_title='BioShock: The Collection', game_id='CUSA03979_00'),
    SubscriptionGame(game_title='The Sims™ 4', game_id='CUSA09209_00'),
    SubscriptionGame(game_title='Firewall Zero Hour™', game_id='CUSA09831_00')
]

PSN_PLUS_MONTHLY_FREE_GAMES_HTML = """
<div class="ems-sdk-strand-paginator">
    <div class="ems-sdk-strand-paginator__body">
         <ul class="psw-strand-scroller ems-sdk-product-tile-list psw-grid-x psw-grid-margin-x psw-tablet-l-up-6 psw-tablet-p-up-3 psw-mobile-p-up-2" data-qa="ems-sdk-product-tile-list" style="transform:translateX(0%);flex-wrap:nowrap">
            <li class="psw-cell">
               <div class="ems-sdk-product-tile" data-qa="ems-sdk-product-tile" data-qa-index="0">
                  <a class="ems-sdk-product-tile-link" href="/en-us/product/UP4040-CUSA03979_00-CONTROLUEBUNDLE0" data-track-content="web:store:product-tile" data-track-click="web:store:product-tile" data-telemetry-meta="{&quot;id&quot;:&quot;UP4040-CUSA03979_00-CONTROLUEBUNDLE0&quot;,&quot;index&quot;:0,&quot;name&quot;:&quot;BioShock: The Collection&quot;,&quot;titleId&quot;:&quot;CUSA03979_00&quot;}" title="BioShock: The Collection">
                     <div class="ems-sdk-product-tile-image" data-qa="ems-sdk-product-tile-image">
                        <div class="ems-sdk-product-tile-image__container">
                           <span data-qa="" class="psw-illustration psw-illustration--default-product-image default-product-img">
                              <svg>
                                 <title></title>
                                 <use href="#ps-illustration:default-product-image"></use>
                              </svg>
                           </span>
                           <span data-qa="ems-sdk-product-tile-image-img" style="width:100%;min-width:100%" class="psw-media-frame psw-fill-x psw-image psw-aspect-1-1">
                              <img aria-hidden="true" loading="lazy" data-qa="ems-sdk-product-tile-image-img#preview" alt="" class="psw-blur psw-top-left psw-l-fit-cover" src="https://image.api.playstation.com/vulcan/ap/rnd/202008/2111/hvVTsd8akckaGtN2eZ3yIuwc.png?w=54&amp;thumb=true"/>
                              <noscript class="psw-layer"><img class="psw-top-left psw-l-fit-cover" loading="lazy" data-qa="ems-sdk-product-tile-image-img#image-no-js" alt="" src="https://image.api.playstation.com/vulcan/ap/rnd/202008/2111/hvVTsd8akckaGtN2eZ3yIuwc.png"/></noscript>
                           </span>
                        </div>
                        <div class="ems-sdk-product-tile-image__badge-container psw-m-r-3xs"><span class="psw-p-x-3xs ems-sdk-product-tile-image__badge" data-qa="ems-sdk-product-tile-image-badge">PS4</span></div>
                     </div>
                     <section class="ems-sdk-product-tile__details" data-qa="ems-sdk-product-tile-details"><span class="psw-body-2 psw-truncate-text-2 psw-p-t-2xs" data-qa="ems-sdk-product-tile-name">BioShock: The Collection</span></section>
                  </a>
               </div>
            </li>
            <li class="psw-cell">
               <div class="ems-sdk-product-tile" data-qa="ems-sdk-product-tile" data-qa-index="2">
                  <a class="ems-sdk-product-tile-link" href="/en-us/product/UP9000-CUSA09209_00-DALLSTARSPLUS001" data-track-content="web:store:product-tile" data-track-click="web:store:product-tile" data-telemetry-meta="{&quot;id&quot;:&quot;UP9000-CUSA09209_00-DALLSTARSPLUS001&quot;,&quot;index&quot;:2,&quot;name&quot;:&quot;The Sims™ 4&quot;,&quot;titleId&quot;:&quot;CUSA09209_00&quot;}" title="The Sims™ 4">
                     <div class="ems-sdk-product-tile-image" data-qa="ems-sdk-product-tile-image">
                        <div class="ems-sdk-product-tile-image__container">
                           <span data-qa="" class="psw-illustration psw-illustration--default-product-image default-product-img">
                              <svg>
                                 <title></title>
                                 <use href="#ps-illustration:default-product-image"></use>
                              </svg>
                           </span>
                           <span data-qa="ems-sdk-product-tile-image-img" style="width:100%;min-width:100%" class="psw-media-frame psw-fill-x psw-image psw-aspect-1-1">
                              <img aria-hidden="true" loading="lazy" data-qa="ems-sdk-product-tile-image-img#preview" alt="" class="psw-blur psw-top-left psw-l-fit-cover" src="https://image.api.playstation.com/vulcan/img/rnd/202010/0513/MYXPEsm7SVKszWWAHhcNfta6.png?w=54&amp;thumb=true"/>
                              <noscript class="psw-layer"><img class="psw-top-left psw-l-fit-cover" loading="lazy" data-qa="ems-sdk-product-tile-image-img#image-no-js" alt="" src="https://image.api.playstation.com/vulcan/img/rnd/202010/0513/MYXPEsm7SVKszWWAHhcNfta6.png"/></noscript>
                           </span>
                        </div>
                        <div class="ems-sdk-product-tile-image__badge-container psw-m-r-3xs"><span class="psw-p-x-3xs ems-sdk-product-tile-image__badge" data-qa="ems-sdk-product-tile-image-badge">PS5</span></div>
                     </div>
                     <section class="ems-sdk-product-tile__details" data-qa="ems-sdk-product-tile-details"><span class="psw-body-2 psw-truncate-text-2 psw-p-t-2xs" data-qa="ems-sdk-product-tile-name">The Sims™ 4</span></section>
                  </a>
               </div>
            </li>
            <li class="psw-cell">
               <div class="ems-sdk-product-tile" data-qa="ems-sdk-product-tile" data-qa-index="3">
                  <a class="ems-sdk-product-tile-link" href="/en-us/product/UP9000-CUSA09831_00-CONCRETEGENIE000" data-track-content="web:store:product-tile" data-track-click="web:store:product-tile" data-telemetry-meta="{&quot;id&quot;:&quot;UP9000-CUSA09831_00-CONCRETEGENIE000&quot;,&quot;index&quot;:3,&quot;name&quot;:&quot;Firewall Zero Hour™&quot;,&quot;titleId&quot;:&quot;CUSA09831_00&quot;}" title="Firewall Zero Hour™">
                     <div class="ems-sdk-product-tile-image" data-qa="ems-sdk-product-tile-image">
                        <div class="ems-sdk-product-tile-image__container">
                           <span data-qa="" class="psw-illustration psw-illustration--default-product-image default-product-img">
                              <svg>
                                 <title></title>
                                 <use href="#ps-illustration:default-product-image"></use>
                              </svg>
                           </span>
                           <span data-qa="ems-sdk-product-tile-image-img" style="width:100%;min-width:100%" class="psw-media-frame psw-fill-x psw-image psw-aspect-1-1">
                              <img aria-hidden="true" loading="lazy" data-qa="ems-sdk-product-tile-image-img#preview" alt="" class="psw-blur psw-top-left psw-l-fit-cover" src="https://image.api.playstation.com/vulcan/img/rnd/202011/0923/lbjNLN1pA9vZiHjECrt3Gnc7.png?w=54&amp;thumb=true"/>
                              <noscript class="psw-layer"><img class="psw-top-left psw-l-fit-cover" loading="lazy" data-qa="ems-sdk-product-tile-image-img#image-no-js" alt="" src="https://image.api.playstation.com/vulcan/img/rnd/202011/0923/lbjNLN1pA9vZiHjECrt3Gnc7.png"/></noscript>
                           </span>
                        </div>
                        <div class="ems-sdk-product-tile-image__badge-container psw-m-r-3xs"><span class="psw-p-x-3xs ems-sdk-product-tile-image__badge" data-qa="ems-sdk-product-tile-image-badge">PS4</span></div>
                     </div>
                     <section class="ems-sdk-product-tile__details" data-qa="ems-sdk-product-tile-details"><span class="psw-body-2 psw-truncate-text-2 psw-p-t-2xs" data-qa="ems-sdk-product-tile-name">Firewall Zero Hour™</span></section>
                  </a>
               </div>
            </li>
            <li class="psw-cell">
               <div class="ems-sdk-product-tile" data-qa="ems-sdk-product-tile" data-qa-index="4">
                  <a class="ems-sdk-product-tile-link" href="https://www.playstation.com/explore/playstation-plus/?smcid=webstore%3Aen-us%3APRODUCT%3AIP9101-NPIA90005_01-1YEARPACKAGE0000" data-track-content="web:store:product-tile" data-track-click="web:store:product-tile" data-telemetry-meta="{&quot;id&quot;:&quot;IP9101-NPIA90005_01-1YEARPACKAGE0000&quot;,&quot;index&quot;:4,&quot;name&quot;:&quot;PlayStation Plus 12-Month Subscription&quot;,&quot;titleId&quot;:&quot;NPIA90005_01&quot;}" title="PlayStation Plus 12-Month Subscription">
                     <div class="ems-sdk-product-tile-image" data-qa="ems-sdk-product-tile-image">
                        <div class="ems-sdk-product-tile-image__container">
                           <span data-qa="" class="psw-illustration psw-illustration--default-product-image default-product-img">
                              <svg>
                                 <title></title>
                                 <use href="#ps-illustration:default-product-image"></use>
                              </svg>
                           </span>
                           <span data-qa="ems-sdk-product-tile-image-img" style="width:100%;min-width:100%" class="psw-media-frame psw-fill-x psw-image psw-aspect-1-1">
                              <img aria-hidden="true" loading="lazy" data-qa="ems-sdk-product-tile-image-img#preview" alt="" class="psw-blur psw-top-left psw-l-fit-cover" src="https://image.api.playstation.com/vulcan/img/cfn/11307_n5ZkkEw-u6TMBK-91JA4Xd09lfjMjBSaPEnIAdVNjcY7gzUw2r3hj4Zw7HUFcQx1WOFQeFPzUYlMCvn8h5TwUPJFSI.png?w=54&amp;thumb=true"/>
                              <noscript class="psw-layer"><img class="psw-top-left psw-l-fit-cover" loading="lazy" data-qa="ems-sdk-product-tile-image-img#image-no-js" alt="" src="https://image.api.playstation.com/vulcan/img/cfn/11307_n5ZkkEw-u6TMBK-91JA4Xd09lfjMjBSaPEnIAdVNjcY7gzUw2r3hj4Zw7HUFcQx1WOFQeFPzUYlMCvn8h5TwUPJFSI.png"/></noscript>
                           </span>
                        </div>
                        <div class="ems-sdk-product-tile-image__badge-container psw-m-r-3xs"></div>
                     </div>
                     <section class="ems-sdk-product-tile__details" data-qa="ems-sdk-product-tile-details"><span class="psw-body-2 psw-truncate-text-2 psw-p-t-2xs" data-qa="ems-sdk-product-tile-name">PlayStation Plus 12-Month Subscription</span></section>
                  </a>
               </div>
            </li>
            <li class="psw-cell">
               <div class="ems-sdk-product-tile" data-qa="ems-sdk-product-tile" data-qa-index="5">
                  <a class="ems-sdk-product-tile-link" href="https://www.playstation.com/explore/playstation-plus/?smcid=webstore%3Aen-us%3APRODUCT%3AIP9101-NPIA90005_01-3MONTHPACKAGE000" data-track-content="web:store:product-tile" data-track-click="web:store:product-tile" data-telemetry-meta="{&quot;id&quot;:&quot;IP9101-NPIA90005_01-3MONTHPACKAGE000&quot;,&quot;index&quot;:5,&quot;name&quot;:&quot;PlayStation Plus 3-Month Subscription&quot;,&quot;titleId&quot;:&quot;NPIA90005_01&quot;}" title="PlayStation Plus 3-Month Subscription">
                     <div class="ems-sdk-product-tile-image" data-qa="ems-sdk-product-tile-image">
                        <div class="ems-sdk-product-tile-image__container">
                           <span data-qa="" class="psw-illustration psw-illustration--default-product-image default-product-img">
                              <svg>
                                 <title></title>
                                 <use href="#ps-illustration:default-product-image"></use>
                              </svg>
                           </span>
                           <span data-qa="ems-sdk-product-tile-image-img" style="width:100%;min-width:100%" class="psw-media-frame psw-fill-x psw-image psw-aspect-1-1">
                              <img aria-hidden="true" loading="lazy" data-qa="ems-sdk-product-tile-image-img#preview" alt="" class="psw-blur psw-top-left psw-l-fit-cover" src="https://image.api.playstation.com/vulcan/img/cfn/11307c-OgyoHp2L_r8dpNZet4gdeCvRTletsGVxaxW2ixVkInZQEZbCGbn14PkuI3_cTWpv-1HIoqGvOiaFNCQzCHZYYr46N.png?w=54&amp;thumb=true"/>
                              <noscript class="psw-layer"><img class="psw-top-left psw-l-fit-cover" loading="lazy" data-qa="ems-sdk-product-tile-image-img#image-no-js" alt="" src="https://image.api.playstation.com/vulcan/img/cfn/11307c-OgyoHp2L_r8dpNZet4gdeCvRTletsGVxaxW2ixVkInZQEZbCGbn14PkuI3_cTWpv-1HIoqGvOiaFNCQzCHZYYr46N.png"/></noscript>
                           </span>
                        </div>
                        <div class="ems-sdk-product-tile-image__badge-container psw-m-r-3xs"></div>
                     </div>
                     <section class="ems-sdk-product-tile__details" data-qa="ems-sdk-product-tile-details"><span class="psw-body-2 psw-truncate-text-2 psw-p-t-2xs" data-qa="ems-sdk-product-tile-name">PlayStation Plus 3-Month Subscription</span></section>
                  </a>
               </div>
            </li>
            <li class="psw-cell">
               <div class="ems-sdk-product-tile" data-qa="ems-sdk-product-tile" data-qa-index="6">
                  <a class="ems-sdk-product-tile-link" href="https://www.playstation.com/explore/playstation-plus/?smcid=webstore%3Aen-us%3APRODUCT%3AIP9101-NPIA90005_01-PLUS1MONTHPACKAG" data-track-content="web:store:product-tile" data-track-click="web:store:product-tile" data-telemetry-meta="{&quot;id&quot;:&quot;IP9101-NPIA90005_01-PLUS1MONTHPACKAG&quot;,&quot;index&quot;:6,&quot;name&quot;:&quot;PlayStation Plus 1-Month Subscription&quot;,&quot;titleId&quot;:&quot;NPIA90005_01&quot;}" title="PlayStation Plus 1-Month Subscription">
                     <div class="ems-sdk-product-tile-image" data-qa="ems-sdk-product-tile-image">
                        <div class="ems-sdk-product-tile-image__container">
                           <span data-qa="" class="psw-illustration psw-illustration--default-product-image default-product-img">
                              <svg>
                                 <title></title>
                                 <use href="#ps-illustration:default-product-image"></use>
                              </svg>
                           </span>
                           <span data-qa="ems-sdk-product-tile-image-img" style="width:100%;min-width:100%" class="psw-media-frame psw-fill-x psw-image psw-aspect-1-1">
                              <img aria-hidden="true" loading="lazy" data-qa="ems-sdk-product-tile-image-img#preview" alt="" class="psw-blur psw-top-left psw-l-fit-cover" src="https://image.api.playstation.com/vulcan/img/cfn/11307ymhpS0kVde1dioghwldgk6oi0CCjmt-jxvL_ilCipOgp0dwNtdJU0tPXlZta0_AQuJNm0UUfduYd4FJcWzj_UkI8DvH.png?w=54&amp;thumb=true"/>
                              <noscript class="psw-layer"><img class="psw-top-left psw-l-fit-cover" loading="lazy" data-qa="ems-sdk-product-tile-image-img#image-no-js" alt="" src="https://image.api.playstation.com/vulcan/img/cfn/11307ymhpS0kVde1dioghwldgk6oi0CCjmt-jxvL_ilCipOgp0dwNtdJU0tPXlZta0_AQuJNm0UUfduYd4FJcWzj_UkI8DvH.png"/></noscript>
                           </span>
                        </div>
                        <div class="ems-sdk-product-tile-image__badge-container psw-m-r-3xs"></div>
                     </div>
                     <section class="ems-sdk-product-tile__details" data-qa="ems-sdk-product-tile-details"><span class="psw-body-2 psw-truncate-text-2 psw-p-t-2xs" data-qa="ems-sdk-product-tile-name">PlayStation Plus 1-Month Subscription</span></section>
                  </a>
               </div>
            </li>
         </ul>
    </div>
</div>
"""
