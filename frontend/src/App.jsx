import React, { useState } from 'react';
import Login from './components/Login';
import Evaluador from './components/Evaluador';
import Dashboard from './components/Dashboard';
import PruebasEstadisticas from './components/PruebasEstadisticas';
import { FileText, BarChart3, LogOut, ShieldCheck, Scale } from 'lucide-react';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeView, setActiveView] = useState('evaluador'); // 'evaluador' | 'dashboard' | 'pruebas'

  if (!isAuthenticated) {
    return <Login onLogin={setIsAuthenticated} />;
  }

  return (
    <div className="min-h-screen bg-[#0b111e] text-gray-100 flex flex-col md:flex-row">
      {/* Círculos decorativos de fondo */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-900/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-900/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* SIDEBAR DE NAVEGACIÓN */}
      <aside className="w-full md:w-64 glass border-b md:border-b-0 md:border-r border-navy-800/80 flex flex-col justify-between shrink-0 relative z-20">
        <div className="p-6">
          {/* Logo / Título */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-navy-800/60 rounded-xl flex items-center justify-center border border-navy-700">
              <ShieldCheck className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white leading-tight">Motor Crediticio</h1>
              <p className="text-[10px] text-gray-400">Tesis Académica 2026</p>
            </div>
          </div>

          {/* Menú de Opciones */}
          <nav className="space-y-1.5">
            <button
              onClick={() => setActiveView('evaluador')}
              className={`w-full px-4 py-3 rounded-lg text-xs font-semibold flex items-center gap-3 transition-all duration-300 ${
                activeView === 'evaluador'
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.05)]'
                  : 'text-gray-400 hover:text-white hover:bg-navy-850 border border-transparent'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Originación (Asesor)</span>
            </button>

            <button
              onClick={() => setActiveView('dashboard')}
              className={`w-full px-4 py-3 rounded-lg text-xs font-semibold flex items-center gap-3 transition-all duration-300 ${
                activeView === 'dashboard'
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.05)]'
                  : 'text-gray-400 hover:text-white hover:bg-navy-850 border border-transparent'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Estadísticas / Reportes</span>
            </button>

            <button
              onClick={() => setActiveView('pruebas')}
              className={`w-full px-4 py-3 rounded-lg text-xs font-semibold flex items-center gap-3 transition-all duration-300 ${
                activeView === 'pruebas'
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.05)]'
                  : 'text-gray-400 hover:text-white hover:bg-navy-850 border border-transparent'
              }`}
            >
              <Scale className="w-4 h-4" />
              <span>Pruebas Estadísticas</span>
            </button>
          </nav>
        </div>

        {/* Footer / Salir */}
        <div className="p-6 border-t border-navy-800/80">
          <button
            onClick={() => setIsAuthenticated(false)}
            className="w-full px-4 py-3 rounded-lg text-xs font-semibold text-red-400 hover:text-red-300 hover:bg-red-950/10 border border-transparent hover:border-red-900/20 flex items-center gap-3 transition-all"
          >
            <LogOut className="w-4 h-4" />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* CONTENEDOR PRINCIPAL */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full relative z-10 overflow-y-auto">
        {activeView === 'evaluador' && <Evaluador />}
        {activeView === 'dashboard' && <Dashboard />}
        {activeView === 'pruebas' && <PruebasEstadisticas />}
      </main>
    </div>
  );
}
