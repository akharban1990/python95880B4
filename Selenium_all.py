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
import webbrowser
import requests
import bs4


# Variables
"""Modules"""
modules = [Selenium_Nordstrom, Selenium_Macys]
module_names = {Selenium_Nordstrom: 'Nordstrom',
                Selenium_Macys: 'Macys'}
"""URL"""
url1 = {'Nordstrom':'https://shop.nordstrom.com/sr?keyword=',
        'Macys': 'https://www.macys.com/shop/featured/',
        'GAP': 'https://www.gap.com/browse/search.do?searchText='}
url2 = {'Nordstrom':'&filtercategoryid=6000011',
        'Macys': '/Gender/Men',
        'GAP': '#pageId=0&department=75'}
search_keyword_punc = {'Nordstrom': '+', 'Macys': '-', 'GAP': '-'}
# num_scroll = {'Nordstrom': 1, 'Macys': 1, 'GAP': 1}

def makeURLASOS(searchTerm):
    url_home = "http://us.asos.com/search/mens%20"  # add search item and ext_home_men
    ext_home_men = "?page=1&q=mens%20"  # add search item
    url=url_home + searchTerm+ext_home_men+searchTerm
    return url


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

def getArticles(url):
    articleName =[]
    linkList =[]
    price = []
    image=[]
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url,headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    for span in soup.find_all(name="span", attrs={"class": "_342BXW_"}):
        price.append(span.text.strip())
    for a in soup.find_all(name="a", attrs={"class": "_3x-5VWa"}):
        articleName.append(a['aria-label'])
        linkList.append(a['href'])
    for div in soup.find_all(name="div", attrs={"class": "_1FN5N-P"}):
        for img in div.find_all(name="img"):
            image.append(img.get("src"))

    return price,articleName,linkList,image

def createHTML(name, url, image, price,link):
    urli = makeURLASOS(link)
    price = price+ (getArticles(urli)[0])
    name = name + (getArticles(urli)[1])
    url = url + (getArticles(urli)[2])
    image = image+ (getArticles(urli)[3])

    f = open('output.html', 'w')
    message = """
    <html><head><title>Easy Clothing</title><meta charset="utf-8" /></head><body><div id="divHome">
    <div style="background-color:aquamarine;border-style:double;border-width:4px">
    <h1>Easy Clothing</h1>
    </div>
    <br />
    <div id="divMainMenu">

    <table style="width:100%;">
    """
    image =['https://www.readjunk.com/wp-content/uploads/2015/09/no-image-found1-900x600.png' if x is None else x for x in image]
    
    i_max = min(len(name), len(url), len(image), len(price)) + 1
    for i in range(1,i_max):
        if i%3==1:
            message = message + """<tr>"""
        message = message + """<td><h3>"""+name[i-1]+"""</h3><br /><a href="""+url[i-1]+"""><img src="""+image[i-1]+""" height="300px"/></a><br /><label style="padding-left:75px">Price:"""+ price[i-1]+"""</label></td>"""
        if i%3==0:
            message = message + """</tr>"""
    f.write(message)
    f.close()
    webbrowser.open('output.html')
    return


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
        
        products_name_all =[]
        products_url_all =[]
        products_img_all=[]
        products_price_all=[]

        for module in modules:
            # Website: Nordstrom, Macys, GAP
            # Dictionary keys
            website = module_names[module]

            search_keyword = search_keyword_raw.replace(" ", search_keyword_punc[website])
            # print("Search:", search_keyword)

            # Browser setup
            print("Searching", website, "...")
            browser = webdriver.Chrome()
            url = url1[website] + search_keyword + url2[website]
            browser.get(url)

            # Scrape content
            products_name_website = []
            products_img_website = []
            products_url_website = []
            products_price_website = []

            # for i in range(0, num_scroll[website]):
            products_name_scrape, products_url_scrape, products_img_scrape, products_price_scrape = module.get_product_info(browser)
            scroll_down(browser)
            products_name_website = products_name_website + products_name_scrape
            products_url_website = products_url_website + products_url_scrape
            products_img_website = products_img_website + products_img_scrape
            products_price_website = products_price_website + products_price_scrape
            # print("products_name_scrape:", len(products_name_scrape), products_name_scrape)
            # print(website, "products", len(products_name_website))
            products_img_all = products_img_all + products_img_website
            products_name_all = products_name_all + products_name_website
            products_price_all = products_price_all + products_price_website
            products_url_all = products_url_all + products_url_website
            
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
        print("Searching Asos ...")
        print("Gathering results ...")
        createHTML(products_name_all, products_url_all, products_img_all, products_price_all,search_keyword)

        df_merge_data = pd.concat(frames, ignore_index=True, axis=0)
        df_merge_data.index = range(1, len(df_merge_data)+1)
        # print("df_merge_data: ", len(df_merge_data), df_merge_data)

        """Pandas to CSV"""
        csv_name = search_keyword + '.csv'
        df_merge_data.to_csv(csv_name, columns=['name', 'link', 'image', 'price'], encoding='utf-8')
        print("Search complete!")
        
    return


if __name__ == '__main__':
    main()
