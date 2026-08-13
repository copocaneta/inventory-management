---
description: Stop the frontend and backend servers
---

Find and stop any processes running on ports 3030 (frontend) and 8090 (backend).

- macOS/Linux: `lsof -ti:3030,8090 | xargs kill 2>/dev/null || true`
- Windows: Use `netstat -aon | findstr :PORT` to find PIDs, then `taskkill /F /PID <pid>`
