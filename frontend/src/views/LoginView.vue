<template>
  <div class="login-container">
    <div class="login-left">
      <div class="welcome-content">
        <h1 class="system-title">Bili-NLP</h1>
        <p class="system-description">AI驱动的B站评论分析平台</p>
      </div>
    </div>
    <div class="login-right">
      <el-card class="login-form-card">
        <template #header>
          <div class="card-header">
            <span>账户登录</span>
          </div>
        </template>
        <el-form @submit.prevent="login" label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="username" placeholder="请输入用户名" size="large" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input type="password" v-model="password" placeholder="请输入密码" show-password size="large"/>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="login" style="width: 100%;" size="large">登 录</el-button>
          </el-form-item>
          <div class="register-link">
            <span>没有账户?</span>
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { login as loginApi } from '@/api/auth'

const username = ref('')
const password = ref('')
const router = useRouter()
const authStore = useAuthStore()

const goToRegister = () => {
  router.push('/register');
}

const login = async () => {
  if (!username.value || !password.value) {
    ElMessage.error('请输入用户名和密码');
    return;
  }
  try {
    const response = await loginApi({ username: username.value, password: password.value });
    // 后端返回的数据结构应为 { code: 200, data: { token: '...' } }
    if (response.data && response.data.token) {
      authStore.setToken(response.data.token);
      router.push('/');
    } else {
      ElMessage.error('登录失败：未在返回数据中找到 Token。');
    }
  } catch (error) {
    // axios 拦截器会自动处理错误消息，这里可以打印日志
    console.error('Login request failed:', error);
  }
}
</script>

<style scoped>
.login-container {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #6a82fb, #fc5c7d);
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
  padding: 40px;
}

.system-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
}

.system-description {
  font-size: 20px;
}

.login-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-form-card {
  width: 70%;
  max-width: 450px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 8px;
}

.card-header {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
}

.register-link {
  margin-top: 15px;
  text-align: center;
}
</style> 