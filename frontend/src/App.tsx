import { useState, useEffect, useRef, useCallback } from 'react';
import { MessageBubble } from './components/MessageBubble';
import { TitleBar } from './components/TitleBar';
import { DashboardView } from './components/DashboardView';
import { SettingsModal } from './components/SettingsModal';
import {
  MessageSquare,
  Settings,
  LayoutDashboard,
  PlusCircle,
  Send,
  Zap,
  Globe,
  Layers,
  Trash2
} from 'lucide-react';
import { io, Socket } from 'socket.io-client';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  metrics?: {
    tokens?: number;
    tps?: number;
    duration?: number;
  };
  timestamp?: string;
}

function App() {
  const [activeView, setActiveView] = useState<'chat' | 'dashboard'>('chat');
  const [showSettings, setShowSettings] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [status, setStatus] = useState('IDLE');
  const [providers, setProviders] = useState<Record<string, string[]>>({});
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [sessions, setSessions] = useState<any[]>([]);

  // Gerador de ID único para sessão
  const generateSessionId = () => `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const [currentSessionId, setCurrentSessionId] = useState<string>(generateSessionId());

  // Modal de Exclusão
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  const openDeleteModal = (sessionId: string) => {
    setSessionToDelete(sessionId);
    setShowDeleteModal(true);
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setSessionToDelete(null);
  };

  const confirmDeleteSession = () => {
    if (sessionToDelete && socketRef.current) {
      socketRef.current.emit('delete_session', { session_id: sessionToDelete });
      closeDeleteModal();
    }
  };

  // Controle de Reset (Estabilidade)
  const [isResetting, setIsResetting] = useState(false);

  const handleNewChat = () => {
    // Hard Reset para evitar travamentos de renderização
    setIsResetting(true);
    setTimeout(() => {
      setMessages([]);
      setCurrentSessionId(generateSessionId());
      setActiveView('chat');
      setIsResetting(false);
    }, 10);
  };

  const handleLoadSession = (sessionId: string) => {
    if (sessionId === currentSessionId) return;
    socketRef.current?.emit('load_session', { session_id: sessionId });
  };

  const socketRef = useRef<Socket | null>(null);
  const thinkingTimeoutRef = useRef<number | null>(null);
  const isFirstChunkRef = useRef(true);

  // --- Controle Central de Áudio (Singleton de UI) ---
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const [loadingAudioIndex, setLoadingAudioIndex] = useState<number | null>(null);
  const [playingMessageIndex, setPlayingMessageIndex] = useState<number | null>(null);

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setPlayingMessageIndex(null);
  }, []);

  const handleToggleAudio = useCallback((index: number, text: string) => {
    // Se clicou na msg que já está tocando: PARA
    if (playingMessageIndex === index) {
      stopAudio();
      return;
    }

    // Se clicou na msg que está carregando: Cancela Load? (opcional, por enquanto ignora ou para)
    if (loadingAudioIndex === index) {
      return; // ou stopAudio()
    }

    // Se clicou em outra: PARA a atual (se houver) e inicia a NOVA
    stopAudio();

    // Define como carregando
    setLoadingAudioIndex(index);
    socketRef.current?.emit('generate_tts', { text, id: index });
  }, [playingMessageIndex, loadingAudioIndex, stopAudio]);

  useEffect(() => {
    // Nova porta padrão 5678 para evitar conflitos (era 5000)
    socketRef.current = io('http://127.0.0.1:5678');

    socketRef.current.on('connect', () => {
      console.log('Backend Online');
      socketRef.current?.emit('get_sessions');
    });

    socketRef.current.on('session_loaded', (data) => {
      setIsResetting(true);
      setTimeout(() => {
        setMessages(data.messages);
        setCurrentSessionId(data.session_id);
        setActiveView('chat');
        setIsResetting(false);
      }, 10);
    });

    socketRef.current.on('system_status', (data) => setStatus(data.status));
    socketRef.current.on('models_data', (data) => {
      setProviders(data.providers);
      if (Object.keys(data.providers).length > 0 && !selectedProvider) {
        const first = Object.keys(data.providers).sort()[0];
        setSelectedProvider(first);
        setSelectedModel(data.providers[first][0] || '');
      }
    });

    socketRef.current.on('chat_chunk', (data) => {
      // Se for o primeiro chunk, aguardar 1.5s para dar sensação de pensamento
      if (isFirstChunkRef.current) {
        isFirstChunkRef.current = false;
        thinkingTimeoutRef.current = window.setTimeout(() => {
          setMessages(prev => {
            const last = prev[prev.length - 1];
            if (last && last.role === 'assistant' && last.content === '...') {
              return [...prev.slice(0, -1), { ...last, content: data.content }];
            }
            return prev;
          });
        }, 600);
      } else {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant') {
            return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
          }
          return [...prev, {
            role: 'assistant',
            content: data.content,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }];
        });
      }
    });

    socketRef.current.on('chat_end', (data) => {
      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant') {
          return [...prev.slice(0, -1), { ...last, content: data.total_content, metrics: data.metrics }];
        }
        return prev;
      });
      socketRef.current?.emit('get_sessions', {});
    });

    socketRef.current.on('sessions_list', (data) => setSessions(data.sessions));

    // Listeners de Áudio (TTS)
    socketRef.current.on('tts_ready', (data) => {
      // Cria novo áudio e substitui a ref global
      if (audioRef.current) {
        audioRef.current.pause();
      }

      const audio = new Audio(data.url);
      audioRef.current = audio;

      // Listener para limpar estado quando acabar
      audio.onended = () => {
        setPlayingMessageIndex(null);
      };

      setLoadingAudioIndex(null); // Parou de carregar
      setPlayingMessageIndex(data.text_id ?? null); // Começou a tocar (se tiver ID)

      // Tenta tocar
      audio.play().catch(e => {
        console.error("Erro ao reproduzir áudio:", e);
        setPlayingMessageIndex(null); // Reseta se falhar
      });

      // AVISO: O 'id' retornado deve bater com o index esperado. 
      // Se user clicou rápido em outro, data.text_id pode ser velho.
      // Se precisarmos validar: if (data.text_id !== playingMessageIndex) audio.pause();
    });

    socketRef.current.on('tts_error', (data) => {
      console.error("Erro no TTS:", data.message);
      setPlayingMessageIndex(null); // Reseta estado
      setLoadingAudioIndex(null); // Reseta estado de carregamento
    });

    // Tratamento de Erro Geral do Chat
    socketRef.current.on('error', (data) => {
      console.error("Erro do Backend:", data);
      setStatus('IDLE');

      // Atualiza a última mensagem do bot (que estaria com '...') para mostrar o erro
      setMessages(prev => {
        const last = prev[prev.length - 1];
        if (last && last.role === 'assistant' && last.content === '...') {
          return [...prev.slice(0, -1), {
            ...last,
            content: `⚠️ **Erro na geração:**\n> ${data.message || "Ocorreu um erro desconhecido."}\n\n_Tente selecionar outro modelo ou verificar sua conexão._`
          }];
        }
        // Se não houver mensagem pendente, adiciona uma nova de sistema/erro
        return [...prev, {
          role: 'assistant',
          content: `⚠️ **Erro de Sistema:** ${data.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }];
      });
    });

    // Listener para Parada Manual
    socketRef.current.on('generation_stopped', () => {
      console.log("Geração interrompida pelo usuário");
      setStatus('IDLE');

    });

    return () => { socketRef.current?.disconnect(); };
  }, [selectedProvider]);



  const handleSendMessage = () => {
    if (!inputValue.trim() || status !== 'IDLE') return;

    // Reset da flag para próxima resposta
    isFirstChunkRef.current = true;
    if (thinkingTimeoutRef.current) {
      clearTimeout(thinkingTimeoutRef.current);
    }

    setMessages(prev => [...prev,
    {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    {
      role: 'assistant',
      content: '...',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    ]);
    socketRef.current?.emit('send_message', {
      content: inputValue,
      session_id: currentSessionId,
      provider: selectedProvider,
      model: selectedModel
    });
    setInputValue('');
  };




  const handleDeleteMessage = useCallback((index: number) => {
    setMessages(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleRetryMessage = useCallback((index: number) => {
    const previousMsgIndex = index - 1;
    if (previousMsgIndex < 0) return;
    const previousMsg = messages[previousMsgIndex];

    // Mantém mensagens até antes da resposta atual (que é o index)
    // Assim, a última msg será a PERGUNTA do usuário.
    // Mas espere! Se eu cortar no 'index', o array vai ter 0..index-1. O index-1 é a pergunta.
    // Então o estado 'messages' terá a pergunta como última.
    // Isso é visualmente estranho se o usuário não vir 'gerando'.
    // Mas o socket.emit vai disparar 'chat_chunk' logo em seguida, o que adicionará uma NOVA mensagem 'assistant'.

    setMessages(prev => prev.slice(0, index));

    socketRef.current?.emit('send_message', {
      content: previousMsg.content, // Reenvia o prompt da mensagem anterior
      session_id: currentSessionId,
      provider: selectedProvider,
      model: selectedModel
    });
  }, [messages, currentSessionId, selectedProvider, selectedModel]);


  return (
    <div className="flex h-screen w-full bg-navy-950 overflow-hidden text-white font-sans select-none">
      {/* Barra de Controle de Janela */}
      <TitleBar />

      {/* Sidebar */}
      <aside className="w-68 border-r border-white/5 flex flex-col bg-[#070b16] z-50 pt-8">
        <div className="p-6 flex items-center gap-3 mb-4">
          <div className="w-9 h-9 bg-electric-blue rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.5)]">
            <Zap size={20} className="fill-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm tracking-tight font-outfit uppercase">Criativos Pro</span>
            <span className="text-[9px] text-white/30 font-bold tracking-widest uppercase">Neural A.I System</span>
          </div>
        </div>

        <div className="px-5 mb-6">
          <button
            onClick={handleNewChat}
            className="flex items-center justify-center gap-3 w-full py-3.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all text-[11px] font-bold uppercase tracking-[0.2em] text-white/90"
          >
            <PlusCircle size={16} /> Novo Chat
          </button>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          <SidebarItem
            icon={<LayoutDashboard size={18} />}
            label="Dashboard"
            active={activeView === 'dashboard'}
            onClick={() => setActiveView('dashboard')}
          />

          <div className="mt-10 mb-4 px-4 flex items-center justify-between">
            <span className="text-[10px] font-bold text-white/20 uppercase tracking-[0.2em]">Recentes</span>
            <MessageSquare size={12} className="text-white/10" />
          </div>

          <div className="space-y-1 overflow-y-auto max-h-[45vh] px-1">
            {sessions.length === 0 ? (
              <div className="flex flex-col items-center py-10 opacity-10">
                <MessageSquare size={24} />
                <span className="text-[10px] mt-2 italic">Silêncio criativo...</span>
              </div>
            ) : (
              sessions.slice(0, 8).map(s => (
                <div key={s.id} className="group relative w-full mb-1">
                  <button
                    onClick={() => handleLoadSession(s.id)}
                    className="w-full text-left px-4 py-3 rounded-xl text-[11px] font-medium text-white/40 hover:text-white hover:bg-white/5 truncate transition-all border border-transparent hover:border-white/5 pr-8"
                  >
                    {s.title || 'Nova Conversa'}
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); openDeleteModal(s.id); }}
                    className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1.5 hover:bg-white/5 hover:text-red-400 text-white/10 transition-all z-10"
                    title="Excluir conversa"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))
            )}
          </div>
        </nav>

        <div className="p-5 mt-auto border-t border-white/5">
          <SidebarItem
            icon={<Settings size={18} />}
            label="Configurações"

            active={showSettings}
            onClick={() => setShowSettings(true)}
          />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[#050811] pt-8">

        {/* Header Premium */}
        <header className="h-20 flex items-center justify-between px-10 flex-shrink-0 z-50">
          <div className="flex-1"></div>

          {/* Seletores Centrais */}
          {/* Seletores Centrais - Apenas visíveis no Chat */}
          {/* Nota: Com o modal, podemos deixar os seletores visíveis sempre que estiver no chat,
              pois o modal vai cobrir tudo. Mas seguindo a lógica atual, mantemos. */}
          {activeView === 'chat' ? (
            <div className="flex items-center gap-4 animate-in fade-in slide-in-from-top-4 duration-500">
              {/* Provedor */}
              <div className="flex flex-col items-center">
                <span className="text-[8px] font-bold text-white/20 uppercase tracking-widest mb-1.5">Engine</span>
                <div className="glass-panel h-11 px-6 rounded-2xl flex items-center gap-3 hover:border-white/10 transition-all cursor-pointer">
                  <Globe size={14} className="text-electric-blue" />
                  <select
                    value={selectedProvider}
                    onChange={(e) => {
                      setSelectedProvider(e.target.value);
                      setSelectedModel(providers[e.target.value]?.[0] || '');
                    }}
                    className="bg-transparent border-none text-[11px] font-bold uppercase tracking-widest text-white/80 outline-none cursor-pointer [&>option]:bg-[#050811] [&>option]:text-white"
                  >
                    {Object.keys(providers).map(p => <option key={p} value={p} className="bg-[#050811] text-white uppercase">{p}</option>)}
                  </select>
                </div>
              </div>

              <div className="h-8 w-px bg-white/5 mx-1 mt-4"></div>

              {/* Modelo */}
              <div className="flex flex-col items-center">
                <span className="text-[8px] font-bold text-white/20 uppercase tracking-widest mb-1.5">Arquitetura</span>
                <div className="glass-panel h-11 px-6 rounded-2xl flex items-center gap-3 hover:border-white/10 transition-all cursor-pointer">
                  <Layers size={14} className="text-electric-blue" />
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="bg-transparent border-none text-[11px] font-bold uppercase tracking-widest text-emerald-500 outline-none cursor-pointer max-w-[180px] truncate [&>option]:bg-[#050811] [&>option]:text-white"
                  >
                    {providers[selectedProvider]?.map(m => <option key={m} value={m} className="bg-[#050811] text-white">{m}</option>)}
                  </select>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center opacity-40">
              <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-white/30">
                {activeView === 'dashboard' ? 'Painel de Controle' : 'Criativos Pro'}
              </span>
            </div>
          )}

          <div className="flex-1 flex justify-end items-center">
            <div className="flex items-center gap-2.5 px-4 py-2 bg-white/5 rounded-full border border-white/5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 status-dot-pulse"></div>
              <span className="text-[9px] font-bold text-emerald-500 uppercase tracking-[0.2em]">Neural Link Active</span>
            </div>
          </div>
        </header>

        {/* View Switcher */}
        <div className="flex-1 relative overflow-hidden">
          {isResetting ? (
            <div className="flex-1 h-full w-full bg-[#050811]" />
          ) : activeView === 'chat' ? (
            <ChatView
              messages={messages}
              inputValue={inputValue}
              setInputValue={setInputValue}
              handleSendMessage={handleSendMessage}
              handleToggleAudio={handleToggleAudio}
              handleDeleteMessage={handleDeleteMessage}
              handleRetryMessage={handleRetryMessage}
              status={status}
              selectedModel={selectedModel}
              playingMessageIndex={playingMessageIndex}
              loadingAudioIndex={loadingAudioIndex}
            />
          ) : (
            <DashboardView socket={socketRef.current} />
          )}
        </div>
      </main>

      {/* Modal de Exclusão */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#0a0f1d] border border-white/10 p-6 rounded-2xl w-[90%] max-w-sm shadow-2xl relative">
            <h3 className="text-lg font-bold text-white mb-2 font-outfit">Excluir conversa?</h3>
            <p className="text-white/50 text-xs mb-6 font-medium">Esta ação não pode ser desfeita. O histórico desta sessão será apagado permanentemente.</p>

            <div className="flex justify-end gap-3">
              <button
                onClick={closeDeleteModal}
                className="px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider text-white/60 hover:text-white hover:bg-white/5 transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={confirmDeleteSession}
                className="px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20 transition-all shadow-lg shadow-red-500/5"
              >
                Excluir
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Configurações (Opção A) */}
      {showSettings && (
        <SettingsModal
          socket={socketRef.current}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}

/* Chat Home View */
function ChatView({ messages, inputValue, setInputValue, handleSendMessage, handleToggleAudio, handleDeleteMessage, handleRetryMessage, status, selectedModel, playingMessageIndex, loadingAudioIndex }: any) {
  // Referência para auto-scroll
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll inteligente: Rola sempre que o conteúdo da última mensagem mudar
  const lastMessageContent = messages[messages.length - 1]?.content;
  useEffect(() => {
    if (messagesEndRef.current) {
      // Usa 'auto' para ser instantâneo durante a geração, evitando lag do 'smooth'
      messagesEndRef.current.scrollIntoView({ behavior: 'auto', block: 'end' });
    }
  }, [lastMessageContent]); // Monitora o conteúdo da última msg

  return (
    <div className="h-full w-full relative flex flex-col">
      {/* 1. Área de Rolagem de Mensagens */}
      <div className="flex-1 overflow-y-auto custom-scrollbar" ref={scrollContainerRef}>
        <div className="w-full max-w-4xl mx-auto p-8 pt-12 pb-60">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center animate-fade-in mt-20">
              <div className="w-20 h-20 bg-electric-blue/10 rounded-3xl flex items-center justify-center mb-10 border border-electric-blue/20 relative shadow-[0_0_50px_rgba(59,130,246,0.1)]">
                <Zap size={40} className="text-electric-blue fill-electric-blue/20" />
                <div className="absolute inset-0 bg-electric-blue/20 blur-2xl -z-10 rounded-full"></div>
              </div>
              <h1 className="text-5xl font-bold font-outfit mb-6 tracking-tight">Como posso ajudar hoje?</h1>
              <p className="text-white/30 max-w-sm text-xs leading-loose font-bold uppercase tracking-[0.3em]">
                Selecione um motor cognitivo acima e inicie uma nova linha de raciocínio.
              </p>
            </div>
          ) : (
            <div className="space-y-8">
              {messages.map((msg: any, i: number) => (
                <MessageBubble
                  key={i}
                  {...msg}
                  onPlay={() => handleToggleAudio(i, msg.content)}
                  isPlaying={playingMessageIndex === i}
                  isAudioLoading={loadingAudioIndex === i}
                  onDelete={() => handleDeleteMessage(i)}
                  onRetry={() => handleRetryMessage(i)}
                />
              ))}
              <div ref={messagesEndRef} /> {/* Âncora para scroll */}
            </div>
          )}
        </div>
      </div>

      {/* 2. Área de Input (Container Sólido na Base) */}
      <div className="flex-none w-full bg-[#050811] pt-2 pb-8 z-30 relative px-6 flex justify-center">
        {/* Gradiente superior para suavizar o corte */}
        <div className="absolute top-[-40px] left-0 right-0 h-10 bg-gradient-to-t from-[#050811] to-transparent pointer-events-none"></div>

        <div className="w-full max-w-3xl">
          <div className="glass-panel p-2.5 rounded-[24px] border-white/10 shadow-[0_30px_70px_rgba(0,0,0,0.6)] backdrop-blur-3xl relative z-40 bg-[#050811]/40">
            <div className="relative flex items-center min-h-[64px] px-5">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                placeholder="Descreva seu projeto..."
                disabled={status !== 'IDLE'}
                className="flex-1 bg-transparent border-none focus:outline-none text-[15px] py-4 resize-none placeholder:text-white/15 h-full font-medium"
                rows={1}
              />
              <div className="flex items-center gap-5 ml-4">
                <div className="hidden lg:flex flex-col items-end opacity-20 group">
                  <span className="text-[8px] font-bold uppercase tracking-widest text-white">Active Engine</span>
                  <span className="text-[9px] font-bold text-electric-blue truncate max-w-[120px] uppercase font-mono">{selectedModel || 'System Ready'}</span>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={status !== 'IDLE' || !inputValue.trim()}
                  className="w-12 h-12 bg-white/5 hover:bg-white/10 rounded-2xl flex items-center justify-center transition-all disabled:opacity-20 active:scale-90 border border-white/10 group shadow-lg"
                >
                  <Send size={18} className="text-white/40 group-hover:text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                </button>
              </div>
            </div>
          </div>
          <div className="mt-4 text-[10px] font-bold text-white/5 uppercase tracking-[0.4em] text-center">
            Criativos Pro Engine V4.4.21
          </div>
        </div>
      </div>
    </div>
  );
}

function SidebarItem({ icon, label, active, onClick }: { icon: any, label: string, active: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-4 w-full px-5 py-3.5 rounded-xl text-[11px] font-bold transition-all uppercase tracking-widest border-l-[3px]",
        active
          ? "bg-electric-blue/10 text-electric-blue border-electric-blue"
          : "text-white/30 hover:text-white underline-none border-transparent hover:bg-white/5"
      )}
    >
      <span className={active ? "text-electric-blue" : "text-white/40"}>{icon}</span>
      {label}
    </button>
  );
}

export default App;
