<template>
  <div class="history-management-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>查询历史管理</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="card" @tab-change="handleTabChange">
        <el-tab-pane label="全部历史" name="all">
          <div class="history-section">
            <el-table :data="historyList" stripe style="width: 100%" v-loading="loading">
              <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.type === 'bv' ? 'primary' : 'success'">
                    {{ scope.row.type === 'bv' ? 'BV查询' : 'UID分析' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="bv" label="BV号/UID" width="200">
                <template #default="scope">
                  {{ scope.row.bv || scope.row.uid }}
                </template>
              </el-table-column>
              <el-table-column prop="query_time" label="查询时间" width="200" />
              <el-table-column prop="data" label="查询结果摘要" />
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    v-if="scope.row.type === 'bv'"
                    size="small" 
                    type="primary" 
                    @click="handleInsertVector(scope.row.bv)"
                    :loading="loadingBV === scope.row.bv"
                  >
                    插入向量
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
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
        </el-tab-pane>
        
        <el-tab-pane label="BV评论查询" name="bv">
          <div class="history-section">
            <el-table :data="historyList" stripe style="width: 100%" v-loading="loading">
              <el-table-column prop="bv" label="BV号" width="200" />
              <el-table-column prop="query_time" label="查询时间" width="200" />
              <el-table-column prop="data" label="查询结果摘要" />
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="handleInsertVector(scope.row.bv)"
                    :loading="loadingBV === scope.row.bv"
                  >
                    插入向量
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
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
        </el-tab-pane>
        
        <el-tab-pane label="UID分析历史" name="uuid">
          <div class="history-section">
            <el-table :data="historyList" stripe style="width: 100%" v-loading="loading">
              <el-table-column prop="uid" label="UID" width="150" />
              <el-table-column prop="query_time" label="分析时间" width="200" />
              <el-table-column label="样本评论" min-width="300">
                <template #default="scope">
                  <div v-if="scope.row.sample_comments && scope.row.sample_comments.length > 0">
                    <el-tag 
                      v-for="(comment, index) in scope.row.sample_comments.slice(0, 3)" 
                      :key="index"
                      size="small"
                      class="comment-tag"
                    >
                      {{ comment.length > 20 ? comment.substring(0, 20) + '...' : comment }}
                    </el-tag>
                  </div>
                  <span v-else class="no-data">暂无样本评论</span>
                </template>
              </el-table-column>
            </el-table>
            
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
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getHistory, insertVectorByBV } from '@/api/bilibili';

const activeTab = ref('all');
const historyList = ref([]);
const loadingBV = ref('');
const loading = ref(false);

// 分页状态
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

const loadHistory = async () => {
  loading.value = true;
  try {
    const response = await getHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      type: activeTab.value
    });
    
    if (response.data) {
      historyList.value = response.data.items || [];
      total.value = response.data.total || 0;
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
    ElMessage.error('加载历史记录失败');
  } finally {
    loading.value = false;
  }
};

const handleTabChange = () => {
  currentPage.value = 1;
  loadHistory();
};

const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  currentPage.value = 1;
  loadHistory();
};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  loadHistory();
};

const handleInsertVector = async (bvId) => {
  loadingBV.value = bvId;
  try {
    const response = await insertVectorByBV(bvId);
    if (response.code === 200) {
      ElMessage.success(`BV${bvId} 向量插入成功`);
    } else {
      ElMessage.error(response.message || '插入向量失败');
    }
  } catch (error) {
    console.error('插入向量失败:', error);
    ElMessage.error('插入向量失败，请检查网络连接或后端服务');
  } finally {
    loadingBV.value = '';
  }
};

onMounted(() => {
  loadHistory();
});
</script>

<style scoped>
.history-management-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-section {
  margin-top: 20px;
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
  color: #909399;
  font-size: 14px;
}
</style>
