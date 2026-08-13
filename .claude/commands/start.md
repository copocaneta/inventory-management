---
description: Start the frontend and backend servers
---

Kill any existing servers on ports 3030 and 8090, then start both the backend (FastAPI on port 8090) and frontend (Vite on port 3030) development servers in the background.

**Backend:** `cd server && uv run python main.py`
**Frontend:** `cd client && npm run dev`

To kill existing processes on a port:
- macOS/Linux: `lsof -ti:3030,8090 | xargs kill -9 2>/dev/null || true`
- Windows: Use `netstat -aon | findstr :PORT` to find PIDs, then `taskkill /F /PID <pid>`

After starting, verify:
- Backend: http://localhost:8090/docs
- Frontend: http://localhost:3030
