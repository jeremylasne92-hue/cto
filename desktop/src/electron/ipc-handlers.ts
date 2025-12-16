import { IpcMain } from 'electron';
import { backendProcess } from './main';
import * as fs from 'fs';
import * as path from 'path';

export function setupIpcHandlers(ipcMain: IpcMain): void {
  ipcMain.handle('backend:call', async (_event, endpoint: string, method: string = 'POST', body: unknown = {}, query: Record<string, string> = {}) => {
    try {
      if (!backendProcess) {
        throw new Error('Backend process not started');
      }

      const backendUrl = backendProcess.getUrl();
      const url = new URL(`${backendUrl}/api/${endpoint}`);
      
      if (query) {
        Object.entries(query).forEach(([key, value]) => {
          url.searchParams.append(key, value as string);
        });
      }

      const response = await fetch(url.toString(), {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: (method !== 'GET' && method !== 'HEAD') ? JSON.stringify(body) : undefined,
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
