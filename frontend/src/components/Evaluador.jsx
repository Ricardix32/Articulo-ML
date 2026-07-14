import React, { useState } from 'react';
import { UserCheck, AlertTriangle, FileText, CheckCircle2, XCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Evaluador() {
  const [formData, setFormData] = useState({
    edad_anios: 35,
    antiguedad_laboral_anios: 5.0,
    amt_income_total: 45000,
    amt_credit: 120000,
    amt_annuity: 9500,
    calificacion_region_ciudad: 2,
    CODE_GENDER: 'F',
    ORGANIZATION_TYPE: 'School',
    NAME_EDUCATION_TYPE: 'Higher education',
  });

  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState('');

  // Ratios calculados en tiempo real para visualización del asesor
  const creditToIncome = formData.amt_income_total > 0 ? (formData.amt_credit / formData.amt_income_total).toFixed(2) : 0;
  const annuityToIncome = formData.amt_income_total > 0 ? ((formData.amt_annuity * 12) / formData.amt_income_total).toFixed(2) : 0; // anualizado

  const handleChange = (e) => {
    const { name, value } = e.target;
    const isNumeric = ['edad_anios', 'antiguedad_laboral_anios', 'amt_income_total', 'amt_credit', 'amt_annuity', 'calificacion_region_ciudad'].includes(name);
    setFormData(prev => ({
      ...prev,
      [name]: isNumeric ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResultado(null);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('No se pudo establecer comunicación con el motor predictivo.');
      }

      const data = await response.json();
      setResultado(data);
    } catch (err) {
      setError(err.message || 'Error al conectar con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between pb-4 border-b border-navy-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Originación de Crédito
          </h2>
          <p className="text-xs text-gray-400 mt-1">Evaluación de riesgo crediticio en tiempo real para nuevos prospectos</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulario */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 glass p-6 rounded-xl space-y-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-900/5 rounded-full blur-2xl pointer-events-none"></div>
          
          <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider mb-2">Datos del Cliente</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Edad */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Edad (años)</label>
              <input
                type="number"
                name="edad_anios"
                value={formData.edad_anios}
                onChange={handleChange}
                min="18"
                max="90"
                required
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              />
            </div>

            {/* Antigüedad Laboral */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Antigüedad Laboral (años)</label>
              <input
                type="number"
                name="antiguedad_laboral_anios"
                value={formData.antiguedad_laboral_anios}
                onChange={handleChange}
                min="0"
                step="0.5"
                required
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              />
            </div>

            {/* Ingresos Totales */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Ingreso Mensual Total ($)</label>
              <input
                type="number"
                name="amt_income_total"
                value={formData.amt_income_total}
                onChange={handleChange}
                min="1"
                required
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              />
            </div>

            {/* Monto Crédito Solicitado */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Monto Solicitado ($)</label>
              <input
                type="number"
                name="amt_credit"
                value={formData.amt_credit}
                onChange={handleChange}
                min="1"
                required
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              />
            </div>

            {/* Anualidad del Crédito */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Cuota Mensual del Crédito ($)</label>
              <input
                type="number"
                name="amt_annuity"
                value={formData.amt_annuity}
                onChange={handleChange}
                min="1"
                required
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              />
            </div>

            {/* Calificación de Región */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Calificación Región de Vivienda</label>
              <select
                name="calificacion_region_ciudad"
                value={formData.calificacion_region_ciudad}
                onChange={handleChange}
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              >
                <option value="1">Categoría 1 (Excelente)</option>
                <option value="2">Categoría 2 (Estándar)</option>
                <option value="3">Categoría 3 (Riesgosa)</option>
              </select>
            </div>

            {/* Género */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Género</label>
              <select
                name="CODE_GENDER"
                value={formData.CODE_GENDER}
                onChange={handleChange}
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              >
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
              </select>
            </div>

            {/* Educación */}
            <div className="space-y-1.5">
              <label className="text-xs text-gray-300 font-medium">Nivel de Instrucción</label>
              <select
                name="NAME_EDUCATION_TYPE"
                value={formData.NAME_EDUCATION_TYPE}
                onChange={handleChange}
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              >
                <option value="Secondary / secondary special">Secundaria / Técnica</option>
                <option value="Higher education">Universitaria / Superior</option>
                <option value="Incomplete higher">Superior Incompleta</option>
                <option value="Lower secondary">Primaria / Básica</option>
              </select>
            </div>

            {/* Sector Económico */}
            <div className="space-y-1.5 md:col-span-2">
              <label className="text-xs text-gray-300 font-medium">Tipo de Organización / Sector Económico</label>
              <select
                name="ORGANIZATION_TYPE"
                value={formData.ORGANIZATION_TYPE}
                onChange={handleChange}
                className="w-full px-3 py-2.5 glass-input rounded-lg text-white text-sm outline-none"
              >
                <option value="Business Entity">Empresa Comercial (Corporativo)</option>
                <option value="School">Educación / Colegio</option>
                <option value="Government">Gobierno / Sector Público</option>
                <option value="Self-employed">Independiente / Autoempleado</option>
                <option value="Other">Otro Sector</option>
              </select>
            </div>
          </div>

          <div className="pt-2 border-t border-navy-800 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-lg shadow-md transition-all flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Analizando riesgo...</span>
                </>
              ) : (
                <>
                  <UserCheck className="w-4 h-4" />
                  <span>Evaluar Solicitud</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Panel de Análisis en Tiempo Real */}
        <div className="glass p-6 rounded-xl space-y-6 h-fit relative">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-900/5 rounded-full blur-2xl pointer-events-none"></div>
          
          <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-wider">Ratios Financieros Estimados</h3>
          
          <div className="space-y-4">
            <div className="p-4 glass-card rounded-lg flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Ratio Crédito / Ingreso</p>
                <p className="text-lg font-bold text-white mt-1">{creditToIncome}x</p>
              </div>
              <div className="text-right">
                <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full ${parseFloat(creditToIncome) > 4 ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
                  {parseFloat(creditToIncome) > 4 ? 'Riesgo Alto' : 'Estable'}
                </span>
              </div>
            </div>

            <div className="p-4 glass-card rounded-lg flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-400">Ratio Cuota Anualizada / Ingreso</p>
                <p className="text-lg font-bold text-white mt-1">{(annuityToIncome * 100).toFixed(1)}%</p>
              </div>
              <div className="text-right">
                <span className={`inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full ${parseFloat(annuityToIncome) > 0.4 ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
                  {parseFloat(annuityToIncome) > 0.4 ? 'Carga Crítica' : 'Aceptable'}
                </span>
              </div>
            </div>
          </div>

          <div className="p-3 bg-blue-900/10 border border-blue-800/20 text-blue-300 text-xs rounded-lg flex gap-2">
            <AlertTriangle className="w-5 h-5 text-blue-400 shrink-0" />
            <span>Los ratios se calculan dinámicamente y se contrastan con las reglas de negocio del motor analítico.</span>
          </div>

          {error && (
            <div className="p-3 bg-red-950/40 border border-red-500/20 text-red-300 text-xs rounded-lg">
              <strong>Error de conexión:</strong> {error}
            </div>
          )}
        </div>
      </div>

      {/* MODAL DE RESULTADOS */}
      {resultado && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md glass p-8 rounded-2xl shadow-2xl relative border border-white/10 animate-fade-in">
            <div className="flex flex-col items-center text-center">
              {resultado.estado === 'APROBADO' ? (
                <>
                  <div className="w-20 h-20 bg-green-950/30 border border-green-500/30 rounded-full flex items-center justify-center mb-6">
                    <CheckCircle2 className="w-12 h-12 text-green-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-green-400 mb-2">Crédito Aprobado</h3>
                  <p className="text-sm text-gray-300 max-w-sm mb-6">
                    El motor de inferencia analítica (LightGBM) ha validado los datos del cliente con éxito.
                  </p>
                </>
              ) : (
                <>
                  <div className="w-20 h-20 bg-red-950/30 border border-red-500/30 rounded-full flex items-center justify-center mb-6">
                    <XCircle className="w-12 h-12 text-red-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-red-400 mb-2">Crédito Rechazado</h3>
                  <p className="text-sm text-gray-300 max-w-sm mb-6">
                    La evaluación ha superado el umbral del 40.0% de probabilidad de impago.
                  </p>
                </>
              )}

              {/* Caja de Métricas */}
              <div className="w-full p-4 bg-navy-900/60 rounded-xl border border-navy-800 space-y-3 mb-6">
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Probabilidad de Impago:</span>
                  <span className={`font-bold ${resultado.estado === 'APROBADO' ? 'text-green-400' : 'text-red-400'}`}>
                    {resultado.probabilidad_impago}%
                  </span>
                </div>
                <div className="w-full bg-navy-850 h-2 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${resultado.estado === 'APROBADO' ? 'bg-green-500' : 'bg-red-500'}`}
                    style={{ width: `${resultado.probabilidad_impago}%` }}
                  ></div>
                </div>
                <div className="text-[10px] text-gray-500 text-left leading-relaxed">
                  *Este dictamen se realiza usando inferencia matemática directa sobre {resultado.estado === 'APROBADO' ? 'baja' : 'alta'} correspondencia con perfiles históricos de impago.
                </div>
              </div>

              <button
                onClick={() => setResultado(null)}
                className="w-full py-3 bg-navy-800 hover:bg-navy-700 text-white font-semibold text-sm rounded-lg transition-colors"
              >
                Cerrar Dictamen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
