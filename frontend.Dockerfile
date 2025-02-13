FROM node:lts-alpine

WORKDIR /app

COPY ./vip-login-site /app/

RUN npm --prefix /app/ install

EXPOSE 5000

CMD ["npm", "run", "dev", "--", "--port", "5000", "--host", "0.0.0.0"]