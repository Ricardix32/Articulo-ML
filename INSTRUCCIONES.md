# Guía de Levantamiento Local y Despliegue en la Nube

Este proyecto es una plataforma científica e interactiva para la **Evaluación y Inferencia de Riesgo Crediticio**, compuesta por:
1. **API Backend (FastAPI)**: Servidor de inferencia operativa y consulta de métricas.
2. **Cliente Frontend (React + Vite + TailwindCSS)**: Portal interactivo de originación y dashboard ejecutivo.
3. **Dashboard Académico (Streamlit)**: Prototipo independiente de sustentación estadística y validación de hipótesis.

---

## 1. Levantamiento Local (Paso a Paso)

### Requisitos Previos
Asegúrate de tener instalado en tu sistema:
* **Python 3.10 o superior**
* **Node.js 18 o superior** (con `npm`)
* **PostgreSQL** (con la base de datos `credit_risk_warehouse` y la capa Gold configurada)

---

### A. Configuración y Ejecución del Backend

1. **Crear e inicializar el entorno virtual (si no está hecho)**:
   ```bash
   # En Windows:
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configurar el archivo de variables de entorno `.env`**:
   Crea un archivo `.env` en la raíz del backend con tus credenciales de PostgreSQL locales:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=credit_risk_warehouse
   DB_USER=etl_admin
   DB_PASSWORD=tu_contraseña_segura
   GOLD_TABLE_NAME=gold.vw_analisis_riesgo_crediticio
   ```
4. **Ejecutar el Motor Analítico Offline (Entrenamiento y Estadísticas)**:
   *Este paso es obligatorio para poblar los reportes y entrenar el modelo ganador LightGBM con pesos calibrados:*
   ```bash
   python model_pipeline.py
   ```
5. **Iniciar el servidor API de FastAPI**:
   ```bash
   python -m uvicorn main:app --port 8000
   ```
   *La API estará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.*

---

### B. Configuración y Ejecución del Frontend (React)

1. **Navegar a la carpeta del frontend**:
   ```bash
   cd frontend
   ```
2. **Instalar dependencias de Node**:
   ```bash
   npm install
   ```
3. **Configurar la URL de la API**:
   Vite utiliza por defecto la dirección `http://localhost:8000`. Si deseas cambiarla, crea un archivo `frontend/.env.local` y añade:
   ```env
   VITE_API_URL=http://localhost:8000
   ```
4. **Iniciar el servidor de desarrollo local**:
   ```bash
   npm run dev
   ```
   *La interfaz de originación y estadísticas ejecutivas estará en `http://localhost:5173/`.*
   *Credenciales de acceso:* Usuario: `admin` | Contraseña: `tesis2026`

---

### C. Ejecución del Dashboard de Streamlit

1. **Abrir una nueva terminal en la raíz del proyecto** (con el entorno virtual activado) y correr:
   ```bash
   .\venv\Scripts\streamlit.exe run dashboard_streamlit.py --server.port 8502
   ```
   *El panel de sustentación se abrirá en `http://localhost:8502/`.*

---

## 2. Configuración de Git y Subida a GitHub

Para desplegar en la nube, primero debes subir el código a un repositorio público o privado en tu cuenta de GitHub:

1. **Inicializar el repositorio Git**:
   ```bash
   git init
   ```
2. **Confirmar archivos incluidos** (nuestro `.gitignore` omitirá las carpetas pesadas `venv/` y `node_modules/`, pero mantendrá los archivos `.pkl` y `static/` precalculados):
   ```bash
   git add .
   ```
3. **Hacer el primer Commit**:
   ```bash
   git commit -m "feat: implementacion completa backend fastapi, frontend react y dashboard streamlit"
   ```
4. **Vincular y Empujar a tu repositorio de GitHub**:
   ```bash
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```

---

## 3. Guía de Despliegue en la Nube

> [!IMPORTANT]
> **Estrategia de Despliegue sin Base de Datos Cloud**
> Dado que la base de datos PostgreSQL está instalada de manera local en tu máquina (`localhost`), los servicios de la nube (como Render) no tendrán acceso a ella durante la compilación.
> **Nuestra Solución:** El repositorio incluye los binarios precalculados (`modelo_riesgo_lgbm.pkl`, `columnas_modelo.pkl`, `static/metrics.json` y los reportes e imágenes en `/static`). 
> De esta forma, FastAPI levantará en Render de manera independiente de la base de datos, cargando los modelos entrenados y sirviendo los reportes precalculados al instante.

### A. Despliegue del Backend en Render

1. Ve a [Render](https://render.com) e inicia sesión.
2. Haz clic en **New +** y selecciona **Web Service**.
3. Conecta tu repositorio de GitHub.
4. Completa la configuración del servicio:
   * **Name**: `tesis-api-backend` (o el nombre que gustes).
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Haz clic en **Deploy Web Service**.
6. Una vez desplegado, copia la URL pública generada (ej: `https://tesis-api-backend.onrender.com`).

---

### B. Despliegue del Frontend en Vercel

1. Ve a [Vercel](https://vercel.com) e inicia sesión.
2. Haz clic en **Add New...** y selecciona **Project**.
3. Importa tu repositorio de GitHub.
4. En la configuración del proyecto:
   * **Root Directory**: Haz clic en *Edit* y selecciona la carpeta **`frontend`** (esto es crucial ya que el frontend está en un subdirectorio).
   * **Framework Preset**: Selecciona **`Vite`** (se detecta automáticamente).
   * **Build Command**: `npm run build`.
   * **Output Directory**: `dist`.
5. En la sección **Environment Variables**, agrega la siguiente variable:
   * **Key**: `VITE_API_URL`
   * **Value**: `https://tesis-api-backend.onrender.com` *(La URL que copiaste de tu backend en Render)*.
6. Haz clic en **Deploy**. Vercel construirá y publicará la aplicación web con su URL pública.
