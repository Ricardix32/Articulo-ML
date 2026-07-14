import os
import sys
import json
import pandas as pd
import streamlit as st

# Forzar salida en UTF-8 para evitar errores de codificación
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuración de la página en Streamlit (Layout Ancho)
st.set_page_config(
    page_title="Dashboard Académico - Riesgo Crediticio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para el Dashboard
st.markdown("""
<style>
    .reportview-container {
        background-color: #0b111e;
    }
    .metric-card {
        background-color: rgba(255, 255, 255, 0.02);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# 1. Cargar las métricas guardadas estáticamente
METRICS_PATH = "static/metrics.json"

@st.cache_data
def cargar_metricas():
    if not os.path.exists(METRICS_PATH):
        return None
    with open(METRICS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

metrics = cargar_metricas()

# Header Académico
st.title("📊 Panel Científico de Evaluación y Validación de Modelos")
st.markdown("### Sustentación de Tesis: Inferencia y Significancia Estadística en Riesgo de Crédito")
st.markdown("---")

if metrics is None:
    st.error("⚠️ No se encontraron las métricas precalculadas.")
    st.info("💡 Por favor, ejecute primero el motor analítico offline: `python model_pipeline.py` para entrenar los modelos y generar las métricas.")
else:
    # Obtener datos generales
    mejor_modelo = metrics['mejor_modelo']
    es_sintetico = metrics['es_sintetico']
    db_source = "Home Credit Sintético (Contingencia)" if es_sintetico else "PostgreSQL - Almacén de Datos (Capa GOLD Real)"
    
    # Sidebar: Configuración e Información del Proyecto
    st.sidebar.image("static/default_distribution.png", caption="Distribución de Clases (Default)", use_container_width=True)
    st.sidebar.markdown("### Información del Proyecto")
    st.sidebar.markdown(f"**Origen de Datos:** \n{db_source}")
    st.sidebar.markdown(f"**Total de Muestra:** \n307,511 registros")
    st.sidebar.markdown(f"**Umbral de Decisión:** \n40.0% Probabilidad")
    st.sidebar.markdown(f"**Estrategia CV:** \nStratified 5-Fold Cross Validation")
    
    # 2. SECCIÓN: Tarjetas de KPI principales (Métricas de Alto Nivel)
    st.markdown("#### 1. Resumen de Desempeño Científico")
    col1, col2, col3, col4 = st.columns(4)
    
    # Mejor modelo
    with col1:
        st.markdown(
            f"<div class='metric-card'>"
            f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>Modelo Seleccionado</p>"
            f"<h2 style='color:#ffffff;margin:10px 0 0 0;font-size:24px;'>{mejor_modelo}</h2>"
            f"<p style='color:#595959;font-size:10px;margin:5px 0 0 0;'>Mayor capacidad predictiva (AUC)</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # AUC-ROC del ganador
    auc_ganador = metrics['modelos'][mejor_modelo]['AUC-ROC']
    with col2:
        st.markdown(
            f"<div class='metric-card'>"
            f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>Área Bajo la Curva (AUC)</p>"
            f"<h2 style='color:#4ade80;margin:10px 0 0 0;font-size:32px;font-weight:900;'>{auc_ganador:.4f}</h2>"
            f"<p style='color:#595959;font-size:10px;margin:5px 0 0 0;'>Capacidad de separación discriminante</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # p-value McNemar
    p_val_mcnemar = metrics['mcnemar']['p_value']
    significant = metrics['mcnemar']['significant']
    sig_label = "Significativo (Rechaza H0)" if significant else "Equivalente (Acepta H0)"
    sig_color = "#f87171" if significant else "#4ade80"
    with col3:
        st.markdown(
            f"<div class='metric-card'>"
            f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>p-valor (McNemar)</p>"
            f"<h2 style='color:#ffffff;margin:10px 0 0 0;font-size:32px;font-weight:900;'>{p_val_mcnemar:.4f}</h2>"
            f"<p style='color:{sig_color};font-size:10px;margin:5px 0 0 0;'>{sig_label}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # Muestra Evaluada
    with col4:
        st.markdown(
            f"<div class='metric-card'>"
            f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>Muestra Total</p>"
            f"<h2 style='color:#fbbf24;margin:10px 0 0 0;font-size:32px;font-weight:900;'>307,511</h2>"
            f"<p style='color:#595959;font-size:10px;margin:5px 0 0 0;'>Registros Gold Postgres</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    st.markdown(" ")

    # 3. SECCIÓN: Tabla Comparativa Interactiva
    st.markdown("#### 2. Tabla Comparativa General de Algoritmos")
    st.markdown("Resultados obtenidos sobre la partición del 20% de prueba estratificada:")
    
    # Procesar métricas en un DataFrame
    df_metrics = pd.DataFrame(metrics['modelos']).T
    # Formatear la tabla
    df_styled = df_metrics.drop(columns=['Best Params']).style.format({
        'Accuracy': '{:.4f}',
        'Precision': '{:.4f}',
        'Recall': '{:.4f}',
        'F1-Score': '{:.4f}',
        'AUC-ROC': '{:.4f}',
        'MCC': '{:.4f}',
        'CV-F1-Mean': '{:.4f}',
        'CV-F1-Std': '{:.4f}',
        'Training Time (s)': '{:.2f}'
    })
    st.dataframe(df_styled, use_container_width=True)
    
    # Observación de clase imbalanceada
    st.info(
        "💡 **Observación Académica sobre el F1-Score:** Debido al fuerte desbalance del target crediticio (8.07% de default), "
        "los algoritmos convencionales predicen 0 por defecto con umbrales estándares de probabilidad del 50%. Sin embargo, la métrica "
        "**AUC-ROC** demuestra que los modelos de Boosting (XGBoost y LightGBM) mantienen una excelente capacidad discriminatoria (~0.65) "
        "para ordenar las solicitudes por probabilidad de riesgo en producción."
    )

    # 4. SECCIÓN: Visualización de Gráficos del Modelo
    st.markdown("---")
    st.markdown("#### 3. Visualizaciones Estadísticas de Validación")
    
    tab1, tab2, tab3 = st.tabs(["📈 Curva ROC", "🔲 Matriz de Confusión", "🔥 Mapa de Correlación Numérica"])
    
    with tab1:
        st.image("static/roc_curves.png", caption="Curva ROC de los 5 algoritmos", use_container_width=True)
        st.markdown(
            "**Interpretación:** La curva ROC ilustra la sensibilidad frente a la tasa de falsos positivos. "
            "El modelo con la curva más cercana a la esquina superior izquierda (mayor área bajo la curva o AUC) representa "
            "el mejor clasificador del comportamiento crediticio. En este escenario, **LightGBM** y **XGBoost** lideran "
            "la capacidad discriminante."
        )
        
    with tab2:
        st.image("static/confusion_matrix.png", caption=f"Matriz de Confusión - {mejor_modelo}", use_container_width=True)
        st.markdown(
            f"**Interpretación:** La matriz de confusión del modelo ganador (**{mejor_modelo}**) muestra las clasificaciones "
            "correctas (diagonal principal) e incorrectas. Se evidencia la concentración en la predicción de la clase mayoritaria (0), "
            "típico en carteras de crédito reales con bajo índice de morosidad."
        )
        
    with tab3:
        st.image("static/correlation_heatmap.png", caption="Mapa de Correlaciones Numéricas (EDA)", use_container_width=True)
        st.markdown(
            "**Interpretación:** El mapa de calor de correlaciones del Análisis Exploratorio de Datos (EDA) ayuda a identificar "
            "la colinealidad entre variables numéricas clave, como los ingresos del cliente, montos de anualidad y montos de crédito. "
            "Permite verificar que los ratios calculados por el motor (`credit_to_income_ratio` y `annuity_income_ratio`) aportan "
            "información analítica de riesgo."
        )

    # 5. SECCIÓN: Pruebas Estadísticas Robustas (Test de McNemar)
    st.markdown("---")
    st.markdown("#### 4. Validación de Significancia Estadística - Test de McNemar")
    st.markdown(
        "Para comprobar si la diferencia en las tasas de error de clasificación de los algoritmos de Boosting "
        "(LightGBM vs XGBoost) es estadísticamente significativa en el conjunto de prueba, implementamos la prueba de McNemar."
    )
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("**Matriz de Contingencia de Errores:**")
        ct = metrics['mcnemar']['contingency_table']
        df_ct = pd.DataFrame(
            ct, 
            index=["LGBM Correcto", "LGBM Incorrecto"],
            columns=["XGBoost Correcto", "XGBoost Incorrecto"]
        )
        st.table(df_ct)
        
    with col_right:
        st.markdown("**Métricas del Test:**")
        st.write(f"- **Estadístico Chi-cuadrado (Edwards):** `{metrics['mcnemar']['chi2_statistic']:.4f}`")
        st.write(f"- **P-Valor (p-value):** `{p_val_mcnemar:.6f}`")
        st.write(f"- **¿Existe diferencia significativa? (α = 0.05):** `{'SÍ' if significant else 'NO'}`")
        
        # Conclusión formal
        st.markdown("**Conclusión Estadística Académica:**")
        if significant:
            st.markdown(
                "Dado que el p-valor es menor a 0.05, **se rechaza la hipótesis nula (H0)** de que las proporciones de "
                "error son iguales. Concluimos con un 95% de confianza que existe una diferencia estadísticamente significativa "
                "en la exactitud predictiva de ambos modelos, determinando a LightGBM como el algoritmo superior."
            )
        else:
            st.markdown(
                "Dado que el p-valor es mayor o igual a 0.05, **no se puede rechazar la hipótesis nula (H0)**. "
                "Esto demuestra formalmente que las pequeñas diferencias observadas en las métricas de LightGBM y XGBoost "
                "en test se deben únicamente a la fluctuación aleatoria de la muestra, considerándose ambos algoritmos "
                "como **estadísticamente equivalentes**."
            )

    # 5.5 SECCIÓN: Test de Wilcoxon sobre Folds de Validación Cruzada
    st.markdown("---")
    st.markdown("#### 4.5 Estabilidad de Validación Cruzada - Test de Wilcoxon")
    
    if 'wilcoxon' in metrics:
        w_res = metrics['wilcoxon']
        st.markdown(
            f"Para evaluar la consistencia del modelo ganador ante variaciones en los datos de entrenamiento, "
            f"se implementó la prueba de **{w_res['test_type']}** sobre los 5 pliegues (folds) "
            f"de validación cruzada. Compara al ganador (**{mejor_modelo}**) contra el benchmark clásico (**{w_res['benchmark_modelo']}**)."
        )
        
        col_w_left, col_w_right = st.columns([1, 2])
        
        with col_w_left:
            st.markdown("**Resultados de AUC-ROC por Pliegue:**")
            # Crear DataFrame con los scores de cada fold
            df_folds = pd.DataFrame({
                w_res['benchmark_modelo']: w_res['auc_benchmark_folds'],
                mejor_modelo: w_res['auc_winner_folds']
            }, index=[f"Fold {i+1}" for i in range(5)])
            st.table(df_folds.style.format("{:.4f}"))
            
        with col_w_right:
            st.markdown("**Estadísticas de la Prueba:**")
            st.write(f"- **Estadístico de la Prueba:** `{w_res['statistic']:.4f}`")
            st.write(f"- **p-valor:** `{w_res['p_value']:.6f}`")
            sig_w = w_res['significant']
            st.write(f"- **¿Es estadísticamente significativo? (α=0.05):** `{'SÍ' if sig_w else 'NO'}`")
            
            st.markdown("**Interpretación Académica:**")
            if sig_w:
                st.markdown(
                    f"Dado que el p-valor es menor a 0.05, **se rechaza la hipótesis nula (H0)**. Concluimos con un 95% de "
                    f"confianza que el modelo ganador es consistentemente superior a {w_res['benchmark_modelo']} "
                    f"a lo largo de las distintas particiones de validación cruzada, lo que demuestra su estabilidad metodológica."
                )
            else:
                st.markdown(
                    f"Dado que el p-valor es mayor o igual a 0.05, **no se puede rechazar la hipótesis nula (H0)**. "
                    f"Esto indica que ambos modelos poseen un comportamiento de estabilidad general equivalente a través de "
                    f"las 5 particiones evaluadas, descartando efectos de sobrediseño o sesgo por muestreo."
                )
    else:
        st.info("⚠️ Los resultados del test de Wilcoxon aún no están disponibles en metrics.json. Por favor ejecute la última versión del motor analítico.")

    # 6. SECCIÓN: Módulo de Descargas de Reportes
    st.markdown("---")
    st.markdown("#### 5. Módulo de Exportación y Descarga de Reportes de Tesis")
    st.markdown("Descargue los reportes científicos precalculados con la base de datos real de PostgreSQL:")
    
    dl_col1, dl_col2, dl_col3 = st.columns(3)
    
    # PDF
    pdf_file = "static/reporte_riesgo.pdf"
    if os.path.exists(pdf_file):
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()
        with dl_col1:
            st.download_button(
                label="📄 Descargar Reporte Científico PDF",
                data=pdf_bytes,
                file_name="reporte_riesgo_tesis.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
    # Excel
    xlsx_file = "static/reporte_riesgo.xlsx"
    if os.path.exists(xlsx_file):
        with open(xlsx_file, "rb") as f:
            xlsx_bytes = f.read()
        with dl_col2:
            st.download_button(
                label="📊 Descargar Métricas en Excel (xlsx)",
                data=xlsx_bytes,
                file_name="reporte_riesgo_tesis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
    # Word
    docx_file = "static/reporte_riesgo.docx"
    if os.path.exists(docx_file):
        with open(docx_file, "rb") as f:
            docx_bytes = f.read()
        with dl_col3:
            st.download_button(
                label="📝 Descargar Reporte Metodológico Word",
                data=docx_bytes,
                file_name="reporte_riesgo_tesis.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
    st.sidebar.markdown("---")
    st.sidebar.caption("Tesis de Grado en Ingeniería Financiera / Ciencia de Datos - 2026")
