from .adli import StoreAdliSpider
from .blcv import StoreBlcvSpider
from .elis import StoreElisSpider
from .mere import StoreMereSpider
from .sela import StoreSelaSpider
from .znwr import StoreZnwrSpider
from .bnprt import StoreBnprtSpider
from .choux import StoreChouxSpider
from .divno import StoreDivnoSpider
from .evefb import StoreEvefbSpider
from .forms import StoreFormsSpider
from .ligio import StoreLigioSpider
from .myari import StoreMyariSpider
from .befree import StoreBefreeSpider
from .gate31 import StoreGate31Spider
from .liklab import StoreLiklabSpider
from .minimo import StoreMinimoSpider
from .mollis import StoreMollisSpider
from .ruxara import StoreRuxaraSpider
from .shishi import StoreShishiSpider
from .soeasy import StoreSoeasySpider
from .topinn import StoreTopinnSpider
from .toptop import StoreToptopSpider
from .voishe import StoreVoisheSpider
from .zarina import StoreZarinaSpider
from .charuel import StoreCharuelSpider
from .ekonika import StoreEkonikaSpider
from .freedom import StoreFreedomSpider
from .imocean import StoreImoceanSpider
from .julitoo import StoreJulitooSpider
from .kapsula import StoreKapsulaSpider
from .latrica import StoreLatrikaSpider
from .mavelty import StoreMaveltySpider
from .samchuk import StoreSamchukSpider
from .sorelle import StoreSorelleSpider
from .storeez import StoreStoreezSpider
from .amestore import StoreAmestoreSpider
from .emkashop import StoreEmkashopSpider
from .infamily import StoreInfamilySpider
from .limeshop import StoreLimeshopSpider
from .namelazz import StoreNamelazzSpider
from .studio29 import StoreStudio29Spider
from .svyataya import StoreSvyatayaSpider
from .ushatava import StoreUshatavaSpider
from .youstore import StoreYoustoreSpider
from .youwanna import StoreYouwannaSpider
from .allweneed import StoreAllweneedSpider
from .daisyknit import StoreDaisyknitSpider
from .droidandi import StoreDroidandiSpider
from .iamstudio import StoreIamstudioSpider
from .indressss import StoreIndressssSpider
from .marchelas import StoreMarchelasSpider
from .moodstore import StoreSpider
from .nevalenki import StoreNevalenkiSpider
from .nudestory import StoreNudestorySpider
from .rogovshop import StoreRogovshopSpider
from .shitrendy import StoreShitrendySpider
from .snowqueen import StoreSnowqueenSpider
from .theselect import StoreTheselectSpider
from .tottishop import StoreTottiShopSpider
from .barmariska import StoreBarmariskaSpider
from .bstatement import StoreBstatementSpider
from .cantikhand import StoreCantikhandSpider
from .charmstore import StoreCharmstoreSpider
from .deapremium import StoreDeapremiumSpider
from .irenvartik import StoreIrenvartikSpider
from .levertyver import StoreLevertyverSpider
from .monochrome import StoreMonochromeSpider
from .radenshoes import StoreRadenshoesSpider
from .shuclothes import StoreShuclothesSpider
from .urbantiger import StoreUrbantigerSpider
from .wearmellow import StoreWearmellowSpider
from .andelinaerf import StoreAngelinaerfSpider
from .chaikastore import StoreChaikastoreSpider
from .darsistudio import StoreDarsiStudioSpider
from .edgedesigns import StoreEdgedesignsSpider
from .inspireshop import StoreInspireshopSpider
from .sashaostrov import StoreSashaostrovSpider
from .sorryiamnot import StoreSorryiamnotSpider
from .thomasmuenz import StoreThomasmuenzSpider
from .tobeblossom import StoreTobeblossomSpider
from .loverepublic import StoreLoverepublicSpider
from .postmeridiem import StorePostmeridiemSpider
from .respectshoes import StoreRespectshoesSpider
from .stefanorossi import StoreStefanorossiSpider
from .tjcollection import StoreTjcollectionSpider
from .asyasemyonova import StoreAsyasemyonovaSpider
from .brusnikabrand import StoreBrusnikabrandSpider
from .ludanikishina import StoreLudanikishinaSpider
from .newberrystore import StoreNewberrystoreSpider
from .rabbirloafers import StoreRabbitloafersSpider
from .sobrightdress import StoreSobrightdressSpider
from .countrytextile import StoreCountrytextileSpider
from .alinecollection import StoreAlinecollectionSpider
from .postpostscriptum import StorePostpostscriptumSpider
from .presentandsimple import StorePresentandsimpleSpider
from .wonderwandershop import StoreWonderwandershopSpider
from .yanabesfamilnaya import StoreYanabesfamilnayaSpider
from .akhmadullinadreams import StoreAkhmadullinadreamsSpider

spiders_map = {
    spider.name: spider
    for spider in [
        StoreSpider,
        StoreGate31Spider,
        StoreElisSpider,
        StoreLatrikaSpider,
        StoreIamstudioSpider,
        StoreTottiShopSpider,
        StoreEmkashopSpider,
        StoreFormsSpider,
        StoreVoisheSpider,
        StoreCharmstoreSpider,
        StoreCantikhandSpider,
        StoreCharuelSpider,
        StoreSobrightdressSpider,
        StoreDroidandiSpider,
        StoreBrusnikabrandSpider,
        StoreIndressssSpider,
        StoreToptopSpider,
        StoreStoreezSpider,
        StoreStudio29Spider,
        StoreNudestorySpider,
        StoreLimeshopSpider,
        StoreAllweneedSpider,
        StoreZarinaSpider,
        StoreLoverepublicSpider,
        StoreSelaSpider,
        StoreJulitooSpider,
        StoreAngelinaerfSpider,
        StoreTheselectSpider,
        StoreDarsiStudioSpider,
        StoreMyariSpider,
        StoreDaisyknitSpider,
        StoreImoceanSpider,
        StoreRuxaraSpider,
        StorePresentandsimpleSpider,
        StoreAmestoreSpider,
        StoreMarchelasSpider,
        StoreNamelazzSpider,
        StoreChaikastoreSpider,
        StoreTopinnSpider,
        StoreWonderwandershopSpider,
        StoreBarmariskaSpider,
        StoreAkhmadullinadreamsSpider,
        StoreLevertyverSpider,
        StoreSvyatayaSpider,
        StoreUrbantigerSpider,
        StoreYoustoreSpider,
        StoreZnwrSpider,
        StoreMollisSpider,
        StoreLiklabSpider,
        StoreSamchukSpider,
        StoreAlinecollectionSpider,
        StoreSorelleSpider,
        StoreUshatavaSpider,
        StoreYouwannaSpider,
        StoreRogovshopSpider,
        StoreMonochromeSpider,
        StoreEvefbSpider,
        StoreMinimoSpider,
        StoreWearmellowSpider,
        StoreInspireshopSpider,
        StoreLigioSpider,
        StoreLudanikishinaSpider,
        StoreBnprtSpider,
        StoreShishiSpider,
        StoreAdliSpider,
        StoreSoeasySpider,
        StoreEdgedesignsSpider,
        StoreSashaostrovSpider,
        StoreNewberrystoreSpider,
        StoreBlcvSpider,
        StoreBefreeSpider,
        StorePostmeridiemSpider,
        StoreShuclothesSpider,
        StoreBstatementSpider,
        StoreFreedomSpider,
        StoreCountrytextileSpider,
        StoreYanabesfamilnayaSpider,
        StorePostpostscriptumSpider,
        StoreSorryiamnotSpider,
        StoreShitrendySpider,
        StoreEkonikaSpider,
        StoreRadenshoesSpider,
        StoreStefanorossiSpider,
        StoreRabbitloafersSpider,
        StoreIrenvartikSpider,
        StoreNevalenkiSpider,
        StoreThomasmuenzSpider,
        StoreTjcollectionSpider,
        StoreRespectshoesSpider,
        StoreDeapremiumSpider,
        StoreDivnoSpider,
        StoreMaveltySpider,
        StoreInfamilySpider,
        StoreTobeblossomSpider,
        StoreSnowqueenSpider,
        StoreChouxSpider,
        StoreKapsulaSpider,
        StoreMereSpider,
        StoreAsyasemyonovaSpider,
    ]
}
