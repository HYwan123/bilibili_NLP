<template>
  <el-main class="main-content">
    <router-view />
  </el-main>
</template>

<script setup lang="ts">
</script>

<style scoped>
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  /* 确保主内容区可以滚动 */
  overflow-y: auto;
  height: calc(100vh - 60px); /* 减去 Header 的高度 */
}
</style> 