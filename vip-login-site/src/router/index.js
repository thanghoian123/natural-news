import axios from "axios";
import { createRouter, createWebHistory } from "vue-router";
import IngredientChecker from "../views/IngredientChecker.vue";
import ChatView from "../views/ChatView.vue";

import LoginView from "../views/LoginView.vue";

const baseURL = import.meta.env.VITE_BASE_URL

axios.defaults.baseURL = baseURL ? baseURL : "https://api-hrs.healthrangerstore.com";
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
    {
      path: "/ingredient-checker",
      name: "ingredient-checker",
      component: ChatView,
    },
  ],
})

export default router
