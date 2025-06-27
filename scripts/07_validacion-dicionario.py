import pandas as pd

file = '../Inkadata/diccionarios/diccionarios.csv'

falt = []

df = pd.read_csv(file)
tvar = df['variable'].dtype
var_falt = df['variable'].value_counts()
for nom, cant in var_falt.items():
    if cant != 3:
        falt.append(nom)
var_fsid = df['sid'].value_counts()
print(f'🪧 Estos son los faltantes {falt}')