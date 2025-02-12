import axios from "axios";
import { createRouter, createWebHistory } from "vue-router";
import ChatView from "../views/ChatView.vue";
import LoginView from "../views/LoginView.vue";

axios.defaults.baseURL = "http://localhost:8000";
axios.defaults.withCredentials = true;

const _get_default_route = async () => {
  try {
    await axios.get("/login");
    return "/chat";
  } catch {
    return "/login";
  }
};

const defaultRoute = await _get_default_route();

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: defaultRoute,
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/chat",
      name: "chat",
      component: ChatView,
    },
  ],
})

export default router
