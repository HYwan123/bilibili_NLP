<template>
  <div class="user-analysis-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户评论获取</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户UID">
          <el-input 
            v-model="form.uid" 
            placeholder="请输入B站用户UID"
            :disabled="loading"
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="fetchComments" 
            :loading="loading"
            :disabled="!form.uid"
            size="large"
          >
            {{ loading ? '获取中...' : '获取用户评论' }}
          </el-button>
          <el-button 
            type="success" 
            @click="getSavedComments" 
            :loading="loadingSaved"
            :disabled="!form.uid"
            size="large"
            style="margin-left: 10px;"
          >
            {{ loadingSaved ? '加载中...' : '查看已保存评论' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="message" class="message-section">
        <el-alert 
          :title="message" 
          :type="messageType" 
          :closable="false"
          show-icon
        />
      </div>

      <div v-if="retrievedComments.length > 0" class="comments-section">
        <h3>用户评论列表 (共{{ retrievedComments.length }}条)</h3>
        <el-table :data="retrievedComments" stripe style="width: 100%" height="700">
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
import { getUserComments, getSavedUserComments } from '@/api/bilibili';

const form = ref({
  uid: '66143532', // Default UID for testing
});

const loading = ref(false);
const loadingSaved = ref(false);
const retrievedComments = ref([]);
const message = ref('');
const messageType = ref('info');

const fetchComments = async () => {
  if (!form.value.uid) {
    ElMessage.error('请输入用户UID');
    return;
  }
  
  // 验证UID格式
  const uid = parseInt(form.value.uid);
  if (isNaN(uid) || uid <= 0) {
    ElMessage.error('请输入有效的用户UID（正整数）');
    return;
  }
  
  loading.value = true;
  message.value = '';
  retrievedComments.value = [];

  try {
    console.log('开始获取用户评论，UID:', uid);
    const response = await getUserComments(uid);
    console.log('获取评论响应:', response);
    
    if (response.data && response.data.comments) {
      retrievedComments.value = response.data.comments;
      message.value = `成功获取 ${response.data.comment_count} 条评论并保存到数据库`;
      messageType.value = 'success';
      ElMessage.success('用户评论获取成功！');
    } else {
      message.value = '未获取到评论数据';
      messageType.value = 'warning';
    }
  } catch (error) {
    console.error('获取评论失败:', error);
    message.value = `获取评论失败: ${error.response?.data?.message || error.message}`;
    messageType.value = 'error';
    ElMessage.error(`获取评论失败: ${error.response?.data?.message || error.message}`);
  } finally {
    loading.value = false;
  }
};

const getSavedComments = async () => {
  if (!form.value.uid) {
    ElMessage.error('请输入用户UID');
    return;
  }
  
  const uid = parseInt(form.value.uid);
  if (isNaN(uid) || uid <= 0) {
    ElMessage.error('请输入有效的用户UID（正整数）');
    return;
  }
  
  loadingSaved.value = true;
  message.value = '';
  retrievedComments.value = [];

  try {
    console.log('开始获取已保存的评论，UID:', uid);
    const response = await getSavedUserComments(uid);
    console.log('获取已保存评论响应:', response);
    
    if (response.data && response.data.length > 0) {
      retrievedComments.value = response.data;
      message.value = `从数据库获取到 ${response.data.length} 条已保存的评论`;
      messageType.value = 'success';
      ElMessage.success('已保存评论获取成功！');
    } else {
      message.value = '数据库中未找到该用户的评论数据，请先获取评论';
      messageType.value = 'info';
    }
  } catch (error) {
    console.error('获取已保存评论失败:', error);
    message.value = `获取已保存评论失败: ${error.response?.data?.message || error.message}`;
    messageType.value = 'error';
    ElMessage.error(`获取已保存评论失败: ${error.response?.data?.message || error.message}`);
  } finally {
    loadingSaved.value = false;
  }
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