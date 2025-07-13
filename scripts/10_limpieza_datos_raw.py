import pandas as pd

year = [2016, 2019, 2022]

for i in year:
    file = f'../Inkadata/data/raw/EAM_{i}.csv'

    eam = pd.read_csv(file,
                           sep=';',
                           low_memory=False,
                           na_values=[' ', '', 'NA', 'NaN', 'n/a', 'ND', '.', '-', '9999999'])

    columnas_con_nan = eam.columns[eam.isna().any()]

    nan_summary = eam[columnas_con_nan].isna().sum().reset_index()
    nan_summary.columns = ['columna', 'cantidad_nan']

    nan_summary['porcentaje_nan'] = (nan_summary['cantidad_nan'] / len(eam)) * 100

    print(f"\n📊 Año {i} | Total filas: {len(eam)}")
    print(nan_summary)

    nan_summary.to_csv(f'../Inkadata/data/processed/columnas_con_nan_{i}.csv', index=False, encoding='utf-8-sig')

    print(f"🪧 Se guardo el archivo columnas_con_nan_{i}.csv")