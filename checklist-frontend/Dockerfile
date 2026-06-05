# 1-Bosqich: Loyihani yig'ish (Build)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# 2-Bosqich: Nginx orqali ishga tushirish (Eng barqaror usul)
FROM nginx:alpine
# Yig'ilgan tayyor fayllarni Nginx veb-server papkasiga nusxalash
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
