<script setup>
import axios from "axios";
import { nextTick, ref } from "vue";
import { RecaptchaV2 } from "vue3-recaptcha-v2";
import router from "../router";

const subscriptionButtonClicked = ref(false);
const baseURL = import.meta.env.VITE_BASE_URL;

axios.defaults.baseURL = baseURL ? baseURL : "https://api-hrs.healthrangerstore.com";
axios.defaults.withCredentials = true;

const username = ref("");
const sessionPassword = ref("");
const usernameError = ref("");
const sessionPasswordError = ref("");
const loading = ref(false);

// Function to validate email format
const validateEmail = (email) => {
  return email.toLowerCase().match(/^([A-Za-z0-9_\-\.])+@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/);
};

// Function to show error messages
const showError = (errorType, message) => {
  if (errorType === "username") {
    usernameError.value = message;
  } else if (errorType === "sessionPassword") {
    sessionPasswordError.value = message;
  }
};

// Function to hide error messages
const hideError = (errorType) => {
  if (errorType === "username") {
    usernameError.value = "";
  } else if (errorType === "sessionPassword") {
    sessionPasswordError.value = "";
  }
};

// Function to make login requests
const postLoginRequest = async (payload) => {
  try {
    loading.value = true;
    const response = await axios.post("/login", payload, {
      headers: { "Content-Type": "application/json;charset=UTF-8" }
    });
    loading.value = false;
    return response.data;
  } catch (error) {
    loading.value = false;
    return error.response?.data || "Unexpected error, please try again later.";
  }
};

// Function to handle email subscription (sending request for session password)
const subscriptEmail = async () => {
  if (!validateEmail(username.value)) {
    showError("username", "Email is not valid!");
    return;
  }

  hideError("username");
  subscriptionButtonClicked.value = true;

  const response = await postLoginRequest({ email: username.value, session_password: "" });
  if (response) {
    if (response.message) {
      showError("username", response.message);
    } else {
      nextTick(() => {
        document.getElementById("sessionPassword").focus();
      });
    }
  }
};

// Function to handle login with session password
const onLogin = async () => {
  if (!sessionPassword.value) {
    showError("sessionPassword", "Session password is required.");
    return;
  }

  hideError("sessionPassword");
  const response = await postLoginRequest({
    email: username.value,
    session_password: sessionPassword.value
  });

  if (response["Authorization"]) {
    // Store the token in localStorage for future requests
    localStorage.setItem("token", response["Authorization"]);
    axios.defaults.headers["Authorization"] = `${response["Authorization"]}`;

    // Redirect user to the chat page after successful login
    router.push({ path: "/chat", replace: true });
  } else {
    showError("sessionPassword", "Password does not match.");
  }
};

const updateUsername = (value) => {
  username.value = value;
};

const updateSessionPassword = (value) => {
  sessionPassword.value = value;
};

</script>

<template>
  <div id="login">
    <RecaptchaV2 />
    <p>Email:</p>
    <input
      type="text"
      id="username"
      class="custom-input"
      name="username"
      @input="updateUsername($event.target.value)"
      @keydown.enter="subscriptEmail"
      placeholder="Enter your email for subscription password"
      :aria-describedby="usernameError ? 'username-error' : null"
    />
    <p v-if="usernameError" id="username-error" class="red">{{ usernameError }}</p>

    <div v-if="subscriptionButtonClicked">
      <p>Session Password:</p>
      <input
        type="text"
        id="sessionPassword"
        class="custom-input"
        name="sessionPassword"
        @input="updateSessionPassword($event.target.value)"
        @keydown.enter="onLogin"
        placeholder="Please check your email for session password"
        :aria-describedby="sessionPasswordError ? 'session-password-error' : null"
      />
      <p v-if="sessionPasswordError" id="session-password-error" class="red">{{ sessionPasswordError }}</p>
      <div v-else="true">
        <br />
      </div>
      <button class="btn-login-page" @click="onLogin" :disabled="loading.value">
        <span v-if="loading.value">Loading...</span>
        <span v-else>Login</span>
      </button>
    </div>

    <div v-else="true">
      <button class="btn-login-page" @click="subscriptEmail" :disabled="loading.value">
        <span v-if="loading.value">Loading...</span>
        <span v-else>Get Password</span>
      </button>
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
