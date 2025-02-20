<script setup>
import axios from "axios";
import { ref } from "vue";
// import Header from "../components/Header.vue";
import User from "@/components/User.vue";
import Video from "@/components/Video.vue";
import { useUserStore } from "@/stores/user";

axios.defaults.baseURL = import.meta.env.VITE_BASE_URL;
axios.defaults.withCredentials = true;

const videos = ref([]);

const getVideos = async (limit = 15, offset = 0) => {
  const path = `/videos?limit=${limit}&offset=${offset}`;
  const responseData = (await axios.get(path)).data;
  for (const video of responseData) {
    videos.value.push({
      url: video.url,
      age: video.age,
      duration: video.duration,
      name: video.name,
      thumbnail: video.thumbnail,
      id:video.embed_url,
      analytics: {
        videoView: video.analytics.video_view
      },
      creator: {
        name: video.creator.name,
        avatarUrl: video.creator.avatar,
      }
    });
  }
}

(async () => await getVideos())();

const userStore = useUserStore();
const user = ref({
  username: userStore.username,
  tokenRemain: userStore.tokenRemain,
});
</script>

<template>
  <div class="chat-view">
    <User :username="user.username" :token-remain="user.tokenRemain" />
    <div class="content">
      <div class="videos">
        <div class="video" v-for="video in videos">
          <Video
            :name="video.name"
            :duration="video.duration"
            :thumbnail="video.thumbnail"
            :channel-avatar="video.creator.avatarUrl"
            :channel-name="video.creator.name"
            :views="video.analytics.videoView"
            :age="video.age"
            :id="video.id"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.videos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

</style>
