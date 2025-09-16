# Многоэтапная сборка для React frontend
FROM node:18-alpine as build

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package файлы
COPY package*.json ./

# Устанавливаем зависимости с исправлением конфликтов
RUN npm install --legacy-peer-deps

# Копируем исходный код
COPY . .

# Собираем production версию
RUN npm run build

# Этап production с Nginx
FROM nginx:stable-alpine

# Копируем собранные файлы
COPY --from=build /app/build /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]

