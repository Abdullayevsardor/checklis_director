# 1-Bosqich: Loyihani yig'ish (Build)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
# Ba'zida npm ci muammo qilsa, npm install ishlatib ko'ring
RUN npm install
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# 2-Bosqich: Nginx orqali ishga tushirish
FROM nginx:alpine
# Standart Nginx konfiguratsiyasini React routerga moslash
RUN echo 'server { listen 80; location / { root /usr/share/nginx/html; index index.html; try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
