'''
Python for Developers
Easy Wardrobe - Webscraper Nordstrom w/ Selenium
Kim Jin
'''


# Import libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time


# Variables
website_name = 'Nordstrom'
website_1 = 'https://shop.nordstrom.com/sr?keyword='
website_2 = '&filtercategoryid=6000011'
n = 1
search_keyword = ''


# Functions
"""Search Prompt"""
def search_prompt():
    search_keyword = input("What would you like to search? Press ENTER to exit the program.\n")
    return search_keyword


"""Get Product Information"""
def get_product_name(browser):
    products = browser.find_elements_by_css_selector("article > a > img")
    product_name = [(product.get_attribute('alt')) for product in products]
    return product_name


def get_product_url(browser):
    products = browser.find_elements_by_css_selector("article > a")
    product_url = [(product.get_attribute('href')) for product in products]
    return product_url


def get_product_img(browser):
    products = browser.find_elements_by_css_selector("article > a > img[alt]")
    product_img = [(product.get_attribute('src')) for product in products]
    return product_img


def get_product_price(browser):
    products = browser.find_elements_by_css_selector("article > div > p:last-child > span.npr-_EO1P")
    product_price = [(product.text) for product in products]
    product_price = [price for price in product_price]
    # print(product_price)
    return product_price


"""Aggregate product info"""
# def get_num_products(browser):
#
#     return num_products


def get_product_info(browser):
    products_name = get_product_name(browser)
    products_url = get_product_url(browser)
    products_img = get_product_img(browser)
    products_price = get_product_price(browser)
    return products_name, products_url, products_img, products_price


def scroll_down(browser):
    browser.execute_script("window.scrollTo(0, 100000);")
    time.sleep(3)
    return


# Main()
def main():
    while 1:
        """Search Keyword"""
        search_keyword = search_prompt()
        if search_keyword == "":
            return
        # print("Search: ", search_keyword)

        start = time.time()

        """Browser Setup & Input Search Keyword"""
        browser = webdriver.Chrome()
        website = website_1 + search_keyword + website_2
        browser.get(website)

        """Scrape Content"""
        products_name_website = []
        products_img_website = []
        products_url_website = []
        products_price_website = []
        for i in range(0, n):
            products_name_scrape, products_url_scrape, products_img_scrape, products_price_scrape = get_product_info(browser)
            scroll_down(browser)
            products_name_website = products_name_website + products_name_scrape
            products_url_website = products_url_website + products_url_scrape
            products_img_website = products_img_website + products_img_scrape
            products_price_website = products_price_website + products_price_scrape
            # print("products_name_scrape:", len(products_name_scrape), products_name_scrape)
        # print("products_name_website", len(products_name_website))

        """Quit Browser"""
        browser.quit()

        """Pandas Data Frame"""
        # index = range(1,21)
        # print(index)
        merge_data = {
            'name': pd.Series(products_name_website),
            'link': pd.Series(products_url_website),
            'image': pd.Series(products_img_website),
            'price': pd.Series(products_price_website)
            # 'name': products_name_website, 'link': products_url_website, 'image': products_img_website, 'price': products_price_website
        }
        df_merge_data = pd.DataFrame(merge_data, columns=['name', 'link', 'image', 'price'])
        df_merge_data = df_merge_data.drop_duplicates(subset=['name'])
        df_merge_data = df_merge_data.dropna(axis=0, how='any')
        df_merge_data.index = range(1, len(df_merge_data)+1)
        # print(df_merge_data)
        # print("merge_data:")
        # print(merge_data)

        """Pandas to CSV"""
        df_merge_data.to_csv('Topshop.csv', columns = ['name', 'link', 'image', 'price'], encoding = 'utf-8')
        # print("created csv")

        end = time.time()
        # print(end - start)
    return


# run main()
if __name__ == "__main__":
    main()
