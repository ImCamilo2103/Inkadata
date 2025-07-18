import hidden
import pandas as pd
import psycopg2 as pg

secrets = hidden.secrets()

conn = pg.connect(
    host = secrets['host'],
    port = secrets['port'],
    database = secrets['database'],
    user = secrets['user'],
    password = secrets['pass'],
)
cur = conn.cursor()

años = [2016, 2019, 2022]
fdict = '../Inkadata/diccionarios/clasificacion_dict.csv'
clasificacion = pd.read_csv(fdict, low_memory=False)

adic = {523: 2016, 694:2019, 836:2022}
categoria = []

clasificacion['sid'] = clasificacion['sid'].astype(int)
clasificacion['año'] = clasificacion['sid'].map(adic)

for types in clasificacion['categoria']:
    if not types in categoria:
        categoria.append(types)

for año in años:
    print(f'🪧 Insertando datos en tablas para el año {año}...')

    eam = pd.read_sql(f"SELECT * FROM eam{año}_raw", conn)
    stable = f'eam{año}_raw'

    for type in categoria:
        ntable = f"{type.lower().replace(' ', '_')}{año}"

        filclass = clasificacion[(clasificacion['año'] == año) & (clasificacion['categoria'] == type)]
        variable = filclass['variable'].tolist()
        excluir = ['nordemp', 'nordest', 'periodo', 'dpto', 'ciiu4']
        variable = [col.lower() for col in variable if col not in excluir]

        if len(variable) == 0:
            print(f"⚡ No hay variables para crear tabla {ntable}, se omite.")
            continue

        if 'empresas_id' not in variable:
            variables = ['empresas_id'] + variable

        colsql = ', '.join(variables)
        colsqls = 'e.id, ' + ', '.join([f'er.{v}' for v in variable])
        

        sql = f'''INSERT INTO {ntable} ({colsql})
            SELECT {colsqls}
            FROM {stable} er
            JOIN empresas{año} e ON er.nordemp = e.nordemp'''
        cur.execute(sql)

conn.commit()
print('📦 Commit realizado exitosamente.')
cur.close()
conn.close()
print('✅ Conexión cerrada.')
print('✅ Proceso completado con éxito.')