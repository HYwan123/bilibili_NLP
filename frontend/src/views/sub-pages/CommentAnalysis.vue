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
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.basic_stats?.total_comments || 0 }}</div>
              <div class="stat-label">总评论数</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.basic_stats?.unique_users || 0 }}</div>
              <div class="stat-label">独立用户数</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-item">
              <div class="stat-number">{{ analysisResult.basic_stats?.average_length || 0 }}</div>
              <div class="stat-label">平均评论长度</div>
            </div>
          </el-col>

        </el-row>
      </el-card>

      <!-- 情感分析 -->
      <el-card class="result-card" v-if="analysisResult.sentiment_analysis">
        <template #header>
          <span>情感分析</span>
        </template>
        <div class="sentiment-stats">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="sentiment-item negative">
                <div class="sentiment-number">{{ analysisResult.sentiment_analysis?.negative || 0 }}</div>
                <div class="sentiment-label">负面评论</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="sentiment-item neutral">
                <div class="sentiment-number">{{ analysisResult.sentiment_analysis?.neutral || 0 }}</div>
                <div class="sentiment-label">中性评论</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="sentiment-item positive">
                <div class="sentiment-number">{{ analysisResult.sentiment_analysis?.positive || 0 }}</div>
                <div class="sentiment-label">正面评论</div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 评论示例 -->
        <div class="comment-examples" v-if="getCommentExamples.length > 0">
          <h4>评论示例分析 (共 {{ getAllCommentExamples().length }} 条)</h4>
          <el-table :data="getCommentExamples" stripe style="width: 100%">
            <el-table-column prop="comment" label="评论内容" min-width="300" show-overflow-tooltip />
            <el-table-column prop="label" label="情感标签" width="120">
              <template #default="scope">
                <el-tag :type="getSentimentType(scope.row.label)">
                  {{ getSentimentText(scope.row.label) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="置信度" width="100">
              <template #default="scope">
                {{ (scope.row.score * 100).toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页组件 -->
          <div class="pagination-container" v-if="getAllCommentExamples().length > pageSize">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="getAllCommentExamples().length"
              :page-sizes="[5, 10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="handleCurrentChange"
              @size-change="handleSizeChange"
            />
          </div>
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
import { ref, reactive, onUnmounted, computed } from 'vue'
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

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(5)

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
  // 处理星级评分格式：{1~5} star
  if (typeof sentiment === 'string' && sentiment.includes('star')) {
    const starMatch = sentiment.match(/\{(\d+)\} star/)
    if (starMatch) {
      const starRating = parseInt(starMatch[1])
      if (starRating >= 1 && starRating <= 2) return 'danger' // 1-2星：负面
      if (starRating === 3) return 'info' // 3星：中性
      if (starRating >= 4 && starRating <= 5) return 'success' // 4-5星：正面
    }
  }
  
  // 处理原有的字符串格式
  switch (sentiment) {
    case '1 star': return 'danger'
    case '2 stars': return 'danger'
    case '4 stars': return 'success'
    case '5 stars': return 'success'
    default: return 'info'

  }
}

const getSentimentText = (sentiment: string) => {

  
  // 处理原有的字符串格式
  switch (sentiment) {
    case '1 star': return '负面'
    case '2 stars': return '负面'
    case '4 stars': return '正面'
    case '5 stars': return '正面'
    default: return '中性'
  }
}

const getKeywordSize = (count: number) => {
  if (count >= 10) return '16px'
  if (count >= 5) return '14px'
  return '12px'
}

// 获取所有评论示例
const getAllCommentExamples = () => {
  if (!analysisResult.value?.sentiment_analysis) return []
  
  const examples = []
  const sentimentData = analysisResult.value.sentiment_analysis
  
  // 遍历sentiment_analysis对象，找到包含label和score的评论示例
  for (const [comment, data] of Object.entries(sentimentData)) {
    if (comment !== 'negative' && comment !== 'neutral' && comment !== 'positive' && 
        typeof data === 'object' && data !== null && 'label' in data && 'score' in data) {
      examples.push({
        comment,
        label: data.label,
        score: data.score
      })
    }
  }
  
  return examples
}

// 获取当前页的评论示例
const getCommentExamples = computed(() => {
  const allExamples = getAllCommentExamples()
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return allExamples.slice(startIndex, endIndex)
})

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 处理每页数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
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

/* 情感分析样式 */
.sentiment-stats {
  margin-bottom: 20px;
}

.sentiment-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
}

.sentiment-item.negative {
  border-left: 4px solid #f56c6c;
}

.sentiment-item.neutral {
  border-left: 4px solid #e6a23c;
}

.sentiment-item.positive {
  border-left: 4px solid #67c23a;
}

.sentiment-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.sentiment-item.negative .sentiment-number {
  color: #f56c6c;
}

.sentiment-item.neutral .sentiment-number {
  color: #e6a23c;
}

.sentiment-item.positive .sentiment-number {
  color: #67c23a;
}

.sentiment-label {
  font-size: 14px;
  color: #666;
}

.comment-examples {
  margin-top: 20px;
}

.comment-examples h4 {
  margin-bottom: 15px;
  color: #333;
  font-weight: 600;
}

/* 分页样式 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
