from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import math
import asyncio

def main():

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox") # linux only    
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--headless=new") # for Chrome >= 109
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")

    service=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://job.rikunabi.com/2025/search/pre/company/result/?fw=&isc=r21rcnc00701")

    WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ts-p-l-body-main"))
    )

    page_total_number = get_total_number(driver)
    
    scraping_result = []
    company_url_name_locations = []
    # for i in range(math.floor(page_total_number / 100)):
    for i in range(2):
        company_url_name_locations.extend(get_companies(driver))
        try:
            driver.find_element(By.CSS_SELECTOR, "a.ts-p-search-pager01-list-item_next").click()
        except:
            print("This Error Is About Pagination Next Button")
        time.sleep(1)

    print("Total Companies Length: %s", len(company_url_name_locations))

    for company_url_name_location in company_url_name_locations:
        driver.get(company_url_name_location['url'])
        time.sleep(3)
        company_main_info = scrape_company_main_info(driver)
        print(company_main_info)
        scraping_result.append({
            "company_url": company_url_name_location['url'],
            "company_name": company_url_name_location['name'],
            "company_location": company_url_name_location['location'],
            "company_members": company_main_info['company_members']
        })
    
    print("The Result Length: %s", len(scraping_result))

def get_total_number(driver):
    total_number = 0
    try:
        total_number_element = driver.find_element(By.CSS_SELECTOR, "span.ts-p-search-resultCounter > span.ts-p-search-resultCounter-count").text
        total_number = int(total_number_element)
    except:
        print("This Error Is About Total Page Number")
    print("Total Page Length: %s", total_number)
    return total_number

def get_companies(driver):
    company_data = []
    try:
        sel = Selector(text = driver.page_source)
        for item in sel.xpath("//div[contains(@class, 'ts-p-l-body-main')] / ul[contains(@class, 'ts-p-search-cassetteList')] / li[contains(@class, 'ts-p-search-cassetteList-item')]"):
            company_data.append({
                'name': item.css('div.ts-p-_cassette > div.ts-p-_cassette-header > div.ts-p-_cassette-header-cell > h2.ts-p-_cassette-title > a::text').get(),
                'url': "https://job.rikunabi.com" + item.css('div.ts-p-_cassette > div.ts-p-_cassette-header > div.ts-p-_cassette-header-cell > h2.ts-p-_cassette-title > a::attr(href)').get(),
                'location': item.css('div.ts-p-_cassette > div.ts-p-_cassette-body > div.ts-p-_cassette-body-main > table.ts-p-_cassette-dataTable > tbody > tr:nth-child(2) > td.ts-p-_cassette-dataTable-cell > div.ts-p-_cassette-dataTable-main::text').get()
            })
    except:
        print("This Error Is About Company Url and Name")
    print(company_data)
    return company_data

def scrape_company_main_info(driver):
    company_members = []
    senior_page_url = ''

    try:
        WebDriverWait(driver=driver, timeout=3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ts-p-company-individualArea"))
        )

        try:
            sel = Selector(text = driver.page_source)
            for item in sel.xpath("//div[contains(@class, 'ts-p-company-upperArea')] / div[contains(@class, 'ts-p-company-tabBar_top')] / a[contains(@class, 'ts-p-company-tabBar-tab')]"):
                tag_href = item.css('.ts-p-company-tabBar-tab::attr(href)').get()
                if tag_href.find('seniors'):
                    senior_page_url = "https://job.rikunabi.com" + tag_href
        except:
            print("This Error Is About Nothing Senior Info")

        if senior_page_url:
            try:
                driver.get(senior_page_url)
                time.sleep(2)

                sel = Selector(text = driver.page_source)
                for item in sel.xpath("//div[contains(@class, 'ts-p-company-individualArea')] / div[contains(@class, 'ts-p-company-section')] / div[contains(@class, 'ts-p-company-cardList')] / a[contains(@class, 'ts-p-company-cardList-item')]"):
                    company_members.append({
                        'article_title': item.css('div.ts-p-company-cardList-item-inner > div.ts-p-company-cardList-item-inner-text > h3.ts-p-company-cardList-item-inner-text-title::text').get(), 
                        'article_url': "https://job.rikunabi.com" + item.css('.ts-p-company-cardList-item_link::attr(href)').get(),
                        'name': item.css('div.ts-p-company-cardList-item-inner > div.ts-p-company-cardList-item-inner-text > div.ts-p-company-cardList-item-inner-text-label:nth-child(2)::text').get()
                    })
            except:
                print("This Error Is About Nothing Senior Info")
    except:
        print("This Page Is Not Found")

    return {
        'company_members': company_members
    }



if __name__ == '__main__':
    main()