import { IpcMain } from 'electron';
import { backendProcess } from './main';
import * as fs from 'fs';
import * as path from 'path';

export function setupIpcHandlers(ipcMain: IpcMain): void {
  ipcMain.handle('backend:call', async (_event, method: string, params: unknown) => {
    try {
      if (!backendProcess) {
        throw new Error('Backend process not started');
      }

      const backendUrl = backendProcess.getUrl();
      const response = await fetch(`${backendUrl}/api/${method}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Backend call failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('IPC handler error:', error);
      throw error;
    }
  });

  ipcMain.handle('backend:health', async () => {
    try {
      if (!backendProcess) {
        return { status: 'stopped' };
      }

      const backendUrl = backendProcess.getUrl();
      const response = await fetch(`${backendUrl}/health`);
      
      if (response.ok) {
        return { status: 'running' };
      }
      return { status: 'error' };
    } catch {
      return { status: 'error' };
    }
  });

  ipcMain.handle('app:getVersion', () => {
    try {
      const packageJsonPath = path.join(__dirname, '../../../package.json');
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      return packageJson.version;
    } catch {
      return '0.1.0';
    }
  });
}
