import psycopg2
import pandas as pd
import numpy as np
import joblib
import json
import re
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, confusion_matrix, recall_score, f1_score
from scipy.stats import chi2, norm

def clean_column_names(df):
    clean_cols = []
    for col in df.columns:
        clean_col = re.sub(r'[{}":,\[\]]', '_', col)
        clean_cols.append(clean_col)
    df.columns = clean_cols
    return df

# ----------------------------------------------------
# IMPLEMENTACIÓN MATEMÁTICA DEL TEST DE DELONG RÁPIDO
# ----------------------------------------------------
def compute_midrank(x):
    """Computes midranks of a 1D numpy array."""
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1)
        i = j
    T2 = np.zeros(N)
    T2[J] = T
    return T2

def fastDeLong(predictions_sorted_transposed, label_1_count):
    """
    Computes DeLong covariance matrix of AUCs.
    Based on Xu Sun and Weichao Xu (2014) O(N log N) optimization.
    """
    m = label_1_count
    n = predictions_sorted_transposed.shape[1] - m
    k = predictions_sorted_transposed.shape[0]
    
    tx = np.zeros((k, m))
    ty = np.zeros((k, n))
    tz = np.zeros((k, m + n))
    
    for i in range(k):
        tx[i] = compute_midrank(predictions_sorted_transposed[i, :m])
        ty[i] = compute_midrank(predictions_sorted_transposed[i, m:])
        tz[i] = compute_midrank(predictions_sorted_transposed[i, :])
        
    sx = np.zeros((k, k))
    sy = np.zeros((k, k))
    
    for i in range(k):
        for j in range(k):
            # Positives structural components
            v10_i = (tz[i, :m] - tx[i]) / n
            v10_j = (tz[j, :m] - tx[j]) / n
            sx[i, j] = np.cov(v10_i, v10_j)[0, 1] if m > 1 else 0.0
            
            # Negatives structural components
            v01_i = (ty[i] - tz[i, m:]) / m
            v01_j = (ty[j] - tz[j, m:]) / m
            sy[i, j] = np.cov(v01_i, v01_j)[0, 1] if n > 1 else 0.0
            
    return sx / m + sy / n

def delong_roc_test(ground_truth, predictions_one, predictions_two):
    """
    Compares two correlated ROC curves using DeLong's test.
    Returns: auc_one, auc_two, p_value, z_statistic, variance
    """
    ground_truth = np.array(ground_truth)
    predictions_one = np.array(predictions_one)
    predictions_two = np.array(predictions_two)
    
    # Sort samples so that positive class comes first
    pos_mask = (ground_truth == 1)
    neg_mask = (ground_truth == 0)
    
    sorted_idx = np.hstack([np.where(pos_mask)[0], np.where(neg_mask)[0]])
    ground_truth = ground_truth[sorted_idx]
    predictions_one = predictions_one[sorted_idx]
    predictions_two = predictions_two[sorted_idx]
    
    m = np.sum(pos_mask)
    n = len(ground_truth) - m
    
    preds = np.vstack([predictions_one, predictions_two])
    cov = fastDeLong(preds, m)
    
    # Calculate AUCs using ranks (Mann-Whitney U relation)
    tz_one = compute_midrank(predictions_one)
    tz_two = compute_midrank(predictions_two)
    
    auc_one = (np.mean(tz_one[:m]) - (m - 1) / 2) / n
    auc_two = (np.mean(tz_two[:m]) - (m - 1) / 2) / n
    
    # Variance of the difference
    var = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    if var > 0:
        z = (auc_one - auc_two) / np.sqrt(var)
        p_value = 2 * (1 - norm.cdf(np.abs(z)))
    else:
        z = 0.0
        p_value = 1.0
        
    return auc_one, auc_two, p_value, z, var

def main():
    print("Conectando a PostgreSQL...")
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="credit_risk_warehouse",
        user="etl_admin",
        password="etl_pass_seguro"
    )
    
    query = "SELECT * FROM gold.vw_analisis_riesgo_crediticio"
    print("Leyendo datos de la vista...")
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Se leyeron {len(df)} registros.")
    
    # Separar la porción de test (20%) de manera idéntica usando random_state=42 y estratificación
    df_train, df_test = train_test_split(
        df, test_size=0.20, random_state=42, stratify=df['flag_morosidad']
    )
    
    y_test = df_test['flag_morosidad'].astype(int).values
    
    # ----------------------------------------------------
    # ESCENARIO A: TRADICIONAL (_2)
    # ----------------------------------------------------
    print("Evaluando Escenario A (Tradicional)...")
    cols_traditional = [
        'monto_credito_solicitado', 'ingresos_totales_cliente', 'monto_anualidad_credito',
        'ratio_credito_ingreso', 'ratio_anualidad_ingreso', 'cantidad_hijos',
        'genero', 'nivel_educativo', 'estado_civil'
    ]
    
    X_trad = df_test[cols_traditional].copy()
    X_trad_encoded = pd.get_dummies(X_trad, drop_first=True)
    X_trad_encoded = clean_column_names(X_trad_encoded)
    
    # Convertir booleanas a int
    for col in X_trad_encoded.select_dtypes(include=['bool']).columns:
        X_trad_encoded[col] = X_trad_encoded[col].astype(int)
        
    columnas_2 = joblib.load("columnas_modelo_2.pkl")
    X_trad_aligned = X_trad_encoded.reindex(columns=columnas_2, fill_value=0)
    
    model_2 = joblib.load("modelo_riesgo_lgbm_2.pkl")
    probs_trad = model_2.predict_proba(X_trad_aligned)[:, 1]
    
    # ----------------------------------------------------
    # ESCENARIO B: ENRIQUECIDO
    # ----------------------------------------------------
    print("Evaluando Escenario B (Enriquecido)...")
    rename_dict = {
        'monto_credito_solicitado': 'amt_credit',
        'ingresos_totales_cliente': 'amt_income_total',
        'monto_anualidad_credito': 'amt_annuity',
        'genero': 'CODE_GENDER',
        'nivel_educativo': 'NAME_EDUCATION_TYPE',
        'sector_economico': 'ORGANIZATION_TYPE',
        'flag_morosidad': 'default'
    }
    
    df_enr_test = df_test.copy()
    df_enr_test.rename(columns=rename_dict, inplace=True)
    
    # Calcular ratios
    ingreso = df_enr_test['amt_income_total']
    df_enr_test['credit_to_income_ratio'] = df_enr_test['amt_credit'] / ingreso.apply(lambda x: x if x > 0 else 1.0)
    df_enr_test['annuity_income_ratio'] = df_enr_test['amt_annuity'] / ingreso.apply(lambda x: x if x > 0 else 1.0)
    
    cols_enr = [
        'edad_anios', 'antiguedad_laboral_anios', 'amt_income_total', 
        'amt_credit', 'amt_annuity', 'calificacion_region_ciudad', 
        'credit_to_income_ratio', 'annuity_income_ratio',
        'CODE_GENDER', 'ORGANIZATION_TYPE', 'NAME_EDUCATION_TYPE'
    ]
    
    X_enr = df_enr_test[cols_enr].copy()
    X_enr_encoded = pd.get_dummies(X_enr, drop_first=True)
    X_enr_encoded = clean_column_names(X_enr_encoded)
    
    # Convertir booleanas a int
    for col in X_enr_encoded.select_dtypes(include=['bool']).columns:
        X_enr_encoded[col] = X_enr_encoded[col].astype(int)
        
    columnas_1 = joblib.load("columnas_modelo.pkl")
    X_enr_aligned = X_enr_encoded.reindex(columns=columnas_1, fill_value=0)
    
    model_1 = joblib.load("modelo_riesgo_lgbm.pkl")
    probs_enr = model_1.predict_proba(X_enr_aligned)[:, 1]
    
    # ----------------------------------------------------
    # METRICAS DE EVALUACION Y DELONG TEST
    # ----------------------------------------------------
    print("Calculando metricas y aplicando Test de DeLong...")
    # Umbral por defecto de calibración en la API
    threshold = 0.40
    preds_trad = (probs_trad >= threshold).astype(int)
    preds_enr = (probs_enr >= threshold).astype(int)
    
    # DeLong test
    auc_t_dl, auc_e_dl, p_val_delong, z_stat_delong, cov_val = delong_roc_test(y_test, probs_trad, probs_enr)
    
    # AUC-ROC tradicional
    fpr_t, tpr_t, _ = roc_curve(y_test, probs_trad)
    fpr_e, tpr_e, _ = roc_curve(y_test, probs_enr)
    
    auc_t = auc(fpr_t, tpr_t)
    auc_e = auc(fpr_e, tpr_e)
    
    # Reducir curvas ROC a una cuadrícula regular de 100 puntos para optimizar JSON
    grid = np.linspace(0, 1, 100)
    tpr_t_interp = np.interp(grid, fpr_t, tpr_t)
    tpr_e_interp = np.interp(grid, fpr_e, tpr_e)
    
    # Matrices de Confusión
    cm_t = confusion_matrix(y_test, preds_trad)
    cm_e = confusion_matrix(y_test, preds_enr)
    
    # Sensibilidad (Recall) y F1-score
    recall_t = recall_score(y_test, preds_trad)
    recall_e = recall_score(y_test, preds_enr)
    f1_t = f1_score(y_test, preds_trad)
    f1_e = f1_score(y_test, preds_enr)
    
    # ----------------------------------------------------
    # TEST DE MCNEMAR INTER-ESCENARIO
    # ----------------------------------------------------
    print("Aplicando el Test de McNemar Inter-Escenario...")
    correct_trad = (preds_trad == y_test)
    correct_enr = (preds_enr == y_test)
    
    c_00 = np.sum(correct_trad & correct_enr)
    c_01 = np.sum(correct_trad & ~correct_enr)
    c_10 = np.sum(~correct_trad & correct_enr)
    c_11 = np.sum(~correct_trad & ~correct_enr)
    
    contingency_table = [[int(c_00), int(c_01)], [int(c_10), int(c_11)]]
    
    b = c_01
    c = c_10
    denominador = b + c
    if denominador > 0:
        chi2_stat = (abs(b - c) - 1) ** 2 / denominador
        p_val_mcnemar = chi2.sf(chi2_stat, 1)
    else:
        chi2_stat = 0.0
        p_val_mcnemar = 1.0
        
    mcnemar_data = {
        "contingency_table": contingency_table,
        "statistic": float(chi2_stat),
        "p_value": float(p_val_mcnemar),
        "significant": bool(p_val_mcnemar < 0.05)
    }

    # ----------------------------------------------------
    # GUARDAR RESULTADOS
    # ----------------------------------------------------
    comparison_data = {
        "metadata": {
            "total_test_records": int(len(y_test)),
            "default_rate": float(np.mean(y_test)),
            "threshold": threshold
        },
        "escenario_a": {
            "nombre": "Tradicional (Escenario A)",
            "auc": float(auc_t),
            "recall": float(recall_t),
            "f1_score": float(f1_t),
            "confusion_matrix": {
                "tn": int(cm_t[0][0]),
                "fp": int(cm_t[0][1]),
                "fn": int(cm_t[1][0]),
                "vp": int(cm_t[1][1])
            },
            "tpr_grid": tpr_t_interp.tolist()
        },
        "escenario_b": {
            "nombre": "Enriquecido (Escenario B)",
            "auc": float(auc_e),
            "recall": float(recall_e),
            "f1_score": float(f1_e),
            "confusion_matrix": {
                "tn": int(cm_e[0][0]),
                "fp": int(cm_e[0][1]),
                "fn": int(cm_e[1][0]),
                "vp": int(cm_e[1][1])
            },
            "tpr_grid": tpr_e_interp.tolist()
        },
        "fpr_grid": grid.tolist(),
        "mcnemar": mcnemar_data,
        "delong": {
            "p_value": float(p_val_delong),
            "z_statistic": float(z_stat_delong),
            "variance": float(cov_val),
            "significant": bool(p_val_delong < 0.05)
        },
        "delta": {
            "auc": float(auc_e - auc_t),
            "recall": float(recall_e - recall_t),
            "f1_score": float(f1_e - f1_t),
            "falsos_negativos_reduccion": int(cm_t[1][0] - cm_e[1][0])
        }
    }
    
    output_path = "static/scenario_comparison.json"
    with open(output_path, "w") as f:
        json.dump(comparison_data, f, indent=2)
        
    # ----------------------------------------------------
    # GENERAR IMAGENES DE COMPARACION CON ANOTACION DELONG
    # ----------------------------------------------------
    print("Guardando graficos comparativos en static/...")
    import matplotlib.pyplot as plt
    
    # 1. Curvas ROC Superpuestas
    plt.figure(figsize=(6, 5))
    plt.plot(grid, tpr_e_interp, label=f"Enriquecido (AUC = {auc_e:.4f})", color="#2563eb", linewidth=2.5)
    plt.plot(grid, tpr_t_interp, label=f"Tradicional (AUC = {auc_t:.4f})", color="#fbbf24", linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    
    # Caja de texto con p-valor de DeLong
    sig_text = "Si" if p_val_delong < 0.05 else "No"
    info_text = f"DeLong Test:\np-val = {p_val_delong:.6f}\nSignificativo: {sig_text}"
    plt.gca().text(
        0.55, 0.15, info_text, fontsize=9, bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", alpha=0.9, edgecolor="#dddddd")
    )
    
    plt.title("Curvas ROC Superpuestas (Delta Estadistico)", fontsize=12, fontweight='bold')
    plt.xlabel("Tasa de Falsos Positivos (FPR)", fontsize=10)
    plt.ylabel("Tasa de Verdaderos Positivos (TPR)", fontsize=10)
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig("static/scenario_comparison_roc.png", dpi=150)
    plt.close()
    
    # 2. Impacto de Negocio (Grouped Bar Chart de Cartera Sana)
    categories = ['Falsos Positivos\n(Clientes Rechazados)', 'Verdaderos Negativos\n(Clientes Aprobados)']
    trad_counts = [int(cm_t[0][1]), int(cm_t[0][0])]
    enr_counts = [int(cm_e[0][1]), int(cm_e[0][0])]
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(x - width/2, trad_counts, width, label='Tradicional (A)', color='#fbbf24')
    ax.bar(x + width/2, enr_counts, width, label='Enriquecido (B)', color='#2563eb')
    
    ax.set_title("Impacto de Negocio en la Cartera Sana", fontsize=12, fontweight='bold')
    ax.set_ylabel("Cantidad de Clientes", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Añadir valores numéricos en la parte superior de cada barra
    for i, val in enumerate(trad_counts):
        ax.text(i - width/2, val + (max(trad_counts)*0.01), f"{val:,}", ha='center', fontsize=9, fontweight='bold')
    for i, val in enumerate(enr_counts):
        ax.text(i + width/2, val + (max(enr_counts)*0.01), f"{val:,}", ha='center', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig("static/scenario_comparison_business.png", dpi=150)
    plt.close()
        
    print(f"Archivo de comparacion guardado con exito en: {output_path}")
    print(f"Delta AUC: +{auc_e - auc_t:.4f}")
    print(f"Delta Recall (Sensibilidad): +{recall_e - recall_t:.4f}")
    print(f"Reduccion de Falsos Negativos (Creditos Incobrables): {cm_t[1][0] - cm_e[1][0]} creditos detectados adicionales.")
    print(f"p-valor de McNemar Inter-Escenario: {p_val_mcnemar:.6f} (Significativo: {p_val_mcnemar < 0.05})")
    print(f"p-valor de DeLong Inter-Escenario: {p_val_delong:.6f} (Significativo: {p_val_delong < 0.05})")

if __name__ == "__main__":
    main()
