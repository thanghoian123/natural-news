<script>
import router from '@/router';

export default {
  props: {
    username: String,
    tokenRemain: Number,
  },
  methods: {
    goToLogin () {
      router.push({
        path: "/login",
        replace: true,
      });
    } 
  }
};
</script>

<template>
  <p v-if="username" class="greeting-user">Hello <span class="text-bold">{{ username }}</span>, You have {{ tokenRemain }} token(s) left!</p>
  <button v-else="" @click="goToLogin" class="btn-login greeting-user">Go to Login</button>
</template>

<style scoped>
.text-bold {
  font-weight: bold;
}
.greeting-user {
  margin-top: 4px;
  font-size: medium;
  margin-left: auto;
}
.btn-login {
    height: 44px;
    border-radius: 3px;
    background-color: hsla(160, 100%, 37%, 1);
    width: 150px;
    color: var(--color-text);
    border: none;
    font-weight: bold;
}
</style>
