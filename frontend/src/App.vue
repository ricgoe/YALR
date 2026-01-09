<script setup lang="ts">
import { Notifications } from '@kyvg/vue3-notification';
import VideoRecorder from './components/VideoRecorder.vue';
</script>

<template>
  <div>
    <img src="/lips.svg" class="logo" alt="YALR logo" />
  </div>
  <VideoRecorder/>
  <notifications />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #511d61aa);
}
</style>
