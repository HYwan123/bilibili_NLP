<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* 全局应用深色模式支持 */
#app {
  min-height: 100vh;
  background: var(--bg-secondary);
}

@media (prefers-color-scheme: dark) {
  #app {
    background: var(--bg-secondary);
  }
}
</style>
