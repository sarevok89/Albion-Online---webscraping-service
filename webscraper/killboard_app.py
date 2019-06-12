import datetime
import json
import logging
import os
import re

import boto3
import pandas as pd

from bs4 import BeautifulSoup
from pandas import ExcelWriter
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from albion_compensations.settings import BASE_DIR, MEDIA_ROOT


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


"""
Script fetching data from Albion Online killboard websites provided by user and 
generating an output Excel file containing all the fetched data in a nice, 
user friendly manner.

"""


class ItemsUnique:

    """
    class ItemsUnique - All fetched data is being saved using this class. Nick,
    Guild, Item power and equipment.This is all raw data
    e.g. main hand - "T6_MAIN_CURSEDSTAFF.png?count=1&quality=2".
    """

    def __init__(self, soup):
        self.nick = soup.find_all(
            'div', {'class': 'mini-profile__value'})[3].text
        self.ip = soup.find_all(
            'div', {'class': 'kill__gear-value-number'})[1].text
        try:
            self.guild = soup.find_all(
                'span', {'data-reactid': '.0.2.1.3.0.0.0.0.2.0.0.1.1.0.1.1'}
            )[0].text
        except IndexError:
            self.guild = None
        except Exception as e:
            logger.exception(e)
            self.guild = None

        try:
            self.helmet_unique = soup.find_all(
                'div', {'class': 'item item--Head'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.helmet_unique = None
        except Exception as e:
            logger.exception(e)
            self.helmet_unique = None

        try:
            self.armor_unique = soup.find_all(
                'div', {'class': 'item item--Armor'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.armor_unique = None
        except Exception as e:
            logger.exception(e)
            self.armor_unique = None

        try:
            self.main_hand_unique = soup.find_all(
                'div', {'class': 'item item--MainHand'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.main_hand_unique = None
        except Exception as e:
            logger.exception(e)
            self.main_hand_unique = None

        try:
            self.off_hand_unique = soup.find_all(
                'div', {'class': 'item item--OffHand'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.off_hand_unique = None
        except Exception as e:
            logger.exception(e)
            self.off_hand_unique = None

        try:
            self.cape_unique = soup.find_all(
                'div', {'class': 'item item--Cape'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.cape_unique = None
        except Exception as e:
            logger.exception(e)
            self.cape_unique = None

        try:
            self.shoes_unique = soup.find_all(
                'div', {'class': 'item item--Shoes'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.shoes_unique = None
        except Exception as e:
            logger.exception(e)
            self.shoes_unique = None

        try:
            self.mount_unique = soup.find_all(
                'div', {'class': 'item item--Mount'})[1].img['src'].replace(
                'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
        except IndexError:
            self.mount_unique = None
        except Exception as e:
            logger.exception(e)
            self.mount_unique = None


class Item:

    """
    Class, which takes a single ItemsUnique attribute, quality_dict and
    items_dict, to create detailed and user friendly output.

    Example input:
    items.main_hand = "T6_MAIN_CURSEDSTAFF.png?count=1&quality=2"

    Example output:
    main_hand.name = 'Cursed Staff'
    main_hand.tier = '6'
    main_hand.quality = 'Good'

    In case there wasn't such item in our items_dict it
    sets it's name to 'Unknown'.

    """

    def __init__(self, item, quality_dict, items_dict):
        if item is not None:
            enchanted = item.find('@')
            if enchanted != -1:
                self.enchancement = item[item.find('@') + 1]
            else:
                self.enchancement = None

            if enchanted != -1:
                self.tier = item[item.find('_') - 1] + '.' + self.enchancement
            else:
                self.tier = item[item.find('_') - 1] + '.' + '0'

            self.quality = quality_dict[item[item.find('quality=') + 8]]

            name = []
            name_start = item.index('_') + 1
            if enchanted != -1:
                name_end = item.index('@')
            else:
                name_end = item.index('.png')

            for i, letter in enumerate(item):
                if i in range(name_start, name_end):
                    name.append(letter)

            name = ''.join(name)
            try:
                self.name = items_dict[name]
            except KeyError:
                self.name = 'Unknown item'

        else:
            self.enchancement = None
            self.tier = None
            self.name = None
            self.quality = None


def create_kill_id_list(text):

    """
    Function which takes user's input and using Regex module searches for
    Albion Online killboard link patterns. Even if user passess:
    `fsdhttps://albiononline.com/pl/killboard/kill/2490053454354`,
    it is still going to get this url:
    `https://albiononline.com/en/killboard/kill/24900534`
    At the end it returns a list with all URLs.

    :param text: Bunch of Albion Online killboard URLs (as mentioned above,
    they can be passed with some noise, e.g.:


    `shilliash 06.02.2019
    https://albiononline.com/en/killboard/kill/25493461asd
    https://albiononline.com/pl/killboard/kill/25497574tr456
    534https://albiononline.com/ru/killboard/kill/25607853....!
    The Fantasy Sandbox MMORPG | Albion Online`


    :return: A list of killboard IDs. From above example it
    would return a list like:

    `['25493461', '25497574', '25607853']`

    """

    base_url = 'https://albiononline.com/'
    killboard_url = '/killboard/kill/'
    url_list = re.findall(base_url + r'\w{2}' + killboard_url + r'\d{8}', text)
    kill_id_list = []
    for item in url_list:
        kill_id_list.append(item[-8:])
    kill_id_list = set(kill_id_list)
    return kill_id_list


def create_table(kill_id_list):

    """
    Function that takes a list of all killboard URLs, returning a "dict_list"
    - list of dictionaries, containing all the user friendly data.

    :param kill_id_list: List returned by 'create_killboard_id_list' function.
    :return: A list of dictionaries. Each dictionary contains all fetched data
    from one URL, where keys are:

    Nick, Guild, Item Power,
    Helmet, Helmet Tier, Helmet Quality,
    Armor, Armor Tier, Armor Quality,
    Shoes, Shoes Tier, Shoes Quality,
    Main Hand, Main Hand Tier, Main Hand Quality,
    Off Hand, Off Hand Tier, Off Hand Quality,
    Cape, Cape Tier, Cape Quality,

    """

    dict_list = []

    def generate_dict(kill_id):

        """
        Function using BeautifulSoup, Selenium and Selenium Webdriver to
        fetch all the data from each killboard URL. It joins each `kill_id`
        with `base_url` to ensure that each url is formatted the same way and
        even if a user passes links from e.g. russian version of
        Albion Online page it is still going to work properly.

        'chrome_bin' is a variable provided by Heroku. To use Chromedriver with
        Heroku it's required to use their `heroku-buildpack-google-chrome` and
        `heroku-buildpack-chromedriver`.

        Beside installing required webdriver and Chrome browser they also
        create environmental variables, which we later use in our script.

        :param kill_id: A single element from kill_id_list.
        :return: Single dictionary 'd' containing data fetched from one of
        `kill_id_list` IDs.
        """

        base_url = 'https://albiononline.com/en/killboard/kill/'
        url = base_url + kill_id
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')

        # Commented out variables are being used for testing script locally.
        browser = webdriver.Chrome('chrome/chromedriver-76/chromedriver',
            options=options)
        # browser = webdriver.Chrome(
        #     options=options, executable_path="chromedriver")
        browser.get(url)

        # Below line was added to wait every time for all required page
        # elements to load.
        WebDriverWait(browser, 20).until(
            lambda x: x.find_element_by_class_name('kill__body'))

        html = browser.page_source
        browser.quit()

        soup = BeautifulSoup(html, 'html5lib')

        """
        We're opening a json file containing all Albion Online items we need. 
        It contains computer friendly names with their user fiendly 
        translations, e.g. `"T6_2H_DUALCROSSBOW_HELL": "Boltcasters"`.
        
        """

        with open(
                os.path.join(BASE_DIR, 'webscraper', 'static', 'webscraper',
                             'items_dict.json'), 'r') as json_file:
            items_dict = json.load(json_file)

        """
        A simple dictionary used for translating items quality, 
        e.g. in `T6_2H_DUALAXE_KEEPER@3.png?count=1&quality=3`
        `quality=3` gets translated to `Outstanding`.
        
        """

        quality_dict = {'1': 'Normal',
                        '2': 'Good',
                        '3': 'Outstanding',
                        '4': 'Excellent',
                        '5': 'Masterpiece'}

        items = ItemsUnique(soup)

        d = dict()

        d['Nick'] = items.nick
        d['Guild'] = items.guild
        d['Item Power'] = int(items.ip)

        helmet = Item(items.helmet_unique, quality_dict, items_dict)
        d['Helmet'] = helmet.name
        d['Helmet Tier'] = helmet.tier
        d['Helmet Quality'] = helmet.quality

        armor = Item(items.armor_unique, quality_dict, items_dict)
        d['Armor'] = armor.name
        d['Armor Tier'] = armor.tier
        d['Armor Quality'] = armor.quality

        shoes = Item(items.shoes_unique, quality_dict, items_dict)
        d['Shoes'] = shoes.name
        d['Shoes Tier'] = shoes.tier
        d['Shoes Quality'] = shoes.quality

        main_hand = Item(items.main_hand_unique, quality_dict, items_dict)
        d['Main Hand'] = main_hand.name
        d['Main Hand Tier'] = main_hand.tier
        d['Main Hand Quality'] = main_hand.quality

        off_hand = Item(items.off_hand_unique, quality_dict, items_dict)
        d['Off Hand'] = off_hand.name
        d['Off Hand Tier'] = off_hand.tier
        d['Off Hand Quality'] = off_hand.quality

        cape = Item(items.cape_unique, quality_dict, items_dict)
        d['Cape'] = cape.name
        d['Cape Tier'] = cape.tier
        d['Cape Quality'] = cape.quality

        return d

    """
    We're looping through each element in 'kill_id_list' and applying our 
    `generate_dict` function. Then we append all the outcome to our `dict_list`.
    
    """

    for item in kill_id_list:
        dict_list.append(generate_dict(item))

    return dict_list


def generate_excel(dict_list, fight_name):
    """
    Function using dict_list to generate an Excel file from a Pandas DataFrame.
    It creates `df` - Pandas DataFrame with specific, given column names and
    data from 'dict_list'. Each file name consists of:
    `day-month-year - fight_name.xlsx`

    :param dict_list: A list of dictionaries where each dictionary contains
    all fetched data from one URL.
    :param fight_name: Name of a fight received from user in our
    `WebscraperForm`. It's being used in creating special name for each
    generated excel file.
    :return: Returns name of a file created by our script.
    """

    df = pd.DataFrame(dict_list, columns=['Guild', 'Nick', 'Item Power',
                                          'Main Hand', 'Main Hand Tier',
                                          'Off Hand', 'Off Hand Tier',
                                          'Helmet', 'Helmet Tier',
                                          'Armor', 'Armor Tier',
                                          'Shoes', 'Shoes Tier',
                                          'Cape', 'Cape Tier', ])

    today = datetime.datetime.today()
    df = df.T
    num_of_files = 0
    current_date = f"{today.day}-{today.month}-{today.year} - "
    file_name = current_date + fight_name + '.xlsx'

    """
    Since Heroku deletes all user upload files every time it restarts we need 
    to store our files on an outside server, which in this case is Amazon S3.
    
    ExcelWriter doesn't allow us to directly create files on S3, so we 
    temporarily create them on Heroku and upload to S3 right after that.
    
    We don't want our files to get overwritten in case user provided the same 
    names for all the files generated on the same day, so each time we check, 
    if a file with a name we want to provide already exists on S3 server. 
    We consecutively add a number to a file's name and check again. 
    We keep checking until we find a name that doesn't yet exist, 
    e.g.: `13-2-2019 - onix vs squad(3).xlsx`.
    
    """

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('albion-compensations')

    objs = list(
        bucket.objects.filter(Prefix='media/compensations/' + file_name))

    if len(objs) == 0:
        writer = ExcelWriter(
            os.path.join(MEDIA_ROOT, 'compensations', file_name))
    else:
        while True:
            objs = list(
                bucket.objects.filter(
                    Prefix='media/compensations/' + file_name))
            if len(objs) > 0:
                num_of_files += 1
                file_name = current_date + fight_name + f'({num_of_files}).xlsx'
                continue
            else:
                break
        writer = ExcelWriter(
            os.path.join(MEDIA_ROOT, 'compensations', file_name))

    """
    We adjust an Excel table to our needs. We remove header, make sure each 
    cell has proper width and the text inside is centered.
    
    """

    df.to_excel(writer, 'Sheet 1', header=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet 1']

    new_format = workbook.add_format()
    new_format.set_align('center')

    worksheet.set_column('A:Z', 18, new_format)

    """
    Then we create a file with this name locally and return it's name,
    so another function can find it on Heroku server and upload it to S3.
    """

    writer.save()
    return file_name
