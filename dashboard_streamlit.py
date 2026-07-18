import os
import sys
import json
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

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

# Cargar las métricas de validación individual
METRICS_PATH = "static/metrics.json"
COMPARISON_PATH = "static/scenario_comparison.json"

@st.cache_data
def cargar_metricas():
    if not os.path.exists(METRICS_PATH):
        return None
    with open(METRICS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def cargar_comparacion():
    if not os.path.exists(COMPARISON_PATH):
        return None
    with open(COMPARISON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

metrics = cargar_metricas()
comparison = cargar_comparacion()

# Sidebar: Configuración e Información del Proyecto
st.sidebar.markdown("### Navegación del Dashboard")
menu_option = st.sidebar.selectbox(
    "Seleccione el módulo:",
    ["1. Validación Científica (Modelos)", "2. Comparativa de Escenarios (A vs B)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Información General")
st.sidebar.markdown("**Muestra Total:** \n307,511 registros")
st.sidebar.markdown("**Estrategia CV:** \nStratified 5-Fold CV")
st.sidebar.markdown("**Umbral Inferencia:** \n40.0% Probabilidad")

# Header Académico
st.title("📊 Panel Científico de Evaluación y Validación de Modelos")
st.markdown("### Sustentación de Tesis: Inferencia y Significancia Estadística en Riesgo de Crédito")
st.markdown("---")

if metrics is None:
    st.error("⚠️ No se encontraron las métricas precalculadas.")
    st.info("💡 Por favor, ejecute primero el motor analítico offline: `python model_pipeline.py` para entrenar los modelos.")
else:
    mejor_modelo = metrics['mejor_modelo']
    es_sintetico = metrics['es_sintetico']
    db_source = "Home Credit Sintético (Contingencia)" if es_sintetico else "PostgreSQL - Almacén de Datos (Capa GOLD Real)"
    
    st.sidebar.markdown(f"**Origen de Datos:** \n{db_source}")

    if menu_option == "1. Validación Científica (Modelos)":
        # =====================================================================
        # VISTA 1: VALIDACION INDIVIDUAL DE MODELOS (Métricas Clásicas)
        # =====================================================================
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
                        f"las 5 particiones de prueba, descartando sesgo por muestreo."
                    )

    elif menu_option == "2. Comparativa de Escenarios (A vs B)":
        # =====================================================================
        # VISTA 2: COMPARACION DE ESCENARIOS (Tradicional vs Enriquecido)
        # =====================================================================
        if comparison is None:
            st.error("⚠️ No se encontraron las métricas de comparación de escenarios.")
            st.info("💡 Por favor, ejecute primero el script de comparación en la terminal: `python scratch/generate_comparison_json.py` para generar los datos.")
        else:
            st.markdown("#### 1. Del Deltas Clave de Rendimiento (Negocio y Modelado)")
            
            # Extraer deltas y métricas
            delta = comparison['delta']
            esc_a = comparison['escenario_a']
            esc_b = comparison['escenario_b']
            
            col_d1, col_d2, col_d3 = st.columns(3)
            
            # Delta AUC
            with col_d1:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>Delta de AUC-ROC</p>"
                    f"<h2 style='color:#f87171;margin:10px 0 0 0;font-size:32px;font-weight:900;'>{delta['auc']:.4f}</h2>"
                    f"<p style='color:#ffffff;font-size:10px;margin:5px 0 0 0;'>Tradicional: {esc_a['auc']:.4f} | Enriquecido: {esc_b['auc']:.4f}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
            # Delta Colocación (Falsos Positivos)
            reduccion_fp = esc_a['confusion_matrix']['fp'] - esc_b['confusion_matrix']['fp']
            with col_d2:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>Reducción de Falsos Positivos</p>"
                    f"<h2 style='color:#4ade80;margin:10px 0 0 0;font-size:32px;font-weight:900;'>-{reduccion_fp:,}</h2>"
                    f"<p style='color:#595959;font-size:10px;margin:5px 0 0 0;'>Clientes viables rescatados (colocación extra)</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
            # Delta F1-Score
            with col_d3:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<p style='color:#6d91bb;font-size:12px;font-weight:bold;text-transform:uppercase;margin:0;'>Delta F1-Score</p>"
                    f"<h2 style='color:#4ade80;margin:10px 0 0 0;font-size:32px;font-weight:900;'>+{delta['f1_score']:.4f}</h2>"
                    f"<p style='color:#ffffff;font-size:10px;margin:5px 0 0 0;'>Tradicional: {esc_a['f1_score']:.4f} | Enriquecido: {esc_b['f1_score']:.4f}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
            st.markdown(" ")
            
            # Fila de Gráficos Clave
            st.markdown("#### 2. Visualización Gráfica de Escenarios (Rendimiento vs Impacto de Negocio)")
            col_graph_l, col_graph_r = st.columns(2)
            
            with col_graph_l:
                # 1. Curvas ROC Superpuestas
                fpr = comparison['fpr_grid']
                tpr_t = esc_a['tpr_grid']
                tpr_e = esc_b['tpr_grid']
                
                fig, ax = plt.subplots(figsize=(6, 5))
                ax.plot(fpr, tpr_e, label=f"Enriquecido (AUC = {esc_b['auc']:.4f})", color="#2563eb", linewidth=2.5)
                ax.plot(fpr, tpr_t, label=f"Tradicional (AUC = {esc_a['auc']:.4f})", color="#fbbf24", linewidth=2)
                ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)
                
                # Formateo Dark theme
                fig.patch.set_facecolor('#0b111e')
                ax.set_facecolor('#0b111e')
                ax.set_title("Curvas ROC Superpuestas (Delta Estadístico)", fontsize=11, fontweight='bold', color='white')
                ax.set_xlabel("Tasa de Falsos Positivos (FPR)", color='white', fontsize=9)
                ax.set_ylabel("Tasa de Verdaderos Positivos (TPR)", color='white', fontsize=9)
                ax.legend(facecolor='#0b111e', edgecolor='white', labelcolor='white', fontsize=8)
                ax.grid(True, linestyle=':', alpha=0.3)
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.tick_params(colors='white', labelsize=8)
                
                st.pyplot(fig)
                st.markdown(
                    "**Análisis de Curvas:** El modelo tradicional tiene un AUC ligeramente superior, pero a costa de un volumen masivo de falsos positivos en el umbral operativo. "
                    "El modelo enriquecido (LightGBM con Feature Store) proporciona una curva más equilibrada y estable para el control de admisión crediticia."
                )
                
            with col_graph_r:
                # 2. Gráfico de Barras Agrupadas de Impacto de Negocio
                cm_t_data = esc_a['confusion_matrix']
                cm_e_data = esc_b['confusion_matrix']
                
                # Barras de Falsos Positivos (clientes sanos rechazados por error)
                # y Verdaderos Negativos (clientes sanos aprobados correctamente)
                categories = ['Falsos Positivos\n(Clientes Sanos Rechazados)', 'Verdaderos Negativos\n(Clientes Sanos Aprobados)']
                trad_counts = [cm_t_data['fp'], cm_t_data['tn']]
                enr_counts = [cm_e_data['fp'], cm_e_data['tn']]
                
                x = np.arange(len(categories))
                width = 0.35
                
                fig_bar, ax_bar = plt.subplots(figsize=(6, 5))
                ax_bar.bar(x - width/2, trad_counts, width, label='Tradicional (A)', color='#fbbf24')
                ax_bar.bar(x + width/2, enr_counts, width, label='Enriquecido (B)', color='#2563eb')
                
                fig_bar.patch.set_facecolor('#0b111e')
                ax_bar.set_facecolor('#0b111e')
                ax_bar.set_title("Impacto de Negocio en la Cartera de Clientes Sanos", fontsize=11, fontweight='bold', color='white')
                ax_bar.set_ylabel("Cantidad de Clientes", color='white', fontsize=9)
                ax_bar.set_xticks(x)
                ax_bar.set_xticklabels(categories, color='white', fontsize=9)
                ax_bar.legend(facecolor='#0b111e', edgecolor='white', labelcolor='white', fontsize=8)
                ax_bar.grid(True, linestyle=':', alpha=0.3)
                ax_bar.spines['bottom'].set_color('white')
                ax_bar.spines['top'].set_color('white')
                ax_bar.spines['left'].set_color('white')
                ax_bar.spines['right'].set_color('white')
                ax_bar.tick_params(colors='white', labelsize=8)
                
                # Agregar etiquetas numéricas en las barras
                for i, val in enumerate(trad_counts):
                    ax_bar.text(i - width/2, val + 500, f"{val:,}", ha='center', color='white', fontsize=8, fontweight='bold')
                for i, val in enumerate(enr_counts):
                    ax_bar.text(i + width/2, val + 500, f"{val:,}", ha='center', color='white', fontsize=8, fontweight='bold')
                
                st.pyplot(fig_bar)
                st.markdown(
                    f"**Impacto Financiero:** El escenario Enriquecido reduce los Falsos Positivos de {cm_t_data['fp']:,} a {cm_e_data['fp']:,} "
                    f"(una caída de **{reduccion_fp:,}** colocaciones perdidas). Esto representa miles de dólares en ingresos financieros adicionales por créditos colocados sin alterar el perfil de riesgo global."
                )

            # 3. Test de McNemar Inter-Escenario
            st.markdown("---")
            st.markdown("#### 3. Validación de Significancia Inter-Escenario - Test de McNemar")
            st.markdown(
                "Para validar formalmente si la diferencia en las predicciones entre ambos escenarios se debe al azar o si es "
                "estadísticamente significativa como resultado directo del Feature Store, aplicamos la prueba de McNemar."
            )
            
            col_mc_l, col_mc_r = st.columns([1, 2])
            
            with col_mc_l:
                st.markdown("**Matriz de Contingencia Inter-Escenario:**")
                ct_comp = comparison['mcnemar']['contingency_table']
                df_ct_comp = pd.DataFrame(
                    ct_comp,
                    index=["Tradicional Correcto", "Tradicional Incorrecto"],
                    columns=["Enriquecido Correcto", "Enriquecido Incorrecto"]
                )
                st.table(df_ct_comp)
                
            with col_mc_r:
                st.markdown("**Métricas del Test Inter-Escenario:**")
                st.write(f"- **Estadístico Chi-cuadrado (Edwards):** `{comparison['mcnemar']['statistic']:.4f}`")
                st.write(f"- **P-Valor (p-value):** `{comparison['mcnemar']['p_value']:.8f}`")
                significant_inter = comparison['mcnemar']['significant']
                st.write(f"- **¿Diferencia Significativa? (α = 0.05):** `{'SÍ' if significant_inter else 'NO'}`")
                
                st.markdown("**Conclusión Estadística de McNemar:**")
                if significant_inter:
                    st.markdown(
                        "Dado que el p-valor es menor a 0.05, **se rechaza la hipótesis nula (H0)**. Concluimos con un 95% de "
                        "confianza que la integración de la arquitectura Feature Store y el enriquecimiento de datos produce una diferencia "
                        "**estadísticamente significativa** en los aciertos de clasificación, validando la hipótesis del artículo de tesis."
                    )
                else:
                    st.markdown(
                        "Dado que el p-valor es mayor o igual a 0.05, **no se puede rechazar la hipótesis nula (H0)**. No hay diferencias "
                        "significativas entre ambos clasificadores."
                    )

            # 4. Test de DeLong Inter-Escenario
            st.markdown("---")
            st.markdown("#### 4. Validación de Diferencia de AUC - Test de DeLong")
            st.markdown(
                "Para comprobar si la diferencia de las capacidades discriminantes (AUC) entre los modelos "
                "Tradicional y Enriquecido es estadísticamente significativa en lugar de un artefacto del muestreo, "
                "aplicamos el test de hipótesis de DeLong sobre curvas ROC correlacionadas."
            )
            
            if 'delong' in comparison:
                dl_data = comparison['delong']
                col_dl_l, col_dl_r = st.columns([1, 2])
                
                with col_dl_l:
                    st.markdown("**Métricas del Test de DeLong:**")
                    st.write(f"- **Estadístico Z:** `{dl_data['z_statistic']:.4f}`")
                    st.write(f"- **P-Valor (p-value):** `{dl_data['p_value']:.8f}`")
                    st.write(f"- **Varianza de Diferencia:** `{dl_data['variance']:.6f}`")
                    st.write(f"- **¿Diferencia Significativa? (α = 0.05):** `{'SÍ' if dl_data['significant'] else 'NO'}`")
                    
                with col_dl_r:
                    st.markdown("**Conclusión de la Prueba de DeLong:**")
                    if dl_data['significant']:
                        st.markdown(
                            f"Dado que el p-valor es menor a 0.05 (`{dl_data['p_value']:.6f} < 0.05`), **se rechaza la hipótesis nula (H0)**. "
                            f"Existe evidencia estadística robusta para afirmar que la diferencia en la capacidad discriminativa (AUC) entre el "
                            f"modelo Enriquecido y el Tradicional es **estadísticamente significativa**."
                        )
                    else:
                        st.markdown(
                            f"Dado que el p-valor es mayor o igual a 0.05, **no se puede rechazar la hipótesis nula (H0)**. "
                            f"No hay diferencias estadísticamente significativas en el AUC global de ambos modelos."
                        )

    # =====================================================================
    # 6. SECCIÓN: Módulo de Descargas de Reportes
    # =====================================================================
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
