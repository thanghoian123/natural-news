import "./assets/main.css";

import { createApp } from "vue";
import { install } from "vue3-recaptcha-v2";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(router);

app.use(
  install, {
    sitekey: "6Ld8pNQqAAAAAGEM2JP0lbyWn-zeNemsafW1Md_2",
    cnDomains: false,
  }
);

app.mount("#app");
