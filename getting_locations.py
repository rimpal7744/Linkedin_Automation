import json
import pickle
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
users_list = []


def load_cookie(driver,user):
    with open(user+'.pkl', 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def login(driver,userr,passw):
    driver.get("https://linkedin.com/login")
    # waiting for the page to load
    time.sleep(5)
    # #entering username
    username=driver.find_element(By.XPATH, '//input[@id="username"]')
    username.send_keys(userr)
    namee=userr.split('@')[0]
    # entering  password
    password = driver.find_element(By.XPATH, '//input[@id="password"]')
    password.send_keys(passw)
    time.sleep(4)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    time.sleep(6)
    path=namee+'.pkl'
    save_cookie(driver,path)

def us_locationn():
    us_df = pd.read_csv('US_locations.csv')
    us_list = us_df['locations'].tolist()

    all = []
    for i in us_list:
        splited = i.split(',')
        for s in splited:
            all.append(s)

    dd = list(set(all))
    us_locations = [x.lower() for x in dd]
    return us_locations

def get_companies_info(driver):
    all_data=driver.find_element(By.XPATH,'//dl[@class="overflow-hidden"]').text
    all_data=all_data.split('\n')
    website=''
    Phone=''
    founded=''
    Size=''
    headq=''
    Industry=''
    for aa in all_data:
        if aa=='Website':
            website=all_data[all_data.index(aa)+1]
        if aa=='Phone':
            try:
                Phone=all_data[all_data.index(aa)+1]
            except:
                Phone=''
        if aa=='Company size':
            try:
                Size=all_data[all_data.index(aa)+1]
            except:
                Size=''
        if aa=='Founded':
            try:
                founded=all_data[all_data.index(aa)+1]
            except:
                founded=''
        if aa=='Headquarters':
            try:
                headq=all_data[all_data.index(aa)+1]
            except:
                headq=''
        if aa=='Industry':
            try:
                Industry=all_data[all_data.index(aa)+1]
            except:
                Industry=''
    return website,Phone,Size,founded,headq,Industry

def getting_links(df):
    companies_list=df.Company_url.tolist()
    updated=[]
    for c in companies_list:
        c=c.replace('/sales','')
        c=c.split('?')[0]
        updated.append(c)
    return updated


def add_to_googlesheet(header,record):
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
    sheet_instance = sheet.get_worksheet(1)
    # get the total number of columns

    if header=='':
        sheet_instance.insert_row(record, 2)  # Write the header row

    if header !='':
        # print(record)
        sheet_instance.clear()
        sheet_instance.insert_row(header,1)
        sheet_instance.insert_row(record, 2)



def main(df,username,password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    updated=getting_links(df)
    df['Company_url']=updated
    driver.get('https://www.linkedin.com')
    time.sleep(5)
    try:
        user=username.split('@')[0]
        driver=load_cookie(driver,user)
    except:
        login(driver,username,password)
    time.sleep(3)

    time.sleep(3)
    count=1
    for i in updated:
        try:
            employess = []
            driver.get(i+'/about')
            time.sleep(random.randint(4,7))
            website,Phone,Size,founded,headq,industry=get_companies_info(driver)
            alltabs=driver.find_elements(By.XPATH,'//a[@class="ember-view pv3 ph4 t-16 t-bold t-black--light org-page-navigation__item-anchor "]')
            for aaaa in alltabs:
                if aaaa.text=='People':
                    aaaa.click()
            time.sleep(random.randint(4, 7))
            geography=driver.find_element(By.XPATH,'//button[@aria-label="Show more people filters"]')
            geography.click()
            time.sleep(random.randint(4,6))
            people=driver.find_element(By.XPATH,'//div[@class="insight-container"]')
            people_list = (people.text).split('\n')
            ceo=df.loc[df['Company_url']==str(i),'Profile_url'].iloc[0]
            company=df.loc[df['Company_url']==str(i),'Company_name'].iloc[0]
            overseas = []
            if len(people_list)>1:
                people_list=people_list[2:]
                people_list = [x.lower() for x in people_list]
                us_loc=us_locationn()

                for p in people_list:
                    for m in us_loc:
                        if m in p:
                            overseas.append(p)
                            break
            final = list(set(people_list) - set(overseas))
            if 'toggle off' in final:
                final.remove('toggle off')

            if len(final)>=1:
                final=json.dumps(final)
                employess.append([company,i,industry,headq,Size,founded,Phone,website,ceo,final,''])
            time.sleep(random.randint(4,8))
            if len(employess)>0:
                if count==1:
                    header=['Company','Companyurl','Industry','Headquators','Size','Founded','Phone','Website','Ceo_url','final','Message']
                    record=list(employess[0])
                    print(record,'hhh')
                    add_to_googlesheet(header, record)
                    count+=1
                else:
                    header=''
                    record=list(employess[0])
                    add_to_googlesheet(header,record)
                    count+=1
        except:
            pass


def getting_input_data(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    username=df.loc[df['keys'] == 'username', 'value'].iloc[0]
    password=df.loc[df['keys'] == 'password', 'value'].iloc[0]
    return username,password

def getting_input_dataframe(SHEET_ID,SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    return df


if __name__ == "__main__":
    #Google sheet id and name having username and password
    SHEET_ID = '1NvcHCO2laW69W_Eqb9bWcE5S7PkO0g5i3atsdCm1eDA'
    SHEET_NAME = 'sheet1'
    #Google sheet id and name having extracted links
    input_sheetid='1i1XNuxrmtAxJo3fDli_ex3LRb_3rnFRcry3n6_LErig'
    input_sheet_number='sheet1'
    username,password=getting_input_data(SHEET_ID,SHEET_NAME)
    input_data=getting_input_dataframe(input_sheetid,input_sheet_number)
    main(input_data,username,password)