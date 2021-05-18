from selenium import webdriver
from selenium.webdrive.common.keys import Keys

PATH = "C:\\Program Files (x86)\\chromedriver.exe"
driver = webdriver.Chrome(PATH)

driver.get("https://survivor.fandom.com/wiki/List_of_Survivor_contestants#Overall")

search = driver.find_element_by_class_name("mw-collapsible-text")
