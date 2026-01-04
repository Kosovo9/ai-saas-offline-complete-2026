import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import {
    Zap,
    Shield,
    TrendingUp,
    ChevronRight,
    Star,
    Cpu,
    Globe,
    Lock,
    ArrowRight
} from 'lucide-react';

import { API_ENDPOINTS } from '../config/api';

const LandingPage: React.FC = () => {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleCheckout = async (tier: string, method: 'mercadopago' | 'paypal' = 'mercadopago') => {
        setIsLoading(true);
        try {
            const response = await axios.post(API_ENDPOINTS.CHECKOUT, {
                tier: tier.toUpperCase(),
                email: email || undefined,
                method: method
            });

            if (response.data.url) {
                window.location.href = response.data.url;
            }
        } catch (error) {
            console.error('Checkout failed:', error);
            alert('Payment system error. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const tiers = [
        {
            name: 'Foundation',
            price: '$9,999',
            description: 'The blueprint for your first million.',
            features: ['Access to Ghost CEO Basic', 'Antigravity Market Scanner', '24/7 Neural Support'],
            gradient: 'from-gray-800 to-gray-900',
            button: 'Start Foundation'
        },
        {
            name: 'Visionary',
            price: '$49,999',
            description: 'Accelerate to billionaire status.',
            features: ['Full Ghost CEO Advisor', 'Real-time Arbitrage Engine', 'Priority API Access', 'Custom AI Strategy'],
            gradient: 'from-yellow-600/20 to-amber-900/40',
            highlight: true,
            button: 'Become Visionary'
        },
        {
            name: 'Immortal',
            price: '$199,999',
            description: 'Legacy-level wealth automation.',
            features: ['Private Instanced AI', 'Direct Antigravity Execution', 'Unlimited Revenue Agents', 'Personal Success Manager'],
            gradient: 'from-amber-500/10 via-yellow-600/20 to-yellow-900/40',
            button: 'Get Immortal Tier'
        }
    ];

    return (
        <div className="min-h-screen bg-black text-white selection:bg-yellow-500/30">
            {/* Background Effects */}
            <div className="fixed inset-0 cyber-grid opacity-20 pointer-events-none" />
            <div className="fixed inset-0 bg-gradient-to-b from-yellow-500/5 via-transparent to-black pointer-events-none" />

            {/* Hero Section */}
            <section className="relative pt-32 pb-20 px-6">
                <div className="max-w-7xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-yellow-500/30 bg-yellow-500/5 mb-6">
                            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                            <span className="text-xs font-cyber tracking-widest text-yellow-500 uppercase">Version 2.0 Premium Prime</span>
                        </div>

                        <h1 className="text-6xl md:text-8xl font-black font-cyber mb-8 leading-tight">
                            THE ONLY AI SYSTEM THAT <br />
                            <span className="text-gold">GUARANTEES</span> YOUR WEALTH.
                        </h1>

                        <p className="max-w-2xl mx-auto text-gray-400 text-lg md:text-xl mb-12 font-light">
                            Don't just use AI. Deploy it. Antigravity V2 is the first autonomous engine designed
                            exclusively for high-net-worth individuals to automate the billion-dollar path.
                        </p>

                        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
                            <div className="flex p-1 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl w-full max-w-md">
                                <input
                                    type="email"
                                    placeholder="Enter your billionaire email..."
                                    className="flex-1 bg-transparent border-none outline-none px-4 py-3 placeholder:text-gray-600"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                                <button className="bg-gold px-6 py-3 rounded-xl font-bold text-black hover:scale-105 transition-transform flex items-center gap-2">
                                    JOIN WAITLIST <ChevronRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="py-20 border-y border-white/5">
                <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
                    {[
                        { label: 'Market Analysis/Sec', value: '450TB+' },
                        { label: 'Guaranteed ROI', value: '150%+' },
                        { label: 'Active Users', value: 'Elite Only' },
                        { label: 'Uptime', value: '99.99%' },
                    ].map((stat, i) => (
                        <div key={i} className="text-center">
                            <div className="text-2xl md:text-3xl font-cyber text-gold mb-2">{stat.value}</div>
                            <div className="text-xs uppercase tracking-widest text-gray-500">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Pricing Tiers */}
            <section className="py-32 px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-20">
                        <h2 className="text-4xl md:text-5xl font-cyber font-bold mb-4">SELECT YOUR TIER</h2>
                        <p className="text-gray-500">Every plan is an investment in your future empire.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {tiers.map((tier, i) => (
                            <motion.div
                                key={i}
                                whileHover={{ y: -10 }}
                                className={`relative p-8 rounded-3xl border ${tier.highlight ? 'border-yellow-500 scale-105 z-10' : 'border-white/10'} glass-card flex flex-col`}
                            >
                                {tier.highlight && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gold px-4 py-1 rounded-full text-black text-xs font-black tracking-tighter">
                                        MOST EXCLUSIVE
                                    </div>
                                )}

                                <h3 className="text-2xl font-cyber mb-2">{tier.name}</h3>
                                <div className="text-4xl font-bold mb-4">{tier.price}</div>
                                <p className="text-gray-400 mb-8 text-sm">{tier.description}</p>

                                <div className="space-y-4 mb-12 flex-1">
                                    {tier.features.map((feature, j) => (
                                        <div key={j} className="flex items-center gap-3 text-sm">
                                            <Zap className="w-4 h-4 text-yellow-500" />
                                            <span>{feature}</span>
                                        </div>
                                    ))}
                                </div>

                                <div className="space-y-3">
                                    <button
                                        onClick={() => handleCheckout(tier.name, 'mercadopago')}
                                        disabled={isLoading}
                                        className={`w-full py-4 rounded-xl font-black font-cyber text-xs tracking-widest transition-all flex items-center justify-center gap-2 ${tier.highlight
                                            ? 'bg-gold text-black hover:shadow-[0_0_30px_rgba(234,179,8,0.4)]'
                                            : 'bg-white/10 text-white hover:bg-white/20 border border-white/10'
                                            }`}>
                                        {isLoading ? 'PROCESSING...' : `PAY BY CARD`}
                                    </button>
                                    <button
                                        onClick={() => handleCheckout(tier.name, 'paypal')}
                                        disabled={isLoading}
                                        className="w-full py-4 rounded-xl font-black font-cyber text-xs tracking-widest transition-all flex items-center justify-center gap-2 bg-blue-600/10 text-blue-400 border border-blue-500/30 hover:bg-blue-600/20"
                                    >
                                        {isLoading ? '...' : `PAY WITH PAYPAL`}
                                    </button>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="py-40 px-6 bg-yellow-500/[0.02]">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
                    {[
                        {
                            icon: <Shield className="w-8 h-8 text-yellow-500" />,
                            title: "Quantum Defense",
                            desc: "Military-grade encryption for all your financial data and AI interactions."
                        },
                        {
                            icon: <TrendingUp className="w-8 h-8 text-yellow-500" />,
                            title: "Reverse Engineering",
                            desc: "Deconstruct top-tier cash flows and replicate them with 98% accuracy."
                        },
                        {
                            icon: <Cpu className="w-8 h-8 text-yellow-500" />,
                            title: "10x Speed Logic",
                            desc: "Decisions made at the speed of light using our proprietary LLM architecture."
                        },
                        {
                            icon: <Globe className="w-8 h-8 text-yellow-500" />,
                            title: "Global Reach",
                            desc: "Automated accounts across 50+ countries for true diversification."
                        },
                        {
                            icon: <Lock className="w-8 h-8 text-yellow-500" />,
                            title: "Blind Trust",
                            desc: "The AI operates without emotional bias, following only the math of profit."
                        },
                        {
                            icon: <ArrowRight className="w-8 h-8 text-yellow-500" />,
                            title: "Direct Execution",
                            desc: "Don't just get advice—Antigravity executes the plan for you."
                        },
                    ].map((f, i) => (
                        <div key={i} className="group">
                            <div className="mb-6 p-4 rounded-2xl bg-white/5 border border-white/10 group-hover:border-yellow-500/50 transition-colors w-fit">
                                {f.icon}
                            </div>
                            <h4 className="text-xl font-cyber mb-3">{f.title}</h4>
                            <p className="text-gray-500 leading-relaxed">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Footer */}
            <footer className="py-20 px-6 border-t border-white/5 text-center">
                <div className="font-cyber text-2xl font-black text-gold mb-4">ANTIGRAVITY V2</div>
                <p className="text-gray-600 text-sm">Created for those who refuse to settle for millions.</p>
                <div className="mt-8 flex justify-center gap-6 text-gray-500 text-xs">
                    <a href="#" className="hover:text-yellow-500">TERMS OF SERVICE</a>
                    <a href="#" className="hover:text-yellow-500">PRIVACY PROTOCOL</a>
                    <a href="#" className="hover:text-yellow-500">CONTACT</a>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
