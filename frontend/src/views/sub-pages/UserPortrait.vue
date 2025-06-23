<template>
  <div class="user-portrait">
    <h2>用户画像分析</h2>
    <el-input v-model="uid" placeholder="请输入用户UID" style="width: 300px; margin-bottom: 10px;" />
    <el-button type="primary" @click="fetchComments" style="margin-right: 10px;">获取评论</el-button>
    <el-button type="success" @click="analyzeUser" :loading="analyzing" style="margin-right: 10px;">分析用户画像</el-button>
    <el-button type="info" @click="getHistoryAnalysis" :loading="loadingHistory">查看历史分析</el-button>
    
    <div v-if="loading" style="margin-top: 10px;">加载中...</div>
    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    
    <!-- 评论内容展示 -->
    <div v-if="comments.length" style="margin-top: 20px;">
      <h3>评论内容（共{{ comments.length }}条）</h3>
      <el-table :data="comments" style="width: 100%; margin-top: 10px;">
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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import request from '@/utils/request';

const uid = ref('');
const comments = ref<any[]>([]);
const analysisResult = ref<any>(null);
const loading = ref(false);
const analyzing = ref(false);
const loadingHistory = ref(false);
const error = ref('');

const fetchComments = async () => {
  if (!uid.value) {
    error.value = '请输入UID';
    return;
  }
  loading.value = true;
  error.value = '';
  comments.value = [];
  try {
    const res = await request.get(`/api/user/comments/redis/${uid.value}`);
    if (res.code === 200) {
      comments.value = res.data;
    } else {
      error.value = res.message || '未找到评论';
    }
  } catch (e: any) {
    error.value = e.message || '请求失败';
  } finally {
    loading.value = false;
  }
};

const analyzeUser = async () => {
  if (!uid.value) {
    error.value = '请输入UID';
    return;
  }
  analyzing.value = true;
  error.value = '';
  try {
    const res = await request.post(`/api/user/analyze/${uid.value}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
    } else {
      error.value = res.message || '分析失败';
    }
  } catch (e: any) {
    error.value = e.message || '分析请求失败';
  } finally {
    analyzing.value = false;
  }
};

const getHistoryAnalysis = async () => {
  if (!uid.value) {
    error.value = '请输入UID';
    return;
  }
  loadingHistory.value = true;
  error.value = '';
  try {
    const res = await request.get(`/api/user/analysis/${uid.value}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
    } else {
      error.value = res.message || '未找到历史分析结果';
    }
  } catch (e: any) {
    error.value = e.message || '获取历史分析失败';
  } finally {
    loadingHistory.value = false;
  }
};

const formatTime = (timestamp: string) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
};
</script>

<style scoped>
.user-portrait {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style> 