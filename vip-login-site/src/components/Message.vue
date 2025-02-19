<script setup>
import { computed } from "vue";
import MarkdownIt from "markdown-it";

const props = defineProps({
  content: String,
  isLlm: Boolean,
});

const md = new MarkdownIt();

// Use computed property to re-render when `content` changes
const renderedMarkdown = computed(() => md.render(props.content || ""));
</script>

<template>
  <div class="chat-message">
    <div v-bind:class="isLlm ? 'assistant message' : 'human message'" v-html="renderedMarkdown"></div>
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
  background-color: #000000;
  float: left;
  color: #ffffff;
}
.human {
  float: right;
  background-color: #ffffff;
  color: #000000;
}
</style>
