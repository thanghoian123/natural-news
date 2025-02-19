<template>
    <Layout v-if="isLayoutRoute">
      <router-view />
    </Layout>
    <router-view v-else />
</template>

<script>
import { useRoute } from "vue-router";
import { computed } from "vue";
import Layout from "./components/Layout.vue";

export default {
  components: { Layout },
  setup() {
    const route = useRoute();

    // Show layout only for specific routes
    const isLayoutRoute = computed(() =>
      ["/video-report","/chat", "/ingredient-checker"].includes(route.path)
    );

    return { isLayoutRoute };
  },
};
</script>
