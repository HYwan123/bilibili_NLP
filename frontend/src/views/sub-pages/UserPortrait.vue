<template>
  <div class="user-portrait">
    <h2>历史用户画像分析记录</h2>

    <!-- 历史 UID 列表 -->
    <el-table :data="uidList" style="width: 100%; margin-top: 20px;" v-loading="loadingHistory">
      <el-table-column prop="uid" label="用户UID" width="200" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewAnalysis(row.uid)">
            查看画像
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 弹出用户画像分析结果 -->
    <el-dialog v-model="dialogVisible" title="用户画像分析结果" width="600px" :before-close="handleCloseDialog">
      <div v-if="analysisResult">
        <p><strong>用户UID:</strong> {{ analysisResult.uid }}</p>
        <p><strong>评论数量:</strong> {{ analysisResult.comment_count }}</p>
        <p><strong>分析时间:</strong> {{ formatTime(analysisResult.timestamp) }}</p>
        <div style="margin-top: 15px;">
          <h4>分析内容:</h4>
          <div style="white-space: pre-line; line-height: 1.6;">{{ analysisResult.analysis }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import request from '@/utils/request';

const uidList = ref<{ uid: string }[]>([]);
const analysisResult = ref<any>(null);
const dialogVisible = ref(false);
const loadingHistory = ref(false);

const error = ref('');

// 获取 UID 列表
const fetchUidList = async () => {
  loadingHistory.value = true;
  try {
    const res = await request.get('/api/get_uids'); // res.data 就是数组了
    const uidArray = res.data; // 直接就是 [{uid: 15133257}, ...]
    if (Array.isArray(uidArray)) {
      uidList.value = uidArray;  // 直接赋值，数组格式已经符合 el-table 要求
    } else {
      error.value = '未获取到UID列表';
    }
  } catch (e: any) {
    error.value = e.message || '请求失败';
  } finally {
    loadingHistory.value = false;
  }
};


// 查看某个 UID 的分析结果
const viewAnalysis = async (uid: string) => {
  try {
    const res = await request.get(`/api/user/analysis/${uid}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
      dialogVisible.value = true;
    } else {
      error.value = res.message || '未找到分析记录';
    }
  } catch (e: any) {
    error.value = e.message || '请求失败';
  }
};

const handleCloseDialog = () => {
  dialogVisible.value = false;
  analysisResult.value = null;
};

const formatTime = (timestamp: string) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
};

// 页面加载时请求 UID 列表
onMounted(() => {
  fetchUidList();
});
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