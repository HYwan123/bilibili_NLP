<template>
  <div class="history-management-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>查询历史管理</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="BV评论查询历史" name="bv">
          <div class="history-section">
            <el-table :data="bvHistory" stripe style="width: 100%">
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

const activeTab = ref('bv');
const bvHistory = ref([]);
const loadingBV = ref('');

const loadHistory = async () => {
  try {
    const response = await getHistory();
    if (response.data) {
      bvHistory.value = response.data.bv_history || [];
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
    ElMessage.error('加载历史记录失败');
  }
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
</style>
