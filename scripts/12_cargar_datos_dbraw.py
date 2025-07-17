import hidden
import pandas as pd
import psycopg2 as pg

secrets = hidden.secrets()
conn = pg.connect(host = secrets['host'],
                  port = secrets['port'],
                  database = secrets['database'],
                  user = secrets['user'],
                  password = secrets['pass'])
cur = conn.cursor()

años = [2016, 2019, 2022]
feam = '../Inkadata/data/cleaned/eam{}.csv'

typemap = {
    'int64': 'BIGINT',
    'float64': 'FLOAT',
    'object': 'TEXT'
}

for año in años:
    print(f'📚 Inicia el {año}...')
    eam = pd.read_csv(feam.format(año), low_memory=False, header=0)

    columnasql = []
    for name, type in zip(eam.columns, eam.dtypes):
        dtype_str = str(type)
        pg_type = typemap.get(dtype_str, 'TEXT')
        columnasql.append(F'"{name}" {pg_type}')
        
    print(f'🧱 Definición SQL para eam{año}:')
    print(',\n'.join(columnasql))

    sql = f'DROP TABLE IF EXISTS eam{año}_raw;'
    cur.execute(sql)

    columnastr = ', '.join(columnasql)
    sql = f'CREATE TABLE eam{año}_raw(id SERIAL, {columnastr});'
    cur.execute(sql)

    cols = ', '.join([f'"{col}"' for col in eam.columns])
    values = ', '.join(['%s'] *len(eam.columns))
    sql = f'INSERT INTO eam{año}_raw({cols}) VALUES ({values})'

    for row in eam.itertuples(index=False, name=None):
        cur.execute(sql, row)

    print(f'🪧 Tabla eam{año}_raw. Fue creada con exito!')

conn.commit()
cur.close()
conn.close()

print("✅ Todas las tablas fueron creadas y cargadas correctamente.")