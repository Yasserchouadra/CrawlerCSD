import time
from urllib.parse import quote

from selenium.webdriver.common.by import By
import os
import database




def save_source_code(driver):    
    try:       
        url = driver.current_url.strip("/")
        title = driver.title.replace(" ", "_").replace("/", "_")
        content = driver.page_source
        database.save_url_content(url, content)
        return title, content

    except:
        print("-----------------------------------")
        print("There is a problem to save the web page content !")
        print("-----------------------------------")
        return None
    






def get_all_profile_links(driver):
    elems = driver.find_elements(by=By.XPATH, value="//a[@href]")
    res = set()
    for elem in elems:
        url = elem.get_attribute("href")
        if url.startswith("https://www.linkedin.com/in/"):
            res.add(url.split("?")[0].strip("/"))
    return res


def click_on_coordonnees(driver):
    driver.find_element(by=By.PARTIAL_LINK_TEXT, value="Coordonnées").click()



    

def login(driver,parameters):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    username = driver.find_element(By.ID,"username")
    username.send_keys(parameters['username'])
    pword = driver.find_element(By.ID,"password")
    pword.send_keys(parameters['password'])        
    driver.find_element(By.XPATH,("//button[@type='submit']")).click()


def search(driver, query, page   ):
    query = quote(query)
    url ="https://www.linkedin.com/search/results/people/?geoUrn=[%22105015875%22]&keywords="+query+"&origin=FACETED_SEARCH&page="+str(page)
    driver.get(url)


def save_done(links):
    with open("data/done.txt", "a") as f:
        f.write("\n".join(links) + "\n")


def is_done(link):
    return database.exist(link)


def get_source_code(driver,link, use_cache=True):
    if use_cache and is_done(link):
        page = database.get_page(link)
        if page is not None:
            return page
    driver.get(link)
    time.sleep(1)
    return None


def scroll_down(driver):
    # From https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
    SCROLL_PAUSE_TIME = 3
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
