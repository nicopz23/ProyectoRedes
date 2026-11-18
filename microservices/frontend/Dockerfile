FROM nginx:alpine

# Copiar configuración personalizada de proxy inverso
COPY microservices/frontend/nginx.conf /etc/nginx/nginx.conf

# Copiar archivos estáticos de la interfaz web
COPY frontend/ /usr/share/nginx/html/

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/health || exit 1

CMD ["nginx", "-g", "daemon off;"]

