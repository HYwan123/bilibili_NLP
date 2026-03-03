<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">登录</h1>
      <p class="login-subtitle">B站智能分析平台</p>
      
      <el-form @submit.prevent="login" class="login-form">
        <el-form-item>
          <el-input 
            v-model="username" 
            placeholder="用户名" 
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            type="password" 
            v-model="password" 
            placeholder="密码" 
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="login"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login" class="login-btn" size="large">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>没有账户？</span>
        <el-link type="primary" @click="goToRegister">立即注册</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { login as loginApi } from '@/api/auth'

const username = ref('')
const password = ref('')
const router = useRouter()
const authStore = useAuthStore()

const goToRegister = () => {
  router.push('/register')
}

const login = async () => {
  if (!username.value || !password.value) {
    ElMessage.error('请输入用户名和密码')
    return
  }
  try {
    const response = await loginApi({ username: username.value, password: password.value })
    if (response.data && response.data.token) {
      authStore.setToken(response.data.token)
      router.push('/')
    } else {
      ElMessage.error('登录失败：未获取到 Token')
    }
  } catch (error) {
    console.error('Login request failed:', error)
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 360px;
  background: var(--bg-card);
  border-radius: 16px;
  padding: 40px 32px;
  border: 1px solid var(--border-light);
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 32px;
}

.login-form {
  margin-bottom: 16px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.login-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.login-footer .el-link {
  margin-left: 4px;
}
</style>