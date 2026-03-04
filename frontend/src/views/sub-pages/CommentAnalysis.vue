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
              <el-tooltip content="B站视频链接中的BV开头字符串" placement="top">
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
              <template #prefix><el-icon><Link /></el-icon></template>
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

          <div class="quick-actions" v-if="!analysisResult">
            <span class="quick-label">快速尝试：</span>
            <el-tag 
              v-for="sample in sampleBVs" 
              :key="sample"
              class="sample-tag"
              @click="form.bvId = sample; startAnalysis()"
              style="cursor: pointer; margin-right: 10px;"
              effect="light"
            >{{ sample }}</el-tag>
          </div>

          <div v-if="analyzing" class="analysis-progress">
            <div class="progress-header">
              <span class="progress-title">正在执行专家级语料分析逻辑</span>
              <span class="progress-percent">{{ jobProgress }}%</span>
            </div>
            <el-progress :percentage="jobProgress" :stroke-width="8" status="success" :show-text="false" />
            <div class="progress-steps">
              <div 
                v-for="(step, idx) in analysisSteps" 
                :key="idx"
                class="step-item"
                :class="{ active: jobProgress >= step.percent }"
              >
                <el-icon><component :is="step.icon" /></el-icon>
                <span>{{ step.text }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分析结果渲染 -->
    <div v-if="analysisResult && !analysisResult.error" class="results-section">
      <div class="result-header">
        <div class="result-title"><el-icon><CircleCheck /></el-icon> 分析完成</div>
        <el-button size="small" @click="resetAnalysis" round><el-icon><RefreshLeft /></el-icon> 新的分析</el-button>
      </div>

      <!-- 数据清洗报告 -->
      <el-card class="result-card cleaning-report-card" v-if="analysisResult.cleaning_report">
        <template #header>
          <div class="section-header">
            <div class="section-title"><el-icon><Filter /></el-icon> 语料预处理报告</div>
            <div class="cleaning-efficiency">有效载荷: <span class="highlight">{{ analysisResult.cleaning_report.efficiency }}</span></div>
          </div>
        </template>
        <div class="cleaning-content">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="cleaning-stat-item">
                <div class="label">原始语料</div>
                <div class="value">{{ analysisResult.cleaning_report.raw_total }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="cleaning-stat-item">
                <div class="label">过滤噪音</div>
                <div class="value warning">{{ analysisResult.cleaning_report.filtered_out }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="cleaning-stat-item">
                <div class="label">清洗后有效</div>
                <div class="value success">{{ analysisResult.cleaning_report.cleaned_total }}</div>
              </div>
            </el-col>
          </el-row>
          <div class="noise-details">
            <h5>噪音构成分布 (Noise Analysis)</h5>
            <div class="noise-tags">
              <el-tag type="info">互动打卡: {{ analysisResult.cleaning_report.noise_breakdown?.check_in || 0 }}</el-tag>
              <el-tag type="info">重复冗余: {{ analysisResult.cleaning_report.noise_breakdown?.spam || 0 }}</el-tag>
              <el-tag type="info">活动噪音: {{ analysisResult.cleaning_report.noise_breakdown?.lottery || 0 }}</el-tag>
              <el-tag type="info">无效过短: {{ analysisResult.cleaning_report.noise_breakdown?.short_noise || 0 }}</el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 核心统计 -->
      <div class="stats-grid">
        <el-row :gutter="16">
          <el-col :span="8"><div class="stat-card primary"><div class="stat-number">{{ analysisResult.basic_stats?.total_comments }}</div><div class="stat-label">有效总数</div></div></el-col>
          <el-col :span="8"><div class="stat-card success"><div class="stat-number">{{ analysisResult.basic_stats?.unique_users }}</div><div class="stat-label">互动用户</div></div></el-col>
          <el-col :span="8"><div class="stat-card warning"><div class="stat-number">{{ analysisResult.basic_stats?.average_length }}</div><div class="stat-label">语义均长</div></div></el-col>
        </el-row>
      </div>

      <!-- 情感分析 -->
      <el-card class="result-card" v-if="analysisResult.sentiment_analysis">
        <template #header><div class="section-title"><el-icon><PieChart /></el-icon> 情感极性建模</div></template>
        <div class="sentiment-content">
          <SentimentPieChart :data="analysisResult.sentiment_analysis" height="300px" />
          <div class="comment-examples">
            <div v-for="(ex, i) in getCommentExamples" :key="i" class="example-item" :class="getSentimentType(ex.label)">
              <div class="example-text">{{ ex.comment }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 词云 -->
      <el-card class="result-card" v-if="analysisResult.keyword_analysis">
        <template #header><div class="section-title"><el-icon><Collection /></el-icon> 特征词提取</div></template>
        <KeywordCloudChart :data="analysisResult.keyword_analysis?.top_keywords || []" height="300px" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { submitCommentAnalysis, getJobStatus } from '@/api/bilibili';
import SentimentPieChart from '@/components/charts/SentimentPieChart.vue';
import KeywordCloudChart from '@/components/charts/KeywordCloudChart.vue';
import {
  ChatDotRound, VideoPlay, Cpu, Link, QuestionFilled, CircleCheck, RefreshLeft,
  PieChart, User, Document, Collection, Download, DataAnalysis, Search, Filter
} from '@element-plus/icons-vue';

const route = useRoute();
const form = reactive({ bvId: '' });
const analyzing = ref(false);
const jobProgress = ref(0);
const analysisResult = ref<any>(null);
const currentPage = ref(1);
const pageSize = ref(5);
const sampleBVs = ['BV1xx411c7mD', 'BV1bK411x7ct', 'BV1S54y1G7h3'];

const analysisSteps = [
  { percent: 0, text: '预处理', icon: Search },
  { percent: 25, text: '去噪', icon: Filter },
  { percent: 50, text: '特征分析', icon: DataAnalysis },
  { percent: 75, text: '极性建模', icon: Collection },
  { percent: 100, text: '完成', icon: CircleCheck }
];

const startAnalysis = async () => {
  if (!form.bvId) return;
  analyzing.value = true;
  analysisResult.value = null;
  jobProgress.value = 0;
  try {
    const res = await submitCommentAnalysis(form.bvId);
    const data = res.data || res;
    
    if (data.error) {
      ElMessage.error(data.error);
      analyzing.value = false;
      return;
    }
    
    if (data.basic_stats || data.cleaning_report || data.sentiment_analysis) {
      analysisResult.value = data;
      analyzing.value = false;
      jobProgress.value = 100;
      ElMessage.success('分析成功');
    } else if (data.job_id) {
      pollJobStatus(data.job_id);
    }
  } catch (e: any) {
    // 拦截 409 冲突错误
    if (e.response && e.response.status === 409) {
      ElMessage.info('该视频正在分析中，系统已自动连接到分析任务');
      // 对于 409，虽然我们没有得到 job_id，但后端在进行分析。
      // 我们尝试直接通过 BV 号来轮询结果，因为 backend 会在完成后写入 comment_analysis_{bv_id}
      pollResultByBvOnly(form.bvId);
    } else {
      ElMessage.error('服务连接失败，请检查网络');
      analyzing.value = false;
    }
  }
};

/**
 * 专门用于没有 job_id 情况下的轮询（如 409 冲突时）
 */
const pollResultByBvOnly = async (bvId: string) => {
  let attempts = 0;
  const maxAttempts = 30; // 约 1 分钟
  
  const poll = async () => {
    try {
      // 尝试获取结果
      const res = await request.get(`/api/comments/analysis/${bvId}`);
      const data = res.data || res;
      
      if (data && (data.basic_stats || data.sentiment_analysis)) {
        analysisResult.value = data;
        analyzing.value = false;
        jobProgress.value = 100;
        ElMessage.success('已获取最新分析结果');
      } else if (attempts < maxAttempts) {
        attempts++;
        jobProgress.value = Math.min(95, attempts * 3); // 模拟进度
        setTimeout(poll, 2000);
      } else {
        ElMessage.error('获取分析结果超时，请稍后刷新重试');
        analyzing.value = false;
      }
    } catch (error) {
      // 如果后端还没准备好数据，可能会报 404，我们继续等
      if (attempts < maxAttempts) {
        attempts++;
        setTimeout(poll, 2000);
      } else {
        analyzing.value = false;
      }
    }
  };
  poll();
};

const pollJobStatus = async (jobId: string) => {
  const poll = async () => {
    try {
      const data = await getJobStatus(jobId);
      const res = data.data || data;
      jobProgress.value = res.progress || 0;
      if (res.status === 'completed') {
        analysisResult.value = res.result;
        analyzing.value = false;
        ElMessage.success('分析完成');
      } else if (res.status === 'failed') {
        ElMessage.error(res.error || '分析引擎报错');
        analyzing.value = false;
      } else {
        setTimeout(() => { poll(); }, 2000);
      }
    } catch { 
      analyzing.value = false; 
    }
  };
  poll();
};

const resetAnalysis = () => { analysisResult.value = null; form.bvId = ''; };

const getAllCommentExamples = () => {
  const s = analysisResult.value?.sentiment_analysis;
  if (!s) return [];
  if (s.examples) return s.examples;
  const ex: any[] = [];
  const exclude = ['positive','neutral','negative','total'];
  Object.entries(s).forEach(([k, v]) => {
    if (!exclude.includes(k) && typeof v === 'object' && (v as any).label) {
      ex.push({ comment: k, label: (v as any).label });
    }
  });
  return ex;
};

const getCommentExamples = computed(() => {
  const all = getAllCommentExamples();
  return all.slice((currentPage.value - 1) * pageSize.value, currentPage.value * pageSize.value);
});

const getSentimentType = (l: any) => {
  const n = typeof l === 'string' ? parseInt(l) : l;
  const map: any = { 1:'danger', 2:'warning', 3:'info', 4:'success', 5:'success' };
  return map[n] || 'info';
};

const getSentimentText = (l: any) => {
  const n = typeof l === 'string' ? parseInt(l) : l;
  const map: any = { 1:'负面', 2:'较差', 3:'中性', 4:'良好', 5:'优秀' };
  return map[n] || '未知';
};

const getKeywordTagType = (i: number) => i < 3 ? 'danger' : (i < 10 ? 'primary' : 'info');
const getKeywordSize = (c: number) => {
  const max = analysisResult.value?.keyword_analysis?.top_keywords?.[0]?.count || 1;
  return (c / max) > 0.7 ? 'large' : 'default';
};

onMounted(() => {
  const bv = route.query.bv as string;
  if (bv) { form.bvId = bv; startAnalysis(); }
});
</script>

<style scoped>
.comment-analysis-page { padding: 32px; max-width: 1200px; margin: 0 auto; background: var(--bg-secondary); min-height: 100vh; }
.page-header { text-align: center; margin-bottom: 40px; }
.page-title { font-size: 32px; font-weight: 800; color: var(--text-primary); display: flex; align-items: center; justify-content: center; gap: 12px; }
.page-title .el-icon { font-size: 40px; color: var(--primary-color); }
.input-card { border-radius: 16px; border: 1px solid var(--border-light); }
.analysis-progress { margin-top: 32px; padding: 24px; background: var(--bg-secondary); border-radius: 12px; border: 1px solid var(--border-light); }
.progress-steps { display: flex; justify-content: space-between; margin-top: 24px; }
.step-item { display: flex; flex-direction: column; align-items: center; gap: 6px; font-size: 12px; opacity: 0.4; }
.step-item.active { opacity: 1; color: var(--primary-color); }
.results-section { display: flex; flex-direction: column; gap: 24px; margin-top: 40px; }
.result-header { background: var(--primary-color); color: white; padding: 16px 24px; border-radius: 12px; display: flex; justify-content: space-between; }
.cleaning-report-card { border-left: 6px solid var(--primary-color); }
.cleaning-stat-item { text-align: center; padding: 16px; background: var(--bg-secondary); border-radius: 12px; border: 1px solid var(--border-light); }
.cleaning-stat-item .value { font-size: 24px; font-weight: 800; }
.value.warning { color: var(--warning-color); }
.value.success { color: var(--success-color); }
.noise-tags { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.stat-card { background: var(--bg-card); padding: 20px; border-radius: 12px; border: 1px solid var(--border-light); display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.stat-card.primary { background: linear-gradient(135deg, #007AFF, #0051D5); color: white; }
.stat-card.success { background: linear-gradient(135deg, #34C759, #248A3D); color: white; }
.stat-card.warning { background: linear-gradient(135deg, #FF9500, #C97300); color: white; }
.stat-number { font-size: 24px; font-weight: 800; }
.example-item { padding: 12px; border-radius: 8px; margin-bottom: 8px; background: var(--bg-secondary); border-left: 4px solid #eee; }
.example-item.danger { border-left-color: var(--error-color); }
.example-item.success { border-left-color: var(--success-color); }
</style>
