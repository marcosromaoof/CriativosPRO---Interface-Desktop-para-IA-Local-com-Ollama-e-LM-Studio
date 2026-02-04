const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = !app.isPackaged;

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        backgroundColor: '#050811',
        frame: false,
        titleBarStyle: 'hidden',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        title: "CriativosPro Desktop"
    });

    if (isDev) {
        console.log("Modo Dev: Carregando via 127.0.0.1");
        mainWindow.loadURL('http://127.0.0.1:5173');
    } else {
        // Em produção, usamos loadFile. O caminho é relativo à raiz do app (onde main.cjs está).
        // Com a configuração "files": ["dist/**/*", "main.cjs"], a pasta dist estará ao lado deste arquivo.
        console.log("Modo Prod: Carregando arquivo local dist/index.html");

        // Tenta carregar usando caminho relativo simples, que o Electron resolve bem dentro do ASAR
        const loadPromise = mainWindow.loadFile('dist/index.html');

        loadPromise.catch(err => {
            console.error("Falha ao carregar index.html:", err);
            // Fallback para caminho absoluto se o relativo falhar (debug)
            const absPath = path.join(__dirname, 'dist/index.html');
            console.log("Tentando caminho absoluto:", absPath);
            mainWindow.loadURL(`file://${absPath}`).catch(e => console.error("Falha absoluta:", e));
        });
    }

    // IPC Handlers para controles de janela
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

// Backend Process Handler
let backendProcess = null;

const startBackend = () => {
    if (isDev) return; // Em dev, rodamos manualmente

    const isWin = process.platform === 'win32';
    const backendName = isWin ? 'criativospro-engine.exe' : 'criativospro-engine';
    const backendPath = path.join(process.resourcesPath, 'extraResources', backendName);

    console.log("Iniciando Backend em:", backendPath);

    // Configurar CWD para a raiz dos recursos para garantir que o backend ache pasta 'backend/bin'
    const cwd = path.join(process.resourcesPath, 'extraResources');

    backendProcess = require('child_process').spawn(backendPath, [], {
        cwd: cwd,
        stdio: 'ignore', // ou 'pipe' para debug
        windowsHide: true
    });

    backendProcess.on('error', (err) => {
        console.error('Falha ao iniciar backend:', err);
    });
};

const stopBackend = () => {
    if (backendProcess) {
        backendProcess.kill(); // Tentativa suave (SIGTERM)
        backendProcess = null;
    }

    // Failsafe para Windows: Mata qualquer processo orfão com o mesmo nome
    if (process.platform === 'win32') {
        require('child_process').exec('taskkill /F /IM criativospro-engine.exe /T', (err) => {
            // Ignora erro se o processo já não existir
        });
    } else {
        // Fallback para Linux/Mac se necessário
        require('child_process').exec('pkill -f criativospro-engine', (err) => {
            // Ignora erro
        });
    }
};

app.whenReady().then(() => {
    startBackend();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    stopBackend();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
