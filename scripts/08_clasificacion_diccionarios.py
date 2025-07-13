import os
import pandas as pd

# Rutas de archivos
fdiccionarios = '../Inkadata/diccionarios/diccionarios.csv'
ftiposdict = '../Inkadata/diccionarios/clasificacion_dict.csv'

df = pd.read_csv(fdiccionarios)

def clasificar_labl(texto):
    texto = str(texto).lower()  
    if 'salario integral' in texto:
        return 'Salario Integral'
    elif 'temporal' in texto:
        return 'Temporal'
    elif 'producción' in texto:
        return 'Producción'
    elif 'administración' in texto or 'administrativos' in texto:
        return 'Administración'
    elif 'activo' in texto:
        return 'Activos'
    elif any(p in texto for p in ['prestaciones', 'salario', 'sueldos', 'remuneración']):
        return 'Sueldos y Prestaciones'
    elif any(p in texto for p in ['energía', 'bagazo', 'combustible', 'carbón', 'diésel', 'gas']):
        return 'Energéticos'
    elif 'impuesto' in texto:
        return 'Impuestos'
    elif any(p in texto for p in ['servicios', 'honorarios', 'comunicaciones', 'publicidad']):
        return 'Servicios contratados'
    else:
        return 'Otros'

df['categoria'] = df['labl'].apply(clasificar_labl)

df[['sid', 'variable', 'labl', 'categoria']].to_csv(ftiposdict, index=False, encoding='utf-8-sig')

print('✅ Archivo clasificado guardado como clasificacion_dict.csv con éxito.')