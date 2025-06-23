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
import { getHistory } from '@/api/bilibili';

const activeTab = ref('bv');
const bvHistory = ref([]);

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