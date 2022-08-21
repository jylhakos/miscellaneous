FROM nginx:1.16.0-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx/nginx.conf /etc/nginx/
COPY ./nginx/sites-available/default.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/default.conf /etc/nginx/sites-enabled/
EXPOSE 80
EXPOSE 443
CMD ["nginx", "-g", "daemon off;"]