import pickle
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import parameters
import random
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
users_list = []

def load_cookie(driver,username):
    # loading cookies with username
    path = username.split('@')[0]+'.pkl'
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


def sending_requests(driver,users_data,username,password):
    driver.get("https://linkedin.com")
    try:
        load_cookie(driver,username)
    except:
        login(driver,username,password)
    time.sleep(4)
    try:
        with open(r'logs\requests_sending.txt', 'r') as f:
            start_number = f.read()
    except:
        start_number=17
    print(start_number)
    for user in users_data[int(start_number):]:
        user_number=users_data.index(user)
        with open(r'logs\requests_sending.txt', 'w') as f:
            f.write(str(user_number))
        try:
            users_data_list=[]
            user_link=user[0]
            user_name=user[1]

            driver.get(user_link)
            time.sleep(random.randint(6,10))
            driver.find_element(By.XPATH,'//button[@class="ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n"]').click()
            time.sleep(3)
            # element=driver.find_element(By.XPATH,'//button[@class="ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n"]')
            element=driver.find_element(By.XPATH,'//div[@class="_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9"]')
            element.send_keys(Keys.TAB)
            time.sleep(3)
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER).perform()
            # element.send_keys(Keys.RETURN)
            time.sleep(4)
            # driver.find_element(By.XPATH,'//textarea[@id="connect-cta-form__invitation"]').send_keys('hello hows you?')
            time.sleep(3)
            driver.find_element(By.XPATH,'//button[@class="button-primary-medium connect-cta-form__send"]').click()

            period=datetime.now()
            users_data_list.append([user_link, user_name,period])
            dff = pd.DataFrame(users_data_list)
            dff.to_csv(r'data_files\connection_sent\data1.csv', mode='a', index=False,
                       header=False)
            time.sleep(4)
        except:
            pass

if __name__ == "__main__":
    username=parameters.username
    password=parameters.password
    df = pd.read_csv(r'data_files\profiles_data\profiles1.csv')
    # print(df.columns)
    data_list = df[['links', 'Name']].values.tolist()
    sending_requests(driver,data_list,username,password)
