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
    Codigo_dpto INTEGER NOT NULL,
    Nombre_dpto VARCHAR(64) NOT NULL,
    CONSTRAINT uq_dpto_codigo UNIQUE(codigo_dpto),
    CONSTRAINT uq_dpto_nombre UNIQUE(nombre_dpto)
    );

    COMMENT ON TABLE dpto IS 'Tabla de departamentos (administrativa)';
    COMMENT ON COLUMN dpto.codigo_dpto IS 'Código DANE del departamento';
    COMMENT ON COLUMN dpto.nombre_dpto IS 'Nombre oficial del departamento';'''
cur.execute(sql)
print('🪧 Tabla dpto creada con exito!')

sql = 'DROP TABLE IF EXISTS ciiu4 CASCADE;'
cur.execute(sql)

sql = '''CREATE TABLE ciiu4 (
    id SERIAL PRIMARY KEY,     
    Clase_ciiu VARCHAR(5) NOT NULL,    
    Descripcion_ciiu TEXT,
    CONSTRAINT uq_ciiu_clase UNIQUE(clase_ciiu)
    );
    
    COMMENT ON TABLE ciiu4 IS 'Tabla de códigos CIIU (clasificación industrial)';
    COMMENT ON COLUMN ciiu4.clase_ciiu IS 'Código CIIU de 5 caracteres';
    COMMENT ON COLUMN ciiu4.descripcion_ciiu IS 'Descripción de la clase CIIU';'''
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
        nordemp VARCHAR(7) NOT NULL,
        periodo INTEGER NOT NULL,
        CONSTRAINT uq_empresas_nordemp_dpto_periodo_{año} UNIQUE (nordemp)
    );'''
    cur.execute(sql)
    cur.execute(f"COMMENT ON TABLE empresas{año} IS 'Tabla de empresas por periodo'")
    cur.execute(f"COMMENT ON COLUMN empresas{año}.nordemp IS 'Código interno de la empresa'")
    print(f'🗃️ Tabla empresas{año} creada!')

    sql = f'''
    CREATE TABLE establecimiento{año} (
        id SERIAL PRIMARY KEY,
        empresas_id INTEGER NOT NULL,
        nordest VARCHAR(7) NOT NULL,
        dpto_id INTEGER NOT NULL,
        ciiu4_id INTEGER NOT NULL,
        CONSTRAINT fk_establecimeinto{año} FOREIGN KEY (empresas_id) REFERENCES empresas{año}(id) ON DELETE CASCADE,
        CONSTRAINT uq_establecimiento_nordest{año} UNIQUE(nordest)
    )'''
    cur.execute(sql)
    cur.execute(f"COMMENT ON TABLE establecimiento{año} IS 'Establecimientos asociados a empresas en el periodo {año}'")
    cur.execute(f"COMMENT ON COLUMN establecimiento{año}.nordest IS 'Código interno de establecimiento'")
    cur.execute(f"COMMENT ON COLUMN establecimiento{año}.dpto_id IS 'Departamento donde opera el establecimiento'")
    cur.execute(f"COMMENT ON COLUMN establecimiento{año}.ciiu4_id IS 'Código CIIU de la actividad'")

    for type in categoria:
        ntable = f"{type.lower().replace(' ', '_')}{año}"

        cur.execute(f'DROP TABLE IF EXISTS {ntable} CASCADE;')
        print(f"✖️ Tabla eliminada si existía: {ntable}")

        filclass = clasificacion[(clasificacion['año'] == año) & (clasificacion['categoria'] == type)]
        variables = filclass['variable'].tolist()
        excluir = ['nordemp', 'nordest', 'periodo', 'dpto', 'ciiu4']
        variables = [col.lower() for col in variables if col not in excluir]

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
            empresas_id INTEGER NOT NULL,
            establecimiento_id INTEGER NOT NULL,
            {schsql},
            CONSTRAINT fk_{ntable}_empresas FOREIGN KEY(empresas_id)
                REFERENCES empresas{año}(id) ON DELETE CASCADE,
            CONSTRAINT fk_{ntable}_establecimiento FOREIGN KEY(establecimiento_id)
                REFERENCES establecimiento{año}(id) ON DELETE CASCADE
            );
            COMMENT ON TABLE {ntable} IS 'Tabla de categoría {type} año {año}';'''
        cur.execute(sql)
        
        print(f'🗃️ Tabla {ntable} creada con éxito')

conn.commit()
cur.close()
conn.close()
print('✅ Proceso completado con éxito.')