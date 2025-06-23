<template>
  <el-aside :width="layoutStore.isCollapse ? '64px' : '200px'">
    <div class="logo-box">
      <img class="logo-img" src="@/assets/logo.png" alt="logo" />
      <span v-if="!layoutStore.isCollapse" class="logo-text"></span>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical-demo"
      :collapse="layoutStore.isCollapse"
      router
    >
      <el-menu-item index="/query">
        <el-icon><Search /></el-icon>
        <template #title><span>视频评论查询</span></template>
      </el-menu-item>      
      <el-menu-item index="/comment-analysis">
        <el-icon><DataAnalysis /></el-icon>
        <template #title><span>评论分析</span></template>
      </el-menu-item>
      <el-menu-item index="/history">
        <el-icon><Tickets /></el-icon>
        <template #title><span>视频查询历史记录</span></template>
      </el-menu-item>
      <el-menu-item index="/user-analysis">
        <el-icon><User /></el-icon>
        <template #title><span>用户评论获取</span></template>
      </el-menu-item>
      <el-menu-item index="/user-portrait">
        <el-icon><Document /></el-icon>
        <span>用户画像分析</span>
      </el-menu-item>
      <el-menu-item index="/structure">
        <el-icon><DataLine /></el-icon>
        <template #title><span>AI 结构</span></template>
      </el-menu-item>


    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useLayoutStore } from '@/stores/layout';
import { Search, DataLine, Tickets, User, Document, DataAnalysis } from '@element-plus/icons-vue';

const route = useRoute();
const layoutStore = useLayoutStore();

const activeMenu = computed(() => route.path);
</script>

<style scoped>
.el-aside {
  background-color: #304156;
  transition: width 0.3s;
  color: #bfcbd9;
}
.el-menu {
  border-right: none;
  background-color: #304156;
}
.el-menu-item {
  color: #bfcbd9;
}
.el-menu-item:hover {
  background-color: #263445 !important;
}
.el-menu-item.is-active {
  color: #409eff !important;
}
.logo-box {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background-color: #2b2f3a;
}
.logo-img {
  width: 224px;
  height: 100px;
}
.logo-text {
  margin-left: 12px;
  font-size: 18px;
  color: #fff;
  font-weight: bold;
}
</style> 