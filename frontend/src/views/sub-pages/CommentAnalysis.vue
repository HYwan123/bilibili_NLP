<template>
  <div class="comment-analysis-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><ChatDotRound /></el-icon>
        评论智能分析
      </h1>
      <p class="page-subtitle">深度分析B站视频评论，洞察用户情感与热点话题</p>
    </div>

    <!-- 输入分析区 -->
    <div class="input-section">
      <el-card class="input-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon><VideoPlay /></el-icon>
              视频评论分析
            </span>
          </div>
        </template>

        <div class="input-form">
          <div class="bv-input-wrapper">
            <div class="input-label">
              <span>BV号</span>
              <el-tooltip content="B站视频链接中的BV开头字符串，如：https://www.bilibili.com/video/BV1xx411c7mD" placement="top">
                <el-icon class="help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
            <el-input
              v-model="form.bvId"
              placeholder="请输入BV号，例如：BV1xx411c7mD"
              size="large"
              clearable
              :disabled="analyzing"
              @keyup.enter="startAnalysis"
            >
              <template #prefix>
                <el-icon><Link /></el-icon>
              </template>
              <template #append>
                <el-button 
                  type="primary" 
                  @click="startAnalysis"
                  :loading="analyzing"
                  :disabled="!form.bvId || analyzing"
                >
                  <el-icon><Cpu /></el-icon>
                  {{ analyzing ? '分析中...' : '开始分析' }}
                </el-button>
              </template>
            </el-input>
          </div>

          <!-- 快速尝试 -->
          <div class="quick-actions" v-if="!analysisResult">
            <span class="quick-label">快速尝试：</span>
            <el-tag 
              v-for="sample in sampleBVs" 
              :key="sample"
              class="sample-tag"
              @click="form.bvId = sample; startAnalysis()"
              effect="light"
              type="info"
            >
              {{ sample }}
            </el-tag>
          </div>

          <!-- 分析进度 -->
          <div v-if="analyzing" class="analysis-progress">
            <div class="progress-header">
              <span class="progress-title">正在分析评论数据</span>
              <span class="progress-percent">{{ jobProgress }}%</span>
            </div>
            <el-progress 
              :percentage="jobProgress" 
              :stroke-width="8"
              status="success"
              :show-text="false"
            />
            <div class="progress-steps">
              <div 
                v-for="(step, idx) in analysisSteps" 
                :key="idx"
                class="step-item"
                :class="{ active: jobProgress >= step.percent, current: jobProgress >= step.percent && jobProgress < (analysisSteps[idx + 1]?.percent || 100) }"
              >
                <el-icon><component :is="step.icon" /></el-icon>
                <span>{{ step.text }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisResult" class="results-section">
      <!-- 结果概览头部 -->
      <div class="result-header">
        <div class="result-title">
          <el-icon><CircleCheck /></el-icon>
          <span>分析完成</span>
        </div>
        <div class="result-meta">
          <el-tag type="success" effect="light">
            <el-icon><ChatLineRound /></el-icon>
            {{ analysisResult.basic_stats?.total_comments || 0 }} 条评论
          </el-tag>
          <el-button size="small" @click="resetAnalysis">
            <el-icon><RefreshLeft /></el-icon>
            重新分析
          </el-button>
        </div>
      </div>

      <!-- 基础统计卡片区 -->
      <div class="stats-grid">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8">
            <div class="stat-card primary">
              <div class="stat-icon">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ analysisResult.basic_stats?.total_comments || 0 }}</div>
                <div class="stat-label">总评论数</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="stat-card success">
              <div class="stat-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ analysisResult.basic_stats?.unique_users || 0 }}</div>
                <div class="stat-label">独立用户</div>
              </div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <div class="stat-card warning">
              <div class="stat-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ analysisResult.basic_stats?.average_length || 0 }}</div>
                <div class="stat-label">平均长度</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 情感分析 -->
      <el-card class="result-card sentiment-card" v-if="analysisResult.sentiment_analysis">
        <template #header>
          <div class="section-header">
            <div class="section-title">
              <el-icon><PieChart /></el-icon>
              <span>情感分析</span>
            </div>
            <div class="sentiment-summary">
              <div class="summary-item positive">
                <div class="summary-dot"></div>
                <span>正面 {{ sentimentPercentages.positive }}%</span>
              </div>
              <div class="summary-item neutral">
                <div class="summary-dot"></div>
                <span>中性 {{ sentimentPercentages.neutral }}%</span>
              </div>
              <div class="summary-item negative">
                <div class="summary-dot"></div>
                <span>负面 {{ sentimentPercentages.negative }}%</span>
              </div>
            </div>
          </div>
        </template>

        <div class="sentiment-content">
          <div class="chart-container">
            <SentimentPieChart :data="analysisResult.sentiment_analysis" width="100%" height="350px" />
          </div>

          <!-- 评论示例 -->
          <div class="comment-examples" v-if="getCommentExamples.length > 0">
            <div class="examples-header">
              <h4>评论情感示例</h4>
              <span class="examples-count">共 {{ getAllCommentExamples().length }} 条</span>
            </div>
            <div class="examples-list">
              <div 
                v-for="(example, idx) in getCommentExamples" 
                :key="idx"
                class="example-item"
                :class="getSentimentType(example.label)"
              >
                <div class="example-sentiment">
                  <el-tag :type="getSentimentType(example.label)" size="small" effect="light">
                    {{ getSentimentText(example.label) }}
                  </el-tag>
                  <span class="confidence">{{ (example.score * 100).toFixed(1) }}%</span>
                </div>
                <div class="example-text">{{ example.comment }}</div>
              </div>
            </div>
            
            <!-- 分页 -->
            <div class="pagination-wrapper" v-if="getAllCommentExamples().length > pageSize">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="getAllCommentExamples().length"
                :page-sizes="[5, 10, 20, 50]"
                layout="total, sizes, prev, pager, next"
                @current-change="handleCurrentChange"
                @size-change="handleSizeChange"
              />
            </div>
          </div>
        </div>
      </el-card>

      <!-- 关键词分析 -->
      <el-card class="result-card keywords-card" v-if="analysisResult.keyword_analysis">
        <template #header>
          <div class="section-header">
            <div class="section-title">
              <el-icon><Collection /></el-icon>
              <span>关键词分析</span>
            </div>
          </div>
        </template>

        <div class="keywords-content">
          <div class="wordcloud-section">
            <h4>词云可视化</h4>
            <div class="wordcloud-container">
              <KeywordCloudChart :data="analysisResult.keyword_analysis" width="100%" height="300px" />
            </div>
          </div>

          <div class="keywords-list-section">
            <h4>热门关键词 TOP20</h4>
            <div class="keywords-tags">
              <el-tag 
                v-for="(keyword, index) in topKeywords" 
                :key="index"
                :type="getKeywordTagType(index)"
                :size="getKeywordSize(keyword.count)"
                effect="light"
                class="keyword-tag"
              >
                {{ keyword.word }}
                <span class="keyword-count">({{ keyword.count }})</span>
              </el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 用户活跃度 -->
      <el-card class="result-card activity-card" v-if="analysisResult.user_activity">
        <template #header>
          <div class="section-header">
            <div class="section-title">
              <el-icon><UserFilled /></el-icon>
              <span>用户活跃度</span>
            </div>
          </div>
        </template>

        <div class="activity-content">
          <div class="top-users-section">
            <h4>最活跃用户 TOP5</h4>
            <div class="top-users-list">
              <div 
                v-for="(user, index) in topUsers" 
                :key="index"
                class="top-user-item"
                :class="{ 'top-3': index < 3 }"
              >
                <div class="user-rank">{{ index + 1 }}</div>
                <div class="user-avatar">
                  <el-icon><Avatar /></el-icon>
                </div>
                <div class="user-info">
                  <div class="user-name">用户 {{ user.user_id }}</div>
                  <div class="user-count">{{ user.comment_count }} 条评论</div>
                </div>
                <el-progress 
                  :percentage="Math.round((user.comment_count / maxUserComments) * 100)" 
                  :stroke-width="6"
                  :show-text="false"
                  class="user-progress"
                />
              </div>
            </div>
          </div>

          <div class="activity-stats">
            <div class="activity-stat-item">
              <div class="stat-value">{{ analysisResult.user_activity?.single_comment_users || 0 }}</div>
              <div class="stat-label">仅评论一次</div>
            </div>
            <div class="activity-stat-item">
              <div class="stat-value">{{ analysisResult.user_activity?.multi_comment_users || 0 }}</div>
              <div class="stat-label">多次评论</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { submitCommentAnalysis, getJobStatus } from '@/api/bilibili';
import SentimentPieChart from '@/components/charts/SentimentPieChart.vue';
import KeywordCloudChart from '@/components/charts/KeywordCloudChart.vue';
import {
  ChatDotRound,
  VideoPlay,
  Cpu,
  Link,
  QuestionFilled,
  CircleCheck,
  ChatLineRound,
  RefreshLeft,
  PieChart,
  User,
  Document,
  Collection,
  UserFilled,
  Avatar,
  Download,
  DataAnalysis,
  Search
} from '@element-plus/icons-vue';

// 状态
const form = ref({ bvId: '' });
const analyzing = ref(false);
const jobProgress = ref(0);
const jobStatusText = ref('');
const analysisResult = ref(null);

// 分页
const currentPage = ref(1);
const pageSize = ref(10);

// 示例BV号
const sampleBVs = ['BV1xx411c7mD', 'BV1bK411x7ct', 'BV1S54y1G7h3'];

// 分析步骤
const analysisSteps = [
  { percent: 0, text: '准备分析', icon: 'Search' },
  { percent: 25, text: '获取评论', icon: 'Download' },
  { percent: 50, text: '情感识别', icon: 'DataAnalysis' },
  { percent: 75, text: '关键词提取', icon: 'Collection' },
  { percent: 100, text: '分析完成', icon: 'CircleCheck' }
];

// 计算属性
const sentimentPercentages = computed(() => {
  if (!analysisResult.value?.sentiment_analysis) {
    return { positive: 0, neutral: 0, negative: 0 };
  }
  const data = analysisResult.value.sentiment_analysis;
  const total = data.positive + data.neutral + data.negative;
  if (total === 0) return { positive: 0, neutral: 0, negative: 0 };
  
  return {
    positive: Math.round((data.positive / total) * 100),
    neutral: Math.round((data.neutral / total) * 100),
    negative: Math.round((data.negative / total) * 100)
  };
});

const topKeywords = computed(() => {
  if (!analysisResult.value?.keyword_analysis) return [];
  return analysisResult.value.keyword_analysis.slice(0, 20);
});

const topUsers = computed(() => {
  if (!analysisResult.value?.user_activity?.top_users) return [];
  return analysisResult.value.user_activity.top_users.slice(0, 5);
});

const maxUserComments = computed(() => {
  if (!topUsers.value.length) return 1;
  return Math.max(...topUsers.value.map(u => u.comment_count));
});

// 方法
const startAnalysis = async () => {
  if (!form.value.bvId) {
    ElMessage.warning('请输入BV号');
    return;
  }

  analyzing.value = true;
  jobProgress.value = 0;
  analysisResult.value = null;

  try {
    const res = await submitCommentAnalysis(form.value.bvId);
    if (res.code === 200) {
      const jobId = res.data.job_id;
      pollJobStatus(jobId);
    } else {
      ElMessage.error(res.message || '提交分析失败');
      analyzing.value = false;
    }
  } catch (error) {
    ElMessage.error('提交分析失败');
    analyzing.value = false;
  }
};

const pollJobStatus = async (jobId) => {
  const poll = async () => {
    try {
      const res = await getJobStatus(jobId);
      if (res.code === 200) {
        jobProgress.value = res.data.progress || 0;
        jobStatusText.value = res.data.status || '分析中...';
        
        if (res.data.status === 'completed') {
          analysisResult.value = res.data.result;
          analyzing.value = false;
          ElMessage.success('分析完成！');
        } else if (res.data.status === 'failed') {
          analyzing.value = false;
          ElMessage.error('分析失败：' + (res.data.error || '未知错误'));
        } else {
          setTimeout(() => poll(), 2000);
        }
      } else {
        analyzing.value = false;
        ElMessage.error('获取任务状态失败');
      }
    } catch (error) {
      analyzing.value = false;
      ElMessage.error('获取任务状态失败');
    }
  };
  poll();
};

const resetAnalysis = () => {
  analysisResult.value = null;
  form.value.bvId = '';
  currentPage.value = 1;
};

const getCommentExamples = computed(() => {
  const examples = getAllCommentExamples();
  const start = (currentPage.value - 1) * pageSize.value;
  return examples.slice(start, start + pageSize.value);
});

const getAllCommentExamples = () => {
  if (!analysisResult.value?.sentiment_analysis?.examples) return [];
  return analysisResult.value.sentiment_analysis.examples;
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
};

const getSentimentType = (label) => {
  const map = {
    1: 'danger',
    2: 'warning',
    3: 'info',
    4: 'success',
    5: 'success'
  };
  return map[label] || 'info';
};

const getSentimentText = (label) => {
  const map = {
    1: '非常负面',
    2: '负面',
    3: '中性',
    4: '正面',
    5: '非常正面'
  };
  return map[label] || '未知';
};

const getKeywordTagType = (index) => {
  if (index < 3) return 'danger';
  if (index < 6) return 'warning';
  if (index < 10) return 'success';
  return 'info';
};

const getKeywordSize = (count) => {
  const max = topKeywords.value[0]?.count || 1;
  const ratio = count / max;
  if (ratio > 0.7) return 'large';
  if (ratio > 0.4) return 'default';
  return 'small';
};
</script>

<style scoped>
.comment-analysis-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 50%, #f0fdf4 100%);
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #065f46, #047857);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-title .el-icon {
  font-size: 36px;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 输入区 */
.input-section {
  margin-bottom: 32px;
}

.input-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.input-form {
  padding: 20px 0;
}

.bv-input-wrapper {
  margin-bottom: 20px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.help-icon {
  color: #9ca3af;
  cursor: help;
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.quick-label {
  font-size: 13px;
  color: #9ca3af;
}

.sample-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.sample-tag:hover {
  background: #065f46;
  color: white;
}

/* 分析进度 */
.analysis-progress {
  margin-top: 24px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.progress-percent {
  font-size: 14px;
  color: #065f46;
  font-weight: 600;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #9ca3af;
  transition: all 0.3s ease;
}

.step-item.active {
  color: #065f46;
}

.step-item.current {
  color: #065f46;
  font-weight: 600;
}

.step-item .el-icon {
  font-size: 20px;
}

/* 结果区 */
.results-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  padding: 16px 24px;
  border-radius: 12px;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 统计卡片 */
.stats-grid {
  margin-bottom: 8px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(6, 95, 70, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 95, 70, 0.15);
}

.stat-card.primary {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  border: none;
}

.stat-card.success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
}

.stat-card.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.9;
}

/* 结果卡片 */
.result-card {
  border-radius: 12px;
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

/* 情感分析 */
.sentiment-summary {
  display: flex;
  gap: 16px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.summary-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.summary-item.positive .summary-dot {
  background: #10b981;
}

.summary-item.neutral .summary-dot {
  background: #6b7280;
}

.summary-item.negative .summary-dot {
  background: #ef4444;
}

.sentiment-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chart-container {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
}

/* 评论示例 */
.comment-examples {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.examples-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.examples-header h4 {
  margin: 0;
  font-size: 16px;
  color: #111827;
}

.examples-count {
  font-size: 13px;
  color: #9ca3af;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.example-item {
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
  border-left: 3px solid #e5e7eb;
}

.example-item.success {
  border-left-color: #10b981;
}

.example-item.warning {
  border-left-color: #f59e0b;
}

.example-item.danger {
  border-left-color: #ef4444;
}

.example-item.info {
  border-left-color: #6b7280;
}

.example-sentiment {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.confidence {
  font-size: 12px;
  color: #9ca3af;
}

.example-text {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* 关键词分析 */
.keywords-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.wordcloud-section,
.keywords-list-section {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.wordcloud-section h4,
.keywords-list-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #111827;
}

.wordcloud-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.keywords-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  transition: all 0.3s ease;
}

.keyword-tag:hover {
  transform: scale(1.05);
}

.keyword-count {
  opacity: 0.7;
  margin-left: 4px;
}

/* 用户活跃度 */
.activity-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.top-users-section {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
}

.top-users-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #111827;
}

.top-users-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.top-user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
}

.top-user-item.top-3 {
  background: linear-gradient(135deg, #f0fdf4, #ffffff);
  border: 1px solid rgba(6, 95, 70, 0.2);
}

.user-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.top-user-item.top-3 .user-rank {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4f46e5;
  font-size: 20px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.user-count {
  font-size: 12px;
  color: #6b7280;
}

.user-progress {
  width: 100px;
}

.activity-stats {
  display: flex;
  gap: 16px;
}

.activity-stat-item {
  flex: 1;
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.activity-stat-item .stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #065f46;
  margin-bottom: 4px;
}

.activity-stat-item .stat-label {
  font-size: 13px;
  color: #6b7280;
}

/* 响应式 */
@media (max-width: 768px) {
  .comment-analysis-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .result-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .sentiment-summary {
    flex-direction: column;
    gap: 8px;
  }
  
  .progress-steps {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
