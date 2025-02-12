FROM node:lts-alpine

WORKDIR /app

COPY ./vip-login-site /app/

RUN npm --prefix /app/ install

EXPOSE 8080

CMD ["npm", "run", "dev", "--", "--port", "8080", "--host", "0.0.0.0"]