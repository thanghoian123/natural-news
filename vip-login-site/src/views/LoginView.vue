<script setup>
import axios from "axios";
import { useCookies } from "vue3-cookies";
import { nextTick, ref } from "vue";
import { RecaptchaV2 } from "vue3-recaptcha-v2";
import router from "../router";

const subscriptionButtonClicked = ref(false);
const cookiesManager = useCookies();

const baseURL = import.meta.env.VITE_BASE_URL

axios.defaults.baseURL = baseURL ? baseURL : "https://api-hrs.healthrangerstore.com";
axios.defaults.withCredentials = true;

const subscriptEmail = async () => {
  const emailCheck = username.value
    .toLowerCase()
    .match(
      /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/
    );
  if (!emailCheck) {
    usernameError.value = "Email is not valid!";
  } else {
    usernameError.value = "";
  }
  if (usernameError.value !== "") {
    return;
  }
  subscriptionButtonClicked.value = ref(true);
  try {

    await axios.post(
      "/login",
      {
        email: username.value,
        session_password: "",
      },
      {
        headers: {
          "Content-Type": "application/json; charset=UTF-8"
        }
      }
    );
    nextTick(() => {
      document.getElementById("sessionPassword").focus();
    });
  } catch (e) {
    console.error(e);
    usernameError.value = "Unexpected error from server, please try again later";
  }
};

const onLogin = async () => {
  try {
    // const response = await axios.post(
    //   "/login",
    //   {
    //     email: username.value,
    //     session_password: sessionPassword.value,
    //   },
    //   {
    //     headers: {
    //       "Content-Type": "application/json;charset=UTF-8"
    //     }
    //   }
    // )
    // const responseDataToken = response.data["hrs-vip"];
    // let date = new Date();
    // date.setMonth(date.getMonth() + 3);
    // cookiesManager.cookies.set("hrs-vip", responseDataToken, date);
    router.push({ path: "/chat", replace: true });
  } catch {
    sessionPasswordError.value = "Password does not match";
  }  
};

const username = ref("");
const sessionPassword = ref("");
const usernameError = ref("");
const sessionPasswordError = ref("");

const updateUsername = (value) => {
  username.value = value;
}

const updateSessionPassword = (value) => {
  sessionPassword.value = value;
}

</script>

<template>
  <div id="login">
    <RecaptchaV2 />
    <p>Email:</p>
    <input type="text" id="username" class="custom-input" name="username" @input="updateUsername($event.target.value)" @keydown.enter="subscriptEmail" placeholder="Enter your email for subscription password" />
    <p v-if="usernameError" class="red">{{ usernameError }}</p>
    <div v-else="">
      <br/>
    </div>
    <div v-if="subscriptionButtonClicked">
      <p>Session Password:</p>
      <input type="text" id="sessionPassword" class="custom-input" name="sessionPassword" @input="updateSessionPassword($event.target.value)" @keydown.enter="onLogin" placeholder="Please check your email for session password" />
      <p v-if="sessionPasswordError" class="red">{{ sessionPasswordError }}</p>
      <div v-else="">
        <br/>
      </div>
      <button class="btn-login-page" @click="onLogin">Login</button>
    </div>
    <div v-else="">
      <button class="btn-login-page" @click="subscriptEmail">Get Password</button>
    </div>
  </div>
</template>

<style scoped>
  #login {
    width: 768px;
  }
  .custom-input {
    width: 500px;
    height: 44px;
    padding-left: 10px;
  }
  .btn-login-page {
    height: 44px;
    border-radius: 3px;
    background-color: hsla(160, 100%, 37%, 1);
    width: 150px;
    color: var(--color-text);
    border: none;
    font-weight: bold;
  }
  .red {
    color: red;
  }
</style>
