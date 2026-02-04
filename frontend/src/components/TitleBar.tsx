import { Minus, Square, X } from 'lucide-react';

// Declaração do tipo para o Electron IPC
declare const window: Window & {
    require?: (module: string) => any;
};

export function TitleBar() {
    const handleMinimize = () => {
        if (window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.send('window-minimize');
        }
    };

    const handleMaximize = () => {
        if (window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.send('window-maximize');
        }
    };

    const handleClose = () => {
        if (window.require) {
            const { ipcRenderer } = window.require('electron');
            ipcRenderer.send('window-close');
        }
    };

    return (
        <div
            className="fixed top-0 left-0 right-0 h-8 bg-[#050811]/80 backdrop-blur-md border-b border-white/5 flex items-center justify-end px-4 z-[9999]"
            style={{ WebkitAppRegion: 'drag' } as any}
        >
            <div className="flex items-center gap-2" style={{ WebkitAppRegion: 'no-drag' } as any}>
                <button
                    onClick={handleMinimize}
                    className="w-8 h-8 flex items-center justify-center hover:bg-white/5 rounded-lg transition-colors group"
                    title="Minimizar"
                >
                    <Minus size={14} className="text-white/30 group-hover:text-white/60" />
                </button>
                <button
                    onClick={handleMaximize}
                    className="w-8 h-8 flex items-center justify-center hover:bg-white/5 rounded-lg transition-colors group"
                    title="Maximizar"
                >
                    <Square size={11} className="text-white/30 group-hover:text-white/60" />
                </button>
                <button
                    onClick={handleClose}
                    className="w-8 h-8 flex items-center justify-center hover:bg-red-500/20 rounded-lg transition-colors group"
                    title="Fechar"
                >
                    <X size={16} className="text-white/30 group-hover:text-red-500" />
                </button>
            </div>
        </div>
    );
}
