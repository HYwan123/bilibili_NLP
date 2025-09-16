<template>
  <div class="new-recommendation">
    <el-card class="recommendation-card">
      <template #header>
        <div class="card-header">
          <span>新版内容推荐系统</span>
          <div class="action-buttons">
            <el-button 
              type="primary" 
              @click="generateBVRecommendations" 
              :loading="generatingBV" 
              :disabled="!selectedUid || generatingBV"
            >
              {{ generatingBV ? '正在生成BV推荐...' : '生成BV推荐' }}
            </el-button>
            <el-button 
              type="success" 
              @click="getVideoDetails" 
              :loading="loadingDetails"
            >
              {{ loadingDetails ? '正在获取视频详情...' : '获取视频详情' }}
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择用户">
          <el-select v-model="selectedUid" placeholder="请选择要推荐的用户ID" :disabled="generatingBV" @change="onUserChange">
            <el-option
              v-for="uid in availableUids"
              :key="uid"
              :label="`用户 ${uid}`"
              :value="uid"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- BV推荐结果 -->
      <div v-if="bvRecommendations && bvRecommendations.length > 0" class="bv-section">
        <el-card class="bv-card">
          <template #header>
            <span>推荐视频BV号 ({{ bvRecommendations.length }} 个)</span>
          </template>
          
          <div class="bv-list">
            <el-tag 
              v-for="(bv, index) in bvRecommendations" 
              :key="index"
              class="bv-tag"
              type="info"
              @click="copyBV(bv)"
            >
              {{ bv }}
              <el-icon class="copy-icon"><DocumentCopy /></el-icon>
            </el-tag>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 视频详情展示 -->
    <div v-if="videoDetails && Object.keys(videoDetails).length > 0" class="video-details-section">
      <el-card class="details-card">
        <template #header>
          <span>推荐视频详情 ({{ Object.keys(videoDetails).length }} 个视频)</span>
        </template>
        
        <div class="videos-grid">
          <el-card 
            v-for="(video, bv) in videoDetails" 
            :key="bv"
            class="video-item"
            shadow="hover"
          >
            <div class="video-header">
              <h3 class="video-title">{{ video.title || '无标题' }}</h3>
              <el-tag :type="getCategoryType(video.tname)" size="small">{{ video.tname || '未知分类' }}</el-tag>
            </div>
            
            <div class="video-content">
              <p class="video-desc">{{ video.desc || '暂无描述' }}</p>
              
              <div class="video-stats">
                <el-row :gutter="10">
                  <el-col :span="6">
                    <div class="stat-item">
                      <el-icon><View /></el-icon>
                      <span>{{ formatViewCount(video.view) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item">
                      <el-icon><ChatDotRound /></el-icon>
                      <span>{{ formatCount(video.reply) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item">
                      <el-icon><Star /></el-icon>
                      <span>{{ formatCount(video.favorite) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="stat-item">
                      <el-icon><Coin /></el-icon>
                      <span>{{ formatCount(video.coin) }}</span>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <div class="video-meta">
                <div class="meta-item">
                  <span class="meta-label">UP主:</span>
                  <span class="meta-value">{{ video.owner?.name || '未知' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">发布时间:</span>
                  <span class="meta-value">{{ formatTimestamp(video.pubdate) }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">时长:</span>
                  <span class="meta-value">{{ formatDuration(video.duration) }}</span>
                </div>
              </div>

              <div class="video-actions">
                <el-button type="primary" size="small" @click="openVideo(bv)">
                  <el-icon><VideoPlay /></el-icon>
                  观看视频
                </el-button>
                <el-button type="info" size="small" @click="copyBV(bv)">
                  <el-icon><DocumentCopy /></el-icon>
                  复制BV号
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

    <!-- 加载状态 -->
    <el-dialog
      v-model="loadingDialog"
      title="处理中"
      width="30%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div style="text-align: center;">
        <el-icon class="loading-icon" size="24"><Loading /></el-icon>
        <p>{{ loadingMessage }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  DocumentCopy, 
  View, 
  ChatDotRound, 
  Star, 
  Coin, 
  VideoPlay,
  Loading 
} from '@element-plus/icons-vue'
import { 
  getAvailableUids, 
  generateVideoRecommendations, 
  getRecommendedVideosInfo,
  getVideoInfo
} from '@/api/bilibili'
import type { BaseResponse } from '@/types/request'

const form = reactive({
  uid: null
})

const generatingBV = ref(false)
const loadingDetails = ref(false)
const selectedUid = ref<string | null>(null)
const availableUids = ref<number[]>([])
const bvRecommendations = ref<string[]>([])
const videoDetails = ref<Record<string, any>>({})
const error = ref('')
const loadingDialog = ref(false)
const loadingMessage = ref('')

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
    ElMessage.error('获取用户列表失败')
  }
}

const onUserChange = () => {
  // 用户切换时清空之前的推荐结果
  bvRecommendations.value = []
  videoDetails.value = {}
}

const generateBVRecommendations = async () => {
  if (!selectedUid.value) {
    ElMessage.warning('请先选择用户')
    return
  }
  
  generatingBV.value = true
  error.value = ''
  loadingDialog.value = true
  loadingMessage.value = '正在生成视频推荐...'
  
  try {
    console.log('开始生成推荐，用户ID:', selectedUid.value)
    const response = await generateVideoRecommendations(selectedUid.value)
    console.log('完整API响应:', response)
    
    // 后端返回的是直接的数据数组，不是BaseResponse格式
    const responseData = response.data
    console.log('原始响应数据:', responseData)
    console.log('响应数据类型:', typeof responseData)
    
    if (Array.isArray(responseData)) {
      // 直接处理数组数据
      bvRecommendations.value = responseData
      console.log('推荐结果:', bvRecommendations.value)
      ElMessage.success(`成功生成 ${bvRecommendations.value.length} 个视频推荐！`)
    } else if (responseData && typeof responseData === 'object' && responseData.code !== undefined) {
      // 如果是BaseResponse格式（兼容性处理）
      console.log('响应数据code:', responseData.code)
      console.log('响应数据message:', responseData.message)
      console.log('响应数据data:', responseData.data)
      
      if (responseData.code === 200) {
        if (Array.isArray(responseData.data)) {
          bvRecommendations.value = responseData.data
          console.log('推荐结果:', bvRecommendations.value)
          ElMessage.success(`成功生成 ${bvRecommendations.value.length} 个视频推荐！`)
        } else {
          console.error('响应数据data不是数组:', responseData.data)
          throw new Error('服务器返回的数据格式不正确')
        }
      } else {
        console.warn('推荐生成失败，响应码:', responseData.code, '消息:', responseData.message)
        throw new Error(responseData.message || '生成推荐失败')
      }
    } else {
      console.error('响应数据格式错误:', responseData)
      throw new Error('服务器返回的数据格式不正确')
    }
  } catch (err: any) {
    console.error('生成推荐错误详情:', err)
    console.error('错误名称:', err.name)
    console.error('错误消息:', err.message)
    console.error('错误堆栈:', err.stack)
    error.value = err.message || '生成推荐时发生错误'
    ElMessage.error(error.value)
  } finally {
    generatingBV.value = false
    loadingDialog.value = false
  }
}

const getVideoDetails = async () => {
  if (!selectedUid.value) {
    ElMessage.warning('请先选择用户')
    return
  }
  
  loadingDetails.value = true
  error.value = ''
  loadingDialog.value = true
  loadingMessage.value = '正在获取视频详情...'
  
  try {
    console.log('开始获取视频详情，用户ID:', selectedUid.value)
    const response = await getRecommendedVideosInfo(Number(selectedUid.value))
    console.log('完整API响应:', response)
    
    const responseData = response.data
    console.log('原始响应数据:', responseData)
    console.log('响应数据类型:', typeof responseData)
    
    if (responseData && typeof responseData === 'object') {
      console.log('响应数据code:', responseData.code)
      console.log('响应数据message:', responseData.message)
      console.log('响应数据data:', responseData.data)
      
      if (responseData.code !== undefined) {
        // 如果是BaseResponse格式
        if (responseData.code === 200) {
          videoDetails.value = responseData.data || {}
          console.log('视频详情数据:', videoDetails.value)
          console.log('视频数量:', Object.keys(videoDetails.value).length)
          
          // 检查是否有视频信息获取失败的情况
          let hasFailedVideos = false
          for (const bv in videoDetails.value) {
            if (videoDetails.value[bv]?.msg === 'fail') {
              hasFailedVideos = true
              console.log(`视频 ${bv} 信息获取失败，尝试使用单个视频API获取`)
              
              // 尝试使用单个视频API获取信息
              try {
                const singleVideoResponse = await getVideoInfo(bv)
                if (singleVideoResponse.data?.code === 200 && singleVideoResponse.data?.data) {
                  videoDetails.value[bv] = singleVideoResponse.data.data
                  console.log(`视频 ${bv} 信息通过单个API获取成功`)
                }
              } catch (singleError) {
                console.error(`获取单个视频 ${bv} 信息失败:`, singleError)
              }
            }
          }
          
          if (hasFailedVideos) {
            ElMessage.warning('部分视频信息获取失败，已尝试重新获取')
          } else {
            ElMessage.success(`成功获取 ${Object.keys(videoDetails.value).length} 个视频详情！`)
          }
        } else {
          console.warn('获取视频详情失败，响应码:', responseData.code, '消息:', responseData.message)
          throw new Error(responseData.message || '获取视频详情失败')
        }
      } else {
        // 如果是直接的数据对象（没有code字段）
        videoDetails.value = responseData
        console.log('视频详情数据:', videoDetails.value)
        console.log('视频数量:', Object.keys(videoDetails.value).length)
        
        // 检查是否有视频信息获取失败的情况
        let hasFailedVideos = false
        for (const bv in videoDetails.value) {
          if (videoDetails.value[bv]?.msg === 'fail') {
            hasFailedVideos = true
            console.log(`视频 ${bv} 信息获取失败，尝试使用单个视频API获取`)
            
            // 尝试使用单个视频API获取信息
            try {
              const singleVideoResponse = await getVideoInfo(bv)
              if (singleVideoResponse.data?.code === 200 && singleVideoResponse.data?.data) {
                videoDetails.value[bv] = singleVideoResponse.data.data
                console.log(`视频 ${bv} 信息通过单个API获取成功`)
              }
            } catch (singleError) {
              console.error(`获取单个视频 ${bv} 信息失败:`, singleError)
            }
          }
        }
        
        if (hasFailedVideos) {
          ElMessage.warning('部分视频信息获取失败，已尝试重新获取')
        } else {
          ElMessage.success(`成功获取 ${Object.keys(videoDetails.value).length} 个视频详情！`)
        }
      }
    } else {
      console.error('响应数据格式错误:', responseData)
      throw new Error('服务器返回的数据格式不正确')
    }
  } catch (err: any) {
    console.error('获取视频详情错误详情:', err)
    console.error('错误名称:', err.name)
    console.error('错误消息:', err.message)
    console.error('错误堆栈:', err.stack)
    error.value = err.message || '获取视频详情时发生错误'
    ElMessage.error(error.value)
  } finally {
    loadingDetails.value = false
    loadingDialog.value = false
  }
}

const hasBVRecommendations = computed(() => bvRecommendations.value.length > 0)

const copyBV = (bv: string) => {
  navigator.clipboard.writeText(bv)
  ElMessage.success(`已复制BV号: ${bv}`)
}

const openVideo = (bv: string) => {
  if (bv) {
    window.open(`https://www.bilibili.com/video/${bv}`, '_blank')
  }
}

const getCategoryType = (category: string) => {
  const typeMap: Record<string, string> = {
    '游戏': 'success',
    '音乐': 'info',
    '科技': 'primary',
    '生活': 'warning',
    '娱乐': 'danger',
    '知识': '',
    '动画': 'info',
    '影视': 'warning',
    '纪录片': 'success',
    '国创': 'danger'
  }
  return typeMap[category] || 'info'
}

const formatViewCount = (count: number) => {
  if (!count) return '0'
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  return count.toString()
}

const formatCount = (count: number) => {
  if (!count) return '0'
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}w`
  }
  return count.toString()
}

const formatTimestamp = (timestamp: number) => {
  if (!timestamp) return '未知'
  try {
    const date = new Date(timestamp * 1000)
    return date.toLocaleDateString('zh-CN')
  } catch {
    return '未知'
  }
}

const formatDuration = (duration: number) => {
  if (!duration) return '00:00'
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.new-recommendation {
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

.action-buttons {
  display: flex;
  gap: 10px;
}

.bv-section {
  margin-top: 20px;
}

.bv-card {
  margin-bottom: 20px;
}

.bv-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.bv-tag {
  cursor: pointer;
  padding: 8px 12px;
  font-family: 'Courier New', monospace;
}

.bv-tag:hover {
  background-color: #f0f2f5;
}

.copy-icon {
  margin-left: 5px;
  font-size: 12px;
}

.video-details-section {
  margin-top: 20px;
}

.videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.video-item {
  height: 100%;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.video-title {
  margin: 0;
  font-size: 16px;
  color: #333;
  flex: 1;
  margin-right: 10px;
  line-height: 1.4;
}

.video-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.video-thumbnail {
  border-radius: 6px;
  overflow: hidden;
}

.video-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-stats {
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

.video-meta {
  background: #f0f2f5;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
}

.meta-item {
  display: flex;
  margin-bottom: 5px;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-label {
  color: #666;
  margin-right: 8px;
  min-width: 60px;
}

.meta-value {
  color: #333;
  font-weight: 500;
}

.video-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.loading-icon {
  animation: rotate 2s linear infinite;
  margin-bottom: 10px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
