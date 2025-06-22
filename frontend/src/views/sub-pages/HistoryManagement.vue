<template>
  <el-card class="page-container">
    <template #header>
      <div class="card-header">
        <span>查询历史记录</span>
      </div>
    </template>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="BV号查询历史" name="bv">
        <el-table :data="bvHistory" stripe height="400">
          <el-table-column type="index" width="50" />
          <el-table-column prop="bv" label="BV号" />
          <el-table-column prop="query_time" label="查询时间" />
          <el-table-column prop="data" label="描述" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="用户ID查询历史" name="uid">
        <el-table :data="uidHistory" stripe height="400">
          <el-table-column type="index" width="50" />
          <el-table-column prop="uid" label="用户UID" />
          <el-table-column prop="query_time" label="查询时间" />
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewResult(row.job_id)" 
                :disabled="!row.job_id">
                查看结果
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                @click="viewComments(row.uid)" 
                style="margin-left: 5px;">
                查看评论
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 结果展示对话框 -->
    <el-dialog v-model="dialogVisible" title="分析结果详情" width="50%">
      <div v-if="isLoadingResult">
        <p>正在加载结果...</p>
      </div>
      <div v-else-if="currentResult">
         <div v-if="currentResult.status === 'Completed'">
            <h4>用户画像向量 (前10维)</h4>
            <pre>{{ currentResult.result.average_vector.slice(0, 10) }}...</pre>
            <h4>相关评论 (部分)</h4>
            <el-table :data="currentResult.result.comments" stripe height="250">
              <el-table-column type="index" width="50" />
              <el-table-column prop="comment_text" label="评论内容" />
            </el-table>
         </div>
         <div v-else>
            <p><strong>任务状态:</strong> {{ currentResult.status }}</p>
            <p><strong>详情:</strong> {{ currentResult.details }}</p>
         </div>
      </div>
       <div v-else>
        <p>未能获取到结果。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 评论展示对话框 -->
    <el-dialog v-model="commentsDialogVisible" title="用户评论详情" width="60%">
      <div v-if="isLoadingComments">
        <p>正在加载评论...</p>
      </div>
      <div v-else-if="userComments.length > 0">
        <h4>用户评论列表 (共{{ userComments.length }}条)</h4>
        <el-table :data="userComments" stripe height="400">
          <el-table-column type="index" width="50" />
          <el-table-column prop="comment_text" label="评论内容" />
        </el-table>
      </div>
      <div v-else>
        <p>未找到该用户的评论数据。</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="commentsDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getHistory, getJobStatus, getUserComments } from '@/api/bilibili'
import { ElMessage } from 'element-plus'

const activeTab = ref('bv')
const bvHistory = ref([])
const uidHistory = ref([])
const dialogVisible = ref(false)
const isLoadingResult = ref(false)
const currentResult = ref(null)
const commentsDialogVisible = ref(false)
const isLoadingComments = ref(false)
const userComments = ref([])

const fetchHistory = async () => {
  try {
    const res = await getHistory()
    bvHistory.value = res.data.bv_history
    uidHistory.value = res.data.uuid_history
  } catch (error) {
    console.error('Failed to fetch history:', error)
    ElMessage.error('获取历史记录失败')
  }
}

const viewResult = async (jobId) => {
  if (!jobId) {
    ElMessage.warning('此记录没有关联的分析任务。')
    return
  }
  dialogVisible.value = true
  isLoadingResult.value = true
  currentResult.value = null

  try {
    const res = await getJobStatus(jobId)
    currentResult.value = res.data
  } catch (error) {
    console.error(`Failed to fetch result for job ${jobId}:`, error)
    ElMessage.error('获取分析结果失败')
    currentResult.value = null // Ensure no stale data is shown
  } finally {
    isLoadingResult.value = false
  }
}

const viewComments = async (uid) => {
  commentsDialogVisible.value = true
  isLoadingComments.value = true
  userComments.value = []

  try {
    const res = await getUserComments(uid)
    userComments.value = res.data.data || []
  } catch (error) {
    console.error(`Failed to fetch comments for user ${uid}:`, error)
    ElMessage.error('获取用户评论失败')
  } finally {
    isLoadingComments.value = false
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.page-container {
  min-height: 100%;
  box-sizing: border-box;
}
.card-header {
  font-size: 18px;
  font-weight: bold;
}
pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 