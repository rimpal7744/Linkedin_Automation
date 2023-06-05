import pickle
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import parameters
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

def checking_connections(driver,links_list,names_list,username,password):
    driver.get("https://linkedin.com")
    try:
        load_cookie(driver,username)
    except:
        login(driver,username,password)
    time.sleep(4)
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(6)
    data = driver.find_elements(By.XPATH, '//div[@class="mn-connection-card__details"]')


    accepted_names=[]
    for full in data:
        full_text = full.text.split('\n')
        print(full_text)
        name = full_text[1]
        if name in names_list:
            accepted_names.append(name)

    for accept in accepted_names[4:]:
        users_data = []
        profile_link=links_list[names_list.index(accept)]
        driver.get(profile_link)
        time.sleep(10)

        contact=driver.find_element(By.XPATH,'//ul[@class="_contact-info-list_hqxetg"]')

        email=contact.find_elements(By.TAG_NAME,'a')
        target_email=''
        for e in email:
            email_search=e.get_attribute('href')
            if str(email_search)[0:4]=='mail':
                target_email=email_search
        driver.find_element(By.XPATH,'//button[@class="ember-view _button_ps32ck _small_ps32ck _primary_ps32ck _emphasized_ps32ck _left_ps32ck _container_iq15dg _message-cta_1xow7n _cta_1xow7n _medium-cta_1xow7n"]').click()
        time.sleep(3)

        time.sleep(5)
        driver.find_element(By.XPATH, '//textarea[@placeholder="Type your message here…"]').send_keys('Hi How are you?')
        time.sleep(5)
        driver.find_element(By.XPATH, '//button[@aria-describedby="artdeco-hoverable-artdeco-gen-43"]').click()
        time.sleep(10)
        users_data.append([accept, profile_link,target_email])
        dff = pd.DataFrame(users_data)
        dff.to_csv(r'data_files\message_sent\sent.csv', mode='a', index=False,
                   header=False)


if __name__ == "__main__":
    username=parameters.username
    password=parameters.password
    df = pd.read_csv(r'data_files\profiles_data\profiles1.csv')
    # print(df.columns)
    links_list = df['links'].values.tolist()
    name_list = df['Name'].values.tolist()
    checking_connections(driver,links_list,name_list,username,password)
