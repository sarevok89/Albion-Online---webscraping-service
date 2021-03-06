import json
import logging
import requests

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


def generate_items_dict():
    """
    Function going through 'albionchest.com' page and fetching data from it.
    Since it doesn't contain all the required data, few additional dictionaries
    are provided down below.

    Note: On 'albionchest.com' there's an error in the name of
    '2H_ENIGMATICORB_MORGANA'. It's 'Eye of Secrets', while it's supposed to be
    'Malevolent Locus'. It get's replaced automatically by this script.

    :return: Returns 'items_dict.json' file containing computer friendly names
    with their user friendly translations of all weapons, armors, shoes,
    helmets, off hands and capes in Albion Online.
    """

    logger.debug('Creating json file for items unique_id > regular_name '
                 'translation')
    weapon_url = 'http://www.albionchest.com/?direction=&page=1&' \
                 'search=&search_chest_tier=&search_chest_type=Weapon&' \
                 'sort=&utf8=%E2%9C%93'
    equipment_url = 'http://www.albionchest.com/?direction=&page=1&' \
                    'search=&search_chest_tier=&search_chest_type=Equipment&' \
                    'sort=&utf8=%E2%9C%93'
    tool_url = 'http://www.albionchest.com/?direction=&page=1&search=&' \
               'search_chest_tier=&search_chest_type=Tool&sort=&utf8=%E2%9C%93'
    skinner_url = 'http://www.albionchest.com/?commit=Search&direction=&' \
                  'page=1&search=skinner&search_chest_tier=&' \
                  'search_chest_type=&sort=&utf8=%E2%9C%93'
    quarrier_url = 'http://www.albionchest.com/?commit=Search&direction=&' \
                   'page=1&search=quarrier&search_chest_tier=&' \
                   'search_chest_type=&sort=&utf8=%E2%9C%93'

    items_dict = {}

    for item in [weapon_url, equipment_url, tool_url,
                 quarrier_url, skinner_url]:
        logger.debug(f'Fetching data from {item}')
        url = item
        start_url = 'http://www.albionchest.com/?direction=&page='

        item_type = url.replace('http://www.albionchest.com/?direction=&'
                                'page=1&search=&search_chest_tier=&'
                                'search_chest_type=', '')
        item_type = item_type.replace('&sort=&utf8=%E2%9C%93', '')

        end_url = f'&search=&search_chest_tier=&' \
            f'search_chest_type={item_type}&sort=&utf8=%E2%9C%93'

        r = requests.get(url)
        c = r.content
        soup = BeautifulSoup(c, 'html.parser')
        pages = soup.find('div', {'class': 'pagination'}).find_all('a')[-2].text

        for page in range(1, int(pages) + 1):
            logger.debug(f'Fetching data from page {page}')
            url = start_url + str(page) + end_url
            r = requests.get(url)
            c = r.content
            soup = BeautifulSoup(c, 'html.parser')
            data = soup.find(
                'div', {'id': 'list-albionchest-items'}).find_all(
                'div', {'class': 'col-xs-12 col-sm-6 col-md-4 col-lg-3 '
                                 'hero-feature no-padding'})

            for data_item in data:
                unique_name = data_item.find(
                    'div', {'class': 'block-item this-panel-imgs'}
                )['data-uniquename'][3:]
                if unique_name == '2H_ENIGMATICORB_MORGANA':
                    name = 'Malevolent Locus'
                else:
                    name = data_item.find(
                        'div', {'class': 'caption text-item'}
                    ).text.replace('\n', "").split()
                    name = ' '.join(name[1:])
                items_dict[unique_name] = name

    with open('extra_data.json') as f:
        extra_items = json.load(f)

    # capes_dict = {'CAPE': 'Regular Cape', 'CAPEITEM_FW_MARTLOCK': 'Martlock Cape', 'CAPEITEM_FW_FORTSTERLING': 'Fort Sterling Cape', 'CAPEITEM_FW_LYMHURST': 'Lymhurst Cape', 'CAPEITEM_FW_BRIDGEWATCH': 'Bridgewatch Cape', 'CAPEITEM_FW_THETFORD': 'Thetford Cape', 'CAPEITEM_DEMON': 'Demon Cape', 'CAPEITEM_MORGANA': 'Morgana Cape', 'CAPEITEM_KEEPER': 'Keeper Cape', 'CAPEITEM_UNDEAD': 'Undead Cape', 'CAPEITEM_HERETIC': 'Heretic Cape'}
    # harvester_dict = {"BACKPACK_GATHERER_FIBER": "Harvester Backpack", "HEAD_GATHERER_FIBER": "Harvester Cap", "ARMOR_GATHERER_FIBER": "Harvester Garb", "SHOES_GATHERER_FIBER": "Harvester Workboots"}
    # miner_dict = {"BACKPACK_GATHERER_ORE": "Miner Backpack", "HEAD_GATHERER_ORE": "Miner Cap", "ARMOR_GATHERER_ORE": "Miner Garb", "SHOES_GATHERER_ORE": "Miner Workboots"}
    # lumberjack_dict = {"BACKPACK_GATHERER_WOOD": "Lumberjack Backpack", "HEAD_GATHERER_WOOD": "Lumberjack Cap", "ARMOR_GATHERER_WOOD": "Lumberjack Garb", "SHOES_GATHERER_WOOD": "Lumberjack Workboots"}

    items_dict.update(extra_items)
    logger.debug('Updating items_dict with extra items')
    # items_dict.update(miner_dict)
    # logger.debug('Updating items_dict with miner_dict.')
    # items_dict.update(lumberjack_dict)
    # logger.debug('Updating items_dict with lumberjack_dict.')
    # items_dict.update(harvester_dict)
    # logger.debug('Updating items_dict with harvester_dict.')

    with open('items_dict.json', 'w') as file:
        json.dump(items_dict, file)


if __name__ == '__main__':
    generate_items_dict()

