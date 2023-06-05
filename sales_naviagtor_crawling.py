import pickle
import random

import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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



# def get_companies_new():
#     alll_comapnies = driver.find_elements(By.XPATH, '//a[@class="app-aware-link "]')
#     alll_comapnies[0].send_keys(Keys.PAGE_DOWN)
#     alll_comapnies[0].send_keys(Keys.PAGE_DOWN)
#     alll_comapnies[0].send_keys(Keys.PAGE_DOWN)
#
#     for aa in alll_comapnies:
#         if aa.text!='':
#             companies_list.append(aa.text)
        # print(aa.text)

def loggin(driver,userr,passs):
    driver.get("https://linkedin.com/login")
    # waiting for the page to load
    time.sleep(5)
    # #entering username
    username=driver.find_element(By.XPATH, '//input[@id="username"]')
    username.send_keys(userr)
    namee=parameters.username.split('@')[0]
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
    for m in range(0,101):
        for i in range(0,10):
            alll_users = driver.find_elements(By.XPATH, '//div[@class="artdeco-entity-lockup__content ember-view"]')
            # try:
            (alll_users[-1]).location_once_scrolled_into_view
            # except:
            #     pass


            for a in alll_users:
                full_user = []
                try:
                    nn2 = a.find_element(By.XPATH, './/div[@class="artdeco-entity-lockup__subtitle ember-view t-14"]')
                    # if (nn2.find_element(By.XPATH, 'a').text).lower() in c_list:
                    nn = a.find_element(By.XPATH, './/div[@class="artdeco-entity-lockup__title ember-view"]')

                    # full_user.append(a.find_element(By.TAG_NAME,'a').get_attribute('href'))
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


# def get_companies(vv):
#     element = driver.find_element(By.XPATH,
#                                   '//a[@class="job-card-container__link job-card-container__company-name ember-view"]')
#     if vv == 'yes':
#         element.send_keys(Keys.TAB)
#     element.send_keys(Keys.PAGE_DOWN)
#     element.send_keys(Keys.PAGE_DOWN)
#     element.send_keys(Keys.PAGE_DOWN)
#     element.send_keys(Keys.PAGE_DOWN)
#     element.send_keys(Keys.PAGE_DOWN)
#     time.sleep(4)
#
#     companies = driver.find_elements(By.XPATH,
#                                      '//a[@class="job-card-container__link job-card-container__company-name ember-view"]')
#     for c in companies:
#         companies_list.append(c.text)


def main(search,outt):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get('https://www.linkedin.com')
    time.sleep(5)
    # parameters
    try:
        user=parameters.username.split('@')
        driver=load_cookie(driver,user)
    except:
        loggin(driver,parameters.username,parameters.password)
    # driver=load_cookie(driver)
    time.sleep(random.randint(5,8))
    driver.get(search)
    time.sleep(10)
    # geography=driver.find_element(By.XPATH,'//fieldset[@title="Geography"]')
    # time.sleep(3)
    # geography.send_keys(Keys.PAGE_UP)
    # geography.find_element(By.XPATH,'.//button[@type="button"]').click()
    # geography=driver.find_element(By.XPATH,'//input[@placeholder="Add locations"]')
    # geography.send_keys('United states')
    # time.sleep(30)


    # time.sleep(10)

    time.sleep(1)
    # for i in range(0,8):
    get_user_link(driver,companies_list)
    time.sleep(1)

    time.sleep(7)

    print(len(users_list))
    print(users_list)
    dfff=pd.DataFrame(users_list)
    dfff.to_csv(outt+'.csv',index=False,header=False)



if __name__ == "__main__":
    search_link='https://www.linkedin.com/sales/search/people?query=(recentSearchParam%3A(id%3A2163387729%2CdoLogHistory%3Atrue)%2Cfilters%3AList((type%3ACOMPANY_HEADCOUNT%2Cvalues%3AList((id%3AD%2Ctext%3A51-200%2CselectionType%3AINCLUDED)%2C(id%3AE%2Ctext%3A201-500%2CselectionType%3AINCLUDED)))%2C(type%3ACOMPANY_HEADQUARTERS%2Cvalues%3AList((id%3A102748797%2Ctext%3ATexas%252C%2520United%2520States%2CselectionType%3AINCLUDED)))%2C(type%3ATITLE%2Cvalues%3AList((id%3A8%2Ctext%3AChief%2520Executive%2520Officer%2CselectionType%3AINCLUDED))%2CselectedSubFilter%3ACURRENT)%2C(type%3AINDUSTRY%2Cvalues%3AList((id%3A4%2Ctext%3ASoftware%2520Development%2CselectionType%3AINCLUDED)%2C(id%3A96%2Ctext%3AIT%2520Services%2520and%2520IT%2520Consulting%2CselectionType%3AINCLUDED)))))&sessionId=xVW%2FE%2FYTSo%2BsEZ9VMHQwDg%3D%3D&viewAllFilters=true'
    output='result.csv'
    main(search_link,output)