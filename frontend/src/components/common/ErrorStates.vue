<template>
  <div class="error-states">
    <!-- 网络错误 -->
    <div v-if="type === 'network'" class="error-container network-error">
      <div class="error-icon">
        <el-icon><Connection /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">网络连接异常</h3>
        <p class="error-message">{{ message || '请检查您的网络连接后重试' }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleRetry" v-if="showRetry">
            <el-icon><Refresh /></el-icon>
            重新连接
          </el-button>
        </div>
      </div>
    </div>

    <!-- 服务器错误 -->
    <div v-else-if="type === 'server'" class="error-container server-error">
      <div class="error-icon">
        <el-icon><Warning /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">服务器异常</h3>
        <p class="error-message">{{ message || '服务器暂时无法响应，请稍后重试' }}</p>
        <div class="error-details" v-if="details">
          <details>
            <summary>错误详情</summary>
            <pre>{{ details }}</pre>
          </details>
        </div>
        <div class="error-actions">
          <el-button type="primary" @click="handleRetry" v-if="showRetry">
            <el-icon><Refresh /></el-icon>
            重试
          </el-button>
          <el-button @click="handleReport" v-if="showReport">
            <el-icon><ChatDotSquare /></el-icon>
            反馈问题
          </el-button>
        </div>
      </div>
    </div>

    <!-- 权限错误 -->
    <div v-else-if="type === 'permission'" class="error-container permission-error">
      <div class="error-icon">
        <el-icon><Lock /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">权限不足</h3>
        <p class="error-message">{{ message || '您没有权限访问此内容' }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleLogin" v-if="showLogin">
            <el-icon><User /></el-icon>
            登录账号
          </el-button>
          <el-button @click="handleBack" v-if="showBack">
            <el-icon><Back /></el-icon>
            返回首页
          </el-button>
        </div>
      </div>
    </div>

    <!-- 数据不存在 -->
    <div v-else-if="type === 'notfound'" class="error-container notfound-error">
      <div class="error-icon">
        <el-icon><DocumentDelete /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">数据不存在</h3>
        <p class="error-message">{{ message || '请求的数据不存在或已被删除' }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleBack" v-if="showBack">
            <el-icon><Back /></el-icon>
            返回
          </el-button>
          <el-button @click="handleRetry" v-if="showRetry">
            <el-icon><Refresh /></el-icon>
            重新查找
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空数据状态 -->
    <div v-else-if="type === 'empty'" class="error-container empty-state">
      <div class="error-icon">
        <el-icon><Box /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">暂无数据</h3>
        <p class="error-message">{{ message || '当前没有相关数据' }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleCreate" v-if="showCreate">
            <el-icon><Plus /></el-icon>
            {{ createText || '创建数据' }}
          </el-button>
          <el-button @click="handleRefresh" v-if="showRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </div>

    <!-- 超时错误 -->
    <div v-else-if="type === 'timeout'" class="error-container timeout-error">
      <div class="error-icon">
        <el-icon><Clock /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">请求超时</h3>
        <p class="error-message">{{ message || '请求处理时间过长，请重试或联系客服' }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleRetry" v-if="showRetry">
            <el-icon><Refresh /></el-icon>
            重试
          </el-button>
        </div>
      </div>
    </div>

    <!-- 维护中 -->
    <div v-else-if="type === 'maintenance'" class="error-container maintenance-error">
      <div class="error-icon">
        <el-icon><Tools /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">系统维护中</h3>
        <p class="error-message">{{ message || '系统正在升级维护，预计很快恢复' }}</p>
        <div class="maintenance-info" v-if="maintenanceTime">
          <p class="maintenance-time">预计恢复时间：{{ maintenanceTime }}</p>
        </div>
        <div class="error-actions">
          <el-button @click="handleRefresh" v-if="showRefresh">
            <el-icon><Refresh /></el-icon>
            检查状态
          </el-button>
        </div>
      </div>
    </div>

    <!-- 通用错误 -->
    <div v-else class="error-container generic-error">
      <div class="error-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>
      <div class="error-content">
        <h3 class="error-title">{{ title || '出现错误' }}</h3>
        <p class="error-message">{{ message || '发生了未知错误，请重试' }}</p>
        <div class="error-actions">
          <el-button type="primary" @click="handleRetry" v-if="showRetry">
            <el-icon><Refresh /></el-icon>
            重试
          </el-button>
          <el-button @click="handleBack" v-if="showBack">
            <el-icon><Back /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  Connection, 
  Warning, 
  Lock, 
  DocumentDelete, 
  Box, 
  Clock, 
  Tools, 
  WarningFilled,
  Refresh,
  ChatDotSquare,
  User,
  Back,
  Plus
} from '@element-plus/icons-vue';

interface Props {
  type?: 'network' | 'server' | 'permission' | 'notfound' | 'empty' | 'timeout' | 'maintenance' | 'generic';
  title?: string;
  message?: string;
  details?: string;
  maintenanceTime?: string;
  createText?: string;
  showRetry?: boolean;
  showReport?: boolean;
  showLogin?: boolean;
  showBack?: boolean;
  showCreate?: boolean;
  showRefresh?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'generic',
  title: '',
  message: '',
  details: '',
  maintenanceTime: '',
  createText: '',
  showRetry: true,
  showReport: false,
  showLogin: false,
  showBack: false,
  showCreate: false,
  showRefresh: false
});

const emit = defineEmits<{
  retry: [];
  report: [];
  login: [];
  back: [];
  create: [];
  refresh: [];
}>();

const handleRetry = () => {
  emit('retry');
};

const handleReport = () => {
  emit('report');
};

const handleLogin = () => {
  emit('login');
};

const handleBack = () => {
  emit('back');
};

const handleCreate = () => {
  emit('create');
};

const handleRefresh = () => {
  emit('refresh');
};
</script>

<style scoped>
.error-states {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  padding: 40px 20px;
}

.error-container {
  text-align: center;
  max-width: 500px;
  width: 100%;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 48px 32px;
  transition: all 0.3s ease;
}

.error-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.error-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  position: relative;
}

.error-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  opacity: 0.1;
  z-index: -1;
}

/* 不同错误类型的颜色 */
.network-error .error-icon {
  color: #06b6d4;
}

.network-error .error-icon::before {
  background: #06b6d4;
}

.server-error .error-icon {
  color: #ef4444;
}

.server-error .error-icon::before {
  background: #ef4444;
}

.permission-error .error-icon {
  color: #f59e0b;
}

.permission-error .error-icon::before {
  background: #f59e0b;
}

.notfound-error .error-icon {
  color: #8b5cf6;
}

.notfound-error .error-icon::before {
  background: #8b5cf6;
}

.empty-state .error-icon {
  color: #64748b;
}

.empty-state .error-icon::before {
  background: #64748b;
}

.timeout-error .error-icon {
  color: #f97316;
}

.timeout-error .error-icon::before {
  background: #f97316;
}

.maintenance-error .error-icon {
  color: #10b981;
}

.maintenance-error .error-icon::before {
  background: #10b981;
}

.generic-error .error-icon {
  color: #6b7280;
}

.generic-error .error-icon::before {
  background: #6b7280;
}

.error-content {
  margin-bottom: 32px;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.error-message {
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
}

.error-details {
  margin-top: 16px;
  text-align: left;
}

.error-details details {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  padding: 12px;
}

.error-details summary {
  cursor: pointer;
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.error-details pre {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

.maintenance-info {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}

.maintenance-time {
  font-size: 0.9rem;
  color: #10b981;
  font-weight: 500;
  margin: 0;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.error-actions .el-button {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.error-actions .el-button:hover {
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-states {
    padding: 20px 16px;
    min-height: 250px;
  }
  
  .error-container {
    padding: 32px 24px;
  }
  
  .error-icon {
    width: 64px;
    height: 64px;
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .error-title {
    font-size: 1.3rem;
  }
  
  .error-message {
    font-size: 0.9rem;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-actions .el-button {
    width: 100%;
  }
}

/* 动画效果 */
.error-container {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
</style>
