# ==============================================================================
# CONFIGURACIÓN INICIAL
# ==============================================================================

# Directorios para salidas
outdir_imgs <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/imagenes/eda"
if (!dir.exists(outdir_imgs)) dir.create(outdir_imgs, recursive = TRUE)

outdir_tablas <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/tablas"
if (!dir.exists(outdir_tablas)) dir.create(outdir_tablas, recursive = TRUE)

outdir_processed <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/data/processed"
if (!dir.exists(outdir_processed)) dir.create(outdir_processed, recursive = TRUE)

# Cargar paquetes
library(DBI)
library(dplyr)
library(e1071)
library(ggplot2)
library(glue)
library(readxl)
library(RPostgres)
library(tidyr)

# Paleta de colores Inkadata
inkadatacolors <- c("#003f5c", "#f9a602", "#2f855a", "#f4f4f4", "#1a202c", "#58508d", "#bc5090", "#ff6361", "#ffa600")

# Función para guardar gráficos
save_plot <- function(plotobj, fname, ancho = 10, alto = 8){
  rutacompleta <- file.path(outdir_imgs, fname)
  ggsave(rutacompleta, plot = plotobj, width = ancho, height = alto, dpi = 300)
  cat("Gráfico guardado en:", rutacompleta, "\n")
}

#=====================================================================
#   CONEXIÓN A BASE DE DATOS
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
  message("✅ Conexión exitosa con la base de datos")
}, error = function(e){
  stop(paste("❌ Error en conexión: ", e$message))
})

#=====================================================================
#    CARGA DE DATOS Y MEDIDAS DESCRIPTIVAS
#=====================================================================
años <- c(2016, 2019, 2022)
var_file <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/diccionarios/variable_utilizar.csv"

variable_df <- read.csv(var_file, fileEncoding = "latin1")
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

for (año in años) {
  vista <- glue("eam{año}")
  cat("📥 Leyendo Vista:", vista, "\n")
  df <- dbGetQuery(conn, glue("SELECT * FROM {vista}"))
  assign(vista, df, envir = .GlobalEnv)
  
  # Guardar CSV
  write.csv(df, file.path(outdir_processed, paste0(vista, ".csv")), row.names = FALSE, fileEncoding = "Latin1")
  
  df_actual <- get(vista)
  
  # Calcular métricas descriptivas
  for (var in variables_a_analizar) {
    if (var %in% colnames(df_actual)) {
      datos <- as.numeric(df_actual[[var]])
      datos_validos <- datos[!is.na(datos)]
      if(length(datos_validos) < 2) next
      
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

write.csv(r_metrica, file.path(outdir_tablas, "medidas_tendencia.csv"), row.names = FALSE, fileEncoding = "latin1")
cat("✅ Métricas descriptivas guardadas.\n")

# ==============================================================================
# ANALISIS 2: GRAFICOS EXPLORATORIOS (EDA) PARA CADA VARIABLE
# ==============================================================================
outdir_imgs <- "C:/Users/Asus/Documents/data_analysis/portafolio/Inkadata/imagenes/eda"
if(!dir.exists(outdir_imgs)) dir.create(outdir_imgs, recursive = TRUE)

for (año in años) {
  nombre_df <- paste0("eam", año)
  
  if (!exists(nombre_df) || !is.data.frame(get(nombre_df))){
    cat(paste("✖️ ERROR CRÍTICO: La variable", nombre_df, "no existe o no es un DataFrame.\n"))
    next
  }
  
  df_actual <- get(nombre_df)
  
  cat("\n📊 Generando gráficos violin + boxplot + regresión para el año:", año, "\n")
  
  for (var in variables_a_analizar) {
    if (var %in% colnames(df_actual)) {
      datos <- as.numeric(df_actual[[var]])
      datos_validos <- datos[!is.na(datos)]
      
      if(length(datos_validos) < 2) next  # evitar variables con muy pocos datos
      
      df_plot <- data.frame(Valor = datos_validos)
      
      # -------------------------------------------------------------
      # Violin + Boxplot + Regresión (si aplica)
      # -------------------------------------------------------------
      p_violin <- ggplot(df_plot, aes(x = "", y = Valor)) +
        geom_violin(fill = inkadatacolors[2], color = inkadatacolors[1], alpha = 0.5, scale = "width") +
        geom_boxplot(width = 0.1, fill = inkadatacolors[3], color = "black", outlier.colour = "red", outlier.shape = 16) +
        geom_smooth(aes(x = 1, y = Valor), method = "loess", color = inkadatacolors[1], se = TRUE, linetype = "dashed") +
        labs(title = glue("Distribución y tendencia - {var} ({año})"),
             x = "",
             y = var) +
        theme_minimal(base_size = 14) +
        theme(panel.background = element_rect(fill = "#f4f4f4"),
              plot.background = element_rect(fill = "#f4f4f4"),
              text = element_text(color = "black"))
      
      # Guardar gráfico
      ggsave(filename = file.path(outdir_imgs, glue("violin_{var}_{año}.png")), plot = p_violin, width = 10, height = 8, dpi = 300)
      
      cat(glue("✅ Gráfico violin generado para {var} ({año})\n"))
    }
  }
}

message("✅ Todos los gráficos violin + boxplot + regresión generados y guardados.")


# Cerrar conexión
dbDisconnect(conn)
message("✅ Conexión cerrada y proceso EDA completado")