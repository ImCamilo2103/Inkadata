import hidden
import pandas as pd
import psycopg2 as pg

secrets = hidden.secrets()

conn = pg.connect(
    host=secrets['host'],
    port=secrets['port'],
    database=secrets['database'],
    user=secrets['user'],
    password=secrets['pass']
)
cur = conn.cursor()

dict = '../Inkadata/diccionarios/clasificacion_dict.csv'
departamentos = '../Inkadata/documentos/DIVIPOLA_Departamentos.xlsx'
codemp = '../Inkadata/documentos/EstructuraDetalladaCIIU_4AC.xls'

dpto = pd.read_excel(departamentos, skiprows=9)
ciiu = pd.read_excel(codemp, skiprows=2)
clasificacion = pd.read_csv(dict, low_memory=False)

sql = 'DROP TABLE IF EXISTS dpto CASCADE;'
cur.execute(sql)

sql = '''CREATE TABLE dpto(
    id SERIAL PRIMARY KEY,
    Codigo INTEGER,
    Nombre VARCHAR(64),
    LATITUD DOUBLE PRECISION,
    LONGITUD DOUBLE PRECISION
);'''
cur.execute(sql)
print('🪧 Tabla dpto creada con exito!')

sql = 'DROP TABLE IF EXISTS ciiu4 CASCADE;'
cur.execute(sql)

sql = '''CREATE TABLE ciiu4(
    id SERIAL PRIMARY KEY,
    Seccion VARCHAR(5),
    Division VARCHAR(5),  
    Grupo VARCHAR(5),     
    Clase INTEGER,    
    Descripcion TEXT);'''
cur.execute(sql)
print('🪧 Tabla ciiu4 creada con exito!')

años = [2016, 2019, 2022]
ndict = {
    523: 2016,
    694: 2019,
    836: 2022
}
categoria = []

clasificacion['sid'] = clasificacion['sid'].astype(int)
clasificacion['año'] = clasificacion['sid'].map(ndict)

for uno in clasificacion['categoria']:
    if uno not in categoria:
        categoria.append(uno)

for año in años:
    print(f'🪧 Creando tablas para el año {año}...')

    sql = f'DROP TABLE IF EXISTS empresas{año} CASCADE;'
    cur.execute(sql)

    sql = f'''
    CREATE TABLE IF NOT EXISTS empresas{año} (
        nordemp INTEGER PRIMARY KEY,
        nordest INTEGER,
        dpto INTEGER REFERENCES dpto(id),
        ciiu4 INTEGER REFERENCES ciiu4(id),
        periodo INTEGER
    );
    '''
    cur.execute(sql)
    print(f'🗃️ Tabla empresas{año} creada!')

    for type_ in categoria:
        ntable = f"{type_.lower().replace(' ', '_')}_{año}"

        cur.execute(f'DROP TABLE IF EXISTS {ntable};')
        print(f"✖️ Tabla eliminada si existía: {ntable}")

        filclass = clasificacion[(clasificacion['año'] == año) & (clasificacion['categoria'] == type_)]
        variables = filclass['variable'].tolist()

        if 'nordemp' not in variables:
            variables = ['nordemp'] + variables

        if variables:
            columnas_unicas = []
            for col in variables:
                if col not in columnas_unicas:
                    columnas_unicas.append(col)

            colsql = ', '.join([f'"{col}" INTEGER' for col in columnas_unicas])

            sql_create = f'''
                CREATE TABLE {ntable} (
                id SERIAL PRIMARY KEY,
                {colsql},
                FOREIGN KEY (nordemp) REFERENCES empresas{año}(nordemp) ON DELETE CASCADE
            );
            '''
            cur.execute(sql_create)
            print(f'🗃️ Tabla {ntable} creada con éxito')
        else:
            print(f'⚠️ No hay columnas para {ntable}, no se crea tabla.')

conn.commit()
cur.close()
conn.close()