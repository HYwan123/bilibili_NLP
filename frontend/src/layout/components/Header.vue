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
  background: var(--bg-card);
  border-bottom: 1px solid var(--separator-color);
  height: 56px;
  padding: 0 24px;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  padding: 8px;
  border-radius: 8px;
}

.collapse-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.el-dropdown-link:hover {
  background: var(--bg-hover);
}
</style> 