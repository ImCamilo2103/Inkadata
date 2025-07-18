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

departamentos = '../Inkadata/documentos/DIVIPOLA_Departamentos.xlsx'
codemp = '../Inkadata/documentos/EstructuraDetalladaCIIU_4AC.xls'

dpto = pd.read_excel(departamentos, skiprows=9, header=0)
ciiu = pd.read_excel(codemp, skiprows=2, header=0)

print('🪧 Inicia insercion de datos a la tabla dpto...')

dpto = dpto[dpto['Nombre'].notna()].copy()
dpto = dpto[~dpto['Nombre'].str.contains('fuente|nota|actualizado', case=False, na=False)]
dpto['Nombre'] = dpto['Nombre'].str.lower()

dpto = dpto.astype({
    'Codigo': 'int',
    'Nombre': 'str'
})

for idx, row in dpto.iterrows():
    placeholder = (row['Codigo'], row['Nombre'])
    print(placeholder)
    sql = '''INSERT INTO dpto(
        Codigo, Nombre)
        values(%s, %s);'''
    cur.execute(sql, placeholder)

print('✅ Tabla dpto insertada completamente.')
print('🪧 Inicia insercion de datos a la tabla ciiu4...')

ciiu = ciiu[ciiu['Clase'].notna()].copy()
ciiu['Clase'] = ciiu['Clase'].astype(int)
ciiu['Clase_str'] = ciiu['Clase'].astype(str).str.zfill(4)

for idx ,row in ciiu.iterrows():
    clase = row['Clase_str']
    descripcion = row['Descripcion']
    print((clase, descripcion))
    
    sql = '''INSERT INTO ciiu4(
    Clase, Descripcion)
    values(%s, %s);'''
    cur.execute(sql, (clase, descripcion))

print('✅ Tabla ciiu4 insertada completamente.')

for año in años:
    print(f'🪧 Iniciamos con la insercion de datos tabla empresas{año}...')

    sql = f'''INSERT INTO empresas{año}(nordemp, nordest, dpto, ciiu4, periodo)
        SELECT DISTINCT
            e.nordemp,
            e.nordest,
            d.id,
            c.id,
            e.periodo
        FROM eam{año}_raw e
        JOIN dpto d ON e.dpto = d.codigo
        JOIN ciiu4 c ON e.ciiu4 = c.clase;'''
    cur.execute(sql)

    print(f'   → Datos insertados en empresas{año}.')

conn.commit()
print('📦 Commit realizado exitosamente.')
cur.close()
conn.close()
print('✅ Conexión cerrada.')