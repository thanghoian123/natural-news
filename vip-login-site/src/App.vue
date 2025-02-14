<script setup>
import { RouterView } from "vue-router";
</script>

<template>
  <header>
    
    <div class="wrapper">
      <img alt="logo" class="logo" src="@/assets/UI-NN-Logo-Independent-Humanitarian-Peace.svg" height="55" />
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
.wrapper {
  position: absolute;
  top: 4px;
}
</style>
