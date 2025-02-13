FROM node:lts-alpine

WORKDIR /app

COPY ./vip-login-site /app/

RUN npm --prefix /app/ install

EXPOSE 8000

CMD ["npm", "run", "dev", "--", "--port", "8000", "--host", "0.0.0.0"]