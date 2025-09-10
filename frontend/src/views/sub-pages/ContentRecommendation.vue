<template>
  <div class="content-recommendation">
    <el-card class="recommendation-card">
      <template #header>
        <div class="card-header">
          <span>内容推荐系统</span>
          <el-button type="primary" @click="generateRecommendations" :loading="generating" :disabled="!selectedUid || generating">
            {{ generating ? '正在生成推荐...' : '生成推荐' }}
          </el-button>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择用户">
          <el-select v-model="selectedUid" placeholder="请选择要推荐的用户ID" :disabled="generating" @change="onUserChange">
            <el-option
              v-for="uid in availableUids"
              :key="uid"
              :label="`用户 ${uid}`"
              :value="uid"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 用户偏好分析 -->
      <div v-if="userPreferences" class="preferences-section">
        <el-card class="preference-card">
          <template #header>
            <span>用户偏好分析</span>
          </template>
          
          <!-- 关键词偏好 -->
          <div class="preference-item">
            <h4>兴趣关键词</h4>
            <div class="keyword-tags">
              <el-tag 
                v-for="keyword in userPreferences.user_keywords?.slice(0, 10)" 
                :key="keyword.word"
                class="keyword-tag"
                :style="{ fontSize: getKeywordSize(keyword.count) }"
              >
                {{ keyword.word }} ({{ keyword.count }})
              </el-tag>
            </div>
          </div>

          <!-- 内容类别偏好 -->
          <div class="preference-item" v-if="userPreferences.content_preferences">
            <h4>内容类别偏好</h4>
            <el-row :gutter="20">
              <el-col :span="8" v-for="(category, index) in userPreferences.content_preferences.top_categories?.slice(0, 3)" :key="index">
                <div class="category-item">
                  <div class="category-name">{{ category[0] }}</div>
                  <div class="category-score">匹配度: {{ category[1] }}</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 用户画像 -->
          <div class="preference-item">
            <h4>用户画像</h4>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="profile-item">
                  <div class="profile-label">情感倾向</div>
                  <div class="profile-value">{{ getSentimentText(userPreferences.sentiment_tendency?.ratio) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="profile-item">
                  <div class="profile-label">参与度</div>
                  <div class="profile-value">{{ getEngagementText(userPreferences.comment_style?.engagement_level) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="profile-item">
                  <div class="profile-label">平均评论长度</div>
                  <div class="profile-value">{{ userPreferences.comment_style?.average_length || 0 }} 字</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="profile-item">
                  <div class="profile-label">评论总数</div>
                  <div class="profile-value">{{ userPreferences.comment_style?.total_comments || 0 }} 条</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 推荐结果展示 -->
    <div v-if="recommendations && recommendations.length > 0" class="recommendations-section">
      <el-card class="result-card">
        <template #header>
          <span>推荐结果 ({{ recommendations.length }} 个推荐)</span>
        </template>
        
        <div class="recommendations-grid">
          <el-card 
            v-for="(rec, index) in recommendations" 
            :key="index"
            class="recommendation-item"
            shadow="hover"
          >
            <div class="rec-header">
              <h3 class="rec-title">{{ rec.title }}</h3>
              <el-tag :type="getCategoryType(rec.category)" size="small">{{ rec.category }}</el-tag>
            </div>
            
            <div class="rec-content">
              <p class="rec-description">{{ rec.description }}</p>
              
              <div class="rec-stats">
                <el-row :gutter="10">
                  <el-col :span="8">
                    <div class="stat-item">
                      <i class="el-icon-view"></i>
                      <span>{{ formatViewCount(rec.view_count) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="stat-item">
                      <i class="el-icon-star-on"></i>
                      <span>{{ rec.recommendation_score || rec.ai_score || 0 }}</span>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="stat-item">
                      <i class="el-icon-time"></i>
                      <span>{{ formatDate(rec.pub_date) }}</span>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <div class="rec-reason">
                <el-tag type="info" size="mini">推荐理由</el-tag>
                <p>{{ rec.reason || rec.ai_reason || '基于您的兴趣推荐' }}</p>
              </div>

              <div class="rec-actions">
                <el-button type="primary" size="small" @click="openVideo(rec.video_id)">
                  <i class="el-icon-video-play"></i>
                  观看视频
                </el-button>
                <el-button type="success" size="small" v-if="rec.recommendation_type === 'ai_based'">
                  <i class="el-icon-cpu"></i>
                  AI推荐
                </el-button>
              </div>
            </div>
          </el-card>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getUserRecommendations, generateUserRecommendations, getUserPreferences, getAvailableUids } from '@/api/bilibili'

const form = reactive({
  uid: null
})

const generating = ref(false)
const selectedUid = ref<number | null>(null)
const availableUids = ref<number[]>([])
const recommendations = ref<any[]>([])
const userPreferences = ref<any>(null)
const error = ref('')

onMounted(async () => {
  await loadAvailableUids()
})

const loadAvailableUids = async () => {
  try {
    const response = await getAvailableUids()
    if (response.code === 200 && response.data) {
      availableUids.value = response.data.map((item: any) => item.uid).filter((uid: number) => uid)
    }
  } catch (err: any) {
    console.error('获取用户列表失败:', err)
  }
}

const onUserChange = async () => {
  if (selectedUid.value) {
    await loadUserPreferences()
    await loadExistingRecommendations()
  }
}

const loadUserPreferences = async () => {
  if (!selectedUid.value) return
  
  try {
    const response = await getUserPreferences(selectedUid.value)
    if (response.code === 200) {
      userPreferences.value = response.data
    }
  } catch (err: any) {
    console.error('获取用户偏好失败:', err)
  }
}

const loadExistingRecommendations = async () => {
  if (!selectedUid.value) return
  
  try {
    const response = await getUserRecommendations(selectedUid.value)
    if (response.code === 200) {
      recommendations.value = response.data
    }
  } catch (err: any) {
    // 如果没有现有推荐，不显示错误
    recommendations.value = []
  }
}

const generateRecommendations = async () => {
  if (!selectedUid.value) {
    ElMessage.warning('请先选择用户')
    return
  }
  
  generating.value = true
  error.value = ''
  
  try {
    const response = await generateUserRecommendations(selectedUid.value)
    
    if (response.code === 200) {
      recommendations.value = response.data.recommendations || []
      userPreferences.value = response.data.user_preferences
      ElMessage.success(`成功生成 ${recommendations.value.length} 个推荐！`)
    } else {
      throw new Error(response.message || '生成推荐失败')
    }
  } catch (err: any) {
    error.value = err.message || '生成推荐时发生错误'
    ElMessage.error(error.value)
  } finally {
    generating.value = false
  }
}

const getKeywordSize = (count: number) => {
  if (count >= 10) return '16px'
  if (count >= 5) return '14px'
  return '12px'
}

const getSentimentText = (ratio: number) => {
  if (!ratio) return '未知'
  if (ratio > 0.7) return '积极正面'
  if (ratio < 0.3) return '较为挑剔'
  return '中性客观'
}

const getEngagementText = (level: string) => {
  switch (level) {
    case 'high': return '高度参与'
    case 'medium': return '中等参与'
    case 'low': return '低度参与'
    default: return '未知'
  }
}

const getCategoryType = (category: string) => {
  const typeMap: Record<string, string> = {
    '科技': 'primary',
    '游戏': 'success',
    '生活': 'warning',
    '娱乐': 'danger',
    '音乐': 'info',
    '教育': ''
  }
  return typeMap[category] || ''
}

const formatViewCount = (count: number) => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  return count.toString()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '未知'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN')
  } catch {
    return '未知'
  }
}

const openVideo = (videoId: string) => {
  if (videoId) {
    window.open(`https://www.bilibili.com/video/${videoId}`, '_blank')
  }
}
</script>

<style scoped>
.content-recommendation {
  padding: 20px;
}

.recommendation-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preferences-section {
  margin-top: 20px;
}

.preference-card {
  margin-bottom: 20px;
}

.preference-item {
  margin-bottom: 20px;
}

.preference-item h4 {
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  margin-bottom: 5px;
}

.category-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.category-name {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.category-score {
  font-size: 12px;
  color: #666;
}

.profile-item {
  text-align: center;
  padding: 10px;
  background: #f0f2f5;
  border-radius: 6px;
}

.profile-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.profile-value {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.recommendations-section {
  margin-top: 20px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.recommendation-item {
  height: 100%;
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.rec-title {
  margin: 0;
  font-size: 16px;
  color: #333;
  flex: 1;
  margin-right: 10px;
}

.rec-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.rec-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.rec-stats {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-size: 12px;
  color: #666;
}

.rec-reason {
  background: #f0f2f5;
  padding: 10px;
  border-radius: 6px;
}

.rec-reason p {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.rec-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.result-card {
  margin-bottom: 20px;
}
</style>
