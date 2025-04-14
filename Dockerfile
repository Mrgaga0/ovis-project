# 빌드 ?�테?��?: React ??빌드
FROM node:16-alpine as build

WORKDIR /app

# ?�요???�일 복사
COPY ovis-core/package*.json ./
RUN npm install

COPY ovis-core/ ./
RUN npm run build

# ?�행 ?�테?��?: FastAPI ?�버
FROM python:3.9-slim

WORKDIR /app

# ?�스???�키지 ?�치 �?캐시 ?�리
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ?�요???�일 복사
COPY ovis-api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pydantic-settings \
    && rm -rf ~/.cache/pip

# 빌드??React ??복사
COPY --from=build /app/build ./static

# API ?�버 코드 복사
COPY ovis-api/ ./

# ?�정 ?�일 복사
COPY config/ /app/config/

# 로그 �??�이???�렉?�리 ?�성
RUN mkdir -p /app/data /app/logs /nas-mount /nas-mount/models /nas-mount/data /nas-mount/logs

# ?�경 변???�정
ENV PORT=528 \
    HOST=0.0.0.0 \
    OVIS_CONFIG=/app/config/local.json \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GEMINI_API_KEY="" \
    OVIS_VERSION="0.19"

# 볼륨 ?�정 (?�이???�구 ?�??
VOLUME /app/data
VOLUME /app/logs
VOLUME /nas-mount

# ?�트 ?�출
EXPOSE 528

# ?�버 ?�행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "528", "--workers", "4"] 
