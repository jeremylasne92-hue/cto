import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';

export class BackendProcess {
  private process: ChildProcess | null = null;
  private backendUrl = 'http://localhost:8765';

  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      const isDev = process.env.NODE_ENV === 'development';
      let backendPath: string;

      if (isDev) {
        backendPath = path.join(__dirname, '../../../backend/main.py');
        this.process = spawn('python', [backendPath], {
          stdio: ['pipe', 'pipe', 'pipe'],
        });
      } else {
        const resourcesPath = process.resourcesPath;
        backendPath = path.join(resourcesPath, 'backend', 'cognisphere');
        this.process = spawn(backendPath, [], {
          stdio: ['pipe', 'pipe', 'pipe'],
        });
      }

      if (!this.process.stdout || !this.process.stderr) {
        reject(new Error('Failed to create backend process streams'));
        return;
      }

      this.process.stdout.on('data', (data: Buffer) => {
        console.log(`Backend: ${data.toString()}`);
        if (data.toString().includes('Backend started')) {
          resolve();
        }
      });

      this.process.stderr.on('data', (data: Buffer) => {
        console.error(`Backend Error: ${data.toString()}`);
      });

      this.process.on('error', (error: Error) => {
        console.error('Failed to start backend:', error);
        reject(error);
      });

      this.process.on('exit', (code: number | null) => {
        console.log(`Backend process exited with code ${code}`);
        this.process = null;
      });

      setTimeout(() => {
        if (this.process) {
          resolve();
        }
      }, 3000);
    });
  }

  stop(): void {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }

  getUrl(): string {
    return this.backendUrl;
  }
}
