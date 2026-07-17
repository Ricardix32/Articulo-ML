from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import re
import os
import json
import sys

# Forzar salida en UTF-8 para evitar errores de caracteres y emojis en consola Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Riesgo Crediticio - Tesis",
    description="Motor de Inferencia y Servidor de Métricas/Reportes Científicos",
    version="2.0.0"
)

# Configurar CORS (Vital para que el frontend en React pueda comunicarse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se restringe a los dominios autorizados
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para el modelo y columnas de inferencia
modelo_produccion = None
columnas_requeridas = None
modelo_cargado = False

def cargar_modelo():
    """
    Intenta cargar el modelo de producción y su lista de columnas.
    Si no existen, permite que la API arranque y esperará al entrenamiento.
    """
    global modelo_produccion, columnas_requeridas, modelo_cargado
    try:
        modelo_path = 'modelo_riesgo_lgbm.pkl'
        columnas_path = 'columnas_modelo.pkl'
        
        if os.path.exists(modelo_path) and os.path.exists(columnas_path):
            modelo_produccion = joblib.load(modelo_path)
            columnas_requeridas = joblib.load(columnas_path)
            modelo_cargado = True
            print("✅ Artefactos de ML cargados exitosamente.")
        else:
            modelo_cargado = False
            print("⚠️ Advertencia: Archivos de modelo 'modelo_riesgo_lgbm.pkl' o 'columnas_modelo.pkl' no encontrados.")
            print("💡 Ejecute el script offline 'model_pipeline.py' para entrenar los modelos y generarlos.")
    except Exception as e:
        modelo_cargado = False
        print(f"⚠️ Error al cargar el modelo de producción: {e}")

# Intento inicial al importar el módulo
cargar_modelo()

# Definir la estructura de datos que enviará React (El formulario del asesor)
class ClienteCredito(BaseModel):
    edad_anios: int
    antiguedad_laboral_anios: float
    amt_income_total: float
    amt_credit: float
    amt_annuity: float
    calificacion_region_ciudad: int
    CODE_GENDER: str
    ORGANIZATION_TYPE: str
    NAME_EDUCATION_TYPE: str

# Montar directorio estático para servir imágenes (matriz de confusión, curvas roc) y documentos pregenerados
os.makedirs('static', exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    status_model = "Listo para inferencia" if modelo_cargado else "Requiere entrenamiento (Ejecute model_pipeline.py)"
    return {
        "mensaje": "API de Evaluación Crediticia - Capa de Inferencia Científica Activa.",
        "estado_modelo": status_model,
        "docs": "/docs"
    }

@app.post("/predict")
def predecir_riesgo(cliente: ClienteCredito):
    global modelo_produccion, columnas_requeridas, modelo_cargado
    
    # Intentar recargar el modelo si no estaba disponible previamente
    if not modelo_cargado:
        cargar_modelo()
        
    if not modelo_cargado:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El motor predictivo no está listo. Ejecute el script offline 'model_pipeline.py' primero para entrenar y guardar el modelo."
        )
        
    try:
        # 1. Convertir el JSON recibido a un DataFrame de Pandas
        data_dict = cliente.dict()
        
        # 2. Calcular los mismos ratios financieros calculados en el pipeline de entrenamiento
        ingreso = data_dict['amt_income_total']
        data_dict['credit_to_income_ratio'] = data_dict['amt_credit'] / ingreso if ingreso > 0 else 0
        data_dict['annuity_income_ratio'] = data_dict['amt_annuity'] / ingreso if ingreso > 0 else 0
        
        df_input = pd.DataFrame([data_dict])
        
        # 3. Aplicar One-Hot Encoding
        df_ohe = pd.get_dummies(df_input)
        
        # 4. Limpiar caracteres especiales de las columnas (XGBoost/LightGBM)
        df_ohe.columns = [re.sub(r'[{}":,\[\]]', '_', col) for col in df_ohe.columns]
        
        # Convertir variables booleanas a enteros 0/1
        bool_cols = df_ohe.select_dtypes(include=['bool']).columns
        for col in bool_cols:
            df_ohe[col] = df_ohe[col].astype(int)
            
        # 5. Alinear columnas con la estructura de entrenamiento (Rellenar con 0 lo faltante)
        df_inferencia = pd.DataFrame(columns=columnas_requeridas)
        for col in columnas_requeridas:
            if col in df_ohe.columns:
                df_inferencia[col] = df_ohe[col]
            else:
                df_inferencia[col] = 0
                
        # Asegurar tipo de datos int para columnas booleanas alineadas
        for col in df_inferencia.columns:
            if df_inferencia[col].dtype == 'bool':
                df_inferencia[col] = df_inferencia[col].astype(int)
                
        # 6. Inferencia probabilística
        prob_default = float(modelo_produccion.predict_proba(df_inferencia)[0][1] * 100)
        
        # 7. Dictamen del negocio
        estado = "APROBADO" if prob_default < 40.0 else "RECHAZADO"
        
        return {
            "estado": estado,
            "probabilidad_impago": round(prob_default, 2),
            "mensaje": f"El crédito ha sido {estado} por el motor de inferencia."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el motor predictivo: {str(e)}"
        )

@app.get("/dashboard/metrics")
def obtener_metricas_dashboard():
    """
    Devuelve las métricas comparativas del entrenamiento, validación cruzada y McNemar.
    Se leen directamente del archivo metrics.json generado de forma estática offline.
    """
    metrics_path = "static/metrics.json"
    if not os.path.exists(metrics_path):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Las métricas de evaluación no están disponibles aún. Ejecute el script offline 'model_pipeline.py'."
        )
    try:
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        return metrics_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar métricas: {str(e)}"
        )

@app.get("/dashboard/comparison")
def obtener_comparativa_escenarios():
    """
    Devuelve las métricas de comparación entre el Escenario Tradicional (A) y el Enriquecido (B).
    Se leen directamente del archivo scenario_comparison.json.
    """
    comparison_path = "static/scenario_comparison.json"
    if not os.path.exists(comparison_path):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Las métricas de comparación no están disponibles aún. Ejecute el script offline 'generate_comparison_json.py'."
        )
    try:
        with open(comparison_path, 'r', encoding='utf-8') as f:
            comp_data = json.load(f)
        return comp_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar métricas comparativas: {str(e)}"
        )

@app.get("/reports/download/{format_type}")
def descargar_reporte(format_type: str):
    """
    Permite descargar los reportes científicos generados por el motor offline.
    Formatos soportados: pdf, excel (xlsx), y word (docx).
    """
    fmt = format_type.lower()
    
    if fmt == "pdf":
        file_path = "static/reporte_riesgo.pdf"
        media = "application/pdf"
        filename = "reporte_riesgo_tesis.pdf"
    elif fmt in ["excel", "xlsx"]:
        file_path = "static/reporte_riesgo.xlsx"
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "reporte_riesgo_tesis.xlsx"
    elif fmt in ["word", "docx"]:
        file_path = "static/reporte_riesgo.docx"
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "reporte_riesgo_tesis.docx"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido. Formatos soportados: pdf, excel, y word."
        )
        
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El reporte en formato {format_type} no se encuentra disponible. Ejecute el script offline 'model_pipeline.py' para generarlo."
        )
        
    return FileResponse(path=file_path, media_type=media, filename=filename)