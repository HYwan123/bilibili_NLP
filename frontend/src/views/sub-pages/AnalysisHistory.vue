<template>
  <div class="analysis-history">
    <h2>分析记录</h2>
    
    <el-alert
      title="功能说明"
      type="info"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      <p>目前系统支持以下功能：</p>
      <ul>
        <li>在"用户画像分析"页面输入UID，点击"查看历史分析"可以查看该用户的已分析结果</li>
        <li>分析结果会自动保存到Redis，避免重复分析</li>
        <li>支持按UID搜索历史分析记录</li>
      </ul>
    </el-alert>
    
    <div class="search-section">
      <el-input 
        v-model="searchUid" 
        placeholder="输入用户UID查看分析结果" 
        style="width: 300px; margin-right: 10px;"
        clearable
      />
      <el-button type="primary" @click="searchAnalysis" :loading="loading">搜索分析结果</el-button>
    </div>
    
    <div v-if="loading" style="margin-top: 20px; text-align: center;">搜索中...</div>
    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    
    <!-- 分析结果展示 -->
    <div v-if="analysisResult" style="margin-top: 20px;">
      <h3>分析结果</h3>
      <el-card>
        <div v-if="analysisResult.uid">
          <p><strong>用户UID:</strong> {{ analysisResult.uid }}</p>
          <p><strong>评论数量:</strong> {{ analysisResult.comment_count }}</p>
          <p><strong>分析时间:</strong> {{ formatTime(analysisResult.timestamp) }}</p>
        </div>
        <div v-if="analysisResult.analysis" style="margin-top: 15px;">
          <h4>分析内容:</h4>
          <div style="white-space: pre-line; line-height: 1.6; max-height: 400px; overflow-y: auto;">
            {{ analysisResult.analysis }}
          </div>
        </div>
        <div v-if="sampleCommentsToShow.length > 0" style="margin-top: 15px;">
          <h4>样本评论:</h4>
          <el-table :data="sampleCommentsToShow" style="width: 100%;">
            <el-table-column type="index" width="50" />
            <el-table-column v-if="isStringArray" label="评论内容">
              <template #default="scope">{{ scope.row }}</template>
            </el-table-column>
            <el-table-column v-else prop="comment_text" label="评论内容" />
          </el-table>
          <div v-if="showExpandBtn" style="margin-top: 8px; text-align: right;">
            <el-button size="small" @click="toggleExpand">{{ expanded ? '收起' : '展开全部' }}</el-button>
          </div>
        </div>
      </el-card>
    </div>
    
    <div v-else-if="!loading && searchUid" style="margin-top: 20px; text-align: center; color: #999;">
      未找到该用户的分析记录，请先进行用户画像分析
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import request from '@/utils/request';

const searchUid = ref('');
const loading = ref(false);
const error = ref('');
const analysisResult = ref<any>(null);

const expanded = ref(false);
const maxShow = 3;

const isStringArray = computed(() => {
  const arr = analysisResult.value?.sample_comments;
  return Array.isArray(arr) && arr.length > 0 && typeof arr[0] === 'string';
});

const sampleCommentsToShow = computed(() => {
  const arr = analysisResult.value?.sample_comments || [];
  if (!expanded.value) {
    return arr.slice(0, maxShow);
  }
  return arr;
});

const showExpandBtn = computed(() => {
  const arr = analysisResult.value?.sample_comments || [];
  return arr.length > maxShow;
});

const toggleExpand = () => {
  expanded.value = !expanded.value;
};

const searchAnalysis = async () => {
  if (!searchUid.value) {
    error.value = '请输入UID';
    return;
  }
  
  loading.value = true;
  error.value = '';
  analysisResult.value = null;
  expanded.value = false;
  
  try {
    const res = await request.get(`/api/user/analysis/${searchUid.value}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
    } else {
      error.value = res.message || '未找到分析结果';
    }
  } catch (e: any) {
    error.value = e.message || '搜索失败';
  } finally {
    loading.value = false;
  }
};

const formatTime = (timestamp: string) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
};
</script>

<style scoped>
.analysis-history {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
</style> 