# 1-Bosqich: Loyihani build qilish (Yig'ish)
FROM node:20-alpine AS builder

WORKDIR /app

# Birinchi dependencies (kutubxonalar) yuklanadi (keshlash samarali bo'lishi uchun)
COPY package*.json ./
RUN npm ci

# Docker-compose'dan kelayotgan argumentni qabul qilamiz
ARG VITE_API_BASE_URL
# Vite muhit o'zgaruvchisini o'rnatamiz (Build vaqtida kod ichiga joylashadi)
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Qolgan barcha kodlarni nusxalash va build qilish
COPY . .
RUN npm run build

# 2-Bosqich: Faqat tayyor build fayllarini ishga tushirish (Production)
FROM node:20-alpine

WORKDIR /app

# Faqat ishga tushirish uchun kerakli vositani o'rnatamiz
RUN npm install -g preview

# 1-bosqichda tayyor bo'lgan 'dist' papkasini nusxalaymiz
COPY --from=builder /app/dist ./dist

EXPOSE 4173

# docker-compose'dagi 4173 portga moslab hostni ochgan holda ishga tushiramiz
CMD ["preview", "--host", "0.0.0.0", "--port", "4173"]
