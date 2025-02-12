<script>
export default {
  props: {
    content: String,
    isLlm: Boolean,
  }
}
</script>

<template>
  <div class="chat-message">
    <div v-bind:class="isLlm ? 'assistant message' : 'human message'">
      <p>{{ content }}</p>
    </div>
  </div>
</template>

<style scoped>
  .chat-message {
    display: inline-block;
    width: 100%;
  }
  .message {
    padding: 10px;
    border: none;
    border-radius: 4px;
    max-width: 90%;
  }
  .assistant {
    background-color: #000;
    float: left;
  }
  .human {
    float: right;
    background-color: #222;
    color: #777;
  }
</style>
