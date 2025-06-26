import os
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from time import sleep

directory = '../Inkadata/web_scraping'
serv = '../Inkadata/scripts/geckodriver.exe'
service = Service(serv)
driver = webdriver.Firefox(service=service)
enlace = []


for file in os.listdir(directory):
    if file.endswith('.csv') and file != 'tags.csv':
        df = pd.read_csv(f'{directory}/{file}')
        links = df.loc[df['name'] == 'Obtener Microdatos', ['name', 'link']]
        enl = links['link'].to_list()
        enlace.append(enl)

print(f'🪧 estos es la cantidad de enlaces obtenidos: {len(enlace)}')
print(enlace)

downloader = []
names = ['EAM2016', 'EAM2019', 'EAM2020']

with open(f'{directory}/descarga_microdatos.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'link'])

    for sublink in enlace:
        for link in sublink:
            driver.get(link)
            sleep(3)
            boton = driver.find_element(By.XPATH, '//input[contains(@onclick, "download")]')
            onclick = boton.get_attribute('onclick')

            parts = onclick.split(',')
            file = parts[0].split('(')[1].strip(" '\"")
            url = parts[1].strip(" '\" );")
        
            writer.writerow([file, url])

driver.quit()