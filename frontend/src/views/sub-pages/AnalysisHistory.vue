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
        <li>默认显示您自己的分析历史记录</li>
      </ul>
    </el-alert>
    
    <div class="search-section">
      <el-input 
        v-model="searchUid" 
        placeholder="输入用户UID查看分析结果" 
        style="width: 300px; margin-right: 10px;"
        clearable
        @clear="handleClearSearch"
      />
      <el-button type="primary" @click="searchAnalysis" :loading="loading">搜索分析结果</el-button>
      <el-button v-if="searchUid" @click="handleClearSearch">显示我的历史</el-button>
    </div>
    
    <!-- 分析历史列表 -->
    <div style="margin-top: 20px;">
      <div v-if="!searchUid" style="margin-bottom: 15px;">
        <h3>我的分析历史</h3>
      </div>
      <div v-else style="margin-bottom: 15px;">
        <h3>搜索结果</h3>
      </div>
      
      <el-table :data="historyList" stripe style="width: 100%" v-loading="loading" empty-text="暂无分析记录">
        <el-table-column prop="uid" label="用户UID" width="150" />
        <el-table-column prop="query_time" label="分析时间" width="180" />
        <el-table-column label="样本评论" min-width="400">
          <template #default="scope">
            <div v-if="scope.row.sample_comments && scope.row.sample_comments.length > 0">
              <el-tag 
                v-for="(comment, index) in scope.row.sample_comments.slice(0, 3)" 
                :key="index"
                size="small"
                class="comment-tag"
                type="success"
              >
                {{ comment.length > 30 ? comment.substring(0, 30) + '...' : comment }}
              </el-tag>
              <el-tag v-if="scope.row.sample_comments.length > 3" size="small" type="info">
                +{{ scope.row.sample_comments.length - 3 }} 更多
              </el-tag>
            </div>
            <span v-else class="no-data">暂无样本评论</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="viewDetail(scope.row.uid)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="searchUid && analysisResult" style="margin-top: 20px;">
        <el-card>
          <div v-if="analysisResult.uid">
            <p><strong>用户UID:</strong> {{ analysisResult.uid }}</p>
            <p><strong>评论数量:</strong> {{ analysisResult.comment_count }}</p>
            <p><strong>分析时间:</strong> {{ formatTime(analysisResult.timestamp) }}</p>
          </div>
          <div v-if="analysisResult.analysis" style="margin-top: 15px;">
            <h4>分析内容:</h4>
            <div style="white-space: pre-line; line-height: 1.6; max-height: 400px; overflow-y: auto; background: var(--bg-secondary); padding: 15px; border-radius: 4px;">
              {{ analysisResult.analysis }}
            </div>
          </div>
          <div v-if="expandedComments.length > 0" style="margin-top: 15px;">
            <h4>样本评论 ({{ expandedComments.length }}条):</h4>
            <el-table :data="expandedComments" style="width: 100%;" max-height="300">
              <el-table-column type="index" width="50" />
              <el-table-column label="评论内容" min-width="400">
                <template #default="scope">
                  <div style="white-space: pre-wrap; word-break: break-all;">{{ scope.row }}</div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </div>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
    
    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import { getHistory } from '@/api/bilibili';

const searchUid = ref('');
const loading = ref(false);
const error = ref('');
const analysisResult = ref<any>(null);
const expandedComments = ref<string[]>([]);

// 分页状态
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const historyList = ref<any[]>([]);

// 加载历史记录
const loadHistory = async () => {
  if (searchUid.value) return; // 搜索模式下不走这里
  
  loading.value = true;
  error.value = '';
  
  try {
    const response = await getHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      type: 'uuid'
    });
    
    if (response.data) {
      historyList.value = response.data.items || [];
      total.value = response.data.total || 0;
    }
  } catch (e: any) {
    console.error('加载历史记录失败:', e);
    error.value = '加载历史记录失败';
  } finally {
    loading.value = false;
  }
};

// 搜索分析结果
const searchAnalysis = async () => {
  if (!searchUid.value) {
    error.value = '请输入UID';
    return;
  }
  
  loading.value = true;
  error.value = '';
  analysisResult.value = null;
  expandedComments.value = [];
  
  try {
    const response = await request.get(`/api/user/analysis/${searchUid.value}`);
    const res = response.data;
    if (res.code === 200) {
      analysisResult.value = res.data;
      expandedComments.value = res.data.sample_comments || [];
      // 同时添加到历史列表显示
      historyList.value = [{
        uid: res.data.uid,
        query_time: formatTime(res.data.timestamp),
        sample_comments: res.data.sample_comments || []
      }];
      total.value = 1;
    } else {
      error.value = res.message || '未找到分析结果';
      historyList.value = [];
      total.value = 0;
    }
  } catch (e: any) {
    error.value = e.message || '搜索失败';
    historyList.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 查看详情
const viewDetail = async (uid: string | number) => {
  searchUid.value = String(uid);
  await searchAnalysis();
};

// 清除搜索
const handleClearSearch = () => {
  searchUid.value = '';
  analysisResult.value = null;
  expandedComments.value = [];
  currentPage.value = 1;
  loadHistory();
};

// 分页变化
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize;
  currentPage.value = 1;
  if (!searchUid.value) {
    loadHistory();
  }
};

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage;
  if (!searchUid.value) {
    loadHistory();
  }
};

const formatTime = (timestamp: string) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
};

onMounted(() => {
  loadHistory();
});
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.comment-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.no-data {
  color: var(--text-tertiary);
  font-size: 14px;
}

h2 {
  margin-bottom: 20px;
  color: var(--primary-color);
}

h3 {
  margin-bottom: 15px;
  color: var(--text-primary);
  font-weight: 600;
}
</style>
