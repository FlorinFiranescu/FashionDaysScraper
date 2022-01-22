import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os
import random
import pandas as pd


# container class
class product:
    def __init__(self):
        self.title = ""
        self.category = ""
        self.base_price = 0.0
        self.reduced_price = 0.0
        self.link = ""

    def obj2list(self):
        return [self.title, self.category, self.base_price, self.reduced_price, self.link]


def getProductPrice(productSoup):
    # product soup is a list. On position 0, main price. On 1, <sup>price</sup>
    mainPrice = productSoup.contents[0]
    if productSoup.sup is not None:
        restPrice = productSoup.sup.string
    return "{},{}".format(mainPrice, restPrice)


def request2BfSoupObj(url_path ):
    page = requests.get(url_path)
    print("\nRequesting Page URL: {}\n".format(url_path))
    if page.status_code == 200:
        print("\nRequest OK: Status code {}\n".format(page.status_code))
    else:
        print("\nError with the request:response: {}\n".format(page.status_code))
        raise ConnectionError("\nError with the request:response: {}\n".format(page.status_code))
        return 0
    page.encoding = 'ISO-885901'
    soup = BeautifulSoup(page.text, 'html.parser')  # using the html parser, easier to search in browser
    return soup


def getNextPage(pageSoups):
    nextPageLink = None
    if not("paginationLinkDisabled" in pageSoups['class']):
        print(pageSoups.get_text())
        nextPageLink = pageSoups['href']
    return nextPageLink

def gen_report_file(listOfItems, scraperType, columns, root_path):
    df = pd.DataFrame(listOfItems, columns=columns)

    while True:
        tmp_file_name = "{}_{}.xlsx".format(scraperType, random.randint(0, 100000))
        tmp_file_name = os.path.join(root_path, tmp_file_name)
        if not os.path.exists(tmp_file_name):
            path = os.path.join(root_path, tmp_file_name)
            break
    df.to_excel(path)
    print("Finished process for {}".format(scraperType))
    print(path)


# Scrapers
def fashionDaysScraper(urlPath, app_path):
    listOfProducts = []
    fashionDays_URL = "https://www.fashiondays.ro"
    # category_URL = "/televizoare/c"

    nextPageLink = urlPath


    while nextPageLink is not None:
        soup = request2BfSoupObj(nextPageLink)
        # Div container <=> our div containing all the products
        divContainer = soup.find('div', id="products-listing")
        nextPage = soup.find(class_="paginationNextPage")

        # nextPageLink = nextPage['href']
        for product in divContainer.find('ul', id='products-listing-list').find_all('li'):
            myProduct = product()
            myProductInfo = product.find(class_='campaign-info')
            myProduct.title = myProductInfo.find(class_="product-description").get_text()
            myProduct.category = "Incaltaminte"
            myProduct.link = product.a['href']
            prices = product.find('span', class_="campaign-discount")
            oldPrice = prices.find('span', class_='no-discount')
            newPrice = prices.find('strong')
            myProduct.reduced_price = float(newPrice.get_text().split()[0])/100
            try:
                myProduct.base_price = float(oldPrice.get_text().split()[1]) / 100
            except:
                myProduct.base_price = myProduct.reduced_price
            tempList = [myProduct.title, myProduct.category, myProduct.link, myProduct.base_price,
                        myProduct.reduced_price]
            listOfProducts.append(tempList)
            print(myProduct.title, myProduct.category, myProduct.link, myProduct.base_price,
                  myProduct.reduced_price)
        nextPageLink = getNextPage(nextPage)
        time.sleep(2)
    gen_report_file(listOfItems=listOfProducts,
                    columns=['title', 'category', 'link', 'base_price', 'reduced_price'],
                    scraperType="fashionDays", root_path=app_path)

fashionDaysScraper("https://www.fashiondays.ro/g/barbati-nike/incaltaminte", os.getcwd())