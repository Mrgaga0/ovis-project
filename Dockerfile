# ë¹Œë“œ ?¤í…Œ?´ì?: React ??ë¹Œë“œ
FROM node:16-alpine as build

WORKDIR /app

# ?„ìš”???Œì¼ ë³µì‚¬
COPY ovis-core/package*.json ./
RUN npm install

COPY ovis-core/ ./
RUN npm run build

# ?¤í–‰ ?¤í…Œ?´ì?: FastAPI ?œë²„
FROM python:3.9-slim

WORKDIR /app

# ?œìŠ¤???¨í‚¤ì§€ ?¤ì¹˜ ë°?ìºì‹œ ?•ë¦¬
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ?„ìš”???Œì¼ ë³µì‚¬
COPY ovis-api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pydantic-settings \
    && rm -rf ~/.cache/pip

# ë¹Œë“œ??React ??ë³µì‚¬
COPY --from=build /app/build ./static

# API ?œë²„ ì½”ë“œ ë³µì‚¬
COPY ovis-api/ ./

# ?¤ì • ?Œì¼ ë³µì‚¬
COPY config/ /app/config/

# ë¡œê·¸ ë°??°ì´???”ë ‰? ë¦¬ ?ì„±
RUN mkdir -p /app/data /app/logs /nas-mount /nas-mount/models /nas-mount/data /nas-mount/logs

# ?˜ê²½ ë³€???¤ì •
ENV PORT=528 \
    HOST=0.0.0.0 \
    OVIS_CONFIG=/app/config/local.json \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GEMINI_API_KEY="" \
    OVIS_VERSION="0.19"

# ë³¼ë¥¨ ?¤ì • (?°ì´???êµ¬ ?€??
VOLUME /app/data
VOLUME /app/logs
VOLUME /nas-mount

# ?¬íŠ¸ ?¸ì¶œ
EXPOSE 528

# ?œë²„ ?¤í–‰
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "528", "--workers", "4"] 
