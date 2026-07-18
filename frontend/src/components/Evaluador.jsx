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
      const response = await fetch(`${API_BASE_URL}/predict_compare`, {
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

      {/* MODAL DE RESULTADOS DUALES LADO A LADO */}
      {resultado && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-2xl glass p-8 rounded-2xl shadow-2xl relative border border-white/10 animate-fade-in max-h-[90vh] overflow-y-auto">
            {/* Banner de Rescate Comercial */}
            {resultado.rescate_comercial && (
              <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-center gap-3 text-emerald-400 animate-pulse">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center shrink-0">
                  <UserCheck className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider">¡Rescate Comercial Exitoso!</h4>
                  <p className="text-[11px] text-emerald-300/90 mt-0.5">
                    La arquitectura de datos enriquecidos previno un rechazo erróneo del cliente.
                  </p>
                </div>
              </div>
            )}

            <h3 className="text-lg font-bold text-white text-center mb-6">Dictamen Analítico Dual de Originación</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Tarjeta Tradicional */}
              <div className="glass p-5 rounded-xl border border-navy-800 flex flex-col justify-between space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-gray-400">Escenario A (Tradicional)</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    resultado.tradicional.estado === 'APROBADO' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {resultado.tradicional.estado}
                  </span>
                </div>
                
                <div className="flex flex-col items-center py-2 text-center">
                  {resultado.tradicional.estado === 'APROBADO' ? (
                    <CheckCircle2 className="w-10 h-10 text-green-400 mb-2" />
                  ) : (
                    <XCircle className="w-10 h-10 text-red-400 mb-2" />
                  )}
                  <span className="text-[10px] text-gray-400">Probabilidad de Impago:</span>
                  <span className="text-xl font-bold font-mono text-white mt-0.5">{resultado.tradicional.probabilidad_impago}%</span>
                </div>

                <p className="text-[10px] text-gray-400 text-center leading-relaxed">
                  {resultado.tradicional.estado === 'APROBADO' 
                    ? 'Viable según variables tradicionales de ingreso y cuota básica.' 
                    : 'Rechazado debido a que los ratios financieros sobrepasan el umbral de riesgo del 40.0%.'}
                </p>
              </div>

              {/* Tarjeta Enriquecida */}
              <div className="glass p-5 rounded-xl border border-navy-800 flex flex-col justify-between space-y-4 relative overflow-hidden">
                {resultado.rescate_comercial && (
                  <div className="absolute top-0 right-0 w-16 h-16 bg-emerald-500/5 rounded-full blur-xl pointer-events-none"></div>
                )}
                
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-blue-400">Escenario B (Enriquecido)</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    resultado.enriquecido.estado === 'APROBADO' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {resultado.enriquecido.estado}
                  </span>
                </div>
                
                <div className="flex flex-col items-center py-2 text-center">
                  {resultado.enriquecido.estado === 'APROBADO' ? (
                    <CheckCircle2 className="w-10 h-10 text-green-400 mb-2" />
                  ) : (
                    <XCircle className="w-10 h-10 text-red-400 mb-2" />
                  )}
                  <span className="text-[10px] text-gray-400">Probabilidad de Impago:</span>
                  <span className="text-xl font-bold font-mono text-white mt-0.5">{resultado.enriquecido.probabilidad_impago}%</span>
                </div>

                <p className="text-[10px] text-gray-400 text-center leading-relaxed">
                  {resultado.enriquecido.estado === 'APROBADO' 
                    ? 'Aprobado. Las variables de comportamiento del feature store compensaron los ratios tradicionales.' 
                    : 'Rechazado. La probabilidad calibrada con el historial cruzado es superior al 40.0%.'}
                </p>
              </div>
            </div>

            <button
              onClick={() => setResultado(null)}
              className="w-full py-3 bg-navy-800 hover:bg-navy-700 text-white font-semibold text-sm rounded-lg transition-colors mt-2"
            >
              Cerrar Dictamen Dual
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
