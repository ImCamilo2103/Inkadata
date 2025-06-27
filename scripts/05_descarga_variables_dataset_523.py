import os
import json
import requests

file = '../Inkadata/diccionarios/523'
os.makedirs(file, exist_ok=True)

for i in range(4344, 4734):
    url = f'https://microdatos.dane.gov.co/index.php/metadata/export_variable/523/V{i}/json'
    response = requests.get(url)
    if response.status_code ==200:
        print(f'📡 Conexion satisfactoria, {response.status_code}')
    else:
        print(f'✖️ NO hay conexion en {url}, el codigo es: {response.status_code}')

    print(f'⬇️ Inicia descarga del diccionario v{i}')
    data = response.json()
    name = data['name']

    with open(f'{file}/{name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'✅ Archivo {name}, guardado con exito!')