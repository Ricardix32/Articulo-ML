import React, { useState, useEffect } from 'react';
import { GitCompare, Info, TrendingUp, CheckCircle2, Scale } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ComparacionEscenarios() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/dashboard/comparison`);
        if (!response.ok) {
          throw new Error('No se pudo cargar la comparación de escenarios.');
        }
        const resData = await response.json();
        setData(resData);
      } catch (err) {
        setError(err.message || 'Error de conexión.');
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <div className="w-10 h-10 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin"></div>
        <p className="text-sm text-gray-400">Cargando métricas comparativas de escenarios...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 glass border border-red-500/20 rounded-xl text-center max-w-lg mx-auto">
        <p className="text-red-400 text-sm font-semibold">⚠️ Error al cargar: {error || 'Datos no disponibles.'}</p>
      </div>
    );
  }

  const { escenario_a, escenario_b, mcnemar, delta } = data;
  const reduccionFP = escenario_a.confusion_matrix.fp - escenario_b.confusion_matrix.fp;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Encabezado */}
      <div className="pb-4 border-b border-navy-800">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <GitCompare className="w-5 h-5 text-blue-400" />
          Comparación de Escenarios (A vs B)
        </h2>
        <p className="text-xs text-gray-400 mt-1">
          Diferencial metodológico y de negocio entre el modelo Tradicional (Escenario A) y el Enriquecido (Escenario B)
        </p>
      </div>

      {/* Delta Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card 1: Delta AUC */}
        <div className="glass p-5 rounded-xl border border-navy-800 flex flex-col justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Delta de AUC-ROC</span>
            <h3 className="text-2xl font-black text-red-400 mt-1">{delta.auc.toFixed(4)}</h3>
          </div>
          <p className="text-[10px] text-gray-400 mt-3 pt-3 border-t border-navy-900">
            Tradicional: <span className="text-white font-mono">{escenario_a.auc.toFixed(4)}</span> | Enriquecido: <span className="text-white font-mono">{escenario_b.auc.toFixed(4)}</span>
          </p>
        </div>

        {/* Card 2: Reducción Falsos Positivos */}
        <div className="glass p-5 rounded-xl border border-navy-800 flex flex-col justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Colocación Extra (Menos Falsos Positivos)</span>
            <h3 className="text-2xl font-black text-green-400 mt-1">-{reduccionFP.toLocaleString()}</h3>
          </div>
          <p className="text-[10px] text-gray-400 mt-3 pt-3 border-t border-navy-900">
            Clientes sanos aprobados correctamente en lugar de rechazados por error.
          </p>
        </div>

        {/* Card 3: Delta F1-Score */}
        <div className="glass p-5 rounded-xl border border-navy-800 flex flex-col justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Delta F1-Score</span>
            <h3 className="text-2xl font-black text-green-400 mt-1">+{delta.f1_score.toFixed(4)}</h3>
          </div>
          <p className="text-[10px] text-gray-400 mt-3 pt-3 border-t border-navy-900">
            Tradicional: <span className="text-white font-mono">{escenario_a.f1_score.toFixed(4)}</span> | Enriquecido: <span className="text-white font-mono">{escenario_b.f1_score.toFixed(4)}</span>
          </p>
        </div>
      </div>

      {/* Visualización de Imágenes Comparativas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico ROC */}
        <div className="glass p-6 rounded-xl space-y-4">
          <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider">1. Curvas ROC Superpuestas (Delta Estadístico)</h4>
          <div className="bg-navy-950/40 p-2 rounded-lg border border-navy-900">
            <img 
              src={`${API_BASE_URL}/static/scenario_comparison_roc.png`} 
              alt="Curvas ROC Superpuestas" 
              className="w-full h-auto rounded"
            />
          </div>
          <p className="text-[11px] text-gray-400 leading-relaxed">
            El escenario Tradicional (A) exhibe un AUC ligeramente mayor, pero genera sobre-rechazo severo. La versión Enriquecida (B) balancea la tasa de error para favorecer la colocación comercial.
          </p>
        </div>

        {/* Gráfico de Impacto de Negocio */}
        <div className="glass p-6 rounded-xl space-y-4">
          <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider">2. Impacto en la Cartera de Clientes Sanos</h4>
          <div className="bg-navy-950/40 p-2 rounded-lg border border-navy-900">
            <img 
              src={`${API_BASE_URL}/static/scenario_comparison_business.png`} 
              alt="Gráfico de Barras Agrupadas de Impacto" 
              className="w-full h-auto rounded"
            />
          </div>
          <p className="text-[11px] text-gray-400 leading-relaxed">
            El modelo enriquecido aprueba a **{escenario_b.confusion_matrix.tn.toLocaleString()}** clientes sanos frente a **{escenario_a.confusion_matrix.tn.toLocaleString()}** del tradicional. Esto rescata **{reduccionFP.toLocaleString()}** créditos viables adicionales.
          </p>
        </div>
      </div>

      {/* Test de McNemar Inter-Escenario */}
      <div className="glass p-6 rounded-xl space-y-5">
        <div>
          <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider">3. Test de McNemar Inter-Escenario (Validación Científica)</h4>
          <p className="text-[11px] text-gray-400 mt-1">
            Comprobación formal de si las discrepancias en test entre ambos escenarios son fruto del azar o debidas a la arquitectura Feature Store.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          {/* Matriz 2x2 */}
          <div className="md:col-span-1 overflow-x-auto">
            <table className="w-full text-[11px] text-left border-collapse border border-navy-800">
              <thead>
                <tr className="bg-navy-900/60">
                  <th className="p-2 border border-navy-800 text-gray-400">Modelo</th>
                  <th className="p-2 border border-navy-800 text-center text-white font-bold">Enr. Correcto</th>
                  <th className="p-2 border border-navy-800 text-center text-white font-bold">Enr. Incorrecto</th>
                </tr>
              </thead>
              <tbody>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="p-2 border border-navy-800 font-bold text-gray-300">Trad. Correcto</td>
                  <td className="p-2 border border-navy-800 text-center text-green-400 font-medium bg-green-500/5">
                    {mcnemar.contingency_table[0][0].toLocaleString()}
                  </td>
                  <td className="p-2 border border-navy-800 text-center text-orange-400 font-medium bg-orange-500/5">
                    {mcnemar.contingency_table[0][1].toLocaleString()}
                  </td>
                </tr>
                <tr className="hover:bg-white/5 transition-colors">
                  <td className="p-2 border border-navy-800 font-bold text-gray-300">Trad. Incorrecto</td>
                  <td className="p-2 border border-navy-800 text-center text-orange-400 font-medium bg-orange-500/5">
                    {mcnemar.contingency_table[1][0].toLocaleString()}
                  </td>
                  <td className="p-2 border border-navy-800 text-center text-red-400 font-medium bg-red-500/5">
                    {mcnemar.contingency_table[1][1].toLocaleString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Estadísticas del Test */}
          <div className="md:col-span-2 space-y-4">
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="border-b border-navy-900 pb-2">
                <span className="text-gray-400">Estadístico Chi2:</span>
                <p className="font-mono font-bold text-white mt-1">{mcnemar.statistic.toFixed(4)}</p>
              </div>
              <div className="border-b border-navy-900 pb-2">
                <span className="text-gray-400">p-valor:</span>
                <p className="font-mono font-bold text-white mt-1">{mcnemar.p_value.toFixed(6)}</p>
              </div>
              <div className="border-b border-navy-900 pb-2">
                <span className="text-gray-400">Diferencia Significativa:</span>
                <p className={`font-bold mt-1 ${mcnemar.significant ? 'text-red-400' : 'text-green-400'}`}>
                  {mcnemar.significant ? 'SÍ (Rechaza H0)' : 'NO'}
                </p>
              </div>
            </div>

            {mcnemar.significant ? (
              <div className="p-3 bg-red-950/20 border border-red-500/20 rounded-lg flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <p className="text-[10.5px] text-red-300 leading-relaxed">
                  **Conclusión Académica:** Dado que p &lt; 0.05, **se rechaza la hipótesis nula**. Se prueba estadísticamente que la integración de la arquitectura Feature Store genera una mejora metodológica significativa.
                </p>
              </div>
            ) : (
              <div className="p-3 bg-green-950/20 border border-green-500/20 rounded-lg flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                <p className="text-[10.5px] text-green-300 leading-relaxed">
                  **Conclusión Académica:** No hay diferencias estadísticamente significativas entre ambos escenarios.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
