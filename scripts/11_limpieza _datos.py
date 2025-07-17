import pandas as pd

años = [2016, 2019, 2022]

fraw = '../Inkadata/data/raw/EAM_{}.csv'
save = '../Inkadata/data/cleaned/eam{}.csv'

for año in años:
    print(f'\n🔁 Procesando archivo {año}...')
    sep_lectura = ';' if año in [2016, 2019] else ','

    eam = pd.read_csv(fraw.format(año), sep=sep_lectura, low_memory=False)

    for column, dtype in zip(eam.columns, eam.dtypes):
        if dtype == 'object':
            eam[column] = pd.to_numeric(eam[column], errors='coerce')
            nans = eam[column].isna().sum()
            if nans > 0:
                print(f'🪧 Columna {column} tiene {nans} NaN, reemplazando por 0')
                eam[column] = eam[column].fillna(0)
            eam[column] = eam[column].astype('int64')
            print(f'Columna {column} convertida a int64')

    eam.to_csv(save.format(año), sep=',', index=False)
    print(f'✅ Archivo limpio de {año} guardado correctamente.')