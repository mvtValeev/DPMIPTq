# 🚀 Деплой проекта Economic Research Platform

## 📦 Backend (FastAPI) — Render.com

1. Зарегистрируйтесь на [https://render.com](https://render.com)
2. Форкните этот репозиторий или загрузите в свой GitHub
3. Нажмите **New > Blueprint**
4. Укажите репозиторий с этим проектом
5. Render автоматически:
   - создаст PostgreSQL базу `econ-db`
   - создаст сервис `econ-backend` из `backend/Dockerfile`
   - настроит переменные окружения через `render.yaml`

> Время деплоя: ~2-5 минут

## 🌐 Frontend (Vite + React) — Vercel

1. Перейдите на [https://vercel.com](https://vercel.com)
2. Импортируйте репозиторий
3. Настройки проекта:
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. В разделе **Environment Variables** укажите:

```
VITE_API_URL=https://<render-backend-url>
```

Замените `<render-backend-url>` на домен вашего backend-сервиса на Render (например: `https://econ-backend.onrender.com`).

---

## ✅ Готово!

- Frontend: Vercel (vite)
- Backend: FastAPI + PostgreSQL (Render)
- Тесты: `pytest` в Docker

> Контейнер запускается из `Dockerfile`, база данных управляется Render, конфигурация задаётся в `render.yaml`.