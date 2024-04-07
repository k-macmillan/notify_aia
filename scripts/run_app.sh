#! /usr/bin/sh

# Use gunicorn for worker management but use the uvicorn workers for running the ASGI

# exec transfers this PID, so it can interpret SIGTERM
if [ "$RELOAD" = "true" ]; then
    echo "Starting reloadable uvicorn app"
    # Cannot reload with gunicorn + uvicorn, so skipping gunicorn...will have logging implications
    # https://github.com/encode/uvicorn/discussions/1638
    # https://github.com/encode/uvicorn/pull/1193 - closed, not merged
    exec uvicorn naia.main:app --host 0.0.0.0 --port 5309 --reload
else
    echo "Starting gunicorn app with $WORKER_COUNT uvicorn workers"
    exec gunicorn naia.main:app -b 0.0.0.0:5309 --pythonpath app -k uvicorn.workers.UvicornWorker -w $WORKER_COUNT
fi
