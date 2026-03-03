<template>
  <div class="home-container">
    <!-- Hero 区域 - Apple 风格 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          B站智能分析平台
        </h1>
        <p class="hero-subtitle">
          基于 AI 驱动的数据分析系统<br>
          深度洞察用户情感与内容趋势
        </p>
        <div class="hero-actions">
          <el-button
            type="primary"
            size="large"
            @click="$router.push('/comment-analysis')"
            class="cta-button"
          >
            开始分析
          </el-button>
          <el-button
            size="large"
            @click="$router.push('/ai-chat')"
            class="cta-button-secondary"
          >
            AI 问答
          </el-button>
        </div>
      </div>
    </section>

    <!-- 统计数据 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-number">{{ formatNumber(stats[0].value) }}</div>
          <div class="stat-label">累计查询</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ formatNumber(stats[1].value) }}</div>
          <div class="stat-label">评论处理</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ formatNumber(stats[2].value) }}</div>
          <div class="stat-label">用户画像</div>
        </div>
      </div>
    </section>

    <!-- 功能特性 -->
    <section class="features-section">
      <div class="section-header">
        <h2 class="section-title">核心功能</h2>
        <p class="section-subtitle">全方位数据分析能力</p>
      </div>
      <div class="features-grid">
        <div 
          v-for="feature in features" 
          :key="feature.title"
          class="feature-card"
          @click="$router.push(feature.path)"
        >
          <div class="feature-icon">
            <el-icon :size="32">
              <component :is="feature.icon" />
            </el-icon>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
          <div class="feature-tags">
            <span v-for="tag in feature.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 区域 -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">开始数据分析之旅</h2>
        <p class="cta-subtitle">几分钟内即可获得专业的数据分析报告</p>
        <el-button
          type="primary"
          size="large"
          @click="$router.push('/comment-analysis')"
          class="cta-button-large"
        >
          免费开始
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { 
  ChatDotRound, 
  User, 
  DataLine, 
  MagicStick 
} from '@element-plus/icons-vue';
import { get_history_data } from '@/api/bilibili';

const stats = ref([
  { value: 0, label: '累计查询' },
  { value: 0, label: '评论处理' },
  { value: 0, label: '用户画像' }
]);

const features = [
  {
    title: '评论智能分析',
    desc: '基于NLP技术深度分析评论情感倾向、关键词提取与话题聚类',
    path: '/comment-analysis',
    icon: 'ChatDotRound',
    tags: ['情感分析', '关键词提取']
  },
  {
    title: '用户画像构建',
    desc: '多维度分析用户行为特征，构建精准的用户群体画像',
    path: '/user-portrait',
    icon: 'User',
    tags: ['行为分析', '群体画像']
  },
  {
    title: '内容推荐优化',
    desc: 'AI驱动的内容推荐策略，提升内容传播效果与用户互动',
    path: '/new-recommendation',
    icon: 'MagicStick',
    tags: ['智能推荐', '趋势预测']
  },
  {
    title: '数据趋势洞察',
    desc: '实时监控数据变化趋势，发现潜在热点与增长机会',
    path: '/user-analysis',
    icon: 'DataLine',
    tags: ['趋势分析', '热点发现']
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
  background: var(--bg-secondary);
}

/* Hero 区域 - Apple 风格 */
.hero-section {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  padding: 80px 24px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
}

.hero-title {
  font-size: clamp(40px, 8vw, 64px);
  font-weight: 700;
  line-height: 1.1;
  color: var(--text-primary);
  margin-bottom: 20px;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: clamp(18px, 3vw, 24px);
  line-height: 1.5;
  color: var(--text-secondary);
  margin-bottom: 40px;
  font-weight: 400;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-button {
  padding: 16px 32px !important;
  font-size: 17px !important;
  font-weight: 500 !important;
  border-radius: 12px !important;
  height: auto !important;
}

.cta-button-secondary {
  padding: 16px 32px !important;
  font-size: 17px !important;
  font-weight: 500 !important;
  border-radius: 12px !important;
  height: auto !important;
  background: var(--bg-tertiary) !important;
  border: none !important;
  color: var(--text-primary) !important;
}

.cta-button-secondary:hover {
  background: var(--bg-hover) !important;
}

/* 统计数据区域 */
.stats-section {
  padding: 60px 24px;
  background: var(--bg-card);
  border-top: 1px solid var(--separator-color);
  border-bottom: 1px solid var(--separator-color);
}

.stats-grid {
  display: flex;
  justify-content: center;
  gap: 60px;
  max-width: 800px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 48px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 400;
}

/* 功能特性区域 */
.features-section {
  padding: 100px 24px;
  background: var(--bg-secondary);
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 40px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  font-weight: 400;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.feature-card {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 32px;
  cursor: pointer;
  border: 1px solid var(--border-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-color);
}

.feature-icon {
  width: 56px;
  height: 56px;
  background: rgba(0, 122, 255, 0.1);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  margin-bottom: 20px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.feature-desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 16px;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: rgba(0, 122, 255, 0.08);
  color: var(--primary-color);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

/* CTA 区域 */
.cta-section {
  padding: 100px 24px;
  background: var(--bg-card);
  text-align: center;
  border-top: 1px solid var(--separator-color);
}

.cta-content {
  max-width: 600px;
  margin: 0 auto;
}

.cta-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.cta-subtitle {
  font-size: 17px;
  color: var(--text-secondary);
  margin-bottom: 32px;
}

.cta-button-large {
  padding: 16px 40px !important;
  font-size: 17px !important;
  font-weight: 500 !important;
  border-radius: 12px !important;
  height: auto !important;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .feature-card:hover {
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  }

  .feature-icon {
    background: rgba(10, 132, 255, 0.15);
  }

  .tag {
    background: rgba(10, 132, 255, 0.12);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    min-height: 60vh;
    padding: 60px 20px;
  }

  .stats-grid {
    gap: 40px;
  }

  .stat-number {
    font-size: 36px;
  }

  .features-section,
  .cta-section {
    padding: 60px 20px;
  }

  .section-title {
    font-size: 32px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>