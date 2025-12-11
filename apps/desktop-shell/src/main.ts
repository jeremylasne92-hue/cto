import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { spawn, ChildProcess } from 'child_process';
import log from 'electron-log';
import treeKill from 'tree-kill';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const API_PORT = 8000;
const AUTH_TOKEN = 'dev-token-placeholder'; // In real app, generate securely

function getBackendPath(): { command: string, args: string[], cwd: string } {
    if (isDev) {
        // In dev, run python from source
        const backendPath = path.resolve(__dirname, '../../../../services/backend');
        return {
            command: 'python3', // Assumes python3 is in PATH and venv is managed or system python has deps
            args: ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', API_PORT.toString()],
            cwd: backendPath
        };
    } else {
        // In prod, run the packaged executable
        // This path depends on how pyinstaller packages it. 
        // Typically resources/backend/backend (or similar)
        const executableName = process.platform === 'win32' ? 'backend.exe' : 'backend';
        const backendPath = path.join(process.resourcesPath, 'backend', executableName);
        return {
            command: backendPath,
            args: [],
            cwd: path.dirname(backendPath)
        };
    }
}

function startBackend() {
    const { command, args, cwd } = getBackendPath();
    log.info(`Starting backend: ${command} ${args.join(' ')} in ${cwd}`);

    backendProcess = spawn(command, args, {
        cwd,
        env: { ...process.env, API_SECRET: AUTH_TOKEN },
        stdio: ['ignore', 'pipe', 'pipe'] // Pipe stdout/err to log
    });

    backendProcess.stdout?.on('data', (data) => {
        log.info(`[Backend]: ${data}`);
    });

    backendProcess.stderr?.on('data', (data) => {
        log.error(`[Backend Error]: ${data}`);
    });

    backendProcess.on('close', (code) => {
        log.info(`Backend process exited with code ${code}`);
        backendProcess = null;
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../../frontend/dist/index.html'));
    }

    mainWindow.webContents.on('did-finish-load', () => {
        mainWindow?.webContents.send('auth-token', AUTH_TOKEN);
    });
}

app.whenReady().then(() => {
    startBackend();
    createWindow();

    ipcMain.handle('check-backend-status', async () => {
        return backendProcess ? 'Running' : 'Stopped';
    });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    if (backendProcess && backendProcess.pid) {
        treeKill(backendProcess.pid);
    }
});
