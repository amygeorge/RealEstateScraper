import selenium
from selenium import webdriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import pandas as pd
from money_parser import price_str


chrome_driver_path = "C:\Python39\Scripts\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument('--headless')
webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)
loc_arr = ['SUNSHINE COAST - SEA-TO-SKY ↓', 'Sunshine Coast', 'Squamish', 'Whistler + Pemberton', 'NORTH SHORE ↓',
           'Bowen Island', 'West Vancouver', 'North Vancouver', 'METRO VANCOUVER ↓', 'Metro Vancouver RD',
           'City of Vancouver', ' ↳ Vancouver Westside', ' ↳ Vancouver Eastside', 'Burnaby', 'New Westminster',
           'Port Moody + Anmore + Belcarra', 'Coquitlam', 'Port Coquitlam', 'Pitt Meadows', 'Maple Ridge', 'Richmond',
           'Ladner + Tsawwassen', 'City of Surrey + White Rock + Delta', ' ↳ North Surrey',
           ' ↳ Central Surrey + Cloverdale + Delta', ' ↳ South Surrey + White Rock', 'Langley', 'FRASER VALLEY ↓',
           'Mission', 'Abbotsford', 'Chilliwack & District', ' ↳ Chilliwack', ' ↳ Chilliwack Rural', ' ↳ Sardis',
           ' ↳ Hope', 'ISLANDS ↓', 'Gulf Islands', 'NORTH COAST ↓', 'Powell River', 'VANCOUVER ISLAND ↓',
           'North Island', 'Campbell River', 'Comox Valley', 'Parksville + Qualicum Beach', 'Alberni Valley', 'Nanaimo',
           'Cowichan Valley', 'Victoria', 'Sooke & Area', 'Saanich & Area + Sidney', 'NORTHERN INTERIOR ↓',
           'Dawson Creek + Chetwynd + Tumbler Ridge', 'Prince George & Area', 'Kamloops & Area',
           'OKANAGAN & KOOTENAYS ↓', 'Vernon & Area + Shuswap', 'Kelowna & Area', 'Penticton & Area + Similkameen',
           'Kootenays', 'BOARD REGIONS ↓', 'Vancouver & Region (REBGV)', 'Fraser Valley Region (FVREB)',
           'Chilliwack & Region (CADREB)', 'REBGV + FVREB + CADREB Regions']


def selectArea(d):
    select = Select(d.find_element_by_name("database"))

    # select by visible text
    metro = "Metro Vancouver RD"
    select.select_by_visible_text(metro)

    # Get price menu
    select = Select(d.find_element_by_name("pricehigh"))

    # # limit price to 250k
    # select.select_by_value('250')

    # limit price to 750k
    select.select_by_value('750')


    # # Get bedrooms menu
    # select = Select(d.find_element_by_name("bedrooms"))
    #
    # # get 3+ bedrooms
    # select.select_by_value('3')
    #
    # # Get bathrooms menu
    # select = Select(d.find_element_by_name("bathrooms"))
    #
    # # get 2+ bathrooms
    # select.select_by_value('2')

    # another way to do the same thing!
    # ---------------------------------
    #  <option value="metro">Metro Vancouver RD</option>
    # username = d.find_element_by_xpath("/option[@value='metro']")

    # this = "//select[@name='database']"
    # search_button = d.find_element_by_xpath(this)
    # search_button.find_element_by_xpath("//option[@value='metro']")
    # search_button.click()


def getSearchResults(pages, wait, d):
    result_arr = []
    wait.until(presence_of_element_located((By.ID, "searchResults")))
    time.sleep(3)
    results = d.find_elements_by_class_name('columns')

    arr = extractData(results)
    result_arr.extend(arr)
    button = "/html/body/div[3]/div/button[2]"
    nextpage = d.find_element_by_xpath(button)
    try:
        nextpage.click()
    except selenium.common.exceptions.ElementNotInteractableException:
        pass
    pages -= 1
    return pages, result_arr


def removeUseless(houses):

    for house in houses:
        try:
            if "Manufactured" in house['style']:
                houses.remove(house)

            elif "Manufactured" in house['storeys']:
                houses.remove(house)

            elif "Floating" in house['style']:
                houses.remove(house)

            elif "Floating Home" in house['storeys']:
                houses.remove(house)

            elif "Co-op" in house['blurb']:
                houses.remove(house)

            elif "19+" in house['blurb']:
                houses.remove(house)

            elif "55+" in house['blurb']:
                houses.remove(house)

            elif "age restricted" in house['blurb']:
                houses.remove(house)

        except ValueError:
            pass
        except KeyError:
            pass
    return houses


def removeExpensive(houses):
    affordable = []
    for house in houses:
        try:
            if house['price'] <= 600000:
                affordable.append(house)
            if house['strata'] > 500:
                houses.remove(house)
        except ValueError:
            pass
        except KeyError:
            pass
    return affordable


def removeAreas(houses):
    desiredArea = []
    for house in houses:
        try:
            if "Surrey" not in house['area']:
                desiredArea.append(house)
        except KeyError:
            pass
    return desiredArea

def collectDF(houses):
    houses = removeUseless(houses)
    houses = removeExpensive(houses)
    houses = removeAreas(houses)

    df = pd.DataFrame(houses)
    print(df.head())
    df.to_excel("houses.xlsx")


def extractData(results):
    houseArray = []
    for column in results:
        try:
            houseDict = {}
            result = column.text.split("\n")
            address = result[0]
            print(result)
            for line in result[:-1]:
                if "MLS" in line:
                    houseDict["MLS"] = line
                if " • " in line:
                    type, storey = line.split(" • ")
                    houseDict["style"] = type
                    houseDict["storeys"] = storey

                blurb = result[len(result) - 1:]
                houseDict["blurb"] = blurb

                houseDict["address"] = address
                if 'Show info on strata building' in result[2]:
                    area = result[3]
                    houseDict["area"] = area
                elif "$" in result[2]:
                    area = result[1]
                    houseDict["area"] = area

                if '     ' in line:
                    bed = line[:1]
                    bath = line[-1:]
                    houseDict["beds"] = bed
                    houseDict["baths"] = bath
                if "Asking Price" in line:
                    value = float(price_str(line))
                    houseDict["price"] = value
                if "Assessed Value" in line:
                    houseDict["assessed"] = line[len("Assessed Value"):]
                if "Size of House" in line:
                    value = float(price_str(line))
                    houseDict["size"] = value
                if "Strata Fee" in line:
                    value = float(price_str(line))
                    houseDict["strata"] = value
                if "Property Taxes" in line:
                    houseDict["tax"] = line[len("Property Taxes"):]
                if "Ownership floaterest" in line:
                    houseDict["ownership"] = line[len("Ownership floaterest"):]
                if "Age of House" in line:
                    houseDict["age"] = line[len("Age of House"):]
                if "Basement" in line:
                    houseDict["basement"] = line[len("Basement"):]
                if "Price per SqFt" in line:
                    value = float(price_str(line))
                    houseDict["pricebyft"] = value
            houseArray.append(houseDict)
        except BaseException:
            pass
    return houseArray


def getWebsite(url):
    fullArray = []
    with webdriver as driver:
        # Set timeout time
        w = WebDriverWait(driver, 5)

        # retrive url in headless browser
        driver.get(url)
        selectArea(driver)

        p = 3
        while p > 0:
            page, arr = getSearchResults(p, w, driver)
            fullArray.extend(arr)
            p = page

        driver.close()
    collectDF(fullArray)


if __name__ == "__main__":
    zealty = 'https://www.vancouverrealestatemap.ca/search-frame.html?&kMapName=vancouver&kUserData=map-v02697' \
             '&kMapServerURL=https%3A//www.vancouverrealestatemap.ca/&kMapClientURL=https%3A//www.Zealty.ca/map.html' \
             '&kListClientURL=https%3A//www.zealty.ca/search.html&kStatsClientURL=https%3A//www.Zealty.ca/stats.html' \
             '&kStrataClientURL=https%3A//www.Zealty.ca/bc-strata-buildings.html&gParametersInit=&r=0' \
             '.42212563969816785 '
    getWebsite(zealty)
