# Cognisphere Desktop

This is the monorepo for the Cognisphere desktop application.

## Structure

- `apps/desktop-shell`: Electron main process and packaging.
- `apps/frontend`: React + Vite frontend.
- `services/backend`: Python FastAPI backend.

## Prerequisites

- Node.js (v18+)
- pnpm
- Python 3.10+
- pip

## Setup

1. Install Node dependencies:
   ```bash
   pnpm install
   ```

2. Install Python dependencies:
   ```bash
   pnpm setup:backend
   ```

## Development

To start the application in development mode (starts Electron, React dev server, and Python backend):

```bash
pnpm dev
```

Note: The Python backend runs from source in dev mode.

## Building

To build the desktop application:

1. Build the Python backend executable:
   ```bash
   cd services/backend
   pnpm build
   # or
   pyinstaller --onefile --name backend main.py
   ```
   (Ensure the output executable is in `services/backend/dist/backend` or `backend.exe`)

2. Build the Electron app:
   ```bash
   pnpm build:desktop
   ```

## Architecture

- **Electron**: Orchestrates the application window and manages the lifecycle of the Python backend process.
- **Frontend**: Connects to the backend via HTTP using a secure token passed via Electron IPC.
- **Backend**: Python FastAPI service handling business logic, database (SQLite + LanceDB), and model management.
- **Storage**: Data is stored in the OS-specific application data directory (e.g., `%APPDATA%/Cognisphere` on Windows, `~/.local/share/Cognisphere` on Linux).
