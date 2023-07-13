import pickle
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import random
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
users_list = []
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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
    time.sleep(random.randint(4,8))
    # entering username
    username=driver.find_element(By.XPATH, '//input[@id="username"]')
    username.send_keys(user_name)
    namee=user_name.split('@')[0]
    # entering  password
    password = driver.find_element(By.XPATH, '//input[@id="password"]')
    password.send_keys(pass_word)
    time.sleep(random.randint(4,8))
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(random.randint(4,8))
    #saving login cookies
    path=namee+'.pkl'
    save_cookie(driver,path)

def add_to_google_sheet(header,record,out,out_number):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)
    # spreadsheet = client.create('mysheet2')
    # get the instance of the Spreadsheet
    sheet = client.open(str(out))
    out_number=out_number.replace('sheet','')
    current_number=int(out_number)-1
    sheet_instance = sheet.get_worksheet(current_number)
    row = sheet_instance.row_values(1)
    if row==header:
        sheet_instance.insert_row(record, 2)
    elif row!=header:
        sheet_instance.insert_row(header,1)
        sheet_instance.insert_row(record,2)

def withdraw_request(driver,username,password):
    driver.get("https://linkedin.com")
    try:
        load_cookie(driver,username)
    except:
        login(driver,username,password)

    time.sleep(random.randint(4,8))
    driver.get('https://www.linkedin.com/mynetwork/invitation-manager/sent/')
    time.sleep(random.randint(4,8))
    data = driver.find_elements(By.XPATH, '//div[@class="invitation-card__details"]')
    withdraw_buttons = driver.find_elements(By.XPATH, '//button[@class="artdeco-button artdeco-button--muted artdeco-button--3 artdeco-button--tertiary ember-view invitation-card__action-btn"]')

    for full in data:
        full_text = full.text.split('\n')
        sent_time = full_text[4]
        weeks_splited=sent_time.split('week')
        if len(weeks_splited)>1:
            if int(weeks_splited[0])>=1:
                withdraw_buttons[data.index(full)].click()
                time.sleep(random.randint(4,8))
                actions = ActionChains(driver)
                actions.send_keys(Keys.TAB).perform()
                actions.send_keys(Keys.TAB).perform()
                actions.send_keys(Keys.TAB).perform()
                time.sleep(random.randint(10,20))
                actions.send_keys(Keys.ENTER).perform()
                time.sleep(random.randint(20,40))


def checking_connections(driver,links_list,names_list,username,password,result_sheet,result_sheet_number):

    driver.get("https://linkedin.com")
    try:
        load_cookie(driver,username)
    except:
        login(driver,username,password)
        print('Logged_in')
    time.sleep(random.randint(4,8))
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    time.sleep(random.randint(4,8))
    data = driver.find_elements(By.XPATH, '//div[@class="mn-connection-card__details"]')


    accepted_names=[]
    for full in data:
        full_text = full.text.split('\n')
        print(full_text)
        name = full_text[1]
        if name in names_list:
            accepted_names.append(name)

    for user_name in accepted_names:
        profile_link=links_list[names_list.index(user_name)]
        driver.get(profile_link)
        time.sleep(random.randint(10,15))

        contact=driver.find_element(By.XPATH,'//ul[@class="_contact-info-list_hqxetg"]')

        email=contact.find_elements(By.TAG_NAME,'a')
        target_email=''
        for e in email:
            email_search=e.get_attribute('href')
            if str(email_search)[0:4]=='mail':
                target_email=email_search[7:]
                # print(target_email,'gggggg')
        driver.find_element(By.XPATH,'//button[@class="ember-view _button_ps32ck _small_ps32ck _primary_ps32ck _emphasized_ps32ck _left_ps32ck _container_iq15dg _message-cta_1xow7n _cta_1xow7n _medium-cta_1xow7n"]').click()
        time.sleep(random.randint(4,8))

        time.sleep(random.randint(4,8))
        driver.find_element(By.XPATH, '//textarea[@placeholder="Type your message here…"]').send_keys('Hi How are you?')
        time.sleep(random.randint(4,8))
        # driver.find_element(By.XPATH, '//button[@aria-describedby="artdeco-hoverable-artdeco-gen-43"]').click()
        time.sleep(random.randint(10,15))
        record=[user_name,profile_link,target_email]
        header=['Name','Profile_link','Email']
        add_to_google_sheet(header,record,result_sheet,result_sheet_number)

def getting_input_data(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    username=df.loc[df['keys'] == 'username', 'value'].iloc[0]
    password=df.loc[df['keys'] == 'password', 'value'].iloc[0]
    sheetid = df.loc[df['keys'] == 'output_sheet_id', 'value'].iloc[0]
    # input_sheet = df.loc[df['keys'] == 'second_crawler_saving_sheet_name', 'value'].iloc[0]
    input_sheet_number = df.loc[df['keys'] == 'third_crawler_saving_sheet_number', 'value'].iloc[0]
    result_sheet = df.loc[df['keys'] == 'fourth_crawler_saving_sheet_name', 'value'].iloc[0]
    result_sheet_number = df.loc[df['keys'] == 'fourth_crawler_saving_sheet_number', 'value'].iloc[0]
    return username,password,sheetid,input_sheet_number,result_sheet,result_sheet_number

def getting_input_dataframe(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    return df



if __name__ == "__main__":
    # Google sheet id and name having username and password
    SHEET_ID = '1l1Q2t81LLk-GB-9qtQyqSDezOxdkKb2hzYXHkjxm59E'
    SHEET_NAME = 'sheet1'

    username,password,input_sheetid,input_sheet_number,result_sheet,result_sheet_number=getting_input_data(SHEET_ID,SHEET_NAME)
    df=getting_input_dataframe(input_sheetid,input_sheet_number)
    links_list = df['User_link'].values.tolist()
    name_list = df['Name'].values.tolist()
    withdraw_request(driver,username,password)
    checking_connections(driver,links_list,name_list,username,password,result_sheet,result_sheet_number)
