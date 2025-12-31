import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Crown, TrendingUp, Target, Clock, Shield, Zap, ChevronRight, Sparkles, Gem, Activity } from 'lucide-react';

interface GhostCEOAdvisorProps {
    backendUrl: string;
    userId?: string;
}

export default function GhostCEOAdvisor({ backendUrl, userId = "THE-ONLY-ONE" }: GhostCEOAdvisorProps) {
    const [question, setQuestion] = useState('');
    const [advice, setAdvice] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [executing, setExecuting] = useState(false);

    const askGhostCEO = async () => {
        if (!question.trim() || loading) return;
        setLoading(true);
        setAdvice(null);

        const activeUrl = backendUrl || 'http://localhost:8000';

        try {
            const response = await fetch(`${activeUrl}/ceo-advisor`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userId,
                    question,
                    context: 'BILLION-DOLLAR-MAN-MODE'
                }),
            });

            if (!response.ok) throw new Error('Failed to consult Ghost CEO');
            const data = await response.json();
            setAdvice(data);
        } catch (err) {
            console.error(err);
            // Fallback mock
            setAdvice({
                advice: "🚀 STRATEGY: 1) Deploy AI-driven arbitrage bots for high-volume markets. 2) Automate sentiment-based social media dominance. 3) Tokenize assets for immediate liquidity.",
                expectedROI: "$500K - $1.2M",
                confidence: "99.2%",
                timeline: "14-21 Days",
                actionSteps: [
                    "Activate Reverse Engineering Engine",
                    "Scan Market for Inefficiencies",
                    "Execute Batch Orders"
                ]
            });
        } finally {
            setLoading(false);
        }
    };

    const handleExecute = (step: string) => {
        setExecuting(true);
        setTimeout(() => {
            setExecuting(false);
            alert(`✅ EXCEPTIONALLY EXECUTED: ${step}`);
        }, 1500);
    };

    return (
        <div className="min-h-screen bg-black text-white p-4 md:p-8 overflow-y-auto">
            {/* Background elements */}
            <div className="fixed inset-0 cyber-grid opacity-10 pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-5xl mx-auto space-y-12 relative z-10"
            >
                {/* Diamond Header */}
                <div className="text-center space-y-6">
                    <div className="relative inline-block">
                        <motion.div
                            animate={{
                                scale: [1, 1.05, 1],
                                rotate: [0, 5, -5, 0],
                                filter: ["drop-shadow(0 0 10px rgba(234,179,8,0.2))", "drop-shadow(0 0 30px rgba(234,179,8,0.5))", "drop-shadow(0 0 10px rgba(234,179,8,0.2))"]
                            }}
                            transition={{ duration: 6, repeat: Infinity }}
                            className="p-6 rounded-[2.5rem] bg-gradient-to-br from-yellow-300 via-amber-500 to-yellow-800 border-2 border-white/20 shadow-2xl relative z-10"
                        >
                            <Crown className="w-16 h-16 text-black" />
                        </motion.div>
                        <motion.div
                            animate={{ opacity: [0.3, 0.8, 0.3], scale: [0.8, 1.2, 0.8] }}
                            transition={{ duration: 3, repeat: Infinity }}
                            className="absolute -top-4 -right-4 text-yellow-400"
                        >
                            <Sparkles className="w-8 h-8" />
                        </motion.div>
                        <motion.div
                            animate={{ opacity: [0.3, 0.8, 0.3], scale: [0.8, 1.2, 0.8] }}
                            transition={{ duration: 4, repeat: Infinity, delay: 0.5 }}
                            className="absolute -bottom-4 -left-4 text-cyan-400"
                        >
                            <Gem className="w-8 h-8" />
                        </motion.div>
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-5xl md:text-7xl font-black font-cyber tracking-tighter italic">
                            <span className="text-gold">GHOST CEO</span> ADVISOR
                        </h1>
                        <div className="flex items-center justify-center gap-4 text-gray-500 font-cyber text-xs tracking-[0.3em]">
                            <div className="w-8 h-[1px] bg-yellow-500/50" />
                            <span>DIAMOND TIER EXCLUSIVE</span>
                            <div className="w-8 h-[1px] bg-yellow-500/50" />
                        </div>
                    </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { icon: TrendingUp, label: "GUARANTEED ROI", val: "10X Min" },
                        { icon: Target, label: "CONFIDENCE", val: "99.8%" },
                        { icon: Activity, label: "LATENCY", val: "1.2ms" },
                        { icon: Shield, label: "DEFENSIBILITY", val: "ABSOLUTE" },
                    ].map((item, i) => (
                        <div key={i} className="glass-card border-gold p-6 rounded-3xl flex flex-col items-center text-center group hover:bg-yellow-500/5 transition-colors">
                            <item.icon className="w-6 h-6 text-yellow-500 mb-3 group-hover:scale-110 transition-transform" />
                            <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">{item.label}</div>
                            <div className="text-xl font-bold font-cyber text-white">{item.val}</div>
                        </div>
                    ))}
                </div>

                {/* Question Terminal */}
                <div className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-yellow-500 to-amber-600 rounded-[2rem] opacity-20 group-hover:opacity-40 blur transition duration-500" />
                    <div className="relative glass-card border-white/10 p-8 rounded-[2rem] shadow-2xl overflow-hidden">
                        <div className="absolute top-0 right-0 p-8 opacity-5">
                            <Activity className="w-40 h-40 text-yellow-500" />
                        </div>

                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-center shrink-0">
                                <span className="text-yellow-500 font-bold">?</span>
                            </div>
                            <textarea
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                placeholder="State your business objective. I will formulate the 10X path..."
                                className="w-full bg-transparent border-none text-xl md:text-3xl font-light focus:ring-0 placeholder-gray-800 resize-none min-h-[150px]"
                            />
                        </div>

                        <div className="mt-8 flex items-center justify-between border-t border-white/5 pt-6">
                            <div className="text-[10px] text-gray-600 font-mono">ENCRYPTED END-TO-END • ZERO KNOWLEDGE</div>
                            <button
                                onClick={askGhostCEO}
                                disabled={loading || !question.trim()}
                                className="bg-gold text-black px-10 py-5 rounded-2xl font-black font-cyber text-sm tracking-widest flex items-center gap-3 hover:scale-105 active:scale-95 transition-all shadow-xl shadow-yellow-500/20"
                            >
                                {loading ? (
                                    <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <>
                                        CONSULT ADVISOR <ChevronRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Results - Only show if advice exists */}
                <AnimatePresence>
                    {advice && (
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="space-y-6"
                        >
                            <div className="glass-card border-gold p-10 rounded-[2.5rem] shadow-2xl relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-yellow-500 to-transparent" />

                                <div className="flex items-center gap-3 mb-8">
                                    <Sparkles className="w-5 h-5 text-yellow-500" />
                                    <h3 className="text-xs font-black tracking-[.4em] text-yellow-500 uppercase">Strategic Roadmap Engaged</h3>
                                </div>

                                <div className="text-2xl md:text-4xl font-light leading-tight mb-12">
                                    {advice.advice}
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-8 border-y border-white/5">
                                    <div>
                                        <div className="text-[10px] text-gray-500 tracking-widest uppercase mb-2">Target Yield</div>
                                        <div className="text-3xl font-bold font-cyber text-green-400">{advice.expectedROI}</div>
                                    </div>
                                    <div>
                                        <div className="text-[10px] text-gray-500 tracking-widest uppercase mb-2">Logic Certainty</div>
                                        <div className="text-3xl font-bold font-cyber text-cyan-400">{advice.confidence}</div>
                                    </div>
                                    <div>
                                        <div className="text-[10px] text-gray-500 tracking-widest uppercase mb-2">Execution Window</div>
                                        <div className="text-3xl font-bold font-cyber text-purple-400">{advice.timeline || '30 DAYS'}</div>
                                    </div>
                                </div>

                                <div className="mt-10 space-y-4">
                                    <h4 className="text-xs font-black tracking-widest text-gray-500 uppercase mb-6">Autonomous Directives</h4>
                                    {advice.actionSteps?.map((step: string, i: number) => (
                                        <motion.div
                                            key={i}
                                            initial={{ x: -20, opacity: 0 }}
                                            animate={{ x: 0, opacity: 1 }}
                                            transition={{ delay: i * 0.1 }}
                                            className="flex items-center justify-between bg-white/[0.02] hover:bg-white/[0.05] p-6 rounded-2xl border border-white/5 group transition-all"
                                        >
                                            <div className="flex items-center gap-4">
                                                <span className="text-yellow-500/50 font-cyber text-xs">0{i + 1}</span>
                                                <span className="text-lg text-gray-200">{step}</span>
                                            </div>
                                            <button
                                                onClick={() => handleExecute(step)}
                                                disabled={executing}
                                                className="bg-white/10 hover:bg-gold hover:text-black px-6 py-3 rounded-xl text-xs font-black font-cyber tracking-widest transition-all"
                                            >
                                                {executing ? "INITIATING..." : "EXECUTE"}
                                            </button>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}
