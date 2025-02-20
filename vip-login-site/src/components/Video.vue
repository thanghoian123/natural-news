<script>
export default {
  props: {
    thumbnail: String,
    duration: String,
    name: String,
    channelAvatar: String,
    channelName: String,
    age: String,
    views: Number,
    id: String
  },
  methods: {
    navigateToVideo() {
      this.$router.push(`/video-report/${this.id}`);
    }
  }
};
</script>

<template>
  <div class="video-card" @click="navigateToVideo">
    <div class="thumbnail">
      <img :src="thumbnail" alt="thumbnail" />
      <div class="duration">{{ duration }}</div>
      <div class="avatar">
        <img :src="channelAvatar" :alt="channelName" />
      </div>
    </div>
    <div class="info">
      <div class="name">{{ name }}</div>
      <div class="desc">
        <div class="desc-item">{{ age }}</div>
        <div class="desc-item">{{ views }} <span>view(s)</span></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-card {
  cursor: pointer;
}
.thumbnail {
  width: 240px;
}
div.thumbnail > img {
  width: 100%;
  height: auto;
}
.duration {
  font-weight: bold;
  background-color: var(--color-background);
  padding: 2px;
  width: 25%;
  text-align: center;
  top: -2rem;
  position: relative;
}
.info {
  top: -2rem;
  position: relative;
  padding: 5px;
}
.avatar {
  height: 35px;
  width: 35px;
  top: -10.65rem;
  position: relative;
  float: right;
}
div.avatar > img {
  width: 100%;
  height: auto;
}
.name {
  font-weight: bold;
  font-size: small;
}
.desc {
  display: flex;
}
.desc-item {
  padding: 2px;
  font-size: smaller;
}
</style>
