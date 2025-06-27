import os
import csv
import requests

cvsfile = '../Inkadata/web_scraping/descarga_microdatos.csv'
ddirectory = '../Inkadata/data/raw'

with open(cvsfile, 'r', encoding='utf-8') as r:
    reader = csv.DictReader(r)
    reader.fieldnames = [col.strip().replace('\ufeff', '') for col in reader.fieldnames]
    
    for row in reader:
        name = row['name']
        url = row['link']

        print(f'⬇️ Descargando {name} desde la url: {url}')

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(ddirectory, name), 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)
            print(f'✅ Guardado como: {name}')
        
        else:
            print(f'✖️ Fallo la descraga: {response.status_code} - {url}')