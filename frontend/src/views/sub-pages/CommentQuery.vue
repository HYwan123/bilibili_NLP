<template>


  <el-card class="cookie_view">
    
    <el-collapse v-model="viewUserCookie" @change="getCookie">
      <el-collapse-item title="查看cookie" name="1">
          <el-text>{{ cookie_user }}</el-text>
          <br></br>
          <el-button type="primary" @click="open">修改cookie</el-button>
        </el-collapse-item>
    </el-collapse>
    {{ message_ }}
</el-card>

    <br></br>
  <el-card class="page-container">
    <template #header>
      <div class="card-header">
        <span>评论查询</span>
      </div>
    </template>
    
    <el-form :inline="true" @submit.prevent="fetchComments">
      <el-form-item label="视频BV号">
        <el-input v-model="bv" placeholder="请输入B站视频BV号"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchComments">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="comments" stripe style="width: 100%">
      <el-table-column prop="user_name" label="用户"></el-table-column>
      <el-table-column prop="comment_text" label="评论"></el-table-column>
      <el-table-column prop="bert_label" label="分类"></el-table-column>
    </el-table>

  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { changeUserCookie, getComments, getCookies } from '@/api/bilibili';
import { ElMessage } from 'element-plus';

const bv = ref('');
const comments = ref([]);
const cookie_user = ref('');
const viewUserCookie = ref(0)
const message_ = ref('')

const getCookie = async () => {
  try {
    const cookie_all = await getCookies();
    cookie_user.value = cookie_all.data.cookie

  } catch (error) {
    console.error('Failed to fetch comments:', error);
    ElMessage.error('查询失败');
    cookie_user.value = "can not get cookie";
  }
};



const fetchComments = async () => {
  if (!bv.value) {
    ElMessage.error('请输入视频BV号');
    return;
  }
  try {
    const response = await getComments(bv.value);
    comments.value = response.data;
  } catch (error) {
    console.error('Failed to fetch comments:', error);
    ElMessage.error('查询失败');
  }
};

const open = () => {
  ElMessageBox.prompt('请输入新cookie', 'Tip', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputErrorMessage: 'cookie错误',
  })
    .then(async({ value }) => {
      ElMessage({
        type: 'success',
        message: `Your email is:${value}`,
      })
      const result = await changeUserCookie(value);
      message_.value = result.message || '暂无cookie';
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: 'Input canceled',
      })
    })
}





</script>

<style scoped>
.page-container {
  height: 100%;
}
.card-header {
  font-size: 18px;
  font-weight: bold;
}
</style> 