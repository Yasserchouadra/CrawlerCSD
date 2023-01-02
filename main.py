import json
import string
from time import sleep
from selenium_accessor import  save_source_code, get_all_profile_links, click_on_coordonnees, login, search, save_done, is_done
from page_parser import parse_page
from selenium import webdriver 
import os
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

parameters = {'username' : "hy_chouadra@esi.dz",
              'password' : "yasser731999+++",
              'GH_token' : "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",
            }




def process_all_profiles_on_page(driver):
    links = set()
    while len(links) < 3:
        links = get_all_profile_links(driver)

    print("Found", len(links), "profiles.")
    for link in links:
        if is_done(link):
            continue
        print("Processing", link)
        sleep(15)
        driver.get(link)
        sleep(15)
        click_on_coordonnees(driver)
        sleep(10)
        save_and_process_page(driver)
    save_done(links)


def save_and_process_page(driver):
#  FIND HTML CONTENT AND TITLE
    title, content = save_source_code(driver)
    
# PARSE HTML DATA
    data = parse_page(content,driver)

# FIND FULLNAME
    fullname = "unknown"
    if data :
        fullname = data["fullname"]
        pathHTML = os.getcwd() +"/data/html/"+ fullname + ".html" 
        pathJSON = os.getcwd() +"/data/json/"+ fullname + ".json" 
        
        # SAVE HTML CONTENT
        soupwebpage = BeautifulSoup(content, features="html.parser")
        with open(pathHTML, "w", encoding="utf-8") as file:
            file.write(str(soupwebpage))

        # SAVE JSON CONTENT
        with open(pathJSON +".json" , "w" , encoding="utf-8") as f:
                f.write(json.dumps(data))





if __name__ == '__main__':
    os.environ['GH_TOKEN'] = parameters['GH_token'] 
    
    while True:
        res = input("Enter the mode you want [manual or  auto ]").strip()
        if res == "m":
            driver = webdriver.Firefox()
            login(driver,parameters)
            while True: 
                    res2 = input("Enter your action [ this or all ]").strip()
                    if res2 == "all":
                            process_all_profiles_on_page(driver)
                            print("DONE.")

                    elif res2 == "this":
                            save_and_process_page(driver)
                            print("DONE.")

        elif res == "a":    
            all_names = []
            path_names = os.getcwd() + "/data/utils/all_names.json"
            with open(path_names) as f:
                   all_names = json.load(f)
                
            # status names  [ 0 - 14 ]: done
            cpt_profile = 14
            driver = webdriver.Firefox()
            login(driver,parameters)
            for name in all_names[14:300]:
                for page in range(1,10,1):
                    print("************************************************************")
                    print("we start looking for "+ str(cpt_profile)+" - "+ name+" profiles in page: "+str(page))
                    sleep(2)
                    search(driver,name,page)
                    sleep(5)
                    process_all_profiles_on_page(driver)
                    # driver.quit()
                    cpt_profile = cpt_profile + 1
                    sleep(20)
                print("Name " +name +" is done.")
            print("Done")
      
