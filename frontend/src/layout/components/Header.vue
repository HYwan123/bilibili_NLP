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
  background: linear-gradient(90deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-bottom: 2px solid rgba(6, 95, 70, 0.2);
  box-shadow: var(--shadow-sm);
  height: 60px;
  padding: 0 20px;
}

.collapse-icon {
  font-size: 24px;
  cursor: pointer;
  color: var(--primary-color);
  transition: all 0.3s ease;
  padding: 8px;
  border-radius: var(--radius-md);
}

.collapse-icon:hover {
  background: rgba(6, 95, 70, 0.1);
  color: var(--primary-light);
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--primary-color);
  font-weight: 500;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.el-dropdown-link:hover {
  background: rgba(6, 95, 70, 0.1);
  color: var(--primary-light);
}
</style> 