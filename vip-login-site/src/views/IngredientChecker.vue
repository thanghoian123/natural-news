<script setup>
import axios from "axios";
import { ref } from "vue";
import { useRouter } from "vue-router";  // Importing useRouter
import Message from "../components/Message.vue";
import User from "../components/User.vue";

// Base URL
const baseURL = import.meta.env.VITE_BASE_URL;
axios.defaults.baseURL = baseURL ? baseURL : "https://api-hrs.healthrangerstore.com";
axios.defaults.withCredentials = true;

// Class definitions
class ChatMessages {
  constructor(content, isLlm) {
    this.content = content;
    this.isLlm = isLlm;
  }
}

class BackendUser {
  constructor(username, tokenRemain) {
    this.username = username;
    this.tokenRemain = tokenRemain;
  }
}

const user = ref(new BackendUser("", 0));
const router = useRouter(); // Initialize router

// Helper to fetch user data
const _check_user = async () => {
  try {
    const token = localStorage.getItem("token"); // Retrieve token from localStorage
    const responseData = (await axios.get("/login", {
      headers: {
        Authorization: `${token}` // Send token in Authorization header
      }
    })).data;

    return new BackendUser(responseData["login"], responseData["token_remain"]);
  } catch {
    return new BackendUser("", 0);
  }
};

// Helper to fetch messages
const _check_messages = async () => {
  try {
    const token = localStorage.getItem("token"); // Retrieve token from localStorage
    const responseData = (await axios.get("/chat", {
      headers: {
        Authorization: `${token}` // Send token in Authorization header
      }
    })).data;

    let retVal = new Array();
    for (const message of responseData) {
      retVal.push(
        new ChatMessages(
          message.content,
          message.is_llm,
        )
      );
    }
    retVal.reverse();
    return retVal;
  } catch {
    return [];
  }
};

(async () => {
  user.value = await _check_user();
})();

const messages = ref([]);
(async () => {
  messages.value = await _check_messages();
})();

let prompt = ref("");

// Function to send messages
const send_messages = async () => {
  messages.value.push(new ChatMessages(prompt.value, false));

  const token = localStorage.getItem("token"); // Retrieve token from localStorage

  await axios.post(
    "/ingredient-chat",
    {
      value: prompt.value,
    },
    {
      headers: {
        "Content-Type": "application/json;charset=UTF-8",
        Authorization: `${token}` // Include token in the header
      }
    }
  );

  document.querySelector("#prompt").value = "";
  messages.value = await _check_messages();
  user.value = await _check_user();
};

// Update prompt value
const updatePrompt = (value) => {
  prompt.value = value;
};

// Function to handle login (assuming you're already doing it elsewhere in your app)
const subscriptEmail = async () => {
  try {
    const email = username.value;
    const response = await axios.post(
      "/login",
      {
        email: email,
        session_password: "",
      },
      {
        headers: {
          "Content-Type": "application/json; charset=UTF-8"
        }
      }
    );

    // Save token from response
    const token = response.data["Authorization"];
    localStorage.setItem("token", token); // Store the token in localStorage

    // Optionally: redirect the user to the chat page after login
    router.push({ path: "/chat", replace: true });
  } catch (e) {
    console.error(e);
    usernameError.value = "Unexpected error from server, please try again later";
  }
};

const username = ref("");
const sessionPassword = ref("");
const usernameError = ref("");
</script>

<template>
  <div class="chat-view">
    <User :username="user.username" :token-remain="user.tokenRemain" />
    <div class="chat-area" v-if="user.username">
      <div v-for="message in messages" :key="message.content">
        <Message :content="message.content" :is-llm="message.isLlm" />
      </div>
    </div>
    <div class="prompt-area" v-if="user.username">
      <textarea name="prompt" id="prompt" @keypress.enter="send_messages" @input="updatePrompt($event.target.value)" />
      <button @click="send_messages" class="btn-prompt"></button>
    </div>
  </div>
</template>

<style scoped>
.chat-view {
  width:  100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.chat-area {
  width: 100%;
  overflow-y: scroll;
  flex-grow: 1;
}

.prompt-area {
  display: flex;
  z-index: 3;
  min-height: 44px;
  background: #fff;
  border: 1px solid #dfe1e5;
  box-shadow: 0px 2px 8px 0px rgba(60, 64, 67, 0.25);
  border-radius: 24px;
  width: 100%;
  padding: 4px;
  margin-bottom: 30px;
}

#prompt {
  border: none;
  width: 100%;

  /* width: 690px; */
  margin-left: 25px;
  overflow: hidden;
  resize: none;
  padding: 2px 20px;
}

.btn-prompt {
  width: 15px;
  margin-left: 0.5rem;
  border: none;
  background: url(../assets/enter.svg) no-repeat center center;
}

.btn-navigate {
  position: absolute;
  top: 20px;
  left: 20px;
  padding: 8px 16px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
}

.btn-navigate:hover {
  background-color: #0056b3;
}
</style>
