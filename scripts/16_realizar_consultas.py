import hidden
import pandas as pd
import psycopg2 as pg

secrets = hidden.secrets()

filedic = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/diccionarios/clasificacion_dict.csv'
filevar = 'C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/diccionarios/variable_utilizar.csv'
dicv = pd.read_csv(filedic)
vari = pd.read_csv(filevar, encoding='latin1', sep=",")

años = {
    523 : 2016,
    694 : 2019,
    836 : 2022
}

conn = pg.connect(
    host = secrets['host'],
    port = secrets['port'],
    database = secrets['database'],
    user = secrets['user'],
    password = secrets['pass']
)
cur = conn.cursor()

dicv['años'] = dicv['sid'].map(años).astype(str)
dicv['ntable'] = dicv['categoria'] + dicv['años']
dicv['ntable'] = dicv['ntable'].str.lower().str.replace(" ", "_")

hm = dicv[dicv['variable'].isin(vari['variable'])].copy()

table = []
year = []
alias = {}
variables = {
    'ntabla' : ['ciiu4', 'ciiu4', 'dpto', 'dpto'],
    'variable' : ['clase', 'descripcion', 'codigo', 'nombre'],
}

for año in hm['años']:
    if not año in year:
        year.append(año)

print('🕵🏻 estos son los años generados:', year)

for part in hm['ntable']:
    if not part in table:
        table.append(part)

print('📚 las tablas que se necesitan son', table)

joins ={
    'ntabla' : ['dpto', 'ciiu4'],
    'siglas' : ['dp', 'c4']
    }

for ann in year:
    eam = f'eam{ann}'

    sql = f'''DROP VIEW IF EXISTS {eam}'''
    cur.execute(sql)

    print(f'🆑 vista {eam}, eliminada con exito')

    for tab in table:
        if tab.endswith(str(ann)):
            if tab in hm['ntable'].values:
                joins['ntabla'].append(tab)
                joins['siglas'].append(tab[:2] + f'{ann}')
                variables['ntabla'].extend(hm[hm['ntable'] == tab]['ntable'].tolist())
                variables.setdefault('variable', []).extend(hm[hm['ntable'] == tab]['variable'].tolist())
                df_variables = pd.DataFrame(variables)
                dicc_siglas = dict(zip(joins['ntabla'], joins['siglas']))
                df_variables['siglas'] = df_variables['ntabla'].map(dicc_siglas)       

                df_variables = df_variables.sort_values(['ntabla', 'variable'])

for anio in year:
    eam = f'eam{anio}'
    cond_anio = df_variables['ntabla'].str.endswith(str(anio))
    df_year = df_variables[cond_anio].sort_values(['ntabla'])
    cols = ", ".join(df_year['siglas'] + "." + df_year['variable'])
    
    print(f"🪧 Inicia creacion de la vista: {eam}")
    
    sql = f'''CREATE VIEW {eam} AS
            SELECT
                e{anio}.nordemp,
                est{anio}.nordest,
                c4.descripcion_ciiu AS clase_ciiu,
                dp.nombre_dpto AS departamento,
                {cols}
            FROM establecimiento{anio} est{anio} 
            JOIN empresas{anio} e{anio} ON e{anio}.id = est{anio}.empresas_id
            JOIN dpto dp ON dp.id = est{anio}.dpto_id
            JOIN ciiu4 c4 ON c4.id = est{anio}.ciiu4_id
            LEFT JOIN activos{anio} ac{anio} ON ac{anio}.establecimiento_id = est{anio}.id
            LEFT JOIN otros{anio} ot{anio} ON ot{anio}.establecimiento_id = est{anio}.id
            LEFT JOIN producción{anio} pr{anio} ON pr{anio}.establecimiento_id = est{anio}.id
            LEFT JOIN sueldos_y_prestaciones{anio} su{anio} ON su{anio}.establecimiento_id = est{anio}.id
            LEFT JOIN temporal{anio} te{anio} ON te{anio}.establecimiento_id = est{anio}.id;'''
    cur.execute(sql)

    print(f"🪧 Se Crea exitosamente la vista {eam}")

conn.commit()
print('📦 Commit realizado exitosamente.')
cur.close()
conn.close()

print("🆑 Se cierra la conexion con exito")