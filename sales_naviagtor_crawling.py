import pickle
import random

import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
companies_list=[]
users_list = []

def load_cookie(driver,userr):
    with open(userr+'.pkl', 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)




def login(driver,userr,passs):
    driver.get("https://linkedin.com/login")
    # waiting for the page to load
    time.sleep(5)
    # #entering username
    username=driver.find_element(By.XPATH, '//input[@id="username"]')
    username.send_keys(userr)
    namee=userr.split('@')[0]
    # entering  password
    password = driver.find_element(By.XPATH, '//input[@id="password"]')
    password.send_keys(passs)
    time.sleep(4)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    time.sleep(6)
    path=namee+'.pkl'
    save_cookie(driver,path)


def get_user_link(driver,compannys):
    c_list=list(map(lambda x: x.lower(),compannys))
    for m in range(0,5):
        try:
            for i in range(0,5):
                alll_users = driver.find_elements(By.XPATH, '//div[@class="artdeco-entity-lockup__content ember-view"]')
                (alll_users[-1]).location_once_scrolled_into_view

                for a in alll_users:
                    full_user = []
                    try:
                        nn2 = a.find_element(By.XPATH, './/div[@class="artdeco-entity-lockup__subtitle ember-view t-14"]')
                        nn = a.find_element(By.XPATH, './/div[@class="artdeco-entity-lockup__title ember-view"]')
                        full_user.append(nn.find_element(By.TAG_NAME, 'a').get_attribute('href'))
                        full_user.append(nn2.find_element(By.XPATH, 'a').text)
                        full_user.append(nn2.find_element(By.XPATH, 'a').get_attribute('href'))
                        if full_user not in users_list:

                            users_list.append(full_user)
                    except:
                        pass
            try:
                driver.find_element(By.XPATH, '//button[@aria-label="Next"]').click()
            except:
                break
            time.sleep(10)
        except:
            pass

def add_google_sheet(header,records):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)
    # spreadsheet = client.create('mysheet2')
    # get the instance of the Spreadsheet
    sheet = client.open('mysheet1')
    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)
    # get the total number of columns
    sheet_instance.clear()
    sheet_instance.insert_row(header, 1)  # Write the header row
    sheet_instance.insert_rows(records, 2)



def main(search,username,password):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get('https://www.linkedin.com')
    time.sleep(5)
    # parameters
    try:
        user=username.split('@')[0]
        driver=load_cookie(driver,user)
    except:
        login(driver,username,password)
    time.sleep(random.randint(5,8))
    driver.get(search)
    time.sleep(10)

    time.sleep(1)
    get_user_link(driver,companies_list)
    time.sleep(1)

    time.sleep(7)

    dfff=pd.DataFrame(users_list)
    header =['Profile_url','Company_name','Company_url']
    records = dfff.values.tolist()
    add_google_sheet(header,records)


def getting_input_data(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    username=df.loc[df['keys'] == 'username', 'value'].iloc[0]
    password=df.loc[df['keys'] == 'password', 'value'].iloc[0]
    sales_urls=df.loc[df['keys'] == 'sales_navigator_url', 'value'].iloc[0]
    return username,password,sales_urls


if __name__ == "__main__":
    SHEET_ID = '1NvcHCO2laW69W_Eqb9bWcE5S7PkO0g5i3atsdCm1eDA'
    SHEET_NAME = 'sheet1'
    username,password,search_link=getting_input_data(SHEET_ID,SHEET_NAME)
    print(username,password,search_link)
    # search_link='https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A2163387729%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A102748797%2Ctext%3ATexas%252C%2520United%2520States%2CselectionType%3AINCLUDED)))%2C(type%3ATITLE%2Cvalues%3AList((id%3A8%2Ctext%3AChief%2520Executive%2520Officer%2CselectionType%3AINCLUDED))%2CselectedSubFilter%3ACURRENT)%2C(type%3AINDUSTRY%2Cvalues%3AList((id%3A4%2Ctext%3ASoftware%2520Development%2CselectionType%3AINCLUDED)%2C(id%3A96%2Ctext%3AIT%2520Services%2520and%2520IT%2520Consulting%2CselectionType%3AINCLUDED)))))&sessionId=xVW%2FE%2FYTSo%2BsEZ9VMHQwDg%3D%3D&viewAllFilters=true'
    # output='result.csv'
    main(search_link,username,password)