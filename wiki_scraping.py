from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date, datetime
from server import *

# db.create_all()

PATH = "C:\\Program Files (x86)\\chromedriver.exe"
driver = webdriver.Chrome(PATH)

def get_survivors():
    driver.get("https://survivor.fandom.com/wiki/List_of_Survivor_contestants#Overall")
    link = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[2]/caption/span')
    driver.execute_script("arguments[0].click();", link)

    table = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[2]')
    body = table.find_element_by_tag_name('tbody')
    rows = body.find_elements_by_tag_name('tr')
    row1 = rows[0]
    td = row1.find_elements_by_tag_name('td')

    names = []

    for row in rows:
        th = row.find_element_by_tag_name('th')
        name = th.text
        td = row.find_elements_by_tag_name('td')
        
        hometown = td[3].text
        placement = td[5].text
        days_lasted = int(td[6].text)
        
        challenge_wins = td[9].text
        if challenge_wins == 'N/A':
            challenge_wins = 0
        else:
            challenge_wins = int(challenge_wins)
        
        if name in names:
            castaway = Castaways.query.filter_by(name=name).first()
            castaway.days_lasted += days_lasted
            castaway.challenge_wins += challenge_wins
        else:
            names.append(name)
            survivor = Castaways(name=name, hometown=hometown, days_lasted=days_lasted, challenge_wins=challenge_wins)
            db.session.add(survivor)
            db.session.commit()

def get_seasons():
    driver.get("https://survivor.fandom.com/wiki/Survivor:_Borneo")

    for i in range(40):
        if i == 0:
            pass
        else:
            if i == 1:
                next = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[4]/div/div/i/a')
            elif i == 23 or i == 39:
                next = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[3]/div[2]/div/i/a')
            else:
                next = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[4]/div[2]/div/i/a')
            driver.execute_script("arguments[0].click();", next)
            driver.implicitly_wait(5)
        
        aside = driver.find_element_by_tag_name('aside')
        header = aside.find_element_by_tag_name('h2')
        name = header.text[10:]
        section = aside.find_element_by_tag_name('section')
        values = section.find_elements_by_class_name('pi-data-value')

        location = values[2].text

        start_date_values = values[4].text.split(' - ')[0]
        if '[' in start_date_values:
            bad_text = start_date_values.find('[')
            start_date_values = start_date_values[:bad_text]
        d = datetime.strptime(start_date_values, '%B %d, %Y')
        start_date = date(int(d.strftime('%Y')), int(d.strftime('%m')), int(d.strftime('%d')))

        end_date_values = values[4].text.split(' - ')[1]
        if '[' in end_date_values:
            bad_text = end_date_values.find('[')
            end_date_values = end_date_values[:bad_text]
        d = datetime.strptime(end_date_values, '%B %d, %Y')
        end_date = date(int(d.strftime('%Y')), int(d.strftime('%m')), int(d.strftime('%d')))

        num_episodes = int(values[5].text)
        num_castaways = int(values[7].text[:2])

        # //*[@id="mw-content-text"]/div/aside/section[1]/div[11]/div

        season = Seasons(name=name, location=location, start_date=start_date, end_date=end_date, num_episodes=num_episodes, num_castaways=num_castaways)
        db.session.add(season)
        db.session.commit()
        
        driver.implicitly_wait(5)

def get_tribes():
    driver.get("https://survivor.fandom.com/wiki/Survivor:_Borneo")
    tribe_dict = {}

    for i in range(40):
        if i == 0:
            pass
        else:
            if i == 1:
                next = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[4]/div/div/i/a')
            elif i == 23 or i == 39:
                next = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[3]/div[2]/div/i/a')
            else:
                next = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[4]/div[2]/div/i/a')
            driver.execute_script("arguments[0].click();", next)
            driver.implicitly_wait(5)
        tribes_container = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[1]/div[11]/div')
        tribes = tribes_container.find_elements_by_tag_name('a')
        tribe_list = [tribe.text for tribe in tribes]
        tribe_dict[i+1] = tribe_list

    return tribe_dict

def get_tribe_info():
    # tribes = get_tribes()
    tribes = {1: ['Pagong', 'Tagi', 'Rattana'], 2: ['Kucha', 'Ogakor', 'Barramundi'], 3: ['Boran', 'Samburu', 'Moto Maji'], 4: ['Maraamu', 'Rotu', 'Soliantu'], 5: ['Chuay Gahn', 'Sook Jai', 'Chuay Jai'], 6: ['Jaburu', 'Tambaqui', 'Jacaré'], 7: ['Drake', 'Morgan', 'The Outcasts', 'Balboa'], 8: ['Chapera', 'Mogo Mogo', 'Saboga', 
    'Chaboga Mogo'], 9: ['Lopevi', 'Yasur', 'Alinta'], 10: ['Koror', 'Ulong'], 11: ['Nakúm', 'Yaxhá', 'Xhakúm'], 12: ['Bayoneta', 'Casaya', 'La Mina', 'Viveros', 
    'Gitanos'], 13: ['Aitutaki', 'Manihiki', 'Puka Puka', 'Rarotonga', 'Aitutonga'], 14: ['Moto', 'Ravu', 'Bula Bula'], 15: ['Fei Long', 'Zhan Hu', 'Hae Da Fung'], 16: ['Airai', 'Malakal', 'Dabu'], 17: ['Fang', 'Kota', 'Nobag'], 18: ['Jalapao', 'Timbira', 'Forza'], 19: ['Foa Foa', 'Galu', 'Aiga'], 20: ['Heroes', 'Villains', 'Yin Yang'], 21: ['Espada', 'La Flor', 'Libertad'], 22: ['Ometepe', 'Zapatera', 'Murlonio'], 23: ['Savaii', 'Upolu', 'Te Tuna'], 24: ['Manono', 'Salani', 'Tikiano'], 25: ['Kalabaw', 'Matsing', 'Tandang', 'Dangrayne'], 26: ['Bikal', 'Gota', 'Enil Edam'], 27: ['Galang', 'Tadhana', 'Kasama'], 28: ['Aparri', 'Luzon', 'Solana', 'Solarrion'], 29: ['Coyopa', 'Hunahpu', 'Huyopa'], 30: ['Escameca', 'Masaya', 'Nagarote', 'Merica'], 31: ['Bayon', 'Ta Keo', 'Angkor', 'Orkun'], 32: ['Chan Loh', 'Gondol', 'To Tang', 'Dara'], 33: ['Takali', 'Vanua', 'Ikabula', 'Vinaka'], 34: ['Mana', 'Nuku', 'Tavua', 'Maku Maku'], 35: ['Levu', 'Soko', 'Yawa', 'Solewa'], 36: ['Malolo', 'Naviti', 'Yanuya', 'Lavita'], 37: ['David/Vuku', 'Goliath/Jabeni', 'Tiva', 'Kalokalo'], 38: ['Kama', 'Manu', 'Lesu', 'Vata'], 39: ['Lairo', 'Vokai', 'Lumuwaku'], 40: ['Dakal', 'Sele', 'Yara', 'Koru']}
    
    for i in range(1, 41):
        season_tribes = tribes[i]
        if i == 37:
            season_tribes[0] = 'Vuku'
            season_tribes[1] = 'Jabeni'
        for tribe in season_tribes:
            if ' ' in tribe:
                tribe_url = ''
                for char in tribe:
                    if char == ' ':
                        tribe_url += '_'
                    else:
                        tribe_url += char
            else:
                tribe_url = tribe
            driver.get('https://survivor.fandom.com/wiki/{}'.format(tribe_url))
            tribe_type = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[1]/div[4]/div').text.lower()
            if tribe_type == 'merged tribe':
                challenge_wins = 'N/A'
            else:
                challenge_wins = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/aside/section[1]/div[8]/div').text
            
            survivor_tribe = Tribes(tribe_name=tribe, tribe_type=tribe_type, season=i, challenge_wins=challenge_wins)
            db.session.add(survivor_tribe)
            db.session.commit()

            tribe_members_table = driver.find_element_by_tag_name('table')
            table_rows = []
            for l in range(1, 5):
                try:
                    row = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[{}]'.format(l))
                    table_rows.append(row)
                except:
                    break

            for j in range(1, (len(table_rows) + 1)):
                data_cells = []
                for k in range(1, 6):
                    try:
                        cell = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[{}]/td[{}]'.format(j, k))
                        data_cells.append(cell)
                    except:
                        break
                for m in range(1, (len(data_cells) + 1)):
                    name = data_cells[(m - 1)].find_element_by_xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr[{}]/td[{}]/table/tbody/tr/td/div/div[1]/table/tbody/tr[1]/td/a/font/b'.format(j, m)).text
                    member = Castaways.query.filter_by(name=name).first()
                    survivor_tribe.castaways_in_tribe.append(member)
                    db.session.commit()

get_tribe_info()
    


driver.quit()