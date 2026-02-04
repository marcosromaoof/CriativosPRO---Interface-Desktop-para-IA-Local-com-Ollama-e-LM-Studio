import { useState, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Activity, Zap, Clock, Database, BarChart2, Server } from 'lucide-react';

interface DashboardViewProps {
    socket: Socket | null;
}

export function DashboardView({ socket }: DashboardViewProps) {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!socket) return;

        const fetchData = () => {
            socket.emit('get_dashboard_data', {});
        };

        // Escuta a resposta
        socket.on('dashboard_data', (data) => {
            setStats(data);
            setLoading(false);
        });

        // Busca inicial
        fetchData();

        // Atualiza a cada 5 segundos
        const interval = setInterval(fetchData, 5000);

        return () => {
            socket.off('dashboard_data');
            clearInterval(interval);
        };
    }, [socket]);

    const formatNumber = (num: number) => {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
        return num.toString();
    };

    if (loading || !stats) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-white/20 animate-pulse">
                <Activity size={48} className="mb-4" />
                <p className="uppercase tracking-widest text-xs font-bold">Carregando Telemetria...</p>
            </div>
        );
    }

    return (
        <div className="h-full overflow-y-auto p-12 animate-fade-in">
            <header className="mb-10">
                <h1 className="text-3xl font-bold font-outfit mb-2 flex items-center gap-3">
                    <BarChart2 className="text-electric-blue" />
                    Centro de Comando
                </h1>
                <p className="text-white/40 text-sm">Visão geral de performance e consumo da IA.</p>
            </header>

            {/* Grid de Cards Principais */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                <StatCard
                    icon={<Database className="text-purple-500" />}
                    label="Total de Tokens"
                    value={formatNumber(stats.totals.total_tokens)}
                    subvalue="Input + Output processados"
                    color="purple"
                />
                <StatCard
                    icon={<Zap className="text-yellow-500" />}
                    label="Requisições"
                    value={stats.totals.total_requests.toString()}
                    subvalue="Sessões de geração"
                    color="yellow"
                />
                <StatCard
                    icon={<Clock className="text-emerald-500" />}
                    label="Latência Média"
                    value={`${stats.totals.avg_latency.toFixed(2)}s`}
                    subvalue="Tempo de resposta"
                    color="emerald"
                />
                <StatCard
                    icon={<Activity className="text-pink-500" />}
                    label="Estabilidade"
                    value="100%"
                    subvalue="Sistema Operacional"
                    color="pink"
                />
            </div>

            {/* Seção de Provedores */}
            <div className="glass-panel p-8 rounded-3xl border border-white/5">
                <h3 className="text-xs font-bold uppercase tracking-widest text-white/50 mb-6 flex items-center gap-2">
                    <Server size={14} /> Performance por Motor
                </h3>

                <div className="space-y-4">
                    {stats.providers.length === 0 ? (
                        <p className="text-white/20 text-sm italic py-4">Nenhum dado registrado ainda.</p>
                    ) : (
                        stats.providers.map((p: any, idx: number) => (
                            <div key={idx} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-lg bg-black/30 flex items-center justify-center text-xs font-bold uppercase text-white/60">
                                        {p.provider.substring(0, 2)}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-sm uppercase tracking-wide">{p.provider}</h4>
                                        <p className="text-[10px] text-white/40">{p.count} gerações</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <span className="text-sm font-mono font-bold text-electric-blue">{p.latency.toFixed(2)}s</span>
                                    <p className="text-[10px] text-white/40">latência média</p>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, label, value, subvalue, color }: any) {
    const colorClasses: any = {
        purple: "bg-purple-500/10 border-purple-500/20 text-purple-400",
        yellow: "bg-yellow-500/10 border-yellow-500/20 text-yellow-400",
        emerald: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
        pink: "bg-pink-500/10 border-pink-500/20 text-pink-400",
    };

    return (
        <div className={`p-6 rounded-2xl border backdrop-blur-md relative overflow-hidden group transition-all hover:-translate-y-1 ${colorClasses[color]}`}>
            <div className="flex justify-between items-start mb-4">
                <div className="p-3 bg-white/5 rounded-xl">
                    {icon}
                </div>
            </div>
            <div className="relative z-10">
                <h3 className="text-3xl font-bold font-outfit mb-1 text-white">{value}</h3>
                <p className="text-[10px] font-bold uppercase tracking-widest opacity-60 mb-1">{label}</p>
                <p className="text-[10px] opacity-40">{subvalue}</p>
            </div>

            {/* Glow effect */}
            <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full blur-2xl opacity-20 ${colorClasses[color].split(" ")[0]}`}></div>
        </div>
    );
}
