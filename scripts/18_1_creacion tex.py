# generar_tabla_latex.py
import pandas as pd

# Ajusta la ruta a tu archivo real
csv_path = r"C:\Users\Asus\Documents\data_analysis\Portafolio\Inkadata\tablas\medidas_tendencia.csv"
out_tex = r"C:\Users\Asus\Documents\data_analysis\Portafolio\Inkadata\tablas\medidas_tendencia_table_correct.tex"

# Leer manejando BOM y separador real (coma)
df = pd.read_csv(csv_path, sep=',', encoding='latin1', engine='python')

# Asegurar que la columna Año quede como texto limpio
if 'Año' in df.columns:
    df['Año'] = df['Año'].apply(lambda x: str(int(float(x))) if pd.notna(x) else x)

# Formato compacto para números largos
pd.options.display.float_format = '{:.6g}'.format

# Generar LaTeX escapando caracteres problemáticos
latex_snippet = df.to_latex(index=False, longtable=False, escape=True)

with open(out_tex, "w", encoding="utf-8") as f:
    f.write(latex_snippet)

print("Tabla LaTeX generada en:", out_tex)
