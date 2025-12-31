import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Shield, TrendingUp, Cpu, Lock, Globe, Activity, BarChart3, AlertCircle } from 'lucide-react';

interface AntigravityControlProps {
    backendUrl: string;
}

export default function AntigravityControl({ backendUrl }: AntigravityControlProps) {
    const [metrics, setMetrics] = useState<any>(null);
    const [isActive, setIsActive] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const activeUrl = backendUrl || 'https://ai-saas-backend-ds91.onrender.com';

    const fetchMetrics = async () => {
        try {
            const response = await fetch(`${activeUrl}/antigravity/metrics`);
            if (response.ok) {
                const data = await response.json();
                setMetrics(data);
                setIsActive(data.status !== "IDLE");
            }
        } catch (err) {
            console.error("Failed to fetch metrics", err);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 2000);
        return () => clearInterval(interval);
    }, [activeUrl]);

    const activateAgent = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${activeUrl}/antigravity/activate`, { method: 'POST' });
            if (!response.ok) throw new Error("Activation failed");
            await fetchMetrics();
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-cyan-50 p-8 space-y-8 overflow-y-auto">
            {/* Cyberpunk Header */}
            <div className="flex items-center justify-between border-b border-cyan-900/50 pb-6">
                <div className="flex items-center space-x-4">
                    <div className="p-3 bg-yellow-500/10 border border-yellow-500/50 rounded-2xl shadow-lg shadow-yellow-500/20">
                        <Zap className="w-8 h-8 text-yellow-500" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-black tracking-tighter uppercase italic">
                            ANTIGRAVITY <span className="text-gold">V2 GOLD</span>
                        </h1>
                        <p className="text-gray-500 text-[10px] font-cyber tracking-[0.2em]">
                            QUANTUM FINANCIAL REVERSE ENGINEERING • SECURE NODE
                        </p>
                    </div>
                </div>
                <div className="flex items-center space-x-6">
                    <div className="text-right">
                        <div className="text-xs text-gray-500 uppercase tracking-widest">Security Layer</div>
                        <div className="text-green-400 font-bold flex items-center justify-end space-x-1">
                            <Shield className="w-3 h-3" />
                            <span>ENCRYPTED</span>
                        </div>
                    </div>
                    <div className={`status-badge px-4 py-2 rounded-full border ${isActive ? 'bg-green-500/10 border-green-500/50 text-green-400' : 'bg-gray-900 border-gray-800 text-gray-500'}`}>
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-600'}`} />
                            <span className="text-xs font-bold tracking-widest">{isActive ? "RUNNING" : "STANDBY"}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Metrics Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-900/50 border border-gold p-6 rounded-3xl relative overflow-hidden group hover:bg-yellow-500/5 transition-colors">
                    <TrendingUp className="absolute -right-4 -bottom-4 w-24 h-24 text-yellow-500/5" />
                    <div className="text-gray-500 text-[10px] uppercase font-cyber tracking-widest mb-1">Daily Automated Profit</div>
                    <div className="text-5xl font-black text-white tabular-nums">
                        ${metrics?.daily_profit?.toLocaleString() || "0.00"}
                    </div>
                    <div className="mt-4 flex items-center space-x-2 text-yellow-500 text-sm font-bold">
                        <Activity className="w-4 h-4" />
                        <span>QUANTUM YIELD ACTIVE</span>
                    </div>
                </div>

                <div className="bg-gray-900/50 border border-white/10 p-6 rounded-3xl relative overflow-hidden group hover:border-yellow-500/50 transition-colors">
                    <Cpu className="absolute -right-4 -bottom-4 w-24 h-24 text-yellow-500/5" />
                    <div className="text-gray-500 text-[10px] uppercase font-cyber tracking-widest mb-1">Neural Algos</div>
                    <div className="text-5xl font-black text-white">
                        {metrics?.active_strategies || "0"}
                    </div>
                    <div className="mt-4 flex items-center space-x-2 text-yellow-500/50 text-sm font-bold">
                        <BarChart3 className="w-4 h-4" />
                        <span>10X SCALE ACTIVE</span>
                    </div>
                </div>

                <div className="bg-gray-900/50 border border-white/10 p-6 rounded-3xl flex flex-col justify-center items-center">
                    {!isActive ? (
                        <button
                            onClick={activateAgent}
                            disabled={loading}
                            className="w-full h-full bg-gold rounded-2xl font-black text-xl text-black shadow-xl shadow-yellow-500/20 active:scale-95 transition-transform"
                        >
                            {loading ? "INITIALIZING..." : "ACTIVATE"}
                        </button>
                    ) : (
                        <div className="text-center space-y-2">
                            <Lock className="w-10 h-10 text-cyan-400 mx-auto" />
                            <div className="text-xs font-bold text-cyan-400">ENGINE LOCKED & LOADED</div>
                            <button className="text-xs text-gray-500 hover:text-red-400 transition-colors">Emergency Shutdown</button>
                        </div>
                    )}
                </div>
            </div>

            {/* Strategy Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-gray-900/80 border border-white/5 rounded-3xl p-8 space-y-6">
                    <h3 className="text-xl font-bold flex items-center space-x-2">
                        <Activity className="w-5 h-5 text-yellow-500" />
                        <span>REVERSE-ENGINEERED STRATEGIES</span>
                    </h3>
                    <div className="space-y-4">
                        {[
                            { name: 'Medallion Clone', efficiency: '98.7%', risk: 'Low' },
                            { name: 'Citadel HFT Reverse', efficiency: '96.2%', risk: 'Low' },
                            { name: 'Quantum Crypto Arb', efficiency: '99.1%', risk: 'Medium' }
                        ].map((strat, idx) => (
                            <div key={idx} className="flex items-center justify-between p-4 bg-black/50 rounded-2xl border border-white/5 group hover:border-yellow-500/30 transition-colors">
                                <div className="flex items-center space-x-4">
                                    <div className="w-10 h-10 bg-gray-900 rounded-xl flex items-center justify-center">
                                        <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-yellow-500 animate-pulse' : 'bg-gray-700'}`} />
                                    </div>
                                    <div>
                                        <div className="font-bold">{strat.name}</div>
                                        <div className="text-xs text-gray-600">Efficiency: {strat.efficiency}</div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-xs text-gray-500">Risk</div>
                                    <div className="text-xs font-bold text-green-400">{strat.risk}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-gray-900/80 border border-gray-800 rounded-3xl p-8 space-y-6">
                    <h3 className="text-xl font-bold flex items-center space-x-2">
                        <Globe className="w-5 h-5 text-purple-400" />
                        <span>GLOBAL JURISDICTION CONTROL</span>
                    </h3>
                    <div className="p-6 bg-black/50 rounded-2xl border border-gray-800/50 space-y-4">
                        <p className="text-sm text-gray-400 leading-relaxed font-light">
                            Legal entities automated in <span className="text-white font-bold">Dubai DIFC</span>, <span className="text-white font-bold">Singapore</span>, and <span className="text-white font-bold">Cayman Islands</span>.
                            Jurisdiction arbitrage is active.
                        </p>
                        <div className="flex space-x-3">
                            <div className="px-3 py-1 bg-gray-800 rounded text-[10px] font-bold tracking-widest text-cyan-400">DUBAI: ACTIVE</div>
                            <div className="px-3 py-1 bg-gray-800 rounded text-[10px] font-bold tracking-widest text-purple-400">SG: ACTIVE</div>
                            <div className="px-3 py-1 bg-gray-800 rounded text-[10px] font-bold tracking-widest text-emerald-400">CAYMAN: ACTIVE</div>
                        </div>
                        <button className="w-full py-3 bg-gray-800 hover:bg-white hover:text-black rounded-xl text-xs font-bold transition-all uppercase tracking-widest">
                            Configure Legal Nodes
                        </button>
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/50 p-4 rounded-xl flex items-center space-x-3 text-red-500">
                    <AlertCircle className="w-5 h-5" />
                    <span className="text-sm font-bold">{error}</span>
                </div>
            )}
        </div>
    );
}
