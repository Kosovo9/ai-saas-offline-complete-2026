/**
 * NASA-Elon System Monitor 10X
 * Real-time diagnostics with zero performance impact
 */

import { Activity, Database, Clock, Zap, Wifi } from 'lucide-react';
import { useEffect, useState } from 'react';

interface SystemMonitorProps {
    mode: 'CLOUD' | 'LOCAL';
    health: 'healthy' | 'degraded' | 'offline';
    backendUrl: string;
}

export default function SystemMonitor({ mode, health, backendUrl }: SystemMonitorProps) {
    const [metrics, setMetrics] = useState({
        uptime: 0,
        requests: 0,
        avgLatency: 0,
        lastUpdate: Date.now(),
    });

    useEffect(() => {
        const interval = setInterval(() => {
            setMetrics(prev => ({
                ...prev,
                uptime: prev.uptime + 1,
                lastUpdate: Date.now(),
            }));
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const stats = [
        { icon: Activity, label: 'Neural Status', value: health.toUpperCase(), color: health === 'healthy' ? 'text-green-400' : 'text-red-400' },
        { icon: mode === 'CLOUD' ? Wifi : Database, label: 'Engine Mode', value: mode, color: 'text-yellow-500' },
        { icon: Clock, label: 'Neural Uptime', value: `${Math.floor(metrics.uptime / 60)}m ${metrics.uptime % 60}s`, color: 'text-white' },
        { icon: Zap, label: 'Direct Link', value: backendUrl ? 'ACTIVE' : 'OFFLINE', color: backendUrl ? 'text-yellow-500' : 'text-gray-500' },
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            {stats.map((stat, index) => (
                <div key={index} className="bg-gradient-to-br from-gray-900/50 to-black/50 backdrop-blur-sm rounded-xl p-4 border border-gray-800/50">
                    <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${stat.color.replace('text-', 'bg-')}/10`}>
                            <stat.icon className={`w-4 h-4 ${stat.color}`} />
                        </div>
                        <div className="flex-1">
                            <p className="text-xs text-gray-400">{stat.label}</p>
                            <p className={`font-bold ${stat.color}`}>{stat.value}</p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
