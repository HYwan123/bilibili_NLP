<template>
  <div class="modern-charts">
    <!-- 情感分析饼图 -->
    <div class="chart-container" v-if="sentimentData">
      <div class="chart-header">
        <h3 class="chart-title">情感分析分布</h3>
        <div class="chart-subtitle">评论情感倾向统计</div>
      </div>
      <div class="chart-content">
        <div class="sentiment-pie-chart" ref="sentimentChart"></div>
        <div class="sentiment-stats">
          <div class="stat-item positive">
            <div class="stat-icon">😊</div>
            <div class="stat-info">
              <div class="stat-label">正面</div>
              <div class="stat-value">{{ sentimentData.positive }}%</div>
            </div>
          </div>
          <div class="stat-item neutral">
            <div class="stat-icon">😐</div>
            <div class="stat-info">
              <div class="stat-label">中性</div>
              <div class="stat-value">{{ sentimentData.neutral }}%</div>
            </div>
          </div>
          <div class="stat-item negative">
            <div class="stat-icon">😔</div>
            <div class="stat-info">
              <div class="stat-label">负面</div>
              <div class="stat-value">{{ sentimentData.negative }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关键词云图 -->
    <div class="chart-container" v-if="keywordData">
      <div class="chart-header">
        <h3 class="chart-title">关键词分析</h3>
        <div class="chart-subtitle">高频词汇可视化</div>
      </div>
      <div class="chart-content">
        <div class="keyword-cloud">
          <div 
            v-for="(keyword, index) in keywordData" 
            :key="keyword.word"
            class="keyword-item"
            :style="getKeywordStyle(keyword.count, index)"
            @click="onKeywordClick(keyword)"
          >
            {{ keyword.word }}
          </div>
        </div>
      </div>
    </div>

    <!-- 用户活跃度条形图 -->
    <div class="chart-container" v-if="activityData">
      <div class="chart-header">
        <h3 class="chart-title">用户活跃度</h3>
        <div class="chart-subtitle">评论数量分布</div>
      </div>
      <div class="chart-content">
        <div class="activity-bars">
          <div 
            v-for="user in activityData" 
            :key="user.username"
            class="activity-bar-item"
          >
            <div class="bar-container">
              <div 
                class="bar-fill"
                :style="{ width: getBarWidth(user.comment_count) + '%' }"
              ></div>
            </div>
            <div class="bar-info">
              <div class="user-name">{{ user.username }}</div>
              <div class="comment-count">{{ user.comment_count }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 质量分析仪表盘 -->
    <div class="chart-container" v-if="qualityData">
      <div class="chart-header">
        <h3 class="chart-title">内容质量评估</h3>
        <div class="chart-subtitle">评论质量分布</div>
      </div>
      <div class="chart-content">
        <div class="quality-dashboard">
          <div class="quality-gauge">
            <div class="gauge-container">
              <div class="gauge-bg"></div>
              <div 
                class="gauge-fill"
                :style="{ transform: `rotate(${getGaugeRotation(qualityData.average_score)}deg)` }"
              ></div>
              <div class="gauge-center">
                <div class="gauge-value">{{ qualityData.average_score }}</div>
                <div class="gauge-label">平均分</div>
              </div>
            </div>
          </div>
          <div class="quality-breakdown">
            <div class="quality-item high">
              <div class="quality-bar">
                <div 
                  class="quality-fill"
                  :style="{ width: getQualityPercent(qualityData.high) + '%' }"
                ></div>
              </div>
              <div class="quality-info">
                <span class="quality-label">高质量</span>
                <span class="quality-count">{{ qualityData.high }}</span>
              </div>
            </div>
            <div class="quality-item medium">
              <div class="quality-bar">
                <div 
                  class="quality-fill"
                  :style="{ width: getQualityPercent(qualityData.medium) + '%' }"
                ></div>
              </div>
              <div class="quality-info">
                <span class="quality-label">中等质量</span>
                <span class="quality-count">{{ qualityData.medium }}</span>
              </div>
            </div>
            <div class="quality-item low">
              <div class="quality-bar">
                <div 
                  class="quality-fill"
                  :style="{ width: getQualityPercent(qualityData.low) + '%' }"
                ></div>
              </div>
              <div class="quality-info">
                <span class="quality-label">低质量</span>
                <span class="quality-count">{{ qualityData.low }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 时间趋势图 -->
    <div class="chart-container" v-if="trendData">
      <div class="chart-header">
        <h3 class="chart-title">评论趋势</h3>
        <div class="chart-subtitle">时间分布统计</div>
      </div>
      <div class="chart-content">
        <div class="trend-chart">
          <div class="trend-line-container">
            <svg class="trend-svg" viewBox="0 0 400 200">
              <defs>
                <linearGradient id="trendGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.8" />
                  <stop offset="100%" style="stop-color:#667eea;stop-opacity:0.1" />
                </linearGradient>
              </defs>
              <path 
                :d="getTrendPath()"
                fill="url(#trendGradient)"
                stroke="#667eea"
                stroke-width="2"
              />
              <path 
                :d="getTrendLine()"
                fill="none"
                stroke="#667eea"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <!-- 数据点 -->
              <circle 
                v-for="(point, index) in getTrendPoints()"
                :key="index"
                :cx="point.x"
                :cy="point.y"
                r="4"
                fill="#667eea"
                class="trend-point"
              />
            </svg>
          </div>
          <div class="trend-labels">
            <div 
              v-for="(label, index) in trendData.labels"
              :key="index"
              class="trend-label"
            >
              {{ label }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';

interface Props {
  sentimentData?: {
    positive: number;
    neutral: number;
    negative: number;
  };
  keywordData?: Array<{
    word: string;
    count: number;
  }>;
  activityData?: Array<{
    username: string;
    comment_count: number;
  }>;
  qualityData?: {
    average_score: number;
    high: number;
    medium: number;
    low: number;
  };
  trendData?: {
    labels: string[];
    values: number[];
  };
}

const props = withDefaults(defineProps<Props>(), {
  sentimentData: undefined,
  keywordData: undefined,
  activityData: undefined,
  qualityData: undefined,
  trendData: undefined
});

const emit = defineEmits<{
  keywordClick: [keyword: { word: string; count: number }];
}>();

// 关键词样式计算
const getKeywordStyle = (count: number, index: number) => {
  const maxCount = Math.max(...(props.keywordData?.map(k => k.count) || [1]));
  const size = Math.max(12, Math.min(32, (count / maxCount) * 32 + 12));
  const colors = ['#667eea', '#764ba2', '#f093fb', '#4ade80', '#fbbf24', '#ef4444'];
  const color = colors[index % colors.length];
  
  return {
    fontSize: `${size}px`,
    color: color,
    fontWeight: count > maxCount * 0.7 ? '700' : count > maxCount * 0.4 ? '600' : '500'
  };
};

// 活跃度条形图宽度计算
const getBarWidth = (count: number) => {
  const maxCount = Math.max(...(props.activityData?.map(a => a.comment_count) || [1]));
  return (count / maxCount) * 100;
};

// 质量仪表盘角度计算
const getGaugeRotation = (score: number) => {
  return (score / 100) * 180 - 90;
};

// 质量分布百分比计算
const getQualityPercent = (count: number) => {
  if (!props.qualityData) return 0;
  const total = props.qualityData.high + props.qualityData.medium + props.qualityData.low;
  return total > 0 ? (count / total) * 100 : 0;
};

// 趋势图路径计算
const getTrendPath = () => {
  if (!props.trendData?.values.length) return '';
  
  const values = props.trendData.values;
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;
  
  const width = 400;
  const height = 200;
  const padding = 20;
  
  let path = `M ${padding} ${height - padding}`;
  
  values.forEach((value, index) => {
    const x = padding + (index / (values.length - 1)) * (width - 2 * padding);
    const y = height - padding - ((value - minValue) / range) * (height - 2 * padding);
    path += ` L ${x} ${y}`;
  });
  
  path += ` L ${width - padding} ${height - padding} Z`;
  return path;
};

const getTrendLine = () => {
  if (!props.trendData?.values.length) return '';
  
  const values = props.trendData.values;
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;
  
  const width = 400;
  const height = 200;
  const padding = 20;
  
  let path = '';
  
  values.forEach((value, index) => {
    const x = padding + (index / (values.length - 1)) * (width - 2 * padding);
    const y = height - padding - ((value - minValue) / range) * (height - 2 * padding);
    path += index === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`;
  });
  
  return path;
};

const getTrendPoints = () => {
  if (!props.trendData?.values.length) return [];
  
  const values = props.trendData.values;
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue || 1;
  
  const width = 400;
  const height = 200;
  const padding = 20;
  
  return values.map((value, index) => ({
    x: padding + (index / (values.length - 1)) * (width - 2 * padding),
    y: height - padding - ((value - minValue) / range) * (height - 2 * padding)
  }));
};

// 关键词点击事件
const onKeywordClick = (keyword: { word: string; count: number }) => {
  emit('keywordClick', keyword);
};
</script>

<style scoped>
.modern-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  padding: 20px;
}

.chart-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
}

.chart-container:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.chart-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
}

.chart-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.chart-subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.chart-content {
  padding: 24px;
}

/* 情感分析样式 */
.sentiment-pie-chart {
  width: 200px;
  height: 200px;
  margin: 0 auto 24px;
  border-radius: 50%;
  background: conic-gradient(
    #4ade80 0deg 120deg,
    #fbbf24 120deg 240deg,
    #ef4444 240deg 360deg
  );
  position: relative;
}

.sentiment-pie-chart::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.sentiment-stats {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item.positive {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.2);
}

.stat-item.neutral {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.stat-item.negative {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.stat-icon {
  font-size: 20px;
}

.stat-info {
  text-align: center;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 关键词云样式 */
.keyword-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  padding: 20px;
}

.keyword-item {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(102, 126, 234, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  user-select: none;
}

.keyword-item:hover {
  transform: scale(1.1);
  background: rgba(102, 126, 234, 0.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

/* 活跃度条形图样式 */
.activity-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-container {
  flex: 1;
  height: 24px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  transition: width 0.6s ease;
  position: relative;
}

.bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), transparent);
  border-radius: 12px;
}

.bar-info {
  min-width: 120px;
  text-align: right;
}

.user-name {
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 500;
}

.comment-count {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 质量仪表盘样式 */
.quality-dashboard {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 32px;
  align-items: center;
}

.gauge-container {
  width: 160px;
  height: 80px;
  position: relative;
  margin: 0 auto;
}

.gauge-bg {
  width: 100%;
  height: 160px;
  border: 8px solid rgba(102, 126, 234, 0.1);
  border-bottom: none;
  border-radius: 80px 80px 0 0;
}

.gauge-fill {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 160px;
  border: 8px solid #667eea;
  border-bottom: none;
  border-radius: 80px 80px 0 0;
  clip-path: polygon(0 100%, 50% 100%, 50% 0, 0 0);
  transform-origin: 50% 100%;
  transition: transform 0.6s ease;
}

.gauge-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -20%);
  text-align: center;
}

.gauge-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
}

.gauge-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.quality-breakdown {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quality-bar {
  flex: 1;
  height: 16px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

.quality-item.high .quality-fill {
  background: linear-gradient(135deg, #4ade80, #22c55e);
}

.quality-item.medium .quality-fill {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.quality-item.low .quality-fill {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.quality-fill {
  height: 100%;
  border-radius: 8px;
  transition: width 0.6s ease;
}

.quality-info {
  display: flex;
  flex-direction: column;
  min-width: 80px;
  text-align: right;
}

.quality-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.quality-count {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 趋势图样式 */
.trend-chart {
  position: relative;
}

.trend-line-container {
  margin-bottom: 16px;
}

.trend-svg {
  width: 100%;
  height: 200px;
}

.trend-point {
  cursor: pointer;
  transition: r 0.3s ease;
}

.trend-point:hover {
  r: 6;
}

.trend-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.trend-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modern-charts {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
  }
  
  .chart-header {
    padding: 16px 16px 12px;
  }
  
  .chart-content {
    padding: 16px;
  }
  
  .sentiment-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .quality-dashboard {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .activity-bar-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .bar-info {
    text-align: left;
    min-width: auto;
  }
}
</style>
