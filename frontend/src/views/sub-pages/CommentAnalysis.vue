<template>
  <div class="comment-analysis-page">
    <!-- 1. 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><ChatDotRound /></el-icon>
        舆情智能看板
      </h1>
      <p class="page-subtitle">多维度深度挖掘视频语料背后的价值密度</p>
    </div>

    <!-- 2. 输入分析区 -->
    <div class="input-section">
      <el-card class="input-card" shadow="hover">
        <div class="input-form">
          <div class="bv-input-wrapper">
            <el-input
              v-model="form.bvId"
              placeholder="请输入BV号进行深度分析..."
              size="large"
              clearable
              :disabled="analyzing"
              @keyup.enter="startAnalysis"
            >
              <template #prefix><el-icon><Link /></el-icon></template>
              <template #append>
                <el-button type="primary" @click="startAnalysis" :loading="analyzing">
                  <el-icon><Cpu /></el-icon> {{ analyzing ? '分析中' : '开始分析' }}
                </el-button>
              </template>
            </el-input>
          </div>
          <div v-if="analyzing" class="analysis-progress">
            <div class="progress-header">
              <span class="status-text">{{ jobStatusText || '正在构建分析模型...' }}</span>
              <span class="percent">{{ jobProgress }}%</span>
            </div>
            <el-progress :percentage="jobProgress" :stroke-width="10" status="success" :show-text="false" striped striped-flow />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 3. 分析结果渲染 -->
    <div v-if="analysisResult && !analysisResult.error" class="dashboard-content">
      
      <!-- 第一行：预处理与基础统计 -->
      <el-row :gutter="20">
        <el-col :md="16">
          <el-card class="dashboard-card cleaning-card">
            <template #header>
              <div class="card-header-flex">
                <span class="title"><el-icon><Filter /></el-icon> 语料预处理报告</span>
                <el-tag type="success" effect="dark" round v-if="analysisResult.cleaning_report">
                  有效载荷 {{ analysisResult.cleaning_report?.efficiency }}%
                </el-tag>
              </div>
            </template>
            <div class="cleaning-dashboard">
              <div class="clean-stat-grid">
                <div class="c-item">
                  <span class="label">原始语料</span>
                  <span class="value">{{ analysisResult.cleaning_report?.raw_total || analysisResult.basic_stats?.total_comments }}</span>
                </div>
                <div class="c-item">
                  <span class="label">噪音过滤</span>
                  <span class="value warning">{{ analysisResult.cleaning_report?.filtered_out || 0 }}</span>
                </div>
                <div class="c-item">
                  <span class="label">入库分析</span>
                  <span class="value success">{{ analysisResult.cleaning_report?.cleaned_total || analysisResult.basic_stats?.total_comments }}</span>
                </div>
              </div>
              <div class="noise-breakdown" v-if="analysisResult.cleaning_report?.noise_breakdown">
                <span class="n-tag">打卡: {{ analysisResult.cleaning_report.noise_breakdown.check_in }}</span>
                <span class="n-tag">灌水: {{ analysisResult.cleaning_report.noise_breakdown.spam }}</span>
                <span class="n-tag">广告: {{ analysisResult.cleaning_report.noise_breakdown.lottery }}</span>
                <span class="n-tag">无效: {{ analysisResult.cleaning_report.noise_breakdown.short_noise }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :md="8">
          <div class="stats-column">
            <div class="mini-stat-card primary">
              <el-icon><User /></el-icon>
              <div class="m-info">
                <div class="m-val">{{ analysisResult.basic_stats?.unique_users }}</div>
                <div class="m-lab">活跃贡献者</div>
              </div>
            </div>
            <div class="mini-stat-card warning">
              <el-icon><Document /></el-icon>
              <div class="m-info">
                <div class="m-val">{{ analysisResult.basic_stats?.average_length }}</div>
                <div class="m-lab">平均语义长度</div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 第二行：可视化图表 -->
      <el-row :gutter="20" class="chart-row">
        <el-col :md="12">
          <el-card class="dashboard-card chart-card">
            <template #header><span class="title"><el-icon><PieChart /></el-icon> 情感极性分布模型</span></template>
            <div class="chart-container">
              <SentimentPieChart :data="analysisResult.sentiment_analysis" height="320px" />
            </div>
          </el-card>
        </el-col>
        <el-col :md="12">
          <el-card class="dashboard-card chart-card">
            <template #header><span class="title"><el-icon><Histogram /></el-icon> 评论互动深度分布</span></template>
            <div class="chart-container">
              <KeywordBarChart 
                :data="formatLengthData(analysisResult.basic_stats?.length_distribution)" 
                title="字符长度区间分布"
                height="320px" 
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第三行：语义特征 -->
      <el-row :gutter="20" class="chart-row">
        <el-col :md="10">
          <el-card class="dashboard-card chart-card">
            <template #header><span class="title"><el-icon><Collection /></el-icon> 高频特征词云</span></template>
            <div class="chart-container">
              <KeywordCloudChart :data="analysisResult.keyword_analysis?.top_keywords || []" height="350px" />
            </div>
          </el-card>
        </el-col>
        <el-col :md="14">
          <el-card class="dashboard-card chart-card">
            <template #header><span class="title"><el-icon><Operation /></el-icon> 核心讨论热点 TOP 10</span></template>
            <div class="chart-container">
              <KeywordBarChart :data="analysisResult.keyword_analysis?.top_keywords || []" height="350px" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第四行：用户排行 -->
      <el-row :gutter="20" class="chart-row" v-if="analysisResult.user_activity">
        <el-col :span="24">
          <el-card class="dashboard-card chart-card">
            <template #header><span class="title"><el-icon><UserFilled /></el-icon> 用户互动贡献度排行</span></template>
            <div class="chart-container">
              <UserActivityChart :data="analysisResult.user_activity?.most_active_users || []" height="300px" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第五行：语料抽样 -->
      <el-card class="dashboard-card sample-card">
        <template #header><span class="title"><el-icon><Memo /></el-icon> 典型极性语料抽样</span></template>
        <div class="sample-list-modern">
          <div v-for="(ex, i) in getCommentExamples" :key="i" class="modern-example-item" :class="getSentimentType(ex.label)">
            <div class="ex-head">
              <span class="ex-tag">{{ getSentimentText(ex.label) }}</span>
              <span class="ex-score" v-if="ex.score">置信度: {{ (ex.score * 100).toFixed(1) }}%</span>
            </div>
            <div class="ex-text">{{ ex.comment }}</div>
          </div>
        </div>
        <div class="pagination-center">
          <el-pagination v-model:current-page="currentPage" :total="getAllCommentExamples().length" :page-size="5" layout="prev, pager, next" @current-change="handleCurrentChange" small />
        </div>
      </el-card>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import { submitCommentAnalysis, getJobStatus } from '@/api/bilibili';
import SentimentPieChart from '@/components/charts/SentimentPieChart.vue';
import KeywordCloudChart from '@/components/charts/KeywordCloudChart.vue';
import KeywordBarChart from '@/components/charts/KeywordBarChart.vue';
import UserActivityChart from '@/components/charts/UserActivityChart.vue';
import {
  ChatDotRound, VideoPlay, Cpu, Link, QuestionFilled, CircleCheck, RefreshLeft,
  PieChart, User, Document, Collection, Download, DataAnalysis, Search, Filter,
  Histogram, Operation, Memo, UserFilled
} from '@element-plus/icons-vue';

const route = useRoute();
const form = reactive({ bvId: '' });
const analyzing = ref(false);
const jobProgress = ref(0);
const jobStatusText = ref('');
const analysisResult = ref<any>(null);
const currentPage = ref(1);
const pageSize = ref(5);
const sampleBVs = ['BV1xx411c7mD', 'BV1bK411x7ct', 'BV1S54y1G7h3'];

const startAnalysis = async () => {
  if (!form.bvId) return;
  analyzing.value = true;
  analysisResult.value = null;
  jobProgress.value = 0;
  jobStatusText.value = '正在提交分析任务...';
  
  try {
    const res = await submitCommentAnalysis(form.bvId);
    const data = res.data || res;
    
    if (data.error) {
      ElMessage.error(data.error);
      analyzing.value = false;
      return;
    }

    // 核心逻辑修复：处理嵌套在 data.data 中的 job_id 或直接结果
    const innerData = data.data || data;
    
    if (innerData.basic_stats || innerData.cleaning_report || innerData.sentiment_analysis) {
      analysisResult.value = innerData;
      analyzing.value = false;
      jobProgress.value = 100;
      ElMessage.success('分析结果调取成功');
    } else if (innerData.job_id) {
      pollJobStatus(innerData.job_id);
    } else {
      // 如果没有任何标识，尝试直接通过BV轮询
      pollResultByBvOnly(form.bvId);
    }
  } catch (e: any) {
    // 拦截 409 冲突：自动接管正在运行的任务
    if (e.response && e.response.status === 409) {
      ElMessage.info('该视频正在分析中，已自动同步进度');
      pollResultByBvOnly(form.bvId);
    } else {
      ElMessage.error('分析服务连接失败');
      analyzing.value = false;
    }
  }
};

const pollJobStatus = async (jobId: string) => {
  const poll = async () => {
    try {
      const data = await getJobStatus(jobId);
      const res = data.data || data;
      jobProgress.value = res.progress || 0;
      jobStatusText.value = res.details || '智能引擎正在处理语料...';
      
      if (res.status === 'Completed' || res.status === 'completed') {
        analysisResult.value = res.result;
        analyzing.value = false;
        ElMessage.success('分析看板构建完成');
      } else if (res.status === 'Failed' || res.status === 'failed') {
        ElMessage.error(res.details || '任务执行失败');
        analyzing.value = false;
      } else {
        setTimeout(poll, 2000);
      }
    } catch { 
      analyzing.value = false; 
    }
  };
  poll();
};

/**
 * 针对冲突(409)或无JobId情况的备选轮询
 */
const pollResultByBvOnly = async (bvId: string) => {
  let attempts = 0;
  const poll = async () => {
    try {
      const res = await request.get(`/api/comments/analysis/${bvId}`);
      const data = res.data || res;
      const inner = data.data || data;
      
      if (inner && (inner.basic_stats || inner.sentiment_analysis)) {
        analysisResult.value = inner;
        analyzing.value = false;
        jobProgress.value = 100;
        ElMessage.success('同步成功');
      } else if (attempts < 40) {
        attempts++;
        jobProgress.value = Math.min(98, attempts * 2.5);
        jobStatusText.value = '正在同步后台任务进度...';
        setTimeout(poll, 3000);
      } else {
        ElMessage.error('等待超时');
        analyzing.value = false;
      }
    } catch {
      if (attempts < 40) { attempts++; setTimeout(poll, 3000); }
      else { analyzing.value = false; }
    }
  };
  poll();
};

const formatLengthData = (dist: any) => {
  if (!dist) return [];
  return Object.entries(dist).map(([k, v]) => ({ word: k, count: v }));
};

const getAllCommentExamples = () => {
  const s = analysisResult.value?.sentiment_analysis;
  if (!s || !s.examples) return [];
  return s.examples;
};

const getCommentExamples = computed(() => {
  return getAllCommentExamples().slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value);
});

const handleCurrentChange = (val: number) => { currentPage.value = val; };

const getSentimentType = (l: any) => {
  const n = parseInt(l);
  return { 1:'danger', 2:'warning', 3:'info', 4:'primary', 5:'success' }[n] || 'info';
};

const getSentimentText = (l: any) => {
  const n = parseInt(l);
  return { 1:'极差', 2:'较差', 3:'中性', 4:'良好', 5:'极佳' }[n] || '未知';
};

onMounted(() => {
  const bv = route.query.bv as string;
  if (bv) { form.bvId = bv; startAnalysis(); }
});
</script>

<style scoped>
.comment-analysis-page { padding: 32px; max-width: 1400px; margin: 0 auto; background: var(--bg-secondary); min-height: 100vh; }
.page-header { text-align: center; margin-bottom: 32px; }
.page-title { font-size: 32px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em; }
.page-title .el-icon { color: var(--primary-color); margin-right: 8px; }

.input-card { border-radius: 20px; border: none; box-shadow: var(--shadow-md); margin-bottom: 32px; padding: 10px; }
.analysis-progress { margin-top: 24px; padding: 0 10px; }
.progress-header { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; font-weight: 600; color: var(--text-secondary); }

.dashboard-content { display: flex; flex-direction: column; gap: 24px; animation: fadeIn 0.6s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.dashboard-card { border-radius: 16px; border: 1px solid var(--border-light); box-shadow: var(--shadow-sm); height: 100%; }
.card-header-flex { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.dashboard-card .title { font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }

.clean-stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.c-item { background: var(--bg-secondary); padding: 16px; border-radius: 12px; text-align: center; border: 1px solid var(--border-light); }
.c-item .label { font-size: 12px; color: var(--text-tertiary); display: block; margin-bottom: 4px; }
.c-item .value { font-size: 24px; font-weight: 800; color: var(--text-primary); }
.value.warning { color: var(--warning-color); }
.value.success { color: var(--success-color); }
.noise-breakdown { display: flex; gap: 10px; flex-wrap: wrap; }
.n-tag { font-size: 12px; padding: 4px 10px; background: var(--bg-secondary); border-radius: 6px; color: var(--text-secondary); border: 1px solid var(--border-light); }

.stats-column { display: flex; flex-direction: column; gap: 16px; height: 100%; }
.mini-stat-card { flex: 1; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; color: white; }
.mini-stat-card.primary { background: linear-gradient(135deg, #007AFF, #0051D5); }
.mini-stat-card.warning { background: linear-gradient(135deg, #FF9500, #C97300); }
.mini-stat-card .el-icon { font-size: 32px; opacity: 0.8; }
.m-val { font-size: 28px; font-weight: 800; line-height: 1; }
.m-lab { font-size: 12px; opacity: 0.9; font-weight: 600; margin-top: 4px; }

.chart-row { margin-bottom: 0px; }
.chart-container { padding: 10px; }

.sample-list-modern { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-bottom: 20px; }
.modern-example-item { padding: 16px; border-radius: 12px; background: var(--bg-secondary); border-top: 4px solid #ddd; transition: all 0.2s; }
.modern-example-item:hover { transform: scale(1.02); }
.ex-head { display: flex; justify-content: space-between; margin-bottom: 8px; }
.ex-tag { font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 4px; color: white; }
.danger .ex-tag { background: var(--error-color); }
.warning .ex-tag { background: var(--warning-color); }
.info .ex-tag { background: var(--text-tertiary); }
.primary .ex-tag { background: var(--primary-color); }
.success .ex-tag { background: var(--success-color); }
.ex-score { font-size: 11px; color: var(--text-tertiary); font-weight: 600; }
.ex-text { font-size: 13px; line-height: 1.5; color: var(--text-primary); }
.pagination-center { display: flex; justify-content: center; padding-top: 10px; }

html.dark .dashboard-card, html.dark .mini-stat-card { border-color: rgba(255,255,255,0.1); }
html.dark .c-item, html.dark .n-tag, html.dark .modern-example-item { background: rgba(255,255,255,0.03); }
</style>
