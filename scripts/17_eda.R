# ==============================================================================
# CONFIGURACIÓN INICIAL
# ==============================================================================

# Directorios para salidas
if (!dir.exists("C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/imagenes")) dir.create("imagenes")
if (!dir.exists("C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/tablas")) dir.create("tablas")

# Cargar paquetes
library(DBI)
library(corrplot)
library(dplyr)
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

eam2016 <- dbGetQuery(conn, "SELECT DISTINCT * FROM eam2016")
