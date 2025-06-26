import os
import csv
import requests
from bs4 import BeautifulSoup

directory = '../Inkadata/web_scraping/tags.csv'
fdirectory = '../Inkadata/web_scraping'
titles = []
links = []
count = 0


with open(directory, 'r', encoding='utf-8') as file:
    for row in file:
        if any(año in row for año in['2016', '2019', '2022']):
            nombre = row.rsplit(',')
            names = nombre[0].rstrip()
            tag = nombre[1].rstrip()
            titles.append(names)
            links.append(tag)

for title, url in zip(titles, links):
    response = requests.get(url)
    print(f'📡 La respuesta es {response.status_code}, para la URL: {url}')

    if response.status_code != 200:
        print(f'✖️ La respuesta no es sactifactoria, la respues es{response.status_code}, Para la URL: {url}')

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('a', href=True)

    with open(f'{fdirectory}/{title}.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'link'])

        for tag in tags:
            nom = tag.get_text(strip=True)
            link = tag['href']
            writer.writerow([nom, link])
            count += 1
        print(f'✅ Links guardados en {title}')
            