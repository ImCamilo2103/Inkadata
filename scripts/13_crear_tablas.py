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

años = [2016, 2019, 2022]

dict_path = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/diccionarios/clasificacion_dict.csv'
departamentos = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/documentos/DIVIPOLA_Departamentos.xlsx'
codemp = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/documentos/EstructuraDetalladaCIIU_4AC.xls'

dpto = pd.read_excel(departamentos, skiprows=9)
ciiu = pd.read_excel(codemp, skiprows=2)
clasificacion = pd.read_csv(dict_path, low_memory=False)

sql = 'DROP TABLE IF EXISTS dpto CASCADE;'
cur.execute(sql)

sql = '''CREATE TABLE dpto(
    id SERIAL PRIMARY KEY,
    Codigo INTEGER,
    Nombre VARCHAR(64)
);'''
cur.execute(sql)
print('🪧 Tabla dpto creada con exito!')

sql = 'DROP TABLE IF EXISTS ciiu4 CASCADE;'
cur.execute(sql)

sql = '''CREATE TABLE ciiu4(
    id SERIAL PRIMARY KEY,     
    Clase VARCHAR(5),    
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
    eam = pd.read_sql(f'SELECT * FROM eam{año}_raw', conn)

    sql = f'DROP TABLE IF EXISTS empresas{año} CASCADE;'
    cur.execute(sql)

    sql = f'''
    CREATE TABLE empresas{año} (
        id SERIAL PRIMARY KEY,
        nordemp VARCHAR(7),
        nordest VARCHAR(7),
        dpto INTEGER REFERENCES dpto(id),
        ciiu4 INTEGER REFERENCES ciiu4(id),
        periodo INTEGER
    );'''
    cur.execute(sql)
    print(f'🗃️ Tabla empresas{año} creada!')

    for type in categoria:
        ntable = f"{type.lower().replace(' ', '_')}{año}"

        cur.execute(f'DROP TABLE IF EXISTS {ntable};')
        print(f"✖️ Tabla eliminada si existía: {ntable}")

        filclass = clasificacion[(clasificacion['año'] == año) & (clasificacion['categoria'] == type)]
        variables = filclass['variable'].tolist()
        excluir = ['nordemp', 'nordest', 'periodo', 'dpto', 'ciiu4']
        variables = [col.lower() for col in variables if col not in excluir]

        if 'empresas_id' not in variables:
            variables = ['empresas_id'] + variables

        if len(variables) == 0:
            print(f"No hay variables para crear tabla {ntable}, se omite.")
            continue
        
        bigintcol =[]
        for col, dtypes in eam.dtypes.items():
            if col.lower() in variables:
                if pd.api.types.is_integer_dtype(dtypes):
                    max = eam[col].max()
                    if max > 2147483647:
                        bigintcol.append(col.lower())

        print("\nVariables que NO son BIGINT:")
        integer = []
        for var in variables:
            if var not in bigintcol:
                integer.append(var)
        print(integer)

        print("\nVariables que SÍ son BIGINT:")
        bigint = []
        for var in variables:
            if var in bigintcol:
                bigint.append(var)
        print(bigint)

        colsql = []
        for var in integer:
            colsql.append(f'{var} INTEGER')

        for var in bigint:
            colsql.append(f'{var} BIGINT')

        schsql = ',\n'.join(colsql)

        sql = f'''CREATE TABLE {ntable}(
            id SERIAL PRIMARY KEY,
            {schsql},
            FOREIGN KEY(empresas_id) REFERENCES empresas{año}(id) ON DELETE CASCADE);'''
        cur.execute(sql)
        
        print(f'🗃️ Tabla {ntable} creada con éxito')

conn.commit()
cur.close()
conn.close()
print('✅ Proceso completado con éxito.')