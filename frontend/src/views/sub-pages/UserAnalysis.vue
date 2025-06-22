<template>
  <div class="user-analysis-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户画像分析</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户UID">
          <el-input v-model="form.uid" placeholder="请输入B站用户UID"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitTask" :loading="loading">提交分析任务</el-button>
        </el-form-item>
      </el-form>

      <div v-if="jobId" class="progress-section">
        <el-progress :percentage="progress" :text-inside="true" :stroke-width="20" status="success" />
        <p class="status-text">{{ statusText }}</p>
      </div>

      <div v-if="analysisResult" class="result-section">
        <h3>分析结果</h3>
        <p>用户的平均画像向量 (前10维):</p>
        <pre class="vector-pre">{{ analysisResult.average_vector.slice(0, 10) }}...</pre>
      </div>

      <div v-if="retrievedComments.length > 0" class="comments-section">
        <h3>用户近期评论</h3>
        <el-table :data="retrievedComments" stripe style="width: 100%" height="300">
          <el-table-column type="index" width="50" />
          <el-table-column prop="comment_text" label="评论内容" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { userAnalysis, getJobStatus } from '@/api/bilibili';

const form = ref({
  uid: '66143532', // Default UID for testing
});

const loading = ref(false);
const jobId = ref('');
const progress = ref(0);
const statusText = ref('');
const analysisResult = ref(null);
const retrievedComments = ref([]);
let pollTimer = null;

const submitTask = async () => {
  if (!form.value.uid) {
    ElMessage.error('请输入用户UID');
    return;
  }
  loading.value = true;
  jobId.value = '';
  progress.value = 0;
  statusText.value = '正在提交任务...';
  analysisResult.value = null;
  retrievedComments.value = [];
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  try {
    const response = await userAnalysis(form.value.uid);
    jobId.value = response.data.job_id;
    statusText.value = '任务已提交，等待处理...';
    ElMessage.success('任务提交成功！');
    pollJobStatus();
  } catch (error) {
    console.error('任务提交失败:', error);
    ElMessage.error('任务提交失败，请查看控制台');
    statusText.value = '任务提交失败';
  } finally {
    loading.value = false;
  }
};

const pollJobStatus = () => {
  pollTimer = setInterval(async () => {
    if (!jobId.value) {
      clearInterval(pollTimer);
      return;
    }
    try {
      const response = await getJobStatus(jobId.value);
      const data = response.data;
      progress.value = data.progress || 0;
      statusText.value = data.details || '...';

      if (data.status === 'Completed') {
        clearInterval(pollTimer);
        statusText.value = '分析完成！';
        analysisResult.value = data.result;
        retrievedComments.value = data.result.comments || [];
        ElMessage.success('用户画像分析已完成！');
      } else if (data.status === 'Failed') {
        clearInterval(pollTimer);
        statusText.value = `任务失败: ${data.details}`;
        ElMessage.error(`任务失败: ${data.details}`);
      }
    } catch (error) {
      clearInterval(pollTimer);
      console.error('轮询状态失败:', error);
      statusText.value = '轮询状态失败';
      ElMessage.error('获取任务状态失败');
    }
  }, 2000);
};
</script>

<style scoped>
.user-analysis-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-section {
  margin-top: 20px;
}

.status-text {
  margin-top: 10px;
  color: #606266;
  text-align: center;
}

.result-section {
  margin-top: 20px;
}

.vector-pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.comments-section {
  margin-top: 20px;
}
</style> 