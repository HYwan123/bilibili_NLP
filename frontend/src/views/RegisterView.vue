<template>
  <div class="register-container">
    <div class="register-left">
      <div class="welcome-content">
        <h1 class="system-title">加入 Bili-NLP</h1>
        <p class="system-description">开启您的 AI 评论分析之旅</p>
      </div>
    </div>
    <div class="register-right">
      <el-card class="register-form-card" @click="cardClicked">
        <template #header>
          <div class="card-header">
            <span>创建新账户</span>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" size="large" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input type="password" v-model="form.password" placeholder="请输入密码" show-password size="large"/>
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input type="password" v-model="form.confirmPassword" placeholder="请再次输入密码" show-password size="large"/>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleRegister" style="width: 100%;" size="large">注 册</el-button>
          </el-form-item>
           <div class="login-link">
            <span>已有账户?</span>
            <el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElNotification } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { register as registerApi } from '@/api/auth';

const router = useRouter();
const formRef = ref<FormInstance>();
const apiError = ref(''); // 用于存储 API 返回的错误信息

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

const validatePass = (rule: any, value: any, callback: any) => {
  if (!value) {
    return callback(new Error('请输入密码'));
  }
  if (value.length < 6) {
    return callback(new Error('密码长度不能小于6位'));
  }
  if (!/^(?=.*[A-Za-z])(?=.*\d)/.test(value)) {
    return callback(new Error('密码必须包含字母和数字'));
  }
  if (form.confirmPassword) {
    formRef.value?.validateField('confirmPassword');
  }
  callback();
};

const validatePass2 = (rule: any, value: any, callback: any) => {
  if (!value) {
    return callback(new Error('请再次输入密码'));
  }
  if (value !== form.password) {
    return callback(new Error("两次输入的密码不一致!"));
  }
  callback();
};

// 动态的 API 错误验证规则
const validateApiError = (rule: any, value: any, callback: any) => {
  if (apiError.value) {
    callback(new Error(apiError.value));
  } else {
    callback();
  }
};

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateApiError, trigger: 'blur' } // 添加 API 错误验证
  ],
  password: [{ required: true, validator: validatePass, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }],
});

const handleRegister = async () => {
  if (!formRef.value) return;
  // 清除上一次的 API 错误
  apiError.value = '';
  formRef.value.validateField('username'); // 触发一次验证来清除旧消息

  try {
    await formRef.value.validate();
    await registerApi({ username: form.username, password: form.password });
    ElNotification({
      title: '成功',
      message: '注册成功！正在跳转到登录页...',
      type: 'success',
    });
    setTimeout(() => {
      router.push('/login');
    }, 1500);
  } catch (error: any) {
    // 检查是否是后端返回的错误
    if (error.response && error.response.data && error.response.data.message) {
      apiError.value = error.response.data.message;
      formRef.value.validateField('username'); // 触发验证以显示 API 错误
    } else {
      console.error('Validation or registration failed:', error);
    }
  }
};

const goToLogin = () => {
  router.push('/login');
};

const cardClicked = () => {
  console.log('卡片区域被点击了！');
};
</script>

<style scoped>
.register-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
}
.register-left {
  flex: 1;
  background: linear-gradient(135deg, #fc5c7d, #6a82fb);
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
.register-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}
.register-form-card {
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
.login-link {
  margin-top: 15px;
  text-align: center;
}
</style> 