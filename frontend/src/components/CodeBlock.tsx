import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Terminal } from 'lucide-react';

interface CodeBlockProps {
    language: string;
    value: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, value }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(value);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy code', err);
        }
    };

    return (
        <div className="relative group my-4 rounded-xl overflow-hidden border border-white/10 bg-[#0a0f1d] shadow-2xl">
            {/* Header do Bloco de Código */}
            <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
                <div className="flex items-center gap-2">
                    <Terminal size={14} className="text-white/40" />
                    <span className="text-xs font-mono font-bold text-white/60 lowercase">
                        {language || 'text'}
                    </span>
                </div>

                <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-white/10 transition-colors"
                    title="Copiar código"
                >
                    {copied ? (
                        <>
                            <Check size={14} className="text-emerald-400" />
                            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Copiado</span>
                        </>
                    ) : (
                        <>
                            <Copy size={14} className="text-white/40 group-hover:text-white/80 transition-colors" />
                            <span className="text-[10px] font-bold text-white/40 group-hover:text-white/80 uppercase tracking-wider transition-colors">Copiar</span>
                        </>
                    )}
                </button>
            </div>

            {/* Área do Código Highlighting */}
            <div className="relative text-xs sm:text-sm">
                <SyntaxHighlighter
                    language={language || 'text'}
                    style={vscDarkPlus}
                    customStyle={{
                        margin: 0,
                        padding: '1.5rem',
                        background: 'transparent',
                        fontSize: 'inherit',
                        lineHeight: '1.6',
                    }}
                    wrapLongLines={true}
                    PreTag="div"
                >
                    {value}
                </SyntaxHighlighter>
            </div>
        </div>
    );
};
