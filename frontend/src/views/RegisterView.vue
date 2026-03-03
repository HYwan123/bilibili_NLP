<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="register-title">注册</h1>
      <p class="register-subtitle">B站智能分析平台</p>
      
      <el-form :model="form" :rules="rules" ref="formRef" class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名" 
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            type="password" 
            v-model="form.password" 
            placeholder="密码（至少6位，含字母和数字）" 
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input 
            type="password" 
            v-model="form.confirmPassword" 
            placeholder="确认密码" 
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-form-item v-if="apiError">
          <el-alert :title="apiError" type="error" show-icon :closable="false" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" class="register-btn" size="large">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-footer">
        <span>已有账户？</span>
        <el-link type="primary" @click="goToLogin">立即登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { register as registerApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const formRef = ref<FormInstance>()
const apiError = ref('')
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule: any, value: any, callback: any) => {
  if (!value) return callback(new Error('请输入密码'))
  if (value.length < 6) return callback(new Error('密码长度不能小于6位'))
  if (!/^(?=.*[A-Za-z])(?=.*\d)/.test(value)) return callback(new Error('密码必须包含字母和数字'))
  if (form.confirmPassword) formRef.value?.validateField('confirmPassword')
  callback()
}

const validatePass2 = (rule: any, value: any, callback: any) => {
  if (!value) return callback(new Error('请再次输入密码'))
  if (value !== form.password) return callback(new Error('两次输入的密码不一致'))
  callback()
}

const rules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, validator: validatePass, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }]
})

const handleRegister = async () => {
  if (!formRef.value || loading.value) return
  
  loading.value = true
  apiError.value = ''
  
  try {
    await formRef.value.validate()
    const response = await registerApi({ username: form.username, password: form.password })
    
    if (response.data?.token) {
      const authStore = useAuthStore()
      authStore.setToken(response.data.token)
    }
    
    ElNotification({ title: '成功', message: '注册成功！', type: 'success' })
    setTimeout(() => router.push('/'), 1500)
  } catch (error: any) {
    if (error.response?.data?.message) {
      apiError.value = error.response.data.message
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => router.push('/login')
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  padding: 24px;
}

.register-card {
  width: 100%;
  max-width: 360px;
  background: var(--bg-card);
  border-radius: 16px;
  padding: 40px 32px;
  border: 1px solid var(--border-light);
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 8px;
}

.register-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 32px;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.register-btn {
  width: 100%;
  border-radius: 8px;
  font-weight: 500;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.register-footer .el-link {
  margin-left: 4px;
}
</style>