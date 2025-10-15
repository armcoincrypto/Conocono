FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY app_fastapi.py /app/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status; sys.exit(0 if r==200 else 1)"
CMD ["uvicorn","app_fastapi:app","--host","0.0.0.0","--port","8000"]
