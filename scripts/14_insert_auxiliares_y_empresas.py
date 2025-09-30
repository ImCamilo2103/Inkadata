import hidden
import pandas as pd
import psycopg2 as pg

secrets = hidden.secrets()

conn = pg.connect(
    host = secrets['host'],
    port = secrets['port'],
    database = secrets['database'],
    user = secrets['user'],
    password = secrets['pass']
)
cur = conn.cursor()

años = [2016, 2019, 2022]

departamentos = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/documentos/DIVIPOLA_Departamentos.xlsx'
codemp = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/documentos/EstructuraDetalladaCIIU_4AC.xls'

dpto = pd.read_excel(departamentos, skiprows=9, header=0)
ciiu = pd.read_excel(codemp, skiprows=2, header=0)

print('🪧 Inicia insercion de datos a la tabla dpto...')
dpto = dpto[dpto['Nombre'].notna()].copy()
dpto = dpto[~dpto['Nombre'].str.contains('fuente|nota|actualizado', case=False, na=False)]
dpto['Nombre'] = dpto['Nombre'].str.lower().str.strip()
dpto = dpto.astype({'Codigo': 'int', 'Nombre': 'str'})
dpto_records = list(dpto[['Codigo', 'Nombre']].itertuples(index=False, name=None))
sql = '''INSERT INTO dpto(
    Codigo_dpto, Nombre_dpto)
    values(%s, %s);'''
cur.executemany(sql, dpto_records)
print('✅ Tabla dpto insertada completamente.')

print('🪧 Inicia insercion de datos a la tabla ciiu4...')
ciiu = ciiu[ciiu['Clase'].notna()].copy()
ciiu['Clase'] = ciiu['Clase'].astype(int)
ciiu['Clase_str'] = ciiu['Clase'].astype(str).str.zfill(4)
ciiu_records = list(ciiu[['Clase_str', 'Descripcion']].itertuples(index=False, name=None))
sql = '''INSERT INTO ciiu4(
    Clase_ciiu,Descripcion_ciiu)
    values(%s, %s);'''
cur.executemany(sql, ciiu_records)
print('✅ Tabla ciiu4 insertada completamente.')

for año in años:
    print(f'🪧 Iniciamos con la insercion de datos tabla empresas{año}...')
    sql = f'''INSERT INTO empresas{año}(nordemp, periodo)
        SELECT DISTINCT
            e.nordemp,
            e.periodo
        FROM eam{año}_raw e;'''
    cur.execute(sql)
    print(f'🪧  → Datos insertados en empresas{año}.')

    print(f'🪧 Iniciamos con la insercion de datos tabla establecimiento{año}...')
    sql = f'''INSERT INTO establecimiento{año}(empresas_id, nordest, dpto_id, ciiu4_id)
        SELECT DISTINCT
            emp.id AS empresas_id,
            e.nordest,
            d.id AS dpto_id,
            c.id AS ciiu4_id
        FROM eam{año}_raw e
        JOIN empresas{año} emp ON emp.nordemp = e.nordemp
            AND emp.periodo = e.periodo
        JOIN dpto d ON d.codigo_dpto = e.dpto
        JOIN ciiu4 c ON c.clase_ciiu = e.ciiu4;'''
    cur.execute(sql)
    print(f'🪧  → Datos insertados en establecimiento{año}.')

conn.commit()
print('📦 Commit realizado exitosamente.')
cur.close()
conn.close()
print('✅ Conexión cerrada.')