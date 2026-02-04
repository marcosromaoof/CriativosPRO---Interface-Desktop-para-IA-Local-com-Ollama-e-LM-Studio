# Barra de Controle de Janela Customizada

## Visão Geral
Este documento descreve a implementação da barra de controle de janela moderna e minimalista integrada ao design Night Blue Glassmorphism do CriativosPro.

## Arquitetura

### 1. Backend (Electron - main.js)
O processo principal do Electron gerencia os handlers IPC para controlar a janela:

```javascript
const { app, BrowserWindow, ipcMain } = require('electron');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        frame: false,  // Remove a barra nativa do sistema
        titleBarStyle: 'hidden',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });

    // Handlers IPC
    ipcMain.on('window-minimize', () => {
        if (mainWindow) mainWindow.minimize();
    });

    ipcMain.on('window-maximize', () => {
        if (mainWindow) {
            if (mainWindow.isMaximized()) {
                mainWindow.unmaximize();
            } else {
                mainWindow.maximize();
            }
        }
    });

    ipcMain.on('window-close', () => {
        if (mainWindow) mainWindow.close();
    });
}
```

### 2. Frontend (TitleBar.tsx)
Componente React que renderiza a barra de controle:

**Localização**: `frontend/src/components/TitleBar.tsx`

**Características**:
- Altura fixa de 32px (h-8)
- Background semi-transparente com blur (`bg-[#050811]/80 backdrop-blur-md`)
- Borda inferior sutil (`border-b border-white/5`)
- Área arrastável para mover a janela (`WebkitAppRegion: 'drag'`)
- Botões com hover states suaves
- Z-index máximo para ficar sempre visível (`z-[9999]`)

**Botões**:
1. **Minimizar**: Ícone Minus (14px)
2. **Maximizar/Restaurar**: Ícone Square (11px)
3. **Fechar**: Ícone X (16px) com hover vermelho

### 3. Integração no App.tsx

```tsx
import { TitleBar } from './components/TitleBar';

function App() {
  return (
    <div className="flex h-screen...">
      <TitleBar />
      
      {/* Sidebar com pt-8 */}
      <aside className="... pt-8">
        ...
      </aside>
      
      {/* Main com pt-8 */}
      <main className="... pt-8">
        ...
      </main>
    </div>
  );
}
```

## Estilos e Design

### Paleta de Cores
- **Background**: `#050811` com 80% de opacidade
- **Borda**: Branco com 5% de opacidade
- **Ícones padrão**: Branco com 30% de opacidade
- **Ícones hover**: Branco com 60% de opacidade
- **Fechar hover**: Vermelho (`red-500`)

### Efeitos Visuais
- **Backdrop Blur**: 16px de desfoque
- **Transições**: 200ms ease para todos os estados hover
- **Border Radius**: 8px nos botões

## Responsividade
A barra ocupa toda a largura da janela e mantém altura fixa de 32px em todas as resoluções.

## Acessibilidade
- Títulos descritivos em cada botão (title attribute)
- Estados hover claramente visíveis
- Área de clique confortável (32x32px por botão)

## Notas Técnicas

### WebkitAppRegion
- A barra principal usa `drag` para permitir mover a janela
- A área dos botões usa `no-drag` para permitir cliques

### Compatibilidade
- Funciona apenas no ambiente Electron
- Verifica a existência de `window.require` antes de enviar eventos IPC
- Degrada graciosamente em ambientes web (botões não funcionam mas não quebram)

## Manutenção

### Para alterar cores:
Edite as classes Tailwind em `TitleBar.tsx`:
- Background: `bg-[#050811]/80`
- Hover dos botões: `hover:bg-white/5`
- Hover do fechar: `hover:bg-red-500/20`

### Para alterar altura:
1. Modifique `h-8` em `TitleBar.tsx`
2. Ajuste `pt-8` em `aside` e `main` no `App.tsx`

### Para adicionar novos controles:
Adicione handlers IPC em `main.js` e botões correspondentes em `TitleBar.tsx`

## Checklist de Implementação

- [x] Configurar `frame: false` no Electron
- [x] Criar handlers IPC no main.js
- [x] Criar componente TitleBar.tsx
- [x] Integrar TitleBar no App.tsx
- [x] Ajustar padding dos elementos principais
- [x] Testar minimizar/maximizar/fechar
- [x] Validar design visual
- [x] Documentar implementação
