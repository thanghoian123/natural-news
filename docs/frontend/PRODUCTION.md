# VIP LOGIN FRONTEND PRODUCTION

Things to do when going to production:

1. Changing default settings of base URL to BackEnd URL for axios in [ChatView.vue file](../../vip-login-site/src/views/ChatView.vue)

2. Changing default settings of base URL to BackEnd URL for axios in [LoginView.vue file](../../vip-login-site/src/views/LoginView.vue)

3. Settings your own Google Recaptcha v2 for correct FrontEnd domain name

4. Using `npm run build` for optimize frontend code instead of `npm run dev`. See [Deploy Vue Apps](https://vite.dev/guide/static-deploy)

Feel free for changing docker compose file
