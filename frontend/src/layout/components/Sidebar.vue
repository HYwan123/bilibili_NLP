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

        <el-menu-item index="/content-recommendation" class="modern-menu-item">
          <el-icon class="menu-icon"><Star /></el-icon>
          <span class="menu-text">内容推荐</span>
        </el-menu-item>

        <el-menu-item index="/new-recommendation" class="modern-menu-item">
          <el-icon class="menu-icon"><MagicStick /></el-icon>
          <span class="menu-text">新版推荐</span>
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
  MagicStick
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
/* 侧边栏主体 */
.modern-sidebar {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.modern-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent 0%, rgba(102, 126, 234, 0.3) 50%, transparent 100%);
}

/* Logo区域 */
.logo-section {
  padding: 24px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.logo-text {
  color: white;
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 2px;
}

.logo-subtitle {
  font-size: 12px;
  opacity: 0.7;
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

/* 菜单组标题 */
.menu-group-title {
  padding: 16px 24px 8px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 8px;
}

.menu-group-title:first-child {
  margin-top: 0;
}

/* 菜单项 */
.modern-menu-item {
  margin: 4px 12px;
  border-radius: 12px !important;
  background: transparent !important;
  border: none !important;
  transition: all 0.3s ease !important;
  position: relative;
  overflow: hidden;
}

.modern-menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.modern-menu-item.is-active::before {
  transform: scaleY(1);
}

.modern-menu-item:hover {
  background: rgba(102, 126, 234, 0.1) !important;
  transform: translateX(4px);
}

.modern-menu-item.is-active {
  background: rgba(102, 126, 234, 0.15) !important;
  color: #667eea !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
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
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.modern-menu-item:hover .menu-icon,
.modern-menu-item.is-active .menu-icon {
  color: #667eea;
  transform: scale(1.1);
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  transition: color 0.3s ease;
}

.modern-menu-item:hover .menu-text,
.modern-menu-item.is-active .menu-text {
  color: #667eea;
}

/* 底部操作区域 */
.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.collapse-btn {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 auto;
}

.collapse-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  transform: scale(1.05);
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

/* 滚动条美化 */
.nav-section::-webkit-scrollbar {
  width: 4px;
}

.nav-section::-webkit-scrollbar-track {
  background: transparent;
}

.nav-section::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 2px;
}

.nav-section::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
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

/* Element Plus 菜单样式覆盖 */
:deep(.el-menu) {
  background: transparent !important;
  border: none !important;
}

:deep(.el-menu-item) {
  background: transparent !important;
  border: none !important;
  color: rgba(255, 255, 255, 0.8) !important;
  padding: 12px 16px !important;
  height: auto !important;
  line-height: normal !important;
}

:deep(.el-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1) !important;
  color: #667eea !important;
}

:deep(.el-menu-item.is-active) {
  background: rgba(102, 126, 234, 0.15) !important;
  color: #667eea !important;
}

:deep(.el-menu--collapse .el-menu-item) {
  padding: 12px 16px !important;
}

:deep(.el-menu--collapse .el-menu-item [class^="el-icon"]) {
  margin: 0 !important;
}
</style>
