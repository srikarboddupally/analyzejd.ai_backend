#!/bin/bash
# Apply database migrations or initialization if needed
# python -c "from app.database.connection import init_db; init_db()"

# Start the application
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
