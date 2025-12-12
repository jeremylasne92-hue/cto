import { app, BrowserWindow, Menu, ipcMain, dialog } from 'electron';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

function createWindow(): void {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'default',
    show: false
  });

  // Load the app
  mainWindow.loadURL('http://localhost:3000');

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Setup menu
  const template: Electron.MenuItemConstructorOptions[] = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Reset Zoom' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Fullscreen' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Start backend process
  startBackend();
}

function startBackend(): void {
  const backendPath = path.join(__dirname, '../../services/backend/dist/backend');
  
  try {
    backendProcess = spawn(backendPath, [], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    backendProcess.stdout?.on('data', (data) => {
      console.log('Backend output:', data.toString());
    });

    backendProcess.stderr?.on('data', (data) => {
      console.error('Backend error:', data.toString());
    });

    backendProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
    });

    console.log('Backend process started');
  } catch (error) {
    console.error('Failed to start backend:', error);
  }
}

function stopBackend(): void {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

// App event handlers
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopBackend();
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// IPC handlers
ipcMain.handle('show-save-dialog', async () => {
  const result = await dialog.showSaveDialog(mainWindow!, {
    filters: [
      { name: 'JSON', extensions: ['json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

// Handle FSRS responses
ipcMain.handle('submit-fsrs-response', async (event, responseData) => {
  // This would communicate with the backend
  console.log('FSRS Response:', responseData);
  return { success: true };
});
