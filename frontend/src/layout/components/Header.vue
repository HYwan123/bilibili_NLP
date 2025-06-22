<template>
  <el-header class="header">
    <el-icon class="collapse-icon" @click="layoutStore.toggleCollapse">
      <component :is="layoutStore.isCollapse ? 'Expand' : 'Fold'" />
    </el-icon>
    <div class="header-right">
      <el-dropdown>
        <span class="el-dropdown-link">
          {{ authStore.username }}
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人信息</el-dropdown-item>
            <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useLayoutStore } from '@/stores/layout';
import { ArrowDown, Expand, Fold } from '@element-plus/icons-vue';

const router = useRouter();
const authStore = useAuthStore();
const layoutStore = useLayoutStore();

const logout = () => {
  authStore.clearToken();
  router.push('/login');
};
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  height: 60px;
}
.collapse-icon {
  font-size: 24px;
  cursor: pointer;
}
</style> 