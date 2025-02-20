<template>
  <Layout v-if="isLayoutRoute">
    <router-view />
  </Layout>
  <router-view v-else />
</template>

<script>
import { useRoute } from "vue-router";
import { computed, watch, ref, onMounted } from "vue";
import Layout from "./components/Layout.vue";

export default {
  components: { Layout },
  setup() {
    const route = useRoute();
    const isLayoutRoute = ref(false);

    // Function to update isLayoutRoute
    const updateIsLayoutRoute = () => {
      console.log("Meta data:", route.meta);
      isLayoutRoute.value = !!route?.meta?.requiresAuth;
    };

    // Watch route.meta or route.fullPath to detect changes
    watch(
      () => route.fullPath,
      () => {
        console.log("Route changed:", route.fullPath);
        updateIsLayoutRoute();
      },
      { immediate: true } // Ensure it runs initially
    );

    return { isLayoutRoute }; // Return ref, not its value
  },
};
</script>
