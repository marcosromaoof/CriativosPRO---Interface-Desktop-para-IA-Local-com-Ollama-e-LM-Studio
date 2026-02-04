import React, { useState, memo } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Zap, Clock, Cpu, Volume2, Copy, Trash2, RefreshCw, Download, Check, StopCircle, Loader2 } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useTypewriter } from '../hooks/useTypewriter';
import { CodeBlock } from './CodeBlock';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface MessageMetrics {
    tokens?: number;
    tps?: number;
    duration?: number;
}

interface MessageBubbleProps {
    role: 'user' | 'assistant' | 'system';
    content: string;
    metrics?: MessageMetrics;
    isPlaying?: boolean;
    isAudioLoading?: boolean;
    onPlay?: () => void;
    timestamp?: string;
    onRetry?: () => void;
    onDelete?: () => void;
}

const MessageBubbleBase: React.FC<MessageBubbleProps> = ({ role, content, metrics, timestamp, onRetry, onDelete, onPlay, isPlaying = false, isAudioLoading = false }) => {
    const isUser = role === 'user';
    const isBot = role === 'assistant';
    const [copied, setCopied] = useState(false);

    // Efeito de digitação apenas para mensagens recentes do bot
    // Assumimos que se tem 'tps' ou metrics, já finalizou, mas para streaming é melhor controlar pelo pai.
    // Hack simplificado: Se content mudar, ativa. Se for mount inicial com texto longo, assume histórico -> desabilita (mas aqui não sabemos).
    // Para simplificar: Bot sempre usa Typewriter, mas se for muito longo no mount inicial, o hook vai catch up rápido.
    // Melhoria: Receber um prop 'isStreaming' seria ideal, mas vamos usar o hook adaptativo.
    const displayedContent = useTypewriter(content, 10, isBot && content !== '...');


    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Falha ao copiar:', err);
        }
    };

    const handleDownload = () => {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `criativos-pro-msg-${new Date().getTime()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handlePlay = () => {
        if (onPlay) onPlay();
    };

    return (
        <div className={cn(
            "flex w-full gap-4 mb-8 animate-in fade-in slide-in-from-bottom-2 duration-400 group",
            isUser ? "flex-row-reverse" : "flex-row"
        )}>
            {/* Avatar Section */}
            <div className={cn(
                "flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-300",
                isUser
                    ? "bg-[#3b82f6]/10 border-[#3b82f6]/30 text-[#3b82f6] shadow-[0_0_20px_rgba(59,130,246,0.15)]"
                    : "bg-white/5 border-white/10 text-white/40 group-hover:text-white"
            )}>
                {isUser ? <User size={18} /> : <Bot size={18} />}
            </div>

            {/* Message Content Section */}
            <div className={cn(
                "flex flex-col max-w-[85%] gap-2",
                isUser ? "items-end" : "items-start"
            )}>
                <div className={cn(
                    "px-6 py-4 rounded-2xl text-sm leading-relaxed transition-all relative",
                    isUser
                        ? "bg-[#3b82f6] text-white rounded-tr-none shadow-xl shadow-blue-900/20"
                        : "bg-[#12182b]/50 border border-white/10 backdrop-blur-md text-white/90 rounded-tl-none w-full"
                )}>
                    <div className="prose prose-invert prose-sm max-w-none">
                        {content === '...' ? (
                            <div className="flex items-center gap-1 py-2">
                                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                            </div>
                        ) : (
                            <ReactMarkdown
                                components={{
                                    // P: Adicionar margem inferior para separar parágrafos
                                    p: ({ children }) => <p className="mb-4 leading-relaxed font-medium last:mb-0">{children}</p>,
                                    // Code: Tratamento Inteligente (Inline vs CodeBlock)
                                    code({ node, inline, className, children, ...props }: any) {
                                        const match = /language-(\w+)/.exec(className || '');
                                        const codeContent = String(children).replace(/\n$/, '');

                                        if (!inline && match) {
                                            return (
                                                <CodeBlock
                                                    language={match[1]}
                                                    value={codeContent}
                                                />
                                            );
                                        } else if (!inline) {
                                            // Bloco sem linguagem definida mas é bloco (multilinha)
                                            return (
                                                <CodeBlock
                                                    language="text"
                                                    value={codeContent}
                                                />
                                            );
                                        }

                                        // Código Inline (`const a = 1`)
                                        return (
                                            <code className="bg-black/30 px-1.5 py-0.5 rounded text-emerald-400 font-mono text-[12px]" {...props}>
                                                {children}
                                            </code>
                                        );
                                    },

                                    // Pre: Wrapper transparente (o CodeBlock já cuida da estrutura)
                                    pre: ({ children }) => <>{children}</>,
                                    // Títulos: Garantir visibilidade e hierarquia
                                    h1: ({ children }) => <h1 className="text-xl font-bold text-white mt-6 mb-4 pb-2 border-b border-white/10">{children}</h1>,
                                    h2: ({ children }) => <h2 className="text-lg font-bold text-white/90 mt-5 mb-3">{children}</h2>,
                                    h3: ({ children }) => <h3 className="text-base font-bold text-white/80 mt-4 mb-2">{children}</h3>,
                                    // Listas: Garantir indentação
                                    ul: ({ children }) => <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>,
                                    ol: ({ children }) => <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>,
                                    li: ({ children }) => <li className="text-white/80 ml-2">{children}</li>,
                                }}
                            >
                                {isBot ? displayedContent : content}
                            </ReactMarkdown>
                        )}
                    </div>
                </div>

                {/* Footer: Layout Invertido - Ações (Esq) | Métricas (Dir) */}
                <div className={cn(
                    "flex items-center gap-4 px-2 w-full mt-1",
                    isUser ? "justify-end" : "justify-between"
                )}>

                    {/* 1. Lado Esquerdo: Barra de Ações (Sempre visível) */}
                    <div className="flex items-center gap-1 opacity-100">
                        <ActionButton icon={copied ? <Check size={13} /> : <Copy size={13} />} onClick={handleCopy} title="Copiar" />
                        <ActionButton icon={<Download size={13} />} onClick={handleDownload} title="Baixar texto" />

                        {isBot && (
                            <>
                                <div className="w-px h-3 bg-white/10 mx-1"></div>
                                <div className="flex items-center gap-1.5 opacity-100 transition-opacity">
                                    <ActionButton
                                        icon={isAudioLoading ? <Loader2 size={13} className="animate-spin text-electric-blue" /> : (isPlaying ? <StopCircle size={13} className="text-electric-blue" /> : <Volume2 size={13} />)}
                                        onClick={handlePlay}
                                        title={isAudioLoading ? "Gerando áudio..." : (isPlaying ? "Parar leitura" : "Ouvir resposta")}
                                        className={isPlaying ? "bg-electric-blue/10 text-electric-blue" : ""}
                                    />
                                </div>
                                {onRetry && <ActionButton icon={<RefreshCw size={13} />} onClick={onRetry} title="Gerar nova resposta" />}
                            </>
                        )}

                        <div className="w-px h-3 bg-white/10 mx-1"></div>
                        <ActionButton
                            icon={<Trash2 size={13} className="text-red-400/70 hover:text-red-400" />}
                            onClick={onDelete}
                            title="Excluir mensagem"
                        />
                    </div>

                    {/* 2. Lado Direito: Timestamp e Métricas (Solicitado pelo usuário) */}
                    <div className="flex items-center gap-4 justify-end">
                        {isBot && metrics && (
                            <div className="flex items-center gap-3 text-[9px] font-bold text-white/20 uppercase tracking-[0.15em] hidden sm:flex text-right mr-3">
                                <div className="flex items-center gap-1.5" title="Tokens gerados">
                                    <Cpu size={10} className="opacity-50" />
                                    <span>{metrics.tokens ?? 0}</span>
                                </div>
                                <div className="flex items-center gap-1.5" title="Velocidade">
                                    <Zap size={10} className="opacity-50 text-emerald-500" />
                                    <span>{metrics.tps?.toFixed(1) ?? '0.0'} TPS</span>
                                </div>
                                <div className="flex items-center gap-1.5" title="Duração">
                                    <Clock size={10} className="opacity-50" />
                                    <span>{metrics.duration?.toFixed(1) ?? '0.0'}s</span>
                                </div>
                            </div>
                        )}

                        {timestamp && <span className="text-[9px] text-white/20 font-bold uppercase tracking-widest">{timestamp}</span>}
                    </div>
                </div>
            </div>
        </div>
    );
};

// Export com memoização para otimizar performance durante streaming
export const MessageBubble = memo(MessageBubbleBase);

// Componente auxiliar
function ActionButton({ icon, onClick, title, className }: any) {
    return (
        <button
            onClick={onClick}
            title={title}
            className={cn(
                "w-7 h-7 flex items-center justify-center rounded-lg hover:bg-white/10 text-white/30 hover:text-white transition-all active:scale-95",
                className
            )}
        >
            {icon}
        </button>
    );
}
