import os
import csv
import json

files = '../Inkadata/diccionarios'

with open(os.path.join(files, 'diccionarios.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['sid', 'survey_idno', 'variable', '#_variable', 'var_dcml', 'loc_width', 'labl', 'var_security',  'var_universe_clusion','var_qstn_qstnlit',  'var_universe', 'var_sumstat_0', 'var_sumstat_type_0', 'var_sumstat_1', 'var_sumstat_type_1', 'var_format_type', 'var_val_range_min', 'var_val_range_max'])

    for file in os.listdir(files):
        path = os.path.join(files, file)
        if os.path.isdir(path):
            print(f'📖 Iniciamos con la carpeta {file}')
        
            for arc in os.listdir(os.path.join(files, file)):
                with open(os.path.join(files, file, arc), 'r', encoding='utf-8-sig') as r:
                    reader = json.load(r)
                
                    sid = reader['sid']
                    survey_idno = reader['survey_idno']
                    variable = reader['name']
                    n_variable = reader['vid']
                    var_dcml = reader['var_dcml']
                    loc_width = reader['loc_width']
                    labl = reader['labl']
                    var_security = reader['var_security']
                    var_qstn_qstnlit = reader['var_qstn_qstnlit']
                    var_universe = reader['var_universe']
                    var_universe_clusion = reader['var_universe_clusion']
                    var_sumstat = reader['var_sumstat'][0]['value']
                    var_sumstat_type_0 = reader['var_sumstat'][0]['type']
                    var_sumstat_1 = reader['var_sumstat'][1]['value']
                    var_sumstat_type_1 = reader['var_sumstat'][1]['type']
                    var_format_type = reader['var_format']['type']
                    var_val_range_min = reader['var_val_range']['min']
                    var_val_range_max = reader['var_val_range']['max']

                    writer.writerow([sid, survey_idno, variable, n_variable, var_dcml, loc_width, labl, var_security,  var_qstn_qstnlit,  var_universe,  var_universe_clusion, var_sumstat, var_sumstat_type_0, var_sumstat_1, var_sumstat_type_1, var_format_type, var_val_range_min, var_val_range_max])

print(f'✅ Se creo el archivo diccionarios.csv con exito!')