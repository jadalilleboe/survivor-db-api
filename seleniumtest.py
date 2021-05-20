from selenium import webdriver
import re

PATH = "C:\\Program Files (x86)\\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("https://survivor.fandom.com/wiki/Malolo?action=edit")
textarea = driver.find_element_by_tag_name('textarea').text

mem_index = textarea.find("==Members==")
hist_index = textarea.find("==Tribe History==")
members_text = textarea[mem_index:hist_index]
day = members_text.find('Day')

if day != -1:
    members_text = members_text[:day]

name_quotes = [a.start() for a in re.finditer("'''", members_text)]

tribe_names = []

for i in range(0, len(name_quotes), 2):
    tribe_name = members_text[(name_quotes[i] + 3):name_quotes[i+1]]
    tribe_names.append(tribe_name)
print(tribe_names)

driver.quit()