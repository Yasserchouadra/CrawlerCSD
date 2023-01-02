import json
import os
import re
import time
from pprint import pprint

from bs4 import BeautifulSoup

from selenium_accessor import get_source_code, scroll_down, save_source_code, login

CI_RE = re.compile(r"ci-([^ ]*)")


EASY_FIELDS = [
    {"name": "fullname", "cat": "h1", "class": "text-heading-xlarge inline t-24 v-align-middle break-words"},
    {"name": "current_job_title", "cat": "div", "class": "text-body-medium break-words"},
    {"name": "location", "cat": "span", "class": "text-body-small inline t-black--light break-words"},
]


def parse_page(content,driver):
    soup = BeautifulSoup(content, features="html.parser")
    data = {}
    sections = soup.find_all("section")
    for section in sections:
        section_class = " ".join(section["class"])
        name_match = CI_RE.search(section_class)
        if name_match is not None:
            name = name_match.group(1)
            data[name] = [x.strip() for x in section.getText().strip().split("\n")[1:]
                          if x.strip()]
    for easy_field in EASY_FIELDS:
        names = soup.find_all(easy_field["cat"], {"class": easy_field["class"]})
        assert len(names) <= 1
        for name in names:
            data[easy_field["name"]] = name.getText().strip()
    section_cards = soup.find_all("section", {"class": "artdeco-card"})
    for section_card in section_cards:
        header_divs = section_card.find_all("div", {"class": "pvs-header__container"})
        if len(header_divs) != 1:
            continue
        header = ""
        for header_div in header_divs:
            header_spans = header_div.find_all("span", {"aria-hidden": "true"})
            for header_span in header_spans:
                header = header_span.getText().strip()
        data[header] = []
        detailled_url = list(set(get_detailled_url(section_card)))
        if detailled_url:
            detailled_content = get_source_code(driver,detailled_url[0], True)
            print("Getting")
            while detailled_content is None:
                time.sleep(3)
                print("Scrolling")
                scroll_down(driver)
                print("Saving")
                save_source_code(driver)
                print(detailled_url[0], driver.current_url)
                if "/404/" in driver.current_url:
                    detailled_content = "404"
                else:
                    detailled_content = get_source_code(driver,detailled_url[0])
            if detailled_content != "404":
                new_soup = BeautifulSoup(detailled_content, features="html.parser")
                section_card = new_soup.find("section", {"class": "artdeco-card"})
        items = section_card.find_all("div", {"class": "display-flex flex-column full-width align-self-center"})
        for item in items:
            spans = item.find_all("span")
            span_texts = []
            for span in spans:
                if span.has_attr("class"):
                    continue
                span_texts.append(span.getText().strip().replace(u'\xa0', u' '))
            data[header].append(span_texts)
    return data


def process_all(driver):
    for filename in os.listdir("data/"):
        if not filename.endswith(".html"):
            continue
        with open("data/" + filename) as f:
            data = parse_page(f.read(),driver)
        with open("data/" + filename.replace(".html", ".json"), "w") as f:
            f.write(json.dumps(data))


def get_detailled_url(soup):
    for link in soup.findAll('a'):
        if "/details/" in link.get("href", "") and "Afficher" in link.getText():
            yield link.get("href").split("?")[0]


