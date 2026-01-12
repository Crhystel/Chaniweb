# Etapa 1: Build (Compilación de React)
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa 2: Producción (Servidor Nginx)
FROM nginx:alpine
# Copiamos los archivos compilados de la Etapa 1
COPY --from=build /app/build /usr/share/nginx/html
# Copiamos nuestra configuración de proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]