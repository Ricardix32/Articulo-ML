import React, { useState } from 'react';
import { ShieldCheck, Lock, User } from 'lucide-react';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Por favor, complete todos los campos.');
      return;
    }

    setLoading(true);
    
    // Simulación de autenticación (fácil de validar en demostraciones académicas)
    setTimeout(() => {
      if (username === 'admin' && password === 'tesis2026') {
        onLogin(true);
      } else {
        setError('Credenciales incorrectas. Pruebe con admin / tesis2026');
      }
      setLoading(false);
    }, 800);
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-[#0b111e] px-4 overflow-hidden">
      {/* Círculos decorativos de fondo con difuminado */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-900/20 rounded-full blur-3xl animate-pulse-slow"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-900/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '3s' }}></div>

      <div className="w-full max-w-md glass p-8 rounded-2xl shadow-2xl relative z-10 animate-fade-in">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-navy-800 rounded-2xl flex items-center justify-center border border-navy-700 shadow-inner mb-4">
            <ShieldCheck className="w-9 h-9 text-blue-400" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Riesgo Crediticio
          </h1>
          <p className="text-sm text-gray-400 mt-1">Plataforma Analítica y Predictiva</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-3 bg-red-900/30 border border-red-500/30 text-red-300 text-sm rounded-lg text-center animate-pulse">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-300 uppercase tracking-wider block">Usuario</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <User className="w-5 h-5 text-gray-500" />
              </span>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ingrese su usuario"
                className="w-full pl-10 pr-4 py-3 glass-input rounded-lg text-white text-sm outline-none transition-all"
                disabled={loading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-300 uppercase tracking-wider block">Contraseña</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Lock className="w-5 h-5 text-gray-500" />
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-3 glass-input rounded-lg text-white text-sm outline-none transition-all"
                disabled={loading}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform active:scale-95 disabled:opacity-50 disabled:scale-100 flex items-center justify-center"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              'Iniciar Sesión'
            )}
          </button>
        </form>

        <div className="mt-8 text-center text-xs text-gray-500">
          Uso académico autorizado - Credenciales: <code className="bg-navy-800 text-gray-300 px-1.5 py-0.5 rounded">admin</code> / <code className="bg-navy-800 text-gray-300 px-1.5 py-0.5 rounded">tesis2026</code>
        </div>
      </div>
    </div>
  );
}
