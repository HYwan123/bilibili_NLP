<template>
  <div class="user-analysis-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户画像分析系统</span>
        </div>
      </template>

      <!-- 输入 UID -->
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户UID">
          <el-input 
            v-model="form.uid" 
            placeholder="请输入B站用户UID"
            :disabled="loading"
            clearable
          ></el-input>
        </el-form-item>

        <!-- 按钮操作区 -->
        <el-form-item>
          <el-button type="primary" @click="fetchComments" :loading="loading" :disabled="!form.uid">
            {{ loading ? '获取中...' : '获取用户评论' }}
          </el-button>
          <el-button type="success" @click="getSavedComments" :loading="loadingSaved" :disabled="!form.uid">
            {{ loadingSaved ? '加载中...' : '查看已保存评论' }}
          </el-button>
          <el-button type="warning" @click="analyzeUser" :loading="analyzing" :disabled="!form.uid">
            分析用户画像
          </el-button>

        </el-form-item>
      </el-form>

      <!-- 消息展示 -->
      <div v-if="message" class="message-section">
        <el-alert :title="message" :type="messageType" :closable="false" show-icon />
      </div>

      <!-- 评论表格 -->
      <div v-if="retrievedComments.length > 0" class="comments-section">
        <h3>用户评论列表 (共{{ retrievedComments.length }}条)</h3>
        <el-table :data="retrievedComments" stripe style="width: 100%" height="700">
          <el-table-column type="index" width="50" />
          <el-table-column prop="comment_text" label="评论内容" />
        </el-table>
      </div>

      <!-- 用户画像分析结果 -->
      <div v-if="analysisResult" style="margin-top: 20px;">
        <h3>用户画像分析结果</h3>
        <el-card>
          <div v-if="analysisResult.uid">
            <p><strong>用户UID:</strong> {{ analysisResult.uid }}</p>
            <p><strong>评论数量:</strong> {{ analysisResult.comment_count }}</p>
            <p><strong>分析时间:</strong> {{ formatTime(analysisResult.timestamp) }}</p>
          </div>
          <div v-if="analysisResult.analysis" style="margin-top: 15px;">
            <h4>分析内容:</h4>
            <div style="white-space: pre-line; line-height: 1.6;">{{ analysisResult.analysis }}</div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>


<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { getUserComments, getSavedUserComments } from '@/api/bilibili';
import request from '@/utils/request';

const form = ref({
  uid: '66143532',
});

const loading = ref(false);
const loadingSaved = ref(false);
const loadingHistory = ref(false);
const analyzing = ref(false);

const retrievedComments = ref([]);
const analysisResult = ref(null);

const message = ref('');
const messageType = ref('info');

// 获取评论（实时）
const fetchComments = async () => {
  const uid = parseInt(form.value.uid);
  if (!uid || uid <= 0) {
    ElMessage.error('请输入有效的用户UID');
    return;
  }

  loading.value = true;
  retrievedComments.value = [];
  message.value = '';

  try {
    const response = await getUserComments(uid);
    if (response.data && response.data.comments) {
      retrievedComments.value = response.data.comments;
      message.value = `成功获取 ${response.data.comment_count} 条评论`;
      messageType.value = 'success';
    } else {
      message.value = '未获取到评论数据';
      messageType.value = 'warning';
    }
  } catch (error) {
    message.value = `获取评论失败: ${error.message}`;
    messageType.value = 'error';
  } finally {
    loading.value = false;
  }
};

// 获取已保存评论
const getSavedComments = async () => {
  const uid = parseInt(form.value.uid);
  if (!uid || uid <= 0) {
    ElMessage.error('请输入有效的用户UID');
    return;
  }

  loadingSaved.value = true;
  retrievedComments.value = [];
  message.value = '';

  try {
    const response = await getSavedUserComments(uid);
    if (response.data && response.data.length > 0) {
      retrievedComments.value = response.data;
      message.value = `数据库中获取到 ${response.data.length} 条评论`;
      messageType.value = 'success';
    } else {
      message.value = '数据库中未找到评论，请先获取评论';
      messageType.value = 'info';
    }
  } catch (error) {
    message.value = `获取失败: ${error.message}`;
    messageType.value = 'error';
  } finally {
    loadingSaved.value = false;
  }
};

// 分析用户画像
const analyzeUser = async () => {
  const uid = form.value.uid;
  if (!uid) {
    ElMessage.error('请输入UID');
    return;
  }

  analyzing.value = true;
  try {
    const res = await request.post(`/api/user/analyze/${uid}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
      ElMessage.success('用户画像分析成功');
    } else {
      ElMessage.error(res.message || '分析失败');
    }
  } catch (e) {
    ElMessage.error(e.message || '分析请求失败');
  } finally {
    analyzing.value = false;
  }
};

// 获取历史分析结果
const getHistoryAnalysis = async () => {
  const uid = form.value.uid;
  if (!uid) {
    ElMessage.error('请输入UID');
    return;
  }

  loadingHistory.value = true;
  try {
    const res = await request.get(`/api/user/analysis/${uid}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
      ElMessage.success('历史分析结果加载成功');
    } else {
      ElMessage.warning(res.message || '未找到历史记录');
    }
  } catch (e) {
    ElMessage.error(e.message || '请求失败');
  } finally {
    loadingHistory.value = false;
  }
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
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

.message-section {
  margin-top: 20px;
}

.comments-section {
  margin-top: 20px;
}
</style> 