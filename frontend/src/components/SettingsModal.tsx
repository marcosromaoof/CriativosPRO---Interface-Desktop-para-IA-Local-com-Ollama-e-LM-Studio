import { useEffect } from 'react';
import { SettingsView } from './SettingsView';
import { X } from 'lucide-react';
import { Socket } from 'socket.io-client';

interface SettingsModalProps {
    socket: Socket | null;
    onClose: () => void;
}

export function SettingsModal({ socket, onClose }: SettingsModalProps) {
    // Fechar com ESC
    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [onClose]);

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#050811]/80 backdrop-blur-md animate-in fade-in duration-200">
            {/* Overlay Click to Close */}
            <div className="absolute inset-0" onClick={onClose} />

            {/* Modal Container */}
            <div className="relative w-full max-w-6xl h-[85vh] bg-[#0a0f1d] border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 flex flex-col">

                {/* Header do Modal */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#0a0f1d] shrink-0">
                    <div className="flex items-center gap-3">
                        <span className="text-sm font-bold text-white/40 uppercase tracking-[0.2em]">Configurações do Sistema</span>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-white/40 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                        title="Fechar"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Conteúdo (Reutilizando SettingsView) */}
                <div className="flex-1 overflow-hidden relative">
                    {/* 
                        O SettingsView original tem 'flex h-full'.
                        Como estamos num container flex-col e este div é flex-1, 
                        o SettingsView deve ocupar todo o espaço.
                     */}
                    <div className="h-full w-full">
                        <SettingsView socket={socket} />
                    </div>
                </div>
            </div>
        </div>
    );
}
