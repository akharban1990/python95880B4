'''
Python for Developers
Easy Wardrobe - Webscraper w/ Selenium - 3 Websites
Kim Jin
'''


# Import libraries
from selenium import webdriver
import pandas as pd
import time
# Import modules
import Selenium_Nordstrom, Selenium_Macys, Selenium_GAP


# Variables
"""Modules"""
modules = [Selenium_Nordstrom, Selenium_Macys, Selenium_GAP]
module_names = {Selenium_Nordstrom: 'Nordstrom',
               Selenium_Macys: 'Macys',
               Selenium_GAP: 'GAP'}
"""URL"""
url1 = {'Nordstrom':'https://shop.nordstrom.com/sr?keyword=',
        'Macys': 'https://www.macys.com/shop/featured/',
        'GAP': 'https://www.gap.com/browse/search.do?searchText='}
url2 = {'Nordstrom':'&filtercategoryid=6000011',
        'Macys': '/Gender/Men',
        'GAP': '#pageId=0&department=75'}
search_keyword_punc = {'Nordstrom': '+', 'Macys': '-', 'GAP': '-'}
num_scroll = {'Nordstrom': 1, 'Macys': 1, 'GAP': 3}


# Functions
"""Search Prompt"""
def search_prompt():
    search_keyword = input("What would you like to search? Press ENTER to exit the program.\n")
    return search_keyword


def scroll_down(browser):
    browser.execute_script("window.scrollTo(0, 100000);")
    return

def merge(frames):
    df = frames[0]
    for frame in frames[1:]:
        df = df.concat(frame)
    return df


# Main()
def main():
    while 1:
        """Search Keyword"""
        search_keyword_raw = search_prompt()
        if search_keyword_raw == "":
            return
        print("Searching", search_keyword_raw, "...")

        """Iteration Loop"""
        frames = []
        for module in modules:
            # Website: Nordstrom, Macys, GAP
            # Dictionary keys
            website = module_names[module]
            # print(module)

            search_keyword = search_keyword_raw.replace(" ", search_keyword_punc[website])
            # print("Search:", search_keyword)

            # Browser setup
            browser = webdriver.Chrome()
            url = url1[website] + search_keyword + url2[website]
            browser.get(url)

            # Scrape content
            products_name_website = []
            products_img_website = []
            products_url_website = []
            products_price_website = []

            for i in range(0, num_scroll[website]):
                products_name_scrape, products_url_scrape, products_img_scrape, products_price_scrape = module.get_product_info(browser)
                scroll_down(browser)
                products_name_website = products_name_website + products_name_scrape
                products_url_website = products_url_website + products_url_scrape
                products_img_website = products_img_website + products_img_scrape
                products_price_website = products_price_website + products_price_scrape
                # print("products_name_scrape:", len(products_name_scrape), products_name_scrape)
            # print(website, "products", len(products_name_website))

            # Quit browser
            browser.quit()

            # Pandas
            website_data = {
                'name': pd.Series(products_name_website),
                'link': pd.Series(products_url_website),
                'image': pd.Series(products_img_website),
                'price': pd.Series(products_price_website)
            }
            df_website_data = pd.DataFrame(website_data, columns=['name', 'link', 'image', 'price'])
            df_website_data = df_website_data.drop_duplicates(subset=['name'])
            df_website_data = df_website_data.dropna(axis=0, how='any')

            # csv_name = website + search_keyword_raw + '.csv'
            # df_website_data.to_csv(csv_name, columns=['name', 'link', 'image', 'price'], encoding='utf-8')

            frames.append(df_website_data)

        """Merge Data"""
        df_merge_data = pd.concat(frames, ignore_index=True, axis=0)
        df_merge_data.index = range(1, len(df_merge_data)+1)
        print("df_merge_data: ", len(df_merge_data), df_merge_data)

        """Pandas to CSV"""
        csv_name = search_keyword + '.csv'
        df_merge_data.to_csv(csv_name, columns=['name', 'link', 'image', 'price'], encoding='utf-8')
        print("Search finished.")
    return


if __name__ == '__main__':
    main()
