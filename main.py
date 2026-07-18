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

# Variables globales para carga dual de modelos
modelo_enriquecido = None
columnas_enriquecidas = None
modelo_tradicional = None
columnas_tradicionales = None
modelos_cargados = False

# Variables de compatibilidad
modelo_produccion = None
columnas_requeridas = None
modelo_cargado = False

def cargar_modelo():
    """
    Carga simultáneamente los modelos Tradicional (A) y Enriquecido (B)
    junto con sus respectivas estructuras de columnas.
    """
    global modelo_enriquecido, columnas_enriquecidas
    global modelo_tradicional, columnas_tradicionales
    global modelos_cargados
    global modelo_produccion, columnas_requeridas, modelo_cargado
    
    try:
        path_enr_model = 'modelo_riesgo_lgbm.pkl'
        path_enr_cols = 'columnas_modelo.pkl'
        path_trad_model = 'modelo_riesgo_lgbm_2.pkl'
        path_trad_cols = 'columnas_modelo_2.pkl'
        
        if (os.path.exists(path_enr_model) and os.path.exists(path_enr_cols) and
            os.path.exists(path_trad_model) and os.path.exists(path_trad_cols)):
            
            modelo_enriquecido = joblib.load(path_enr_model)
            columnas_enriquecidas = joblib.load(path_enr_cols)
            
            modelo_tradicional = joblib.load(path_trad_model)
            columnas_tradicionales = joblib.load(path_trad_cols)
            
            # Compatibilidad
            modelo_produccion = modelo_enriquecido
            columnas_requeridas = columnas_enriquecidas
            modelo_cargado = True
            
            modelos_cargados = True
            print("✅ Carga Dual de Modelos completada (Tradicional y Enriquecido en memoria).")
        else:
            modelos_cargados = False
            modelo_cargado = False
            print("⚠️ Advertencia: Algunos archivos de modelos o columnas no fueron encontrados.")
            print("💡 Por favor, asegúrese de contar con: modelo_riesgo_lgbm.pkl, columnas_modelo.pkl, modelo_riesgo_lgbm_2.pkl, columnas_modelo_2.pkl.")
    except Exception as e:
        modelos_cargados = False
        modelo_cargado = False
        print(f"⚠️ Error en la carga dual de modelos: {e}")

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

@app.post("/predict_compare")
def predecir_riesgo_dual(cliente: ClienteCredito):
    global modelo_enriquecido, columnas_enriquecidas, modelo_tradicional, columnas_tradicionales, modelos_cargados
    
    if not modelos_cargados:
        cargar_modelo()
        
    if not modelos_cargados:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Los modelos predictivos no están listos. Ejecute el entrenamiento primero."
        )
        
    try:
        # A. PROCESAMIENTO MODELO ENRIQUECIDO (B)
        data_dict_enr = cliente.dict()
        ingreso = data_dict_enr['amt_income_total']
        data_dict_enr['credit_to_income_ratio'] = data_dict_enr['amt_credit'] / ingreso if ingreso > 0 else 0.0
        data_dict_enr['annuity_income_ratio'] = data_dict_enr['amt_annuity'] / ingreso if ingreso > 0 else 0.0
        
        df_input_enr = pd.DataFrame([data_dict_enr])
        df_ohe_enr = pd.get_dummies(df_input_enr)
        df_ohe_enr.columns = [re.sub(r'[{}":,\[\]]', '_', col) for col in df_ohe_enr.columns]
        
        # Convertir booleanas
        for col in df_ohe_enr.select_dtypes(include=['bool']).columns:
            df_ohe_enr[col] = df_ohe_enr[col].astype(int)
            
        df_inf_enr = pd.DataFrame(columns=columnas_enriquecidas)
        for col in columnas_enriquecidas:
            if col in df_ohe_enr.columns:
                df_inf_enr[col] = df_ohe_enr[col]
            else:
                df_inf_enr[col] = 0
                
        for col in df_inf_enr.columns:
            if df_inf_enr[col].dtype == 'bool':
                df_inf_enr[col] = df_inf_enr[col].astype(int)
                
        prob_enr = float(modelo_enriquecido.predict_proba(df_inf_enr)[0][1] * 100)
        estado_enr = "APROBADO" if prob_enr < 40.0 else "RECHAZADO"
        
        # B. PROCESAMIENTO MODELO TRADICIONAL (A)
        data_dict_trad = {
            'monto_credito_solicitado': cliente.amt_credit,
            'ingresos_totales_cliente': cliente.amt_income_total,
            'monto_anualidad_credito': cliente.amt_annuity,
            'ratio_credito_ingreso': cliente.amt_credit / ingreso if ingreso > 0 else 0.0,
            'ratio_anualidad_ingreso': cliente.amt_annuity / ingreso if ingreso > 0 else 0.0,
            'cantidad_hijos': 0,
            'genero_M': 1 if cliente.CODE_GENDER == 'M' else 0,
            'genero_XNA': 1 if cliente.CODE_GENDER == 'XNA' else 0,
            'nivel_educativo_Higher education': 1 if cliente.NAME_EDUCATION_TYPE == 'Higher education' else 0,
            'nivel_educativo_Incomplete higher': 1 if cliente.NAME_EDUCATION_TYPE == 'Incomplete higher' else 0,
            'nivel_educativo_Lower secondary': 1 if cliente.NAME_EDUCATION_TYPE == 'Lower secondary' else 0,
            'nivel_educativo_Secondary / secondary special': 1 if cliente.NAME_EDUCATION_TYPE == 'Secondary / secondary special' else 0,
            'estado_civil_Married': 0,
            'estado_civil_Separated': 0,
            'estado_civil_Single / not married': 0,
            'estado_civil_Unknown': 0,
            'estado_civil_Widow': 0
        }
        df_inf_trad = pd.DataFrame([data_dict_trad])
        df_inf_trad = df_inf_trad.reindex(columns=columnas_tradicionales, fill_value=0)
        
        prob_trad = float(modelo_tradicional.predict_proba(df_inf_trad)[0][1] * 100)
        estado_trad = "APROBADO" if prob_trad < 40.0 else "RECHAZADO"
        
        # Rescate comercial (tradicional rechaza pero enriquecido aprueba)
        rescate_comercial = bool(estado_trad == "RECHAZADO" and estado_enr == "APROBADO")
        
        return {
            "tradicional": {
                "probabilidad_impago": round(prob_trad, 2),
                "estado": estado_trad
            },
            "enriquecido": {
                "probabilidad_impago": round(prob_enr, 2),
                "estado": estado_enr
            },
            "rescate_comercial": rescate_comercial
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en inferencia comparativa: {str(e)}"
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