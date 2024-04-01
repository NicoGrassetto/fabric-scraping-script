import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/"
driver = webdriver.Firefox()
driver.get(url)

driver.maximize_window()
driver.execute_script("window.scrollTo(0, 500)")    
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "region-selector")))

select_element = driver.find_element(By.ID, "region-selector")
select = Select(select_element)

# Create a dataframe to hold the data from the table
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
tables = soup.find_all("table")
table = tables[1]
headers = table.find_all("th")
headers_text = [header.text for header in headers]
df = pd.DataFrame(columns=headers_text)
df["Region"] = ""

# This makes sure we select the euro currency for our prices
currency_select_element = driver.find_element(By.ID, "currency-selector")
currency_select = Select(currency_select_element)
currency_select.select_by_index(5)

# We iterate over the different regions
for idx_select, option in enumerate(select.options):
    select.select_by_index(idx_select)
    region_name = option.text
        
    # We get the data from the table
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    table = tables[1]
    rows = table.find_all("tr")
    rows_text = [[cell.text for cell in row.find_all("td")] for row in rows]
    
    # We create the pd series with the data + the region and add it to the df
    for row in rows_text[1:]:
        series = pd.Series(row, index=headers_text)
        series["Region"] = region_name
        df = pd.concat([df, pd.DataFrame([series])], ignore_index=True)

df.to_excel("onelake-storage.xlsx", index=False)
driver.quit()
