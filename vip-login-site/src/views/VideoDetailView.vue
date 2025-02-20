<script>
import { useRoute } from 'vue-router';

export default {
  setup() {
    const route = useRoute();
    const videoId = route.params.id;
    const videoUrl = `https://www.brighteon.com/embed/${videoId}`;
    
    return { videoUrl };
  }
};
</script>

<template>
  <div class="video-report">
    <h1>Video Report</h1>
    <iframe :src="videoUrl" frameborder="0" allowfullscreen></iframe>
  </div>
</template>

<style scoped>
.video-report {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  padding: 20px;
}
iframe {
  width: 100%;
  height: 500px;
}
</style>
