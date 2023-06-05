import pickle
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import parameters
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
users_list = []

def load_cookie(driver,username):
    # loading cookies with username
    path = username+'.pkl'
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver

def save_cookie(driver, path):
    # Saving cookies for login
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def login(driver,user_name,pass_word):
    driver.get("://linkedin.com/login")
    # waiting for the page to load
    time.sleep(5)
    # entering username
    username=driver.find_element(By.XPATH, '//input[@id="username"]')
    username.send_keys(user_name)
    namee=user_name.split('@')[0]
    # entering  password
    password = driver.find_element(By.XPATH, '//input[@id="password"]')
    password.send_keys(pass_word)
    time.sleep(4)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(6)
    #saving login cookies
    path=namee+'.pkl'
    save_cookie(driver,path)


def withdraw_request(driver,username,password):
    driver.get("https://linkedin.com")
    try:
        load_cookie(driver,username)
    except:
        login(driver,username,password)

    time.sleep(4)
    driver.get('https://www.linkedin.com/mynetwork/invitation-manager/sent/')
    time.sleep(6)
    data = driver.find_elements(By.XPATH, '//div[@class="invitation-card__details"]')
    withdraw_buttons = driver.find_elements(By.XPATH, '//button[@class="artdeco-button artdeco-button--muted artdeco-button--3 artdeco-button--tertiary ember-view invitation-card__action-btn"]')

    for full in data:
        full_text = full.text.split('\n')
        sent_time = full_text[4]
        weeks_splited=sent_time.split('week')
        if len(weeks_splited)>1:
            if int(weeks_splited[0])>=1:
                withdraw_buttons[data.index(full)].click()
                time.sleep(5)
                actions = ActionChains(driver)
                actions.send_keys(Keys.TAB).perform()
                actions.send_keys(Keys.TAB).perform()
                actions.send_keys(Keys.TAB).perform()
                time.sleep(10)
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(10)


if __name__ == "__main__":
    username=parameters.username
    password=parameters.password
    withdraw_request(driver,username,password)
