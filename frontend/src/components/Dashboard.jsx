import React, { useState, useEffect } from 'react';
import { BarChart3, Download, RefreshCw, Cpu, Award, Zap, TrendingUp, Info } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('roc'); // 'roc' | 'confusion' | 'heatmap'

  const fetchMetrics = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/metrics`);
      if (!response.ok) {
        throw new Error('No se pudieron obtener las métricas de sustentación.');
      }
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(err.message || 'Error de conexión con el backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleDownload = (format) => {
    window.open(`${API_BASE_URL}/reports/download/${format}`, '_blank');
  };

  // Encontrar el ganador de las métricas para destacar en las tarjetas
  const getWinnerMetrics = () => {
    if (!metrics) return null;
    const winnerName = metrics.mejor_modelo;
    return metrics.modelos[winnerName];
  };

  const winnerMetrics = getWinnerMetrics();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Encabezado */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-navy-800 gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            Dashboard de Evaluación de Modelos
          </h2>
          <p className="text-xs text-gray-400 mt-1">Sustentación científica de validación, significancia estadística y métricas de ML</p>
        </div>
        <button
          onClick={fetchMetrics}
          disabled={loading}
          className="w-fit px-4 py-2 bg-navy-800 hover:bg-navy-700 disabled:opacity-50 text-white font-medium text-xs rounded-lg transition-colors flex items-center gap-2 self-start sm:self-center"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar Datos</span>
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
          <p className="text-sm text-gray-400">Cargando métricas y resultados del almacén de datos...</p>
        </div>
      ) : error ? (
        <div className="p-6 glass border border-red-500/20 rounded-xl space-y-4 max-w-xl mx-auto text-center">
          <p className="text-red-400 text-sm font-semibold">⚠️ {error}</p>
          <p className="text-xs text-gray-500">
            Asegúrese de haber ejecutado el pipeline de entrenamiento offline primero corriendo 
            <code className="bg-navy-900 px-2 py-1 rounded text-red-300 ml-1">python model_pipeline.py</code>.
          </p>
        </div>
      ) : (
        <>
          {/* Tarjetas de Métricas Principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Modelo Ganador */}
            <div className="glass p-5 rounded-xl border border-white/5 relative overflow-hidden flex flex-col justify-between min-h-[120px]">
              <div className="absolute top-0 right-0 w-16 h-16 bg-blue-900/10 rounded-full blur-xl"></div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase">Modelo Ganador</span>
                <Cpu className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <p className="text-xl font-bold text-white mt-2">{metrics.mejor_modelo}</p>
                <p className="text-[10px] text-gray-400 mt-1">Seleccionado por mayor AUC/F1-Score</p>
              </div>
            </div>

            {/* AUC-ROC Ganador */}
            <div className="glass p-5 rounded-xl border border-white/5 relative overflow-hidden flex flex-col justify-between min-h-[120px]">
              <div className="absolute top-0 right-0 w-16 h-16 bg-green-900/10 rounded-full blur-xl"></div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase">Área bajo la curva (AUC)</span>
                <Award className="w-4 h-4 text-green-400" />
              </div>
              <div>
                <p className="text-3xl font-black text-green-400 mt-1">{winnerMetrics ? winnerMetrics['AUC-ROC'].toFixed(4) : 'N/A'}</p>
                <p className="text-[10px] text-gray-400 mt-1">Capacidad de discriminación predictiva</p>
              </div>
            </div>

            {/* McNemar p-value */}
            <div className="glass p-5 rounded-xl border border-white/5 relative overflow-hidden flex flex-col justify-between min-h-[120px]">
              <div className="absolute top-0 right-0 w-16 h-16 bg-purple-900/10 rounded-full blur-xl"></div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase">p-valor (McNemar)</span>
                <Zap className="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <p className="text-3xl font-black text-purple-400 mt-1">{metrics.mcnemar.p_value.toFixed(4)}</p>
                <p className="text-[10px] text-gray-400 mt-1">
                  {metrics.mcnemar.significant ? 'Diferencia Significativa' : 'Sin Dif. Significativa'}
                </p>
              </div>
            </div>

            {/* Muestra Real */}
            <div className="glass p-5 rounded-xl border border-white/5 relative overflow-hidden flex flex-col justify-between min-h-[120px]">
              <div className="absolute top-0 right-0 w-16 h-16 bg-yellow-900/10 rounded-full blur-xl"></div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase">Muestra Histórica</span>
                <TrendingUp className="w-4 h-4 text-yellow-400" />
              </div>
              <div>
                <p className="text-3xl font-black text-yellow-400 mt-1">307.5K</p>
                <p className="text-[10px] text-gray-400 mt-1">Registros cargados de PostgreSQL</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Visualización de Gráficos (Izquierda y Centro) */}
            <div className="lg:col-span-2 glass p-6 rounded-xl space-y-6">
              <div className="flex items-center justify-between border-b border-navy-800 pb-3">
                <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider">Visualizaciones del Modelo</h3>
                
                {/* Tabs de control de gráficos */}
                <div className="flex gap-1.5 bg-navy-900/60 p-1 rounded-lg border border-navy-850">
                  <button
                    onClick={() => setActiveTab('roc')}
                    className={`px-3 py-1 text-[11px] font-semibold rounded ${activeTab === 'roc' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white transition-colors'}`}
                  >
                    Curva ROC
                  </button>
                  <button
                    onClick={() => setActiveTab('confusion')}
                    className={`px-3 py-1 text-[11px] font-semibold rounded ${activeTab === 'confusion' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white transition-colors'}`}
                  >
                    Matriz de Confusión
                  </button>
                  <button
                    onClick={() => setActiveTab('heatmap')}
                    className={`px-3 py-1 text-[11px] font-semibold rounded ${activeTab === 'heatmap' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white transition-colors'}`}
                  >
                    Mapa de Correlación
                  </button>
                </div>
              </div>

              {/* Contenedor de Imagen */}
              <div className="bg-navy-950/40 rounded-lg border border-navy-900 flex items-center justify-center p-2 min-h-[350px]">
                {activeTab === 'roc' && (
                  <div className="text-center w-full">
                    <img 
                      src={`${API_BASE_URL}/static/roc_curves.png`} 
                      alt="Curvas ROC" 
                      className="max-h-[360px] mx-auto rounded shadow-lg object-contain"
                    />
                    <p className="text-xs text-gray-500 mt-2 italic">Curvas ROC comparativas evaluadas sobre el conjunto de test (80/20).</p>
                  </div>
                )}
                {activeTab === 'confusion' && (
                  <div className="text-center w-full">
                    <img 
                      src={`${API_BASE_URL}/static/confusion_matrix.png`} 
                      alt="Matriz de Confusión" 
                      className="max-h-[360px] mx-auto rounded shadow-lg object-contain"
                    />
                    <p className="text-xs text-gray-500 mt-2 italic">Matriz de confusión obtenida por el clasificador ganador en test.</p>
                  </div>
                )}
                {activeTab === 'heatmap' && (
                  <div className="text-center w-full">
                    <img 
                      src={`${API_BASE_URL}/static/correlation_heatmap.png`} 
                      alt="Mapa de Correlación" 
                      className="max-h-[360px] mx-auto rounded shadow-lg object-contain"
                    />
                    <p className="text-xs text-gray-500 mt-2 italic">Mapa de calor de correlaciones del EDA para variables cuantitativas.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Módulo de Descargas y McNemar (Derecha) */}
            <div className="space-y-6">
              {/* Descargas de Reportes */}
              <div className="glass p-6 rounded-xl space-y-4">
                <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider pb-2 border-b border-navy-800">
                  Descarga de Reportes
                </h3>
                
                <p className="text-xs text-gray-400 leading-relaxed">
                  Exportación de resultados consolidados con tablas, figuras estadísticas e interpretaciones científicas.
                </p>

                <div className="space-y-3 pt-2">
                  <button
                    onClick={() => handleDownload('pdf')}
                    className="w-full py-3 bg-red-950/20 hover:bg-red-950/40 border border-red-900/30 hover:border-red-500/40 text-red-300 rounded-lg text-xs font-bold transition-all flex items-center justify-between px-4"
                  >
                    <span>Reporte Científico PDF</span>
                    <Download className="w-4 h-4 text-red-400" />
                  </button>

                  <button
                    onClick={() => handleDownload('excel')}
                    className="w-full py-3 bg-green-950/20 hover:bg-green-950/40 border border-green-900/30 hover:border-green-500/40 text-green-300 rounded-lg text-xs font-bold transition-all flex items-center justify-between px-4"
                  >
                    <span>Métricas y Tablas Excel</span>
                    <Download className="w-4 h-4 text-green-400" />
                  </button>

                  <button
                    onClick={() => handleDownload('word')}
                    className="w-full py-3 bg-blue-950/20 hover:bg-blue-950/40 border border-blue-900/30 hover:border-blue-500/40 text-blue-300 rounded-lg text-xs font-bold transition-all flex items-center justify-between px-4"
                  >
                    <span>Reporte Metodológico Word</span>
                    <Download className="w-4 h-4 text-blue-400" />
                  </button>
                </div>
              </div>

              {/* Información del Test McNemar */}
              <div className="glass p-6 rounded-xl space-y-4 relative">
                <h3 className="text-sm font-bold text-purple-400 uppercase tracking-wider pb-2 border-b border-navy-800 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-purple-400" />
                  Test de McNemar
                </h3>

                <div className="text-xs text-gray-400 space-y-2.5">
                  <div className="flex justify-between border-b border-navy-900 pb-1.5">
                    <span>Chi-cuadrado:</span>
                    <span className="font-bold text-white">{metrics.mcnemar.chi2_statistic.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between border-b border-navy-900 pb-1.5">
                    <span>p-valor:</span>
                    <span className="font-bold text-white">{metrics.mcnemar.p_value.toFixed(6)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Significativo (α=0.05):</span>
                    <span className={`font-bold ${metrics.mcnemar.significant ? 'text-red-400' : 'text-green-400'}`}>
                      {metrics.mcnemar.significant ? 'SÍ (Rechaza H0)' : 'NO (Acepta H0)'}
                    </span>
                  </div>

                  <p className="text-[10px] text-gray-500 leading-relaxed pt-2">
                    {metrics.mcnemar.significant ? (
                      "*La prueba de McNemar demuestra que existe una diferencia estadísticamente significativa en el rendimiento predictivo de clasificación entre LightGBM y XGBoost."
                    ) : (
                      "*La prueba estadística demuestra que la diferencia en las tasas de error de clasificación de LightGBM y XGBoost se debe a la variabilidad aleatoria; ambos modelos tienen capacidad predictiva equivalente."
                    )}
                  </p>
                </div>
              </div>

              {/* Información del Test de Wilcoxon */}
              {metrics.wilcoxon && (
                <div className="glass p-6 rounded-xl space-y-4 relative">
                  <h3 className="text-sm font-bold text-green-400 uppercase tracking-wider pb-2 border-b border-navy-800 flex items-center gap-1.5">
                    <Info className="w-4 h-4 text-green-400" />
                    Test de Wilcoxon (CV Folds)
                  </h3>

                  <div className="text-xs text-gray-400 space-y-2.5">
                    <div className="flex justify-between border-b border-navy-900 pb-1.5">
                      <span>Test aplicado:</span>
                      <span className="font-bold text-white">{metrics.wilcoxon.test_type}</span>
                    </div>
                    <div className="flex justify-between border-b border-navy-900 pb-1.5">
                      <span>Estadístico:</span>
                      <span className="font-bold text-white">{metrics.wilcoxon.statistic.toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between border-b border-navy-900 pb-1.5">
                      <span>p-valor:</span>
                      <span className="font-bold text-white">{metrics.wilcoxon.p_value.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Significativo (α=0.05):</span>
                      <span className={`font-bold ${metrics.wilcoxon.significant ? 'text-red-400' : 'text-green-400'}`}>
                        {metrics.wilcoxon.significant ? 'SÍ (Rechaza H0)' : 'NO (Acepta H0)'}
                      </span>
                    </div>

                    <p className="text-[10px] text-gray-500 leading-relaxed pt-2">
                      {metrics.wilcoxon.significant ? (
                        `*Demuestra con significancia estadística que la superioridad del modelo ganador es estable frente a ${metrics.wilcoxon.benchmark_modelo} a lo largo de las particiones.`
                      ) : (
                        `*Ambos modelos se comportan de forma estadísticamente equivalente en términos de estabilidad de validación cruzada.`
                      )}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
