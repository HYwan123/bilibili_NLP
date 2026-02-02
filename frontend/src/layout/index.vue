<template>
  <el-container class="layout-container-demo" style="height: 100vh">
    <Sidebar />
    <el-container class="content-wrapper">
      <Header />
      <AppMain />
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import Sidebar from './components/Sidebar.vue';
import Header from './components/Header.vue';
import AppMain from './components/AppMain.vue';
</script>

<style scoped>
.main-content {
  padding: 0%;
}
.layout-container-demo {
  
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
.content-wrapper {
  flex-direction: column;
}
</style> 