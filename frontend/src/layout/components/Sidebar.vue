<template>
  <el-aside :width="layoutStore.isCollapse ? '64px' : '240px'" class="modern-sidebar">
    <!-- Logo区域 -->
    <div class="logo-section">
      <div class="logo-container">
        <div class="logo-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <transition name="fade-slide">
          <div v-if="!layoutStore.isCollapse" class="logo-text">
            <div class="logo-title">B站分析</div>
            <div class="logo-subtitle">智能平台</div>
          </div>
        </transition>
      </div>
    </div>

    <!-- 导航菜单 -->
    <div class="nav-section">
      <!-- 核心功能组 -->
      <div v-if="!layoutStore.isCollapse" class="menu-group-title">核心功能</div>
      
      <el-menu
        :default-active="activeMenu"
        class="modern-menu"
        :collapse="layoutStore.isCollapse"
        router
        :collapse-transition="true"
      >
        <el-menu-item index="/home" class="modern-menu-item">
          <el-icon class="menu-icon"><House /></el-icon>
          <span class="menu-text">首页概览</span>
        </el-menu-item>
        
        <el-menu-item index="/query" class="modern-menu-item">
          <el-icon class="menu-icon"><Search /></el-icon>

          <span class="menu-text">cookie管理</span>
        </el-menu-item>   

        <el-menu-item index="/comment-analysis" class="modern-menu-item">
          <el-icon class="menu-icon"><DataAnalysis /></el-icon>
          <span class="menu-text">智能分析</span>
        </el-menu-item>

        <el-menu-item index="/ai-chat" class="modern-menu-item">
          <el-icon class="menu-icon"><ChatDotRound /></el-icon>
          <span class="menu-text">AI 问答</span>
        </el-menu-item>

      </el-menu>

      <!-- 用户分析组 -->
      <div v-if="!layoutStore.isCollapse" class="menu-group-title">用户洞察</div>
      
      <el-menu
        :default-active="activeMenu"
        class="modern-menu"
        :collapse="layoutStore.isCollapse"
        router
        :collapse-transition="true"
      >

        <el-menu-item index="/user-analysis" class="modern-menu-item">
          <el-icon class="menu-icon"><UserFilled /></el-icon>
          <span class="menu-text">行为分析</span>
        </el-menu-item>


        <el-menu-item index="/new-recommendation" class="modern-menu-item">
          <el-icon class="menu-icon"><MagicStick /></el-icon>
          <span class="menu-text">内容推荐</span>
        </el-menu-item>
      </el-menu>

      <!-- 数据管理组 -->
      <div v-if="!layoutStore.isCollapse" class="menu-group-title">数据管理</div>
      
      <el-menu
        :default-active="activeMenu"
        class="modern-menu"
        :collapse="layoutStore.isCollapse"
        router
        :collapse-transition="true"
      >
        <el-menu-item index="/history" class="modern-menu-item">
          <el-icon class="menu-icon"><Tickets /></el-icon>
          <span class="menu-text">历史记录</span>
        </el-menu-item>
            <el-menu-item index="/user-portrait" class="modern-menu-item">
          <el-icon class="menu-icon"><User /></el-icon>
          <span class="menu-text">用户画像</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 底部操作区域 -->
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useLayoutStore } from '@/stores/layout';
import { 
  Search, 
  Tickets, 
  User, 
  UserFilled,
  DataAnalysis, 
  House, 
  Star,
  TrendCharts,
  Expand,
  Fold,
  MagicStick,
  ChatDotRound
} from '@element-plus/icons-vue';

const route = useRoute();
const layoutStore = useLayoutStore();

const activeMenu = computed(() => route.path);

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  layoutStore.toggleCollapse();
};
</script>

<style scoped>
/* Apple 风格侧边栏主体 */
.modern-sidebar {
  background: var(--bg-secondary);
  box-shadow: 1px 0 0 var(--separator-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-right: none;
  position: relative;
  overflow: hidden;
}

/* Logo区域 - Apple 风格 */
.logo-section {
  padding: 24px 20px;
  background: transparent;
  border-bottom: 1px solid var(--separator-color);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: var(--primary-color);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.logo-text {
  color: var(--text-primary);
}

.logo-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 1px;
  letter-spacing: -0.01em;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 400;
}

/* 导航菜单区域 */
.nav-section {
  flex: 1;
  padding: 0;
  overflow-y: auto;
}

.modern-menu {
  background: transparent !important;
  border: none !important;
  padding: 16px 0;
}

/* Apple 风格菜单组标题 */
.menu-group-title {
  padding: 20px 24px 8px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.menu-group-title:first-child {
  margin-top: 0;
}

/* Apple 风格菜单项 */
.modern-menu-item {
  margin: 2px 12px;
  border-radius: 8px !important;
  background: transparent !important;
  border: none !important;
  transition: all 0.2s ease !important;
  position: relative;
  overflow: hidden;
  height: 40px !important;
  line-height: 40px !important;
}

.modern-menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background: var(--primary-color);
  transform: scaleY(0);
  transition: transform 0.2s ease;
  border-radius: 0 2px 2px 0;
}

.modern-menu-item.is-active::before {
  transform: scaleY(1);
}

.modern-menu-item:hover {
  background: var(--bg-hover) !important;
}

.modern-menu-item.is-active {
  background: rgba(0, 122, 255, 0.1) !important;
  color: var(--primary-color) !important;
}

.menu-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0;
}

.menu-icon {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  margin-right: 12px;
}

.modern-menu-item:hover .menu-icon {
  color: var(--text-primary);
}

.modern-menu-item.is-active .menu-icon {
  color: var(--primary-color);
}

.menu-text {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-primary);
  transition: color 0.2s ease;
}

.modern-menu-item:hover .menu-text {
  color: var(--text-primary);
}

.modern-menu-item.is-active .menu-text {
  color: var(--primary-color);
  font-weight: 500;
}

/* 底部操作区域 */
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--separator-color);
  background: transparent;
}

.collapse-btn {
  width: 36px;
  height: 36px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);
  margin: 0 auto;
}

.collapse-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* Apple 风格滚动条 - Sidebar专用 */
.nav-section::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.nav-section::-webkit-scrollbar-track {
  background: transparent;
}

.nav-section::-webkit-scrollbar-track:hover {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 10px;
}

.nav-section::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  border: 1px solid transparent;
  background-clip: padding-box;
  min-height: 40px;
}

.nav-section::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

.nav-section::-webkit-scrollbar-thumb:active {
  background: rgba(0, 0, 0, 0.35);
}

.nav-section::-webkit-scrollbar-corner {
  background: transparent;
}

/* Firefox滚动条支持 */
.nav-section {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
}

/* 折叠状态优化 */
.modern-sidebar.el-aside--collapsed .menu-group-title {
  display: none;
}

.modern-sidebar.el-aside--collapsed .modern-menu-item {
  margin: 4px 8px;
  justify-content: center;
}

.modern-sidebar.el-aside--collapsed .menu-item-content {
  justify-content: center;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .modern-sidebar {
    box-shadow: none;
  }
  
  .logo-section {
    padding: 16px;
  }
  
  .menu-group-title {
    padding: 12px 16px 6px;
  }
  
  .modern-menu-item {
    margin: 2px 8px;
  }
}

/* Apple 风格 Element Plus 菜单样式覆盖 */
:deep(.el-menu) {
  background: transparent !important;
  border: none !important;
}

:deep(.el-menu-item) {
  background: transparent !important;
  border: none !important;
  color: var(--text-primary) !important;
  padding: 0 16px !important;
  height: 40px !important;
  line-height: 40px !important;
}

:deep(.el-menu-item:hover) {
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
}

:deep(.el-menu-item.is-active) {
  background: rgba(0, 122, 255, 0.1) !important;
  color: var(--primary-color) !important;
}

:deep(.el-menu--collapse .el-menu-item) {
  padding: 0 16px !important;
}

:deep(.el-menu--collapse .el-menu-item [class^="el-icon"]) {
  margin: 0 !important;
}
</style>
