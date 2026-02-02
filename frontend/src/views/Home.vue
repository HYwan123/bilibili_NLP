<template>
  <div class="home-container">
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-background">
        <div class="gradient-overlay"></div>
        <div class="floating-shapes">
          <div class="shape shape-1"></div>
          <div class="shape shape-2"></div>
          <div class="shape shape-3"></div>
        </div>
      </div>

      <div class="hero-content">
        <div class="hero-badge fade-in">
          <span>AI 驱动的数据分析平台</span>
        </div>

        <h1 class="hero-title text-gradient fade-in" style="animation-delay: 0.1s">
          B站智能分析平台
        </h1>

        <p class="hero-subtitle fade-in" style="animation-delay: 0.2s">
          基于AI驱动的B站评论分析系统，为内容创作者和研究者提供深度数据洞察，
          <br class="hidden-sm" />
          助您精准把握用户情感与内容趋势
        </p>

        <div class="hero-actions fade-in" style="animation-delay: 0.3s">
          <el-button
            type="primary"
            size="large"
            @click="goTo('/comment-analysis')"
            class="cta-button modern-button"
          >
            立即开始分析
          </el-button>
          <el-button
            size="large"
            @click="goTo('/query')"
            class="cta-button-secondary"
          >
            查询历史记录
          </el-button>
        </div>

        <!-- 统计数据 -->
        <div class="hero-stats" ref="statsRef">
          <div
            v-for="(stat, index) in stats"
            :key="stat.key"
            class="stat-item"
            :class="{ 'visible': statsVisible }"
            :style="{ animationDelay: `${0.4 + index * 0.1}s` }"
          >
            <div class="stat-number">{{ formatNumber(stat.value) }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <!-- 向下滚动提示 -->
      <div class="scroll-indicator" @click="scrollToFeatures">
        <div class="mouse">
          <div class="wheel"></div>
        </div>
        <div class="arrow">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </section>

    <!-- 功能特性区域 -->
    <section class="features-section" ref="featuresRef">
      <div class="container">
        <div class="section-header" :class="{ 'visible': featuresVisible }">
          <span class="section-tag">核心功能</span>
          <h2 class="section-title">全方位数据分析能力</h2>
          <p class="section-desc">整合多种AI分析模型，提供深度内容洞察与用户画像</p>
        </div>

        <div class="features-grid">
          <div
            v-for="(feature, index) in features"
            :key="feature.title"
            class="feature-card"
            :class="{ 'visible': featuresVisible }"
            :style="{ transitionDelay: `${index * 0.1}s` }"
            @click="goTo(feature.path)"
          >
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.desc }}</p>
            <div class="feature-tags">
              <span v-for="tag in feature.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 技术优势区域 -->
    <section class="advantages-section" ref="advantagesRef">
      <div class="container">
        <div class="section-header light" :class="{ 'visible': advantagesVisible }">
          <span class="section-tag light">技术优势</span>
          <h2 class="section-title">为什么选择我们</h2>
          <p class="section-desc light">采用业界领先的AI技术，确保分析结果的准确性与实时性</p>
        </div>

        <div class="advantages-grid">
          <div
            v-for="(advantage, index) in advantages"
            :key="advantage.title"
            class="advantage-item"
            :class="{ 'visible': advantagesVisible }"
            :style="{ transitionDelay: `${index * 0.15}s` }"
          >
            <div class="advantage-number">0{{ index + 1 }}</div>
            <h4 class="advantage-title">{{ advantage.title }}</h4>
            <p class="advantage-desc">{{ advantage.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="process-section" ref="processRef">
      <div class="container">
        <div class="section-header" :class="{ 'visible': processVisible }">
          <span class="section-tag">使用流程</span>
          <h2 class="section-title">三步开启数据分析</h2>
          <p class="section-desc">简单快捷的操作流程，让数据分析触手可及</p>
        </div>

        <div class="process-steps">
          <div
            v-for="(step, index) in steps"
            :key="step.title"
            class="process-step"
            :class="{ 'visible': processVisible }"
            :style="{ transitionDelay: `${index * 0.2}s` }"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3 class="step-title">{{ step.title }}</h3>
              <p class="step-desc">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA区域 -->
    <section class="cta-section" ref="ctaRef">
      <div class="cta-background">
        <div class="gradient-orb orb-1"></div>
        <div class="gradient-orb orb-2"></div>
      </div>
      <div class="container">
        <div class="cta-content" :class="{ 'visible': ctaVisible }">
          <h2 class="cta-title">开始您的数据分析之旅</h2>
          <p class="cta-subtitle">几分钟内即可获得专业的B站数据分析报告，洞察内容价值</p>
          <div class="cta-buttons">
            <el-button
              type="primary"
              size="large"
              @click="goTo('/comment-analysis')"
              class="cta-button modern-button"
            >
              免费开始分析
            </el-button>
          </div>
          <p class="cta-note">无需信用卡，永久免费使用基础功能</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { get_history_data } from '@/api/bilibili';

const router = useRouter();

// 统计数据
const stats = ref([
  { key: 'analysis', value: 0, label: '累计查询' },
  { key: 'comments', value: 0, label: '评论处理' },
  { key: 'users', value: 0, label: '用户画像' }
]);

// 功能列表
const features = [
  {
    title: '评论智能分析',
    desc: '基于NLP技术深度分析评论情感倾向、关键词提取与话题聚类',
    path: '/comment-analysis',
    tags: ['情感分析', '关键词提取', '话题聚类']
  },
  {
    title: '用户画像构建',
    desc: '多维度分析用户行为特征，构建精准的用户群体画像',
    path: '/user-portrait',
    tags: ['行为分析', '群体画像', '兴趣标签']
  },
  {
    title: '内容推荐优化',
    desc: 'AI驱动的内容推荐策略，提升内容传播效果与用户互动',
    path: '/new-recommendation',
    tags: ['智能推荐', '趋势预测', '内容优化']
  },
  {
    title: '数据趋势洞察',
    desc: '实时监控数据变化趋势，发现潜在热点与增长机会',
    path: '/user-analysis',
    tags: ['趋势分析', '热点发现', '增长洞察']
  }
];

// 优势列表
const advantages = [
  {
    title: '精准分析',
    desc: '采用先进的大语言模型，确保情感分析准确率达95%以上'
  },
  {
    title: '实时处理',
    desc: '支持高并发实时数据处理，秒级返回分析结果'
  },
  {
    title: '深度洞察',
    desc: '不止于表面数据，提供深层次的用户行为与内容洞察'
  }
];

// 流程步骤
const steps = [
  {
    title: '输入视频链接',
    desc: '粘贴B站视频链接，系统自动解析视频信息'
  },
  {
    title: 'AI智能分析',
    desc: '多维度AI模型并行分析，提取关键数据指标'
  },
  {
    title: '查看报告',
    desc: '可视化数据报告，支持导出与分享'
  }
];

// 可见性状态
const statsVisible = ref(false);
const featuresVisible = ref(false);
const advantagesVisible = ref(false);
const processVisible = ref(false);
const ctaVisible = ref(false);

// Refs for intersection observer
const statsRef = ref<HTMLElement>();
const featuresRef = ref<HTMLElement>();
const advantagesRef = ref<HTMLElement>();
const processRef = ref<HTMLElement>();
const ctaRef = ref<HTMLElement>();

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return num.toLocaleString();
};

// 页面跳转
const goTo = (path: string) => {
  router.push(path);
};

// 滚动到功能区域
const scrollToFeatures = () => {
  featuresRef.value?.scrollIntoView({ behavior: 'smooth' });
};

// 数字滚动动画
const animateNumber = (target: { value: number }, endValue: number, duration = 2000) => {
  const startTime = Date.now();
  const startValue = 0;

  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);

    target.value = currentValue;

    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };

  animate();
};

// Intersection Observer 设置
let observer: IntersectionObserver | null = null;

onMounted(async () => {
  // 加载历史数据
  try {
    const response = await get_history_data();
    if (response.code === 200 && response.data) {
      const data = response.data;

      // 延迟启动数字动画
      setTimeout(() => {
        animateNumber(stats.value[0], data.leiji ?? 0, 2000);
        animateNumber(stats.value[1], data.chuli ?? 0, 2500);
        animateNumber(stats.value[2], data.huaxiang ?? 0, 2200);
      }, 500);
    }
  } catch (err) {
    console.error('获取历史数据失败:', err);
  }

  // 设置 Intersection Observer
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          if (entry.target === statsRef.value) statsVisible.value = true;
          if (entry.target === featuresRef.value) featuresVisible.value = true;
          if (entry.target === advantagesRef.value) advantagesVisible.value = true;
          if (entry.target === processRef.value) processVisible.value = true;
          if (entry.target === ctaRef.value) ctaVisible.value = true;
        }
      });
    },
    { threshold: 0.2, rootMargin: '0px 0px -50px 0px' }
  );

  // 观察所有区域
  [statsRef, featuresRef, advantagesRef, processRef, ctaRef].forEach((ref) => {
    if (ref.value) observer?.observe(ref.value);
  });

  // 初始状态：hero区域立即显示
  statsVisible.value = true;
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>

<style scoped>
/* ========== 基础布局 ========== */
.home-container {
  width: 100%;
  overflow-x: hidden;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ========== Hero 区域 ========== */
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #134e4a 0%, #065f46 50%, #047857 100%);
  color: white;
  text-align: center;
  padding: 100px 20px 60px;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.gradient-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 20% 80%, rgba(255,255,255,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 50%);
}

/* 浮动形状动画 */
.floating-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  animation: float 20s infinite ease-in-out;
}

.shape-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  left: -50px;
  animation-delay: -7s;
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: 10%;
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 900px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 20px;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 32px;
  opacity: 0;
  animation: fadeInUp 0.6s ease forwards;
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 50%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  opacity: 0;
  animation: fadeInUp 0.6s ease 0.1s forwards;
}

.hero-subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  line-height: 1.7;
  opacity: 0.9;
  margin-bottom: 40px;
  font-weight: 400;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  opacity: 0;
  animation: fadeInUp 0.6s ease 0.2s forwards;
}

.hidden-sm {
  display: block;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 60px;
  opacity: 0;
  animation: fadeInUp 0.6s ease 0.3s forwards;
}

.cta-button {
  padding: 16px 32px !important;
  font-size: 1.1rem !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  background: white !important;
  color: #065f46 !important;
  border: none !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
  transition: all 0.3s ease !important;
}

.cta-button:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3) !important;
}

.cta-button-secondary {
  padding: 16px 32px;
  font-size: 1.1rem;
  border-radius: 12px;
  font-weight: 600;
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.5);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

.cta-button-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: white;
  transform: translateY(-3px);
}

/* 统计数据 */
.hero-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 28px 36px;
  min-width: 160px;
  text-align: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}

.stat-item.visible {
  opacity: 1;
  transform: translateY(0) scale(1);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-item:hover {
  transform: translateY(-8px) scale(1.02);
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #ffffff, #a7f3d0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  font-weight: 500;
}

/* 滚动指示器 */
.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.scroll-indicator:hover {
  opacity: 1;
}

.mouse {
  width: 26px;
  height: 40px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-radius: 13px;
  position: relative;
}

.wheel {
  width: 4px;
  height: 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 2px;
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  animation: scroll 1.5s infinite;
}

@keyframes scroll {
  0% { opacity: 1; transform: translateX(-50%) translateY(0); }
  100% { opacity: 0; transform: translateX(-50%) translateY(12px); }
}

.arrow {
  margin-top: 8px;
}

.arrow span {
  display: block;
  width: 8px;
  height: 8px;
  border-right: 2px solid rgba(255, 255, 255, 0.6);
  border-bottom: 2px solid rgba(255, 255, 255, 0.6);
  transform: rotate(45deg);
  margin: 0 auto;
  animation: arrow 1.5s infinite;
}

.arrow span:nth-child(2) { animation-delay: 0.1s; }
.arrow span:nth-child(3) { animation-delay: 0.2s; }

@keyframes arrow {
  0% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}

/* ========== 功能特性区域 ========== */
.features-section {
  padding: 100px 0;
  background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.section-header.visible {
  opacity: 1;
  transform: translateY(0);
}

.section-header.light .section-title,
.section-header.light .section-desc {
  color: white;
}

.section-tag {
  display: inline-block;
  background: linear-gradient(135deg, rgba(6, 95, 70, 0.08), rgba(4, 120, 87, 0.08));
  color: #065f46;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 16px;
  border: 1px solid rgba(6, 95, 70, 0.15);
}

.section-tag.light {
  background: rgba(255, 255, 255, 0.12);
  color: white;
  border-color: rgba(255, 255, 255, 0.25);
}

.section-title {
  font-size: clamp(2rem, 4vw, 2.5rem);
  font-weight: 700;
  color: #111827;
  margin-bottom: 12px;
}

.section-desc {
  font-size: 1.1rem;
  color: #6b7280;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  opacity: 0;
  transform: translateY(40px);
}

.feature-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #134e4a, #059669);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 12px;
}

.feature-desc {
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.tag {
  background: linear-gradient(135deg, rgba(6, 95, 70, 0.06), rgba(4, 120, 87, 0.06));
  color: #065f46;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid rgba(6, 95, 70, 0.12);
}

/* ========== 技术优势区域 ========== */
.advantages-section {
  padding: 100px 0;
  background: linear-gradient(135deg, #134e4a 0%, #065f46 50%, #047857 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.advantages-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.08) 0%, transparent 40%),
    radial-gradient(ellipse at 70% 80%, rgba(255,255,255,0.08) 0%, transparent 40%);
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 32px;
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.advantage-item {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 40px 32px;
  text-align: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  transform: translateY(30px);
}

.advantage-item.visible {
  opacity: 1;
  transform: translateY(0);
}

.advantage-item:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.advantage-number {
  font-size: 3rem;
  font-weight: 800;
  opacity: 0.25;
  margin-bottom: 8px;
}

.advantage-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.advantage-desc {
  opacity: 0.9;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* ========== 流程区域 ========== */
.process-section {
  padding: 100px 0;
  background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
}

.process-steps {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.process-step {
  flex: 1;
  min-width: 250px;
  max-width: 300px;
  text-align: center;
  position: relative;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.process-step.visible {
  opacity: 1;
  transform: translateY(0);
}

.step-number {
  width: 48px;
  height: 48px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #134e4a, #059669);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  box-shadow: 0 4px 15px rgba(6, 95, 70, 0.3);
}

.step-content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.process-step:hover .step-content {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.step-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 8px;
}

.step-desc {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
}

.step-connector {
  position: absolute;
  top: 80px;
  right: -30px;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.connector-line {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #065f46, #059669);
  opacity: 0.3;
}

.connector-arrow {
  position: absolute;
  color: #065f46;
  opacity: 0.5;
  font-size: 1rem;
}

/* ========== CTA 区域 ========== */
.cta-section {
  padding: 100px 0;
  background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
  position: relative;
  overflow: hidden;
}

.cta-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, rgba(6, 95, 70, 0.2), rgba(4, 120, 87, 0.2));
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, rgba(5, 150, 105, 0.15), rgba(16, 185, 129, 0.15));
  bottom: -50px;
  right: -50px;
}

.cta-content {
  text-align: center;
  position: relative;
  z-index: 1;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.cta-content.visible {
  opacity: 1;
  transform: translateY(0);
}

.cta-title {
  font-size: clamp(2rem, 4vw, 2.8rem);
  font-weight: 700;
  color: #111827;
  margin-bottom: 16px;
}

.cta-subtitle {
  font-size: 1.1rem;
  color: #6b7280;
  margin-bottom: 32px;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.cta-note {
  font-size: 0.85rem;
  color: #9ca3af;
}

/* ========== 动画 ========== */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========== 响应式设计 ========== */
@media (max-width: 968px) {
  .process-steps {
    flex-direction: column;
    align-items: center;
  }

  .process-step {
    max-width: 100%;
    width: 100%;
  }

  .step-connector {
    display: none;
  }

  .hidden-sm {
    display: none;
  }

  .hero-stats {
    gap: 16px;
  }

  .stat-item {
    min-width: 140px;
    padding: 20px 24px;
  }

  .stat-number {
    font-size: 2rem;
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: 80px 16px 60px;
    min-height: auto;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .cta-button,
  .cta-button-secondary {
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }

  .hero-stats {
    flex-direction: column;
    align-items: center;
  }

  .stat-item {
    width: 100%;
    max-width: 200px;
  }

  .features-section,
  .advantages-section,
  .process-section,
  .cta-section {
    padding: 60px 0;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .feature-card {
    padding: 28px 24px;
  }

  .advantages-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .advantage-item {
    padding: 28px 24px;
  }

  .container {
    padding: 0 16px;
  }

  .scroll-indicator {
    display: none;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .stat-number {
    font-size: 1.8rem;
  }
}
</style>