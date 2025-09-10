<template>
  <div class="home-container gradient-bg">
    <!-- 英雄区域 -->
    <div class="hero-section">
      <div class="hero-content fade-in">
        <h1 class="hero-title text-gradient">
          B站智能分析平台
        </h1>
        <p class="hero-subtitle">
          基于AI驱动的B站评论分析系统，为内容创作者和研究者提供深度数据洞察
        </p>
        <div class="hero-stats">
          <div class="stat-item bounce-in">
            <div class="stat-number">{{ totalAnalysis }}</div>
            <div class="stat-label">累计查询</div>
          </div>
          <div class="stat-item bounce-in" style="animation-delay: 0.1s">
            <div class="stat-number">{{ totalComments }}</div>
            <div class="stat-label">评论处理</div>
          </div>
          <div class="stat-item bounce-in" style="animation-delay: 0.2s">
            <div class="stat-number">{{ totalUsers }}</div>
            <div class="stat-label">用户画像</div>
          </div>

      <div class="container text-center">
        <h2 class="cta-title">开始您的数据分析之旅</h2>
        <p class="cta-subtitle">几分钟内即可获得专业的B站数据分析报告</p>
        <div class="cta-buttons">
          <el-button 
            type="primary" 
            size="large" 
            @click="goTo('/comment-analysis')"
            class="cta-button modern-button"
          >
            立即开始分析
          </el-button>

        </div>
      </div>

        </div>
      </div>
    </div>
<!--

    <div class="features-section container">
      <h2 class="section-title text-center mb-4">核心功能</h2>
      <div class="features-grid grid grid-3">
        <div class="feature-card modern-card slide-in-right" @click="goTo('/comment-analysis')" style="animation-delay: 0.1s">
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon"><DataAnalysis /></el-icon>
          </div>
          <h3 class="feature-title">智能评论分析</h3>
          <p class="feature-desc">
            AI驱动的情感分析、关键词提取、用户活跃度统计，深度洞察评论数据
          </p>
          <div class="feature-tags">
            <span class="tag">情感分析</span>
            <span class="tag">关键词提取</span>
            <span class="tag">质量评估</span>
          </div>
        </div>

        <div class="feature-card modern-card slide-in-right" @click="goTo('/user-portrait')" style="animation-delay: 0.2s">
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon"><User /></el-icon>
          </div>
          <h3 class="feature-title">用户画像分析</h3>
          <p class="feature-desc">
            精准构建用户兴趣模型，分析行为偏好，生成个性化用户画像报告
          </p>
          <div class="feature-tags">
            <span class="tag">行为分析</span>
            <span class="tag">兴趣建模</span>
            <span class="tag">偏好识别</span>
          </div>
        </div>

        <div class="feature-card modern-card slide-in-right" @click="goTo('/content-recommendation')" style="animation-delay: 0.3s">
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon"><Star /></el-icon>
          </div>
          <h3 class="feature-title">智能内容推荐</h3>
          <p class="feature-desc">
            基于用户画像和内容分析，提供个性化内容推荐和创作建议
          </p>
          <div class="feature-tags">
            <span class="tag">个性推荐</span>
            <span class="tag">协同过滤</span>
            <span class="tag">内容匹配</span>
          </div>
        </div>

        <div class="feature-card modern-card slide-in-right" @click="goTo('/query')" style="animation-delay: 0.4s">
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon"><Search /></el-icon>
          </div>
          <h3 class="feature-title">视频评论查询</h3>
          <p class="feature-desc">
            快速获取任意BV号视频的评论数据，支持批量处理和数据导出
          </p>
          <div class="feature-tags">
            <span class="tag">快速查询</span>
            <span class="tag">批量处理</span>
            <span class="tag">数据导出</span>
          </div>
        </div>

        <div class="feature-card modern-card slide-in-right" @click="goTo('/history')" style="animation-delay: 0.5s">
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon"><Tickets /></el-icon>
          </div>
          <h3 class="feature-title">历史记录管理</h3>
          <p class="feature-desc">
            智能管理分析历史，支持搜索过滤、数据对比和趋势分析
          </p>
          <div class="feature-tags">
            <span class="tag">历史追踪</span>
            <span class="tag">数据对比</span>
            <span class="tag">趋势分析</span>
          </div>
        </div>

        <div class="feature-card modern-card slide-in-right" @click="goTo('/user-analysis')" style="animation-delay: 0.6s">
          <div class="feature-icon-wrapper">
            <el-icon class="feature-icon"><Document /></el-icon>
          </div>
          <h3 class="feature-title">用户行为分析</h3>
          <p class="feature-desc">
            深度分析用户评论行为模式，识别活跃用户和意见领袖
          </p>
          <div class="feature-tags">
            <span class="tag">行为模式</span>
            <span class="tag">影响力分析</span>
            <span class="tag">社交网络</span>
          </div>
        </div>
      </div>
    </div>


    <div class="advantages-section">
      <div class="container">
        <h2 class="section-title text-center mb-4">技术优势</h2>
        <div class="advantages-grid grid grid-2">
          <div class="advantage-item fade-in" style="animation-delay: 0.2s">
            <div class="advantage-icon">🚀</div>
            <h4>高效处理</h4>
            <p>Redis缓存 + 异步任务队列，秒级响应大量数据处理</p>
          </div>
          <div class="advantage-item fade-in" style="animation-delay: 0.3s">
            <div class="advantage-icon">🤖</div>
            <h4>AI智能</h4>
            <p>集成先进NLP模型，提供精准的情感分析和内容理解</p>
          </div>
          <div class="advantage-item fade-in" style="animation-delay: 0.4s">
            <div class="advantage-icon">📊</div>
            <h4>可视化</h4>
            <p>丰富的图表展示，直观呈现数据分析结果和趋势</p>
          </div>
          <div class="advantage-item fade-in" style="animation-delay: 0.5s">
            <div class="advantage-icon">🔒</div>
            <h4>安全可靠</h4>
            <p>完善的用户认证和数据保护机制，确保信息安全</p>
          </div>
        </div>
      </div>
    </div>


    <div class="cta-section">
      <div class="container text-center">
        <h2 class="cta-title">开始您的数据分析之旅</h2>
        <p class="cta-subtitle">几分钟内即可获得专业的B站数据分析报告</p>
        <div class="cta-buttons">
          <el-button 
            type="primary" 
            size="large" 
            @click="goTo('/comment-analysis')"
            class="cta-button modern-button"
          >
            立即开始分析
          </el-button>

        </div>
      </div>
    </div>
-->


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Document, User, Tickets, DataAnalysis, Search, Star } from '@element-plus/icons-vue';
import { get_history_data } from '@/api/bilibili';
const history_data = ref()
const router = useRouter();
const loadHistoryData = async () => {
  try {
    const response = await get_history_data()
    if (response.code === 200 && response.data) {
      history_data.value = response.data
    }
  } catch (err: any) {
    console.error('获取用户列表失败:', err)
  }
}
// 统计数据
const totalAnalysis = computed(() => history_data.value?.leiji ?? 0)
const totalComments = computed(() => history_data.value?.chuli ?? 0)
const totalUsers = computed(() => history_data.value?.huaxiang ?? 0)

// 页面跳转
const goTo = (path: string) => {
  router.push(path);
};

// 数字滚动动画
const animateNumber = (target: any, endValue: number, duration = 2000) => {
  const startTime = Date.now();
  const startValue = 0;
  
  const animate = () => {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // 使用缓动函数
    const easeOutQuart = 1 - Math.pow(1 - progress, 4);
    const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);
    
    target.value = currentValue;
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  };
  
  animate();
};

// 组件挂载后启动数字动画
onMounted(() => {
  setTimeout(() => {
    loadHistoryData()
    animateNumber(totalAnalysis, 1208, 2000);
    animateNumber(totalComments, 45672, 2500);
    animateNumber(totalUsers, 3456, 2200);
  }, 800);
});
</script>

<style scoped>
/* 整体容器 */
.home-container {
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

/* 英雄区域 */
.hero-section {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 80px 20px;
}

.hero-content {
  max-width: 800px;
  z-index: 2;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 48px;
  font-weight: 300;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}

.hero-stats .stat-item {
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  min-width: 120px;
  transition: all 0.3s ease;
}

.hero-stats .stat-item:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.15);
}

.hero-stats .stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
}

.hero-stats .stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  font-weight: 500;
}

/* 功能特性区域 */
.features-section {
  padding: 100px 20px;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 60px;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  border-radius: 2px;
}

.features-grid {
  max-width: 1200px;
  margin: 0 auto;
  gap: 32px;
}

.feature-card {
  padding: 40px 32px;
  text-align: center;
  cursor: pointer;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.feature-icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.feature-icon {
  font-size: 32px;
  color: white;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.feature-desc {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 24px;
  font-size: 1rem;
}

.feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.tag {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  color: var(--primary-color);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

/* 技术优势区域 */
.advantages-section {
  padding: 100px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.advantages-section .section-title {
  color: white;
}

.advantages-section .section-title::after {
  background: rgba(255, 255, 255, 0.8);
}

.advantages-grid {
  max-width: 800px;
  margin: 0 auto;
  gap: 40px;
}

.advantage-item {
  text-align: center;
  padding: 32px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.advantage-item:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.15);
}

.advantage-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
}

.advantage-item h4 {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.advantage-item p {
  opacity: 0.9;
  line-height: 1.6;
}

/* CTA区域 */
.cta-section {
  padding: 100px 20px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  text-align: center;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.cta-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  margin-bottom: 40px;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-button {
  padding: 16px 32px !important;
  font-size: 1.1rem !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.cta-button:hover {
  transform: translateY(-2px);
}

.cta-button-secondary {
  padding: 16px 32px;
  font-size: 1.1rem;
  border-radius: 12px;
  font-weight: 600;
  background: transparent;
  border: 2px solid var(--primary-color);
  color: var(--primary-color);
  transition: all 0.3s ease;
}

.cta-button-secondary:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-stats {
    gap: 24px;
  }
  
  .hero-stats .stat-number {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features-section,
  .advantages-section,
  .cta-section {
    padding: 60px 20px;
  }
  
  .feature-card {
    padding: 32px 24px;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .cta-button,
  .cta-button-secondary {
    width: 250px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 60px 16px;
  }
  
  .hero-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-stats .stat-item {
    width: 200px;
  }
}

/* 文本居中工具类 */
.text-center {
  text-align: center;
}
</style>
