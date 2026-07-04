FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY . /usr/share/nginx/html

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /etc/nginx/nginx.conf

EXPOSE 8080 8443

CMD ["nginx", "-g", "daemon off;"]
