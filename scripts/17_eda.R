# ==============================================================================
# CONFIGURACIÓN INICIAL
# ==============================================================================

# Directorios para salidas
if (!dir.exists("C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/imagenes")) dir.create("imagenes")
if (!dir.exists("C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/tablas")) dir.create("tablas")
if (!dir.exists("C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/data/processed")) dir.create("processed")

# Cargar paquetes
library(DBI)
library(corrplot)
library(dplyr)
library(e1071)
library(ggplot2)
library(glue)
library(kableExtra)
library(readxl)
library(RPostgres)
library(scales)
library(stringr)
library(tidyr)

# Paleta de colores Vulcan Forge
inkadatacolors <- c("#003f5c", "#f9a602", "#2f855a", "#f4f4f4", "#1a202c", "#58508d", "#bc5090", "#ff6361", "#ffa600")
save <- function(plotobj = NULL, fname, ancho = 10, alto = 8){
          rutacompleta <- file.path("grafico_eda", fname)
        
            if(is.null(plotobj)){
              ggsave(rutacompleta, width = ancho, height = alto, dpi = 300)
            } else {
              ggsave(rutacompleta, plot = plotobj, width = ancho, height = alto, dpi = 300)
            }
          
          cat("Gráfico guardado en:", rutacompleta, "\n")
}

fdic <- "C:/Users/Asus/Documents/data_analysis/Portafolio/Inkadata/diccionarios/clasificacion_dict.csv"

#=====================================================================
#   CONEXION BASE DE DATOS
#=====================================================================

source("hidden.R")
cred <- secrets()

tryCatch({
  conn <- dbConnect(
    Postgres(),
    host = cred$host,
    port = cred$port,
    dbname = cred$database,
    user = cred$user,
    password = cred$pass 
  )
  message("✅  Conexion exitosa con la base de datos")
  }, error = function(e){
    message(paste("❌ Error en conexión: ", e$message))
  })

#=====================================================================
#    ANALISIS 1: MEDIDAS DE TENDENCIA Y DISPERCION.
#=====================================================================
años <- c(2016, 2019, 2022)

outdir <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/data/processed"

for (año in años) {
  vista <- glue::glue("eam{año}")
  cat("📥 Leyendo Vista:", vista, "\n")
  
  df <- dbGetQuery(conn, glue("SELECT * FROM {vista}"))
  assign(vista, df, envir = .GlobalEnv)
  
  csv_path <- file.path(outdir, paste0(vista, ".csv"))
  write.csv(df, csv_path, row.names = FALSE, fileEncoding = "Latin1")
  cat("✅ Vista guardada como CSV:", csv_path, "\n")
}

var_file <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/diccionarios/variables_estadisticas.csv"
outdir_tablas <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/tablas"

variable_df <- read.csv(var_file, fileEncoding = "Latin1", sep = ";")
variables_a_analizar <- variable_df$variable

r_metrica <- data.frame(
  Año = character(),
  Variable = character(),
  Media = numeric(),
  Mediana = numeric(),
  Cuartil_Q1 = numeric(),
  Cuartil_Q3 = numeric(),
  Rango = numeric(),
  Desviacion_Estandar = numeric(),
  Varianza = numeric(),
  Coeficiente_Variacion = numeric(),
  Asimetria = numeric(),
  Curtosis = numeric()
)
cat("🪧 \nniciando cálculo de medidas descriptivas completas......\n")

for (año in años) {
  nombre_df <- paste0("eam", año)
  
  if (!exists(nombre_df) || !is.data.frame(get(nombre_df))){
    cat(paste("✖️ ERROR CRÍTICO: La variable", nombre_df, "no existe o no es un DataFrame.\n"))
    next
  }
  
  df_actual <- get(nombre_df)
  cat("📊 Procesando datos para el año:", año, "\n")
  
  for (var in variables_a_analizar) {
    if (var %in% colnames(df_actual)) {
      datos <- as.numeric(df_actual[[var]])
      datos_validos <- datos[!is.na(datos)]
      
      if (length(datos_validos) > 1){
        media <- mean(datos_validos)
        mediana <- median(datos_validos)
        
        desv_estandar <- sd(datos_validos)
        varianza <- var(datos_validos)
        
        cuartiles <- quantile(datos_validos, probs = c(0.25, 0.75))
        rango_val <- max(datos_validos) - min(datos_validos)
        
        cv <- (desv_estandar / media) * 100
        asimetria_val <- skewness(datos_validos, type = 2)
        curtosis_val <- kurtosis(datos_validos, type = 2)
        
        nueva_fila <- data.frame(
          Año = as.character(año),
          Variable = var,
          Media = media,
          Mediana = mediana,
          Cuartil_Q1 = cuartiles[1],
          Cuartil_Q3 = cuartiles[2],
          Rango = rango_val,
          Desviacion_Estandar = desv_estandar,
          Varianza = varianza,
          Coeficiente_Variacion = cv,
          Asimetria = asimetria_val,
          Curtosis = curtosis_val
        )
        
        r_metrica <- rbind(r_metrica, nueva_fila)
      }
    }
  }
}

tabla_path <- file.path(outdir_tablas, "medidas_tendencia_dispersion_final.csv")
write.csv(r_metrica, tabla_path, row.names = FALSE, quote =  FALSE, fileEncoding = "Latin1")
cat(paste("\n✅ Proceso de métricas descriptivas completo. Tabla guardada en:", tabla_path, "\n"))

dbDisconnect(conn)
message("✅ Se cerro la conexion a la base de datos")