import axios from "axios";
import { defineStore } from "pinia";

axios.defaults.baseURL = import.meta.env.VITE_BASE_URL;
axios.defaults.withCredentials = true;

export const useUserStore = defineStore("user", {
  state: () => {
    return {
      username: "",
      tokenRemain: 0,
    }
  },
  actions: {
    async checkUser () {
      try {
        const responseData = (await axios.get("/login")).data;
        this.username = responseData.login;
        this.tokenRemain = responseData.token_remain;
      } catch (e) {
        console.log(e);
        this.username = "";
        this.tokenRemain = 0;
      }
    }
  }
});
