<template>
  <div class="comment-analysis">
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span>评论分析</span>
          <el-button type="primary" @click="startAnalysis" :loading="analyzing" :disabled="analyzing">
            {{ analyzing ? '正在分析中...' : '开始分析' }}
          </el-button>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="BV视频ID">
          <el-input v-model="form.bvId" placeholder="请输入BV视频ID，如：BV1xx411c7mD" :disabled="analyzing" />
        </el-form-item>
      </el-form>

      <!-- 进度条和状态 -->
      <div v-if="analyzing" class="progress-container">
        <el-progress :percentage="jobProgress" :text-inside="true" :stroke-width="20" status="success" />
        <p class="job-status">{{ jobStatusText }}</p>
      </div>
    </el-card>

    <!-- 分析结果展示 -->
    <div v-if="analysisResult" class="analysis-results">
      <!-- 基础统计 -->
      <el-card class="result-card">
        <template #header>
          <span>基础统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.basic_stats?.total_comments || 0 }}</div>
              <div class="stat-label">总评论数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.basic_stats?.unique_users || 0 }}</div>
              <div class="stat-label">独立用户数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.basic_stats?.average_length || 0 }}</div>
              <div class="stat-label">平均评论长度</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.content_quality?.average_quality_score || 0 }}</div>
              <div class="stat-label">平均质量评分</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 情感分析 -->
      <el-card class="result-card" v-if="analysisResult.sentiment_analysis">
        <template #header>
          <span>情感分析</span>
        </template>
        <div v-if="analysisResult.sentiment_analysis.overall_sentiment">
          <el-tag :type="getSentimentType(analysisResult.sentiment_analysis.overall_sentiment)">
            {{ getSentimentText(analysisResult.sentiment_analysis.overall_sentiment) }}
          </el-tag>
        </div>
        <div v-if="analysisResult.sentiment_analysis.analysis_text" class="analysis-text">
          {{ analysisResult.sentiment_analysis.analysis_text }}
        </div>
      </el-card>

      <!-- 关键词分析 -->
      <el-card class="result-card" v-if="analysisResult.keyword_analysis">
        <template #header>
          <span>关键词分析</span>
        </template>
        <div class="keyword-section">
          <h4>高频词汇</h4>
          <div class="keyword-list">
            <el-tag 
              v-for="keyword in analysisResult.keyword_analysis.top_keywords?.slice(0, 10)" 
              :key="keyword.word"
              class="keyword-tag"
              :style="{ fontSize: getKeywordSize(keyword.count) }"
            >
              {{ keyword.word }} ({{ keyword.count }})
            </el-tag>
          </div>
        </div>
        <div class="keyword-section" v-if="analysisResult.keyword_analysis.top_phrases">
          <h4>高频短语</h4>
          <div class="keyword-list">
            <el-tag 
              v-for="phrase in analysisResult.keyword_analysis.top_phrases?.slice(0, 8)" 
              :key="phrase.phrase"
              type="success"
              class="keyword-tag"
            >
              {{ phrase.phrase }} ({{ phrase.count }})
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 用户活跃度分析 -->
      <el-card class="result-card" v-if="analysisResult.user_activity">
        <template #header>
          <span>用户活跃度分析</span>
        </template>
        <div class="activity-section">
          <h4>最活跃用户</h4>
          <el-table :data="analysisResult.user_activity.most_active_users?.slice(0, 5)" stripe>
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="comment_count" label="评论数量" />
          </el-table>
        </div>
        <div class="activity-stats">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="stat-item">
                <div class="stat-number">{{ analysisResult.user_activity.activity_distribution?.single_comment_users || 0 }}</div>
                <div class="stat-label">单次评论用户</div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="stat-item">
                <div class="stat-number">{{ analysisResult.user_activity.activity_distribution?.multiple_comment_users || 0 }}</div>
                <div class="stat-label">多次评论用户</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 内容质量分析 -->
      <el-card class="result-card" v-if="analysisResult.content_quality">
        <template #header>
          <span>内容质量分析</span>
        </template>
        <div class="quality-section">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="quality-item">
                <div class="quality-number high">{{ analysisResult.content_quality.quality_distribution?.high || 0 }}</div>
                <div class="quality-label">高质量评论</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="quality-item">
                <div class="quality-number medium">{{ analysisResult.content_quality.quality_distribution?.medium || 0 }}</div>
                <div class="quality-label">中等质量评论</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="quality-item">
                <div class="quality-number low">{{ analysisResult.content_quality.quality_distribution?.low || 0 }}</div>
                <div class="quality-label">低质量评论</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="error = ''"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { submitCommentAnalysis } from '@/api/bilibili'
import { getJobStatus } from '@/api/bilibili' // 引入查询状态的API
import { ElMessage } from 'element-plus'

const form = reactive({
  bvId: ''
})

const analyzing = ref(false)
const analysisResult = ref<any>(null)
const error = ref('')

// 新增用于任务轮询的状态
const jobId = ref<string | null>(null)
const jobProgress = ref(0)
const jobStatusText = ref('')
let pollingTimer: number | null = null

const startAnalysis = async () => {
  if (!form.bvId.trim()) {
    ElMessage.warning('请输入BV视频ID')
    return
  }
  
  // Reset UI state before request
  analyzing.value = true
  error.value = ''
  analysisResult.value = null
  jobProgress.value = 0
  jobStatusText.value = '正在检查缓存或提交任务...'

  try {
    const response = await submitCommentAnalysis(form.bvId)
    
    // Case 1: Cached result is returned immediately
    if (response.code === 200) {
      analysisResult.value = response.data
      ElMessage.success('成功从缓存中获取分析结果！')
      jobStatusText.value = '已从缓存加载。'
      jobProgress.value = 100
      // Keep analyzing state true for a moment to show progress bar full, then hide.
      setTimeout(() => { analyzing.value = false; }, 500);

    } 
    // Case 2: New job is submitted, start polling
    else if (response.code === 202 && response.data.job_id) {
      jobId.value = response.data.job_id
      ElMessage.success('分析任务已成功提交，正在后台处理...')
      pollJobStatus()
    } 
    // Case 3: Other handled errors from the backend (like 409 Conflict)
    else {
      throw new Error(response.message || '提交分析任务失败')
    }
  } catch (err: any) {
    // This catches network errors or explicit rejections (like 409)
    error.value = err.message || '提交任务时发生错误'
    ElMessage.error(error.value)
    analyzing.value = false
  }
}

const pollJobStatus = () => {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
  }

  if (!jobId.value) {
    analyzing.value = false
    return
  }

  pollingTimer = window.setTimeout(async () => {
    try {
      const statusResponse = await getJobStatus(jobId.value!)
      const job = statusResponse.data;

      jobProgress.value = job.progress || 0
      jobStatusText.value = job.details || ''

      if (job.status === 'Completed') {
        analysisResult.value = job.result
        ElMessage.success('分析任务已完成！')
        analyzing.value = false
        clearTimeout(pollingTimer!)
      } else if (job.status === 'Failed') {
        throw new Error(job.details || '分析任务失败')
      } else {
        // 继续轮询
        pollJobStatus()
      }
    } catch (err: any) {
      error.value = err.message || '获取任务状态失败'
      ElMessage.error(error.value)
      analyzing.value = false
      clearTimeout(pollingTimer!)
    }
  }, 2000) // 每2秒查询一次
}

// 组件卸载时清除定时器
onUnmounted(() => {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
  }
})

const getSentimentType = (sentiment: string) => {
  switch (sentiment) {
    case 'positive': return 'success'
    case 'negative': return 'danger'
    default: return 'info'
  }
}

const getSentimentText = (sentiment: string) => {
  switch (sentiment) {
    case 'positive': return '正面'
    case 'negative': return '负面'
    default: return '中性'
  }
}

const getKeywordSize = (count: number) => {
  if (count >= 10) return '16px'
  if (count >= 5) return '14px'
  return '12px'
}
</script>

<style scoped>
.comment-analysis {
  padding: 20px;
}

.analysis-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-results {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.analysis-text {
  margin-top: 10px;
  line-height: 1.6;
  color: #333;
}

.keyword-section {
  margin-bottom: 20px;
}

.keyword-section h4 {
  margin-bottom: 10px;
  color: #333;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  margin-bottom: 5px;
}

.activity-section {
  margin-bottom: 20px;
}

.activity-section h4 {
  margin-bottom: 10px;
  color: #333;
}

.activity-stats {
  margin-top: 20px;
}

.quality-section {
  text-align: center;
}

.quality-item {
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
}

.quality-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.quality-number.high {
  color: #67c23a;
}

.quality-number.medium {
  color: #e6a23c;
}

.quality-number.low {
  color: #f56c6c;
}

.quality-label {
  font-size: 14px;
  color: #666;
}

.progress-container {
  margin-top: 20px;
  text-align: center;
}

.job-status {
  margin-top: 10px;
  color: #666;
}
</style> 