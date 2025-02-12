<script setup>
import axios from "axios";
import { ref } from "vue";
import Message from "../components/Message.vue";
import User from "../components/User.vue";
import router from "../router";

axios.defaults.withCredentials = true;
axios.defaults.baseURL = "http://localhost:8000";

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

const _check_user = async () => {
  try {
    const responseData = (await axios.get("/login")).data;
    return new BackendUser(responseData["login"], responseData["token_remain"]);
  } catch {
    return new BackendUser("", 0);
  }
};

const _check_messages = async () => {
  try {
    const responseData = (await axios.get("/chat")).data;
    let retVal = new Array();
    for (const message of responseData) {
      console.log(message);
      retVal.push(
        new ChatMessages(
          message.content,
          message.is_llm,
        )
      )
    }
    retVal.reverse();
    return retVal;
  } catch {
    return [];
  }
}

(async () => {
  user.value = await _check_user();
})();

const messages = ref([]);
(async () => {
  messages.value = await _check_messages();
})();
let prompt = ref("");


const send_messages = async () => {
  messages.value.push(new ChatMessages(prompt.value, false));
  await axios.post(
    "/chat",
    {
      value: prompt.value,
    },
    {
      headers: {
        "Content-Type": "application/json;charset=UTF-8"
      }
    }
  )
  document.querySelector("#prompt").value = "";
  messages.value = await _check_messages();
  user.value = await _check_user();
};

const updatePrompt = (value) => {
  prompt = ref(value);
}
</script>

<template>
  <div class="chat-view">
    <User :username="user.username" :token-remain="user.tokenRemain" />
    <div class="chat-area" v-if="user.username">
      <div v-for="message in messages">
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
    width: 768px;
    height: 100vh;
    display: flex;
    flex-direction: column;
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
    width: 768px;
    padding: 4px;
    margin-bottom: 30px;
  }
  #prompt {
    border: none;
    width: 690px;
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
</style>
