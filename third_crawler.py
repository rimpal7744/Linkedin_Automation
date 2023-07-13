import pickle
import re
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless=new')

driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome(ChromeDriverManager().install())
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
    time.sleep(random.randint(5,12))
    #saving login cookies
    path=namee+'.pkl'
    save_cookie(driver,path)

def add_logs(out,number,text):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    print(out,number)
    # authorize the clientsheet
    client = gspread.authorize(creds)
    # spreadsheet = client.create('mysheet2')
    # get the instance of the Spreadsheet
    sheet = client.open(out)
    # get the first sheet of the Spreadsheet
    number = number.replace('sheet', '')
    current_sheet = int(number) - 1
    sheet_instance = sheet.get_worksheet(current_sheet)
    # get the total number of columns
    # sheet_instance.clear()
    date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    sheet_instance.insert_row([date_time+' = '+ text]) # Write the header row
    # sheet_instance.insert_rows(records, 2)


def getting_info(user_link):
    time.sleep(random.randint(5,8))
    namee=driver.find_element(By.XPATH, '//h1[@data-anonymize="person-name"]').text
    headline=driver.find_element(By.XPATH, '//span[@data-anonymize="headline"]').text
    place=driver.find_element(By.XPATH, '//div[@class="_lockup-caption_sqh8tm _bodyText_1e5nen _default_1i6ulk _sizeSmall_1e5nen _lowEmphasis_1i6ulk"]').text
    connections=driver.find_elements(By.XPATH, '//div[@class="_lockup-caption_sqh8tm _bodyText_1e5nen _default_1i6ulk _sizeSmall_1e5nen _lowEmphasis_1i6ulk"]')[1].text
    show_moree=driver.find_elements(By.XPATH, '//button[@class="_ellipsis-button_1d1vlq _unstyled-button_4edpgz"]')
    for s in show_moree:
        try:
            s.click()
            time.sleep(random.randint(5,8))
        except:
            pass

        about=driver.find_elements(By.XPATH, '//p[@data-anonymize="person-blurb"]')
        text=''
        for a in about:
            text+=a.text
            text+='\n'
            text+='------------------'

        text=text.replace('Show less','')
        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
        if len(emails)>1:
            emails=','.join(emails)
        if len(emails)==1:
            emails=emails[0]
        if len(emails)==0:
            emails=''
        period = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Profile_data_list=[user_link,namee,headline,place,connections,emails,period]
        time.sleep(random.randint(5,8))
        return Profile_data_list

def add_to_googlesheet(record,header,out,out_number):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    # authorize the clientsheet
    client = gspread.authorize(creds)
    # spreadsheet = client.create('mysheet2')
    # get the instance of the Spreadsheet
    sheet = client.open(str(out))
    # get the first sheet of the Spreadsheet
    out_number=out_number.replace('sheet','')
    current_sheet=int(out_number)-1
    sheet_instance = sheet.get_worksheet(current_sheet)
    # get the total number of columns
    if header == '':
        sheet_instance.insert_row(record, 2)  # Write the header row

    if header != '':
        sheet_instance.clear()
        sheet_instance.insert_row(header, 1)
        sheet_instance.insert_row(record, 2)

def sending_requests(driver,users_data,username,password,out_name,out_number,log_name,log_number):
    # print(users_data)
    driver.get("https://linkedin.com")
    try:
        load_cookie(driver,username)
    except:
        login(driver,username,password)
    print('logged_in')
    add_logs(log_name,log_number,'logged_in')
    time.sleep(4)
    # try:
    #     with open(r'requests_sending.txt', 'r') as f:
    #         start_number = f.read()
    # except:
    #     start_number=0
    start_number=0
    for user_link in users_data[int(start_number):]:
        user_number=users_data.index(user_link)
        # print('Sending_connection_rrequest_to_user_number: '+str(user_number))
        add_logs(log_name, log_number, 'Sending_connection_rrequest_to_user_number: '+str(user_number))
        # with open(r'requests_sending.txt', 'w') as f:
        #     f.write(str(user_number))
        try:
            driver.get(user_link)
            time.sleep(random.randint(6,10))
            target_df=getting_info(user_link)
            time.sleep(random.randint(5,8))
            driver.find_element(By.XPATH,'//button[@class="ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n"]').click()
            time.sleep(3)
            element=driver.find_element(By.XPATH,'//div[@class="_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9"]')
            # print(element.text,'ffffffff')
            if 'Connect — Pending' not in element.text.split('\n'):

                element.send_keys(Keys.TAB)
                time.sleep(random.randint(3,5))
                actions = ActionChains(driver)
                actions.send_keys(Keys.ENTER).perform()
                # element.send_keys(Keys.RETURN)
                time.sleep(random.randint(3,7))
                # driver.find_element(By.XPATH,'//textarea[@id="connect-cta-form__invitation"]').send_keys('hello hows you?')
                # driver.find_element(By.XPATH,'//button[@class="button-primary-medium connect-cta-form__send"]').click()
                if user_number==0:
                    # header=['User_link','Name','Headline','Location','Connections','Description','Email(if available)','Sent_time']
                    header=['User_link','Name','Headline','Location','Connections','Email(if available)','Sent_time']
                    add_to_googlesheet(target_df,header,out_name,out_number)
                else:
                    header=''
                    add_to_googlesheet(target_df,header,out_name,out_number)
                time.sleep(4)

        except:
            pass

    add_logs(log_name, log_number, 'Script_END')
def getting_input_data(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    username=df.loc[df['keys'] == 'username', 'value'].iloc[0]
    password=df.loc[df['keys'] == 'password', 'value'].iloc[0]
    sheetid = df.loc[df['keys'] == 'output_sheet_id', 'value'].iloc[0]
    # input_sheet = df.loc[df['keys'] == 'second_crawler_saving_sheet_name', 'value'].iloc[0]
    input_sheet_number = df.loc[df['keys'] == 'second_crawler_saving_sheet_number', 'value'].iloc[0]
    result_sheet = df.loc[df['keys'] == 'third_crawler_saving_sheet_name', 'value'].iloc[0]
    result_sheet_number = df.loc[df['keys'] == 'third_crawler_saving_sheet_number', 'value'].iloc[0]
    log_sheet_name = df.loc[df['keys'] == 'third_crawler_log_sheet_name', 'value'].iloc[0]
    log_sheet_number = df.loc[df['keys'] == 'third_crawler_log_sheet_number', 'value'].iloc[0]
    return username, password, sheetid, input_sheet_number, result_sheet, result_sheet_number,log_sheet_name,log_sheet_number
    # return username,password

def getting_input_dataframe(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    return df


if __name__ == "__main__":
    # Google sheet id and name having username and password
    SHEET_ID = '1l1Q2t81LLk-GB-9qtQyqSDezOxdkKb2hzYXHkjxm59E'
    SHEET_NAME = 'sheet1'
    # Google sheet id and name having extracted links
    # input_sheetid = '1i1XNuxrmtAxJo3fDli_ex3LRb_3rnFRcry3n6_LErig'
    # input_sheetid='1ZyRVdZkn7zXxmu79D9LOR31piijIp0MzPf7J4cMnOs8'
    # input_sheet_number = 'sheet2'
    username, password ,input_sheetid,input_sheet_number,result_sheet, result_sheet_number,log_name,log_number= getting_input_data(SHEET_ID, SHEET_NAME)
    input_data = getting_input_dataframe(input_sheetid, input_sheet_number)
    data_list=input_data['Ceo_url'].values.tolist()
    sending_requests(driver,data_list,username,password,result_sheet,result_sheet_number,log_name,log_number)
