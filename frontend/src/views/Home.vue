<template>
  <div class="home-container">
    <!-- Hero 区域 -->
    <section class="hero-section">
      <h1 class="hero-title">B站智能分析平台</h1>
      <p class="hero-subtitle">AI 驱动的数据分析系统，深度洞察用户情感与内容趋势</p>
      <div class="hero-actions">
        <el-button type="primary" size="large" @click="$router.push('/comment-analysis')">
          开始分析
        </el-button>
        <el-button size="large" @click="$router.push('/ai-chat')">
          AI 问答
        </el-button>
      </div>
      <!-- 统计数据 -->
      <div class="hero-stats">
        <div v-for="(stat, idx) in stats" :key="idx" class="stat-item">
          <span class="stat-number">{{ formatNumber(stat.value) }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </section>

    <!-- 功能卡片 -->
    <section class="features-section">
      <div class="features-grid">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="feature-card"
          @click="$router.push(feature.path)"
        >
          <component :is="feature.icon" class="feature-icon" />
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ChatDotRound, User, DataLine, MagicStick } from '@element-plus/icons-vue';
import { get_history_data } from '@/api/bilibili';

const stats = ref([
  { value: 0, label: '累计查询' },
  { value: 0, label: '评论处理' },
  { value: 0, label: '用户画像' }
]);

const features = [
  {
    title: '评论分析',
    desc: '深度分析评论情感与关键词',
    path: '/comment-analysis',
    icon: ChatDotRound
  },
  {
    title: '用户画像',
    desc: '构建精准用户群体画像',
    path: '/user-portrait',
    icon: User
  },
  {
    title: '内容推荐',
    desc: 'AI 驱动的智能推荐策略',
    path: '/new-recommendation',
    icon: MagicStick
  },
  {
    title: '趋势洞察',
    desc: '发现潜在热点与增长机会',
    path: '/user-analysis',
    icon: DataLine
  }
];

const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return num.toLocaleString();
};

const animateNumber = (index: number, endValue: number, duration = 2000) => {
  const startTime = Date.now();
  const startValue = 0;

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);

    stats.value[index].value = currentValue;

    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };

  animate();
};

onMounted(async () => {
  try {
    const response = await get_history_data();
    if (response.code === 200 && response.data) {
      const data = response.data;
      setTimeout(() => {
        animateNumber(0, data.leiji ?? 0, 2000);
        animateNumber(1, data.chuli ?? 0, 2500);
        animateNumber(2, data.huaxiang ?? 0, 2200);
      }, 500);
    }
  } catch (err) {
    console.error('获取历史数据失败:', err);
  }
});
</script>

<style scoped>
.home-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  background: var(--bg-secondary);
}

/* Hero 区域 */
.hero-section {
  text-align: center;
  margin-bottom: 80px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  max-width: 400px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 统计数据 */
.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin-top: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 功能卡片 */
.features-section {
  width: 100%;
  max-width: 800px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.feature-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.feature-icon {
  width: 28px;
  height: 28px;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 响应式 */
@media (max-width: 600px) {
  .hero-title {
    font-size: 32px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
