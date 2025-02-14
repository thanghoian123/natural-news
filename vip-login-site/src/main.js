import "./assets/main.css";

import { createApp } from "vue";
import { install } from "vue3-recaptcha-v2";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(router);

app.use(
  install, {
    sitekey: "6Ldh-NYqAAAAAOiHmQEzA9aKbOvPuLo-N6UahU0I",
    cnDomains: false,
  }
);

app.mount("#app");
