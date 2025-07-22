# Stage 1: Build Remix on Node 20
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

# Copy your npmrc so engine‑strict=false is in effect
COPY frontend/.npmrc .npmrc

# Copy package manifests
COPY frontend/package.json frontend/package-lock.json ./

# Install only production deps
ENV NODE_ENV=production
RUN npm ci --omit=dev

# Copy the rest of the frontend code & build
COPY frontend .
RUN npm run build

# Stage 2: Prepare your FastAPI backend + copy in the built frontend (optional static serve)
FROM python:3.11-slim
# install system deps (if any)
WORKDIR /app

# install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy backend code
COPY backend ./backend

# copy built frontend into a static folder (if you want to serve it via FastAPI StaticFiles)
COPY --from=frontend-build /app/frontend/public ./backend/static

# set env
ENV PYTHONPATH=/app/backend

# expose port
EXPOSE 8000

# start uvicorn (and you could mount StaticFiles in your FastAPI app at /)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
