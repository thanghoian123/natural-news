import "./assets/main.css";
import { createPinia } from "pinia";

import { createApp } from "vue";
import { install } from "vue3-recaptcha-v2";
import App from "./App.vue";
import router from "./router";
const pinia = createPinia();

const app = createApp(App);
app.use(router);

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth && userStore.username === "") return "/login";
});

app.use(
  install, {
    sitekey: "6Ldh-NYqAAAAAOiHmQEzA9aKbOvPuLo-N6UahU0I",
    cnDomains: false,
  }
);
app.use(pinia);

app.mount("#app");
