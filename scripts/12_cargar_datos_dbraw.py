import hidden
import pandas as pd
import psycopg2 as pg

# Conexión a PostgreSQL
secrets = hidden.secrets()
conn = pg.connect(host=secrets['host'],
                  port=secrets['port'],
                  database=secrets['database'],
                  user=secrets['user'],
                  password=secrets['pass'])
cur = conn.cursor()

años = [2016, 2019, 2022]
feam = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/data/cleaned/eam{}.xlsx'

typemap = {
    'int64': 'BIGINT',
    'float64': 'FLOAT',
    'object': 'TEXT',
    'bool': 'BOOLEAN',
    'datetime64[ns]': 'TIMESTAMP',
}

for año in años:
    print(f'📚 Inicia el {año}...')

    eam = pd.read_excel(feam.format(año), dtype={'nordemp': str, 'nordest': str, 'ciiu4': str}, header=0)
    eam.columns =[col.lower() for col in eam.columns]
    team = f'eam{año}_raw'
    
    colsql = []
    for name, type in zip(eam.columns, eam.dtypes):
        dtpe = str(type)
        pgtype = typemap.get(dtpe, 'TEXT')
        colsql.append(f'{name} {pgtype}')
        
    print(f'🧱 Definición SQL para {team}:')
    print(',/n'.join(colsql))

    sql = f'DROP TABLE IF EXISTS {team} CASCADE;'
    cur.execute(sql)

    placeholder = ','.join(colsql)
    sql = f'''CREATE TABLE {team}(
        id SERIAL, {placeholder});'''
    cur.execute(sql)

    cols = ', '.join([f'{col}' for col in eam.columns])
        
    values = ', '.join(['%s'] * len(eam.columns))
    sql = f'''INSERT INTO {team}(
        {cols})
        VALUES({values})'''
    
    for row in eam.itertuples(index=False, name=None):
        cur.execute(sql, row)
    print(f'🪧 Tabla eam{año}_raw. Fue creada con exito!')

conn.commit()
cur.close()
conn.close()

print("✅ Todas las tablas fueron creadas y cargadas correctamente.")