import os
import csv
import requests
from bs4 import BeautifulSoup

directory = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/web_scraping'
os.makedirs(directory, exist_ok=True)
count = 0

with open(f'{directory}/tags.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['name', 'link'])
    links = set()

    for i in range(1, 3):
        url = f'https://microdatos.dane.gov.co/index.php/catalog/?collection[]=Ind-Microdatos&page={i}'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        print(f"📡 esta es la respuesta: {response.status_code}")

        if response.status_code != 200:
            print(f"✖️ Error al obtener la pagina. Codigo: {response.status_code}")
            exit()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        tags = soup.find_all('a', href=True)

        for tag in tags:
            name = tag.get_text(strip=True) or "link sin texto"
            link = tag['href']

            if name.startswith('Encuesta Anual Manufacturera'):
                if link not in links:
                    if link.startswith('/'):
                        link = 'https://microdatos.dane.gov.co' + link

                    writer.writerow([name, link])
                    links.add(link)
                    count +=1
         
print(f"📖 Archivo creado con exito! Enlaces Unicos {count}")