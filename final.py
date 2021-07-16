from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import bs4
import pandas as pd
import re
import json
import numpy as np

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

url = 'https://www.fda.gov/news-events/fda-meetings-conferences-and-workshops/fda-meetings-conferences-and-workshops-past-events'

wd = webdriver.Chrome('chromedriver', options=options)
wd.get(url)

delay = 3
try:
    myElem = WebDriverWait(wd, delay).until(EC.presence_of_element_located((By.ID, 'DataTables_Table_0')))
    print("Page is ready!")
except TimeoutException:
    print("Loading took too much time!, Please try again.")

wd.find_element_by_xpath('//*[@id="DataTables_Table_0_length"]/label/select/option[5]').click()

html = wd.page_source
df = pd.read_html(html)
df = np.array(df, dtype=np.unicode_)
df = df.tolist()

data = []

html2 = bs4.BeautifulSoup(html, 'html.parser')
table = html2.find('table')

templinks = []
for a in table.find_all('a', href=True):
    templinks.append(a)

for i in range(len(df[0])):
    temp_info = {'Start Date:': df[0][i][0],
                 'End Date:': df[0][i][1],
                 'Event:': df[0][i][2],
                 'Event type:': df[0][i][3],
                 'Center': df[0][i][4],
                 }

    if i == 0:
        event_link = str(templinks[0])
        event_link = re.search('"(.*?)"', event_link).group(1)
        event_type_link = str(templinks[1])
        event_type_link = re.search('"(.*?)"', event_type_link).group(1)
        center_link = str(templinks[2])
        center_link = re.search('"(.*?)"', center_link).group(1)
    else:
        event_link = str(templinks[(i*3)])
        event_link = re.search('"(.*?)"', event_link).group(1)
        event_type_link = str(templinks[((i*3)+1)])
        event_type_link = re.search('"(.*?)"', event_type_link).group(1)
        center_link = str(templinks[((i*3)+2)])
        center_link = re.search('"(.*?)"', center_link).group(1)

    temp_link = {
        'Event': "https://www.fda.gov" + event_link,
        'Event_type:': "https://www.fda.gov" + event_type_link,
        'Center': "https://www.fda.gov" + center_link,
        }

    data.append(temp_info)
    data.append(temp_link)

with open('data.json', 'w') as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=0)
