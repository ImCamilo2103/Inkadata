import pandas as pd

años = [2016, 2019, 2022]

fraw = '../Inkadata/data/raw/EAM_{}.csv'
save = '../Inkadata/data/cleaned/eam{}.xlsx'

obj = ['nordemp', 'nordest', 'ciiu4']

for año in años:
    print(f'\n🔁 Procesando archivo {año}...')
    sep_lectura = ';' if año in [2016, 2019] else ','
    eam = pd.read_csv(fraw.format(año), sep=sep_lectura, low_memory=False)

    print(f'\n🔍 Revisión de valores nulos en el archivo {año}:')
    nulos_por_columna = eam.isna().sum()
    nulos_por_columna = nulos_por_columna[nulos_por_columna > 0]
    if not nulos_por_columna.empty:
        print(nulos_por_columna)
    else:
        print('✅ No hay valores nulos en este archivo.')

    for column, dtype in zip(eam.columns, eam.dtypes):
        if dtype == 'object' or dtype =='float64':
            eam[column] = pd.to_numeric(eam[column], errors='coerce')
            nans = eam[column].isna().sum()
            if nans > 0:
                print(f'🪧 Columna {column} tiene {nans} NaN, reemplazando por 0')
                eam[column] = eam[column].fillna(0)
                
            eam[column] = eam[column].astype('int64')
            print(f'Columna {column} convertida a int64')

    for col in obj:
        if col == 'ciiu4' and col in eam.columns:
            eam[col] = eam[col].astype(str).str.zfill(4)
            print(f'📎 Columna {col} convertida a str (object), con 4 letras')
        else:
            eam[col] = eam[col].astype(str)
            print(f'📎 Columna {col} convertida a str (object)')

    eam.to_excel(save.format(año), index=False)
    
    print(f'✅ Archivo limpio de {año} guardado correctamente.')