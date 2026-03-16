module.exports = {
  apps: [
    {
      name: "qa-live-api",
      script: "/var/www/qa-live-api/venv/bin/uvicorn",
      args: "main:app --host 127.0.0.1 --port 8001 --workers 2",
      cwd: "/var/www/qa-live-api",
      interpreter: "none",        // uvicorn is the executable, not a .py file
      autorestart: true,
      watch: false,
      max_memory_restart: "256M",
      env: {
        PYTHONPATH: "/var/www/qa-live-api",
      },
    },
  ],
};