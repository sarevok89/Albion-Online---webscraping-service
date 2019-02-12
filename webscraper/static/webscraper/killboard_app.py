from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from pandas import ExcelWriter
import datetime
import json
import os
import re
from albion_compensations.settings import BASE_DIR, MEDIA_ROOT
import boto3


'''
Script fetching data from Albion Online killboard websites provided by user.
At the end it generates an Excel file with all the data.

def create_kill_id_list(text) - function which takes user's input and using regex searches
for Albion Online killboard link patterns. Even if user passess: "fsdhttps://albiononline.com/pl/killboard/kill/2490053454354",
it is still going to get this "https://albiononline.com/en/killboard/kill/24900534" link. It returns a list with all URLs.

def create_table(kill_id_list) - function that takes a list of all killboard URLs, returning a "dict_list" - dictionary containing all
the user friendly data.

def generate_dict(kill_id, dict_list) - function which taking a single url and using Selenium module with BeautifulSoup fetches
all the required data.

class ItemsUnique - All fetched data is being saved using this class. Nick, Guild, Item power and equipment.
This is all raw data i.e. weapon -  "T6_MAIN_CURSEDSTAFF.png?count=1&quality=2".

class Item - Another class, which takes ItemsUnique objects and using them creates more detailed and user friendly output.

def generate_excel(dict_list, fight_name) - function which uses dict_list to generate an Excel file from a Pandas DataFrame.

'''


def create_kill_id_list(text):
    base_url = 'https://albiononline.com/'
    killboard_url = '/killboard/kill/'
    url_list = re.findall(base_url + r'\w{2}' + killboard_url + r'\d{8}', text)
    kill_id_list = []
    for item in url_list:
        kill_id_list.append(item[-8:])
    kill_id_list = set(kill_id_list)
    return kill_id_list


def create_table(kill_id_list):

    dict_list = []

    def generate_dict(kill_id, dict_list):
        url = 'https://albiononline.com/en/killboard/kill/' + kill_id
        chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
        options = webdriver.ChromeOptions()
        options.binary_location = chrome_bin
        options.add_argument('headless')
        # browser = webdriver.Chrome(options=options, executable_path=os.path.join(BASE_DIR, r'webscraper\static\webscraper\chromedriver-windows.exe'))
        browser = webdriver.Chrome(options=options, executable_path="chromedriver")
        browser.get(url)
        element = WebDriverWait(browser, 10).until(lambda x: x.find_element_by_class_name('kill__body'))
        html = browser.page_source
        browser.quit()

        soup = BeautifulSoup(html, 'html5lib')

        class ItemsUnique:
            def __init__(self):
                self.nick = soup.find_all('div', {'class': 'mini-profile__value'})[3].text
                self.ip = soup.find_all('div', {'class': 'kill__gear-value-number'})[1].text
                try:
                    self.guild = soup.find_all('span', {'data-reactid': '.0.2.1.3.0.0.0.0.2.0.0.1.1.0.1.1'})[0].text
                except:
                    self.guild = None

                try:
                    self.helmet_unique = soup.find_all('div', {'class': 'item item--Head'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.helmet_unique = None

                try:
                    self.armor_unique = soup.find_all('div', {'class': 'item item--Armor'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.armor_unique = None

                try:
                    self.main_hand_unique = soup.find_all('div', {'class': 'item item--MainHand'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.main_hand_unique = None

                try:
                    self.off_hand_unique = soup.find_all('div', {'class': 'item item--OffHand'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.off_hand_unique = None

                try:
                    self.cape_unique = soup.find_all('div', {'class': 'item item--Cape'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.cape_unique = None

                try:
                    self.shoes_unique = soup.find_all('div', {'class': 'item item--Shoes'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.shoes_unique = None

                try:
                    self.mount_unique = soup.find_all('div', {'class': 'item item--Mount'})[1].img['src'].replace(
                        'https://gameinfo.albiononline.com/api/gameinfo/items/', "")
                except:
                    self.mount_unique = None

        with open(os.path.join(BASE_DIR, 'webscraper', 'static', 'webscraper', 'items_dict.json'), 'r') as json_file:
            items_dict = json.load(json_file)

        quality_dict = {'1': 'Normal', '2': 'Good', '3': 'Outstanding', '4': 'Excellent', '5': 'Masterpiece'}

        items = ItemsUnique()

        class Item:
            def __init__(self, item):
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

        d = {}

        d['Nick'] = items.nick
        d['Guild'] = items.guild
        d['Item Power'] = int(items.ip)

        helmet = Item(items.helmet_unique)
        d['Helmet'] = helmet.name
        d['Helmet Tier'] = helmet.tier
        d['Helmet Quality'] = helmet.quality

        armor = Item(items.armor_unique)
        d['Armor'] = armor.name
        d['Armor Tier'] = armor.tier
        d['Armor Quality'] = armor.quality

        shoes = Item(items.shoes_unique)
        d['Shoes'] = shoes.name
        d['Shoes Tier'] = shoes.tier
        d['Shoes Quality'] = shoes.quality

        main_hand = Item(items.main_hand_unique)
        d['Main Hand'] = main_hand.name
        d['Main Hand Tier'] = main_hand.tier
        d['Main Hand Quality'] = main_hand.quality

        off_hand = Item(items.off_hand_unique)
        d['Off Hand'] = off_hand.name
        d['Off Hand Tier'] = off_hand.tier
        d['Off Hand Quality'] = off_hand.quality

        cape = Item(items.cape_unique)
        d['Cape'] = cape.name
        d['Cape Tier'] = cape.tier
        d['Cape Quality'] = cape.quality

        dict_list.append(d)

    for item in kill_id_list:
        generate_dict(item, dict_list)

    return dict_list


def generate_excel(dict_list, fight_name):
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

    s3 = boto3.resource('s3', aws_access_key_id='AKIAJZ7G7LLNHVOEGTKA',
                        aws_secret_access_key='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')
    bucket = s3.Bucket('albion-compensations')
    objs = list(bucket.objects.filter(Prefix=file_name))

    if len(objs) == 0 or objs[0].key != file_name:
        writer = ExcelWriter(os.path.join('media', file_name))
    else:
        while True:
            if len(objs) > 0 and objs[0].key == file_name:
                num_of_files += 1
                file_name = current_date + fight_name + f'({num_of_files}).xlsx'
                continue
            else:
                writer = ExcelWriter(os.path.join('media', file_name))
                break

    df.to_excel(writer, 'Sheet 1', header=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet 1']

    new_format = workbook.add_format()
    new_format.set_align('center')

    worksheet.set_column('A:Z', 18, new_format)

    writer.save()
    return file_name
