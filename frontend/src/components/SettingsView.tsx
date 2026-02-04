import { useState, useEffect } from 'react';
import { User, Brain, Cpu, RefreshCw, Save, Check } from 'lucide-react';
import { Socket } from 'socket.io-client';

interface SettingsViewProps {
    socket: Socket | null;
}

type SettingsTab = 'profile' | 'engines' | 'prompts';

export function SettingsView({ socket }: SettingsViewProps) {
    const [activeTab, setActiveTab] = useState<SettingsTab>('profile');

    // Estados de Salvamento SEPARADOS por contexto
    const [profileSaveStatus, setProfileSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
    const [enginesSaveStatus, setEnginesSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
    const [promptsSaveStatus, setPromptsSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    // Estados do Perfil
    const [profile, setProfile] = useState({
        display_name: '',
        email: '',
        gender: '',
        birthdate: '',
        custom_instructions: ''
    });

    // Estados dos Prompts
    const [prompts, setPrompts] = useState({
        ollama: '',
        lmstudio: ''
    });

    // Estados dos Modelos
    const [providers] = useState(['ollama', 'lmstudio']);
    const [selectedProvider, setSelectedProvider] = useState('ollama');
    const [providerModels, setProviderModels] = useState<any[]>([]);
    const [providerSettings, setProviderSettings] = useState({ base_url: '' });
    const [syncingProvider, setSyncingProvider] = useState<string | null>(null);

    // 1. Listeners GLOBAIS (Não dependem do provedor selecionado)
    useEffect(() => {
        if (!socket) return;
        console.log('[Settings] Inicializando listeners globais');

        // Carregar dados iniciais globais
        socket.emit('load_user_profile', {});
        socket.emit('load_system_prompts', {});

        // Listeners
        const handleProfileLoaded = (data: any) => { if (data.profile) setProfile(data.profile); };
        const handlePromptsLoaded = (data: any) => { if (data.prompts) setPrompts(data.prompts); };
        const handleAllModelsConfig = (data: any) => {
            setProviderModels(data.models || []);
            setSyncingProvider(null);
            setErrorMessage(null);
        };
        const handleModelsSynced = (data: any) => {
            setProviderModels(data.models || []);
            setSyncingProvider(null);
            setErrorMessage(null);
        };

        // Handlers ESPECÍFICOS de Sucesso por Contexto
        const handleProfileSaved = (data?: any) => {
            console.log('[Settings] Perfil salvo:', data);
            setProfileSaveStatus('saved');
            setErrorMessage(null);
            setTimeout(() => setProfileSaveStatus('idle'), 2000);
        };

        const handleEnginesSaved = (data?: any) => {
            console.log('[Settings] Configurações de motor salvas:', data);
            setEnginesSaveStatus('saved');
            setErrorMessage(null);
            setTimeout(() => setEnginesSaveStatus('idle'), 2000);
        };

        const handlePromptsSaved = (data?: any) => {
            console.log('[Settings] Prompts salvos:', data);
            setPromptsSaveStatus('saved');
            setErrorMessage(null);
            setTimeout(() => setPromptsSaveStatus('idle'), 2000);
        };

        // Handler Unificado de Erro
        const handleError = (data: any) => {
            console.error('[Settings] Erro recebido:', JSON.stringify(data, null, 2));
            // Resetar todos os status de salvamento
            setProfileSaveStatus('error');
            setEnginesSaveStatus('error');
            setPromptsSaveStatus('error');
            setSyncingProvider(null);
            setErrorMessage(data.message || 'Erro desconhecido ao processar ação.');
            setTimeout(() => {
                setProfileSaveStatus('idle');
                setEnginesSaveStatus('idle');
                setPromptsSaveStatus('idle');
            }, 4000);
        };

        socket.on('profile_loaded', handleProfileLoaded);
        socket.on('prompts_loaded', handlePromptsLoaded);
        socket.on('all_models_config', handleAllModelsConfig);
        socket.on('models_synced', handleModelsSynced);

        // Eventos de Confirmação ESPECÍFICOS
        socket.on('profile_saved', handleProfileSaved);
        socket.on('settings_saved', handleEnginesSaved);  // Para configurações de motores
        socket.on('prompts_saved', handlePromptsSaved);

        // Eventos de Erro
        socket.on('sync_error', handleError);
        socket.on('settings_error', handleError);

        return () => {
            socket.off('profile_loaded', handleProfileLoaded);
            socket.off('prompts_loaded', handlePromptsLoaded);
            socket.off('all_models_config', handleAllModelsConfig);
            socket.off('models_synced', handleModelsSynced);
            socket.off('profile_saved', handleProfileSaved);
            socket.off('settings_saved', handleEnginesSaved);
            socket.off('prompts_saved', handlePromptsSaved);
            socket.off('sync_error', handleError);
            socket.off('settings_error', handleError);
        };
    }, [socket]); // Executa apenas ao montar ou mudar conexão socket

    // 2. Listeners LOCAIS (Reagem a mudanças de aba/provedor)
    useEffect(() => {
        if (!socket || !selectedProvider) return;

        const handleProviderSettings = (data: any) => {
            if (data.provider === selectedProvider) {
                setProviderSettings(data.settings);
            }
        };

        socket.on('provider_settings_loaded', handleProviderSettings);

        return () => {
            socket.off('provider_settings_loaded', handleProviderSettings);
        };
    }, [socket, selectedProvider]);


    // Carregar modelos e settings ao selecionar provedor
    useEffect(() => {
        if (socket && selectedProvider) {
            socket.emit('get_all_models_config', { provider: selectedProvider });
            socket.emit('load_provider_settings', { provider: selectedProvider });
        }
    }, [socket, selectedProvider]);

    const saveProfile = () => {
        if (!socket) {
            console.error('[Settings] Socket não está disponível!');
            return;
        }
        console.log('[Settings] Iniciando salvamento de perfil...', profile);
        setProfileSaveStatus('saving');
        socket.emit('save_user_profile', { profile });
        console.log('[Settings] Evento save_user_profile emitido');
    };

    const savePrompts = () => {
        if (!socket) {
            console.error('[Settings] Socket não está disponível!');
            return;
        }
        console.log('[Settings] Iniciando salvamento de prompts...', prompts);
        setPromptsSaveStatus('saving');
        socket.emit('save_system_prompts', { prompts });
        console.log('[Settings] Evento save_system_prompts emitido');
    };

    const saveProviderSettings = () => {
        if (!socket) {
            console.error('[Settings] Socket não está disponível!');
            return;
        }
        console.log('[Settings] Iniciando salvamento de configurações do provedor...', { provider: selectedProvider, settings: providerSettings });
        setEnginesSaveStatus('saving');
        socket.emit('save_provider_settings', {
            provider: selectedProvider,
            settings: providerSettings
        });
        console.log('[Settings] Evento save_provider_settings emitido');
    };

    const syncProviderModels = () => {
        if (!socket) return;
        setSyncingProvider(selectedProvider);
        socket.emit('sync_provider_models', { provider: selectedProvider });
    };

    const toggleModel = (modelName: string, isActive: boolean) => {
        if (!socket) return;
        socket.emit('toggle_model', {
            provider: selectedProvider,
            model_name: modelName,
            is_active: isActive
        });

        // Atualizar localmente
        setProviderModels(prev =>
            prev.map(m => m.model_name === modelName ? { ...m, is_active: isActive ? 1 : 0 } : m)
        );
    };

    const toggleProvider = (isActive: boolean) => {
        if (!socket) return;
        socket.emit('toggle_provider', {
            provider: selectedProvider,
            is_active: isActive
        });
        // Atualiza todos os modelos locais
        setProviderModels(prev => prev.map(m => ({ ...m, is_active: isActive ? 1 : 0 })));
    };

    return (
        <div className="flex h-full">
            {/* Sidebar Interna de Configurações */}
            <aside className="w-64 border-r border-white/5 bg-[#070b16] p-6">
                <h2 className="text-xs font-bold text-white/40 uppercase tracking-[0.2em] mb-6">Configurações</h2>

                <nav className="space-y-2">
                    <SettingsTabButton
                        icon={<User size={18} />}
                        label="Perfil e Identidade"
                        active={activeTab === 'profile'}
                        onClick={() => setActiveTab('profile')}
                    />
                    <SettingsTabButton
                        icon={<Cpu size={18} />}
                        label="Motores Cognitivos"
                        active={activeTab === 'engines'}
                        onClick={() => setActiveTab('engines')}
                    />
                    <SettingsTabButton
                        icon={<Brain size={18} />}
                        label="Cérebro e Prompts"
                        active={activeTab === 'prompts'}
                        onClick={() => setActiveTab('prompts')}
                    />
                </nav>
            </aside>

            {/* Área de Conteúdo */}
            <main className="flex-1 overflow-y-auto p-12">
                {activeTab === 'profile' && (
                    <ProfilePanel
                        profile={profile}
                        setProfile={setProfile}
                        onSave={saveProfile}
                        saveStatus={profileSaveStatus}
                        errorMessage={errorMessage}
                    />
                )}

                {activeTab === 'engines' && (
                    <EnginesPanel
                        providers={providers}
                        selectedProvider={selectedProvider}
                        setSelectedProvider={setSelectedProvider}
                        providerModels={providerModels}
                        providerSettings={providerSettings}
                        setProviderSettings={setProviderSettings}
                        syncingProvider={syncingProvider}
                        onSync={syncProviderModels}
                        onToggleModel={toggleModel}
                        onToggleProvider={toggleProvider}
                        onSaveSettings={saveProviderSettings}
                        saveStatus={enginesSaveStatus}
                        errorMessage={errorMessage}
                    />
                )}

                {activeTab === 'prompts' && (
                    <PromptsPanel
                        prompts={prompts}
                        setPrompts={setPrompts}
                        onSave={savePrompts}
                        saveStatus={promptsSaveStatus}
                    />
                )}
            </main>
        </div>
    );
}

// Componente de Botão de Tab
function SettingsTabButton({ icon, label, active, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-xs font-bold transition-all uppercase tracking-wider ${active
                ? 'bg-electric-blue/10 text-electric-blue border-l-2 border-electric-blue'
                : 'text-white/40 hover:text-white hover:bg-white/5'
                }`}
        >
            <span className={active ? 'text-electric-blue' : 'text-white/40'}>{icon}</span>
            {label}
        </button>
    );
}

// Painel de Perfil
function ProfilePanel({ profile, setProfile, onSave, saveStatus }: any) {
    return (
        <div className="max-w-3xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-outfit mb-2">Perfil e Identidade</h1>
                <p className="text-white/40 text-sm">Personalize sua experiência com o CriativosPro</p>
            </div>

            <div className="space-y-6">
                <InputField
                    label="Nome de Exibição"
                    value={profile.display_name}
                    onChange={(e: any) => setProfile({ ...profile, display_name: e.target.value })}
                    placeholder="Como você gostaria de ser chamado?"
                />

                <InputField
                    label="Email"
                    type="email"
                    value={profile.email}
                    onChange={(e: any) => setProfile({ ...profile, email: e.target.value })}
                    placeholder="seu@email.com"
                />

                <div className="grid grid-cols-2 gap-6">
                    <SelectField
                        label="Gênero"
                        value={profile.gender}
                        onChange={(e: any) => setProfile({ ...profile, gender: e.target.value })}
                        options={[
                            { value: '', label: 'Selecione...' },
                            { value: 'male', label: 'Masculino' },
                            { value: 'female', label: 'Feminino' },
                            { value: 'other', label: 'Outro' },
                            { value: 'prefer_not_say', label: 'Prefiro não dizer' }
                        ]}
                    />

                    <InputField
                        label="Data de Nascimento"
                        type="date"
                        value={profile.birthdate}
                        onChange={(e: any) => setProfile({ ...profile, birthdate: e.target.value })}
                    />
                </div>

                <TextAreaField
                    label="Instruções Customizadas"
                    value={profile.custom_instructions}
                    onChange={(e: any) => setProfile({ ...profile, custom_instructions: e.target.value })}
                    placeholder="Descreva como a IA deve se comportar com você... (ex: 'Seja sempre formal', 'Use linguagem técnica', etc.)"
                    rows={4}
                />

                <SaveButton onClick={onSave} status={saveStatus} />
            </div>
        </div>
    );
}

// Painel de Motores
function EnginesPanel({
    providers, selectedProvider, setSelectedProvider,
    providerModels, providerSettings, setProviderSettings,
    syncingProvider, onSync, onToggleModel, onToggleProvider,
    onSaveSettings, saveStatus, errorMessage
}: any) {
    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-outfit mb-2">Motores Cognitivos</h1>
                <p className="text-white/40 text-sm">Gerencie os modelos de IA locais</p>
                {errorMessage && (
                    <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs font-bold uppercase tracking-wide flex items-center gap-2">
                        <span>⚠️</span> {errorMessage}
                    </div>
                )}
            </div>

            {/* Seletor de Provedor */}
            <div className="flex gap-3 mb-8 flex-wrap">
                {providers.map((provider: string) => (
                    <button
                        key={provider}
                        onClick={() => setSelectedProvider(provider)}
                        className={`px-6 py-3 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${selectedProvider === provider
                            ? 'bg-electric-blue text-white'
                            : 'bg-white/5 text-white/40 hover:bg-white/10 hover:text-white'
                            }`}
                    >
                        {provider}
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Coluna Esquerda: Configurações */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-2xl">
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-sm font-bold text-white uppercase tracking-widest">Configuração</h3>
                            <button
                                onClick={() => onToggleProvider(true)}
                                className="text-[10px] text-emerald-500 font-bold uppercase hover:bg-emerald-500/10 px-2 py-1 rounded"
                            >
                                Ativar Tudo
                            </button>
                        </div>

                        <div className="space-y-4">
                            <InputField
                                label="URL do Servidor Local"
                                value={providerSettings.base_url || ''}
                                onChange={(e: any) => setProviderSettings({ ...providerSettings, base_url: e.target.value })}
                                placeholder="http://localhost:..."
                            />

                            <div className="pt-2">
                                <SaveButton onClick={onSaveSettings} status={saveStatus} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Coluna Direita: Modelos e Sincronização */}
                <div className="space-y-6">
                    <button
                        onClick={onSync}
                        disabled={syncingProvider !== null}
                        className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 rounded-xl text-xs font-bold uppercase tracking-widest transition-all disabled:opacity-50 border border-emerald-500/20"
                    >
                        <RefreshCw size={14} className={syncingProvider ? 'animate-spin' : ''} />
                        {syncingProvider ? 'Sincronizando...' : 'Sincronizar Modelos'}
                    </button>

                    <div className="glass-panel p-6 rounded-2xl">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-white/60 uppercase tracking-widest">
                                Modelos ({providerModels.length})
                            </h3>
                            <button
                                onClick={() => onToggleProvider(false)}
                                className="text-[10px] text-red-500 font-bold uppercase hover:bg-red-500/10 px-2 py-1 rounded"
                            >
                                Desativar Tudo
                            </button>
                        </div>

                        {providerModels.length === 0 ? (
                            <p className="text-white/20 text-sm italic py-4 text-center">Nenhum modelo detectado.</p>
                        ) : (
                            <div className="space-y-2 max-h-72 overflow-y-auto pr-2 custom-scrollbar">
                                {providerModels.map((model: any) => (
                                    <div
                                        key={model.id}
                                        className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all border border-transparent hover:border-white/5"
                                    >
                                        <span className="text-xs font-medium text-white/80 truncate max-w-[200px]" title={model.model_name}>{model.display_name || model.model_name}</span>
                                        <label className="relative inline-flex items-center cursor-pointer flex-shrink-0">
                                            <input
                                                type="checkbox"
                                                checked={model.is_active === 1}
                                                onChange={(e) => onToggleModel(model.model_name, e.target.checked)}
                                                className="sr-only peer"
                                            />
                                            <div className="w-9 h-5 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500"></div>
                                        </label>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Painel de Prompts
function PromptsPanel({ prompts, setPrompts, onSave, saveStatus }: any) {
    return (
        <div className="max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-bold font-outfit mb-2">Cérebro e Prompts</h1>
                <p className="text-white/40 text-sm">Configure como a IA se comporta em diferentes contextos</p>
            </div>

            <div className="space-y-6">

                <PromptField
                    label="Prompt Ollama"
                    description="Específico para modelos locais via Ollama"
                    value={prompts.ollama}
                    onChange={(e: any) => setPrompts({ ...prompts, ollama: e.target.value })}
                />

                <PromptField
                    label="Prompt LM Studio"
                    description="Específico para modelos locais via LM Studio"
                    value={prompts.lmstudio}
                    onChange={(e: any) => setPrompts({ ...prompts, lmstudio: e.target.value })}
                />

                <SaveButton onClick={onSave} status={saveStatus} />
            </div>
        </div>
    );
}

// Componentes de Formulário
function InputField({ label, type = 'text', value, onChange, placeholder }: any) {
    return (
        <div>
            <label className="block text-xs font-bold text-white/60 uppercase tracking-widest mb-2">{label}</label>
            <input
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-electric-blue/50 transition-all"
            />
        </div>
    );
}

function SelectField({ label, value, onChange, options }: any) {
    return (
        <div>
            <label className="block text-xs font-bold text-white/60 uppercase tracking-widest mb-2">{label}</label>
            <select
                value={value}
                onChange={onChange}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-electric-blue/50 transition-all"
            >
                {options.map((opt: any) => (
                    <option key={opt.value} value={opt.value} className="bg-navy-950">
                        {opt.label}
                    </option>
                ))}
            </select>
        </div>
    );
}

function TextAreaField({ label, value, onChange, placeholder, rows = 3 }: any) {
    return (
        <div>
            <label className="block text-xs font-bold text-white/60 uppercase tracking-widest mb-2">{label}</label>
            <textarea
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                rows={rows}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-electric-blue/50 transition-all resize-none"
            />
        </div>
    );
}

function PromptField({ label, description, value, onChange }: any) {
    return (
        <div className="glass-panel p-6 rounded-2xl">
            <div className="mb-3">
                <h3 className="text-sm font-bold text-white uppercase tracking-widest">{label}</h3>
                <p className="text-xs text-white/40 mt-1">{description}</p>
            </div>
            <textarea
                value={value}
                onChange={onChange}
                rows={4}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-electric-blue/50 transition-all resize-none"
                placeholder="Digite o prompt de sistema..."
            />
        </div>
    );
}

function SaveButton({ onClick, status }: any) {
    return (
        <button
            onClick={onClick}
            disabled={status === 'saving'}
            className="flex items-center gap-2 px-8 py-4 bg-electric-blue hover:bg-electric-blue/80 text-white rounded-xl text-sm font-bold uppercase tracking-widest transition-all disabled:opacity-50 shadow-lg"
        >
            {status === 'saving' ? (
                <>
                    <RefreshCw size={16} className="animate-spin" />
                    Salvando...
                </>
            ) : status === 'saved' ? (
                <>
                    <Check size={16} />
                    Salvo!
                </>
            ) : status === 'error' ? (
                <>
                    <span className="text-xl">⚠️</span>
                    Erro!
                </>
            ) : (
                <>
                    <Save size={16} />
                    Salvar Alterações
                </>
            )}
        </button>
    );
}
