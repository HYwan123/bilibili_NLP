<template>
  <div class="loading-states">
    <!-- 页面级别加载 -->
    <div v-if="type === 'page'" class="page-loading">
      <div class="loading-container">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">{{ text || '正在加载...' }}</div>
        <div v-if="progress !== undefined" class="loading-progress">
          <div class="progress-bar">
            <div 
              class="progress-fill"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
          <div class="progress-text">{{ progress }}%</div>
        </div>
      </div>
    </div>

    <!-- 卡片级别加载 -->
    <div v-else-if="type === 'card'" class="card-loading">
      <div class="card-loading-content">
        <div class="loading-dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="loading-text small">{{ text || '处理中...' }}</div>
      </div>
    </div>

    <!-- 按钮级别加载 -->
    <div v-else-if="type === 'button'" class="button-loading">
      <div class="loading-spinner small">
        <div class="spinner-circle"></div>
      </div>
      <span v-if="text">{{ text }}</span>
    </div>

    <!-- 骨架屏加载 -->
    <div v-else-if="type === 'skeleton'" class="skeleton-loading">
      <div class="skeleton-header">
        <div class="skeleton-line skeleton-title"></div>
        <div class="skeleton-line skeleton-subtitle"></div>
      </div>
      <div class="skeleton-content">
        <div class="skeleton-line" v-for="n in (lines || 3)" :key="n"></div>
      </div>
    </div>

    <!-- 列表加载 -->
    <div v-else-if="type === 'list'" class="list-loading">
      <div class="list-item-skeleton" v-for="n in (count || 5)" :key="n">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-content">
          <div class="skeleton-line skeleton-name"></div>
          <div class="skeleton-line skeleton-description"></div>
        </div>
      </div>
    </div>

    <!-- 图表加载 -->
    <div v-else-if="type === 'chart'" class="chart-loading">
      <div class="chart-skeleton">
        <div class="chart-title-skeleton"></div>
        <div class="chart-content-skeleton">
          <div class="chart-bars">
            <div 
              v-for="i in 6" 
              :key="i"
              class="chart-bar-skeleton"
              :style="{ height: Math.random() * 80 + 20 + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 默认加载 -->
    <div v-else class="default-loading">
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
      </div>
      <div class="loading-text">{{ text || '加载中...' }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type?: 'page' | 'card' | 'button' | 'skeleton' | 'list' | 'chart' | 'default';
  text?: string;
  progress?: number;
  lines?: number;
  count?: number;
}

withDefaults(defineProps<Props>(), {
  type: 'default',
  text: '',
  progress: undefined,
  lines: 3,
  count: 5
});
</script>

<style scoped>
.loading-states {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 页面级别加载 */
.page-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.loading-spinner {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.spinner-ring {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.1);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 5px;
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.3s;
}

.spinner-ring:nth-child(3) {
  animation-delay: -0.6s;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 16px;
}

.loading-text.small {
  font-size: 0.9rem;
  margin-bottom: 0;
}

.loading-progress {
  margin-top: 20px;
}

.progress-bar {
  width: 200px;
  height: 8px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* 卡片级别加载 */
.card-loading {
  padding: 40px;
  text-align: center;
}

.card-loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 按钮级别加载 */
.button-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner.small {
  margin-bottom: 0;
}

.spinner-circle {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 骨架屏加载 */
.skeleton-loading {
  padding: 20px;
}

.skeleton-header {
  margin-bottom: 20px;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  border-radius: 8px;
  margin-bottom: 12px;
}

.skeleton-title {
  height: 24px;
  width: 60%;
  margin-bottom: 8px;
}

.skeleton-subtitle {
  height: 16px;
  width: 40%;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 列表加载 */
.list-loading {
  padding: 20px;
}

.list-item-skeleton {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

.skeleton-content {
  flex: 1;
}

.skeleton-name {
  width: 40%;
  height: 16px;
  margin-bottom: 8px;
}

.skeleton-description {
  width: 70%;
  height: 14px;
}

/* 图表加载 */
.chart-loading {
  padding: 20px;
  min-height: 300px;
}

.chart-skeleton {
  height: 100%;
}

.chart-title-skeleton {
  height: 24px;
  width: 50%;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  border-radius: 8px;
  margin-bottom: 20px;
}

.chart-content-skeleton {
  height: 200px;
  display: flex;
  align-items: end;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 12px;
}

.chart-bars {
  display: flex;
  align-items: end;
  gap: 12px;
  width: 100%;
  height: 100%;
}

.chart-bar-skeleton {
  flex: 1;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  border-radius: 4px 4px 0 0;
  min-height: 20px;
}

/* 默认加载 */
.default-loading {
  padding: 40px;
  text-align: center;
}

.default-loading .loading-spinner {
  justify-content: center;
}

.default-loading .spinner-ring {
  width: 32px;
  height: 32px;
  border-width: 3px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .loading-container {
    padding: 32px 24px;
    margin: 20px;
  }
  
  .progress-bar {
    width: 160px;
  }
  
  .chart-content-skeleton {
    height: 150px;
    padding: 16px;
  }
}
</style>
