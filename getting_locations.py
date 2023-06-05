import pickle
import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import random

import parameters

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


def loggin(driver,userr,passw):
    driver.get("https://linkedin.com/login")
    # waiting for the page to load
    time.sleep(5)
    # #entering username
    username=driver.find_element(By.XPATH, '//input[@id="username"]')
    username.send_keys(userr)
    namee=parameters.username.split('@')[0]
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
    print(all_data)
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
    companies_list=df.company_url.tolist()
    print(companies_list)
    updated=[]
    for c in companies_list:
        c=c.replace('/sales','')
        c=c.split('?')[0]
        updated.append(c)
    return updated

def main(df,outt):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    updated=getting_links(df)
    df['linkedin_url_comapnies']=updated
    driver.get('https://www.linkedin.com')
    time.sleep(5)
    try:
        user=parameters.username.split('@')
        driver=load_cookie(driver,user)
    except:
        loggin(driver,parameters.username,parameters.password)
    time.sleep(3)

    time.sleep(3)

    for i in updated:
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
        ceo=df.loc[df['linkedin_url_comapnies']==str(i),'ceo'].iloc[0]
        company=df.loc[df['linkedin_url_comapnies']==str(i),'company'].iloc[0]
        overseas = []
        if len(people_list)>1:
            people_list=people_list[2:]
            people_list = [x.lower() for x in people_list]
            us_loc=us_locationn()

            for p in people_list:
                print(p)
                for m in us_loc:
                    if m in p:
                        # res.remove(i)
                        print(m)
                        overseas.append(p)
                        break
        final = set(people_list) - set(overseas)
        if len(final)>=1:
            employess.append([company,i,industry,headq,Size,founded,Phone,website,ceo,final])
        time.sleep(random.randint(4,8))

        dfff=pd.DataFrame(employess)
        dfff.to_csv(outt+'.csv',mode='a',index=False,header=False)




if __name__ == "__main__":
    input_path='ITandsoftware.csv'
    inputt=pd.read_csv(input_path)
    output='result.csv'
    main(inputt,output)