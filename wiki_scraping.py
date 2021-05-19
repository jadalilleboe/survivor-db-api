from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from server import *

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
    driver.get("https://survivor.fandom.com/wiki/Category:Seasons")
    first_ten_seasons = driver.find_element_by_xpath('//*[@id="mw-content-text"]/div[3]/div[1]/ul')
    list_items = first_ten_seasons.find_elements_by_tag_name('li')

    for item in list_items:
        link = item.find_element_by_tag_name('a')
        driver.execute_script("arguments[0].click();", link)
        driver.back()

get_seasons()