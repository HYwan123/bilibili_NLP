<template>
  <div class="cookie-management-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <h1 class="page-title">Cookie 管理</h1>
      <p class="page-subtitle">管理B站API访问凭证，确保数据采集功能正常运行</p>
    </div>

    <!-- Cookie 状态概览 -->
    <el-row :gutter="20" class="status-overview">
      <el-col :xs="24" :sm="12" :md="8">
        <div class="status-card" :class="{ 'active': hasCookie }">
          <div class="status-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">当前状态</div>
            <div class="status-value" :class="{ 'success': hasCookie, 'warning': !hasCookie }">
              {{ hasCookie ? '已登录' : '未登录' }}
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="status-card">
          <div class="status-icon update">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">上次更新</div>
            <div class="status-value">{{ lastUpdateTime || '暂无记录' }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="status-card">
          <div class="status-icon security">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="status-info">
            <div class="status-label">安全状态</div>
            <div class="status-value">本地存储</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Cookie 管理卡片 -->
    <el-card class="management-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Key /></el-icon>
            <span>Cookie 配置</span>
          </div>
          <el-button type="primary" @click="openEditDialog" :icon="Edit">
            修改 Cookie
          </el-button>
        </div>
      </template>

      <div class="cookie-display-section">
        <div class="section-label">当前 Cookie 值</div>
        <div class="cookie-value-box" :class="{ 'empty': !cookie_user }">
          <code v-if="cookie_user" class="cookie-code">{{ cookie_user }}</code>
          <div v-else class="empty-placeholder">
            <el-icon><Warning /></el-icon>
            <span>暂无 Cookie，请通过下方二维码登录</span>
          </div>
        </div>
        
        <div class="cookie-actions-row">
          <el-button 
            type="info" 
            plain 
            @click="showCookieDetail" 
            :disabled="!cookie_user"
            :icon="View"
          >
            查看完整内容
          </el-button>
          <el-button 
            type="danger" 
            plain 
            @click="clearCookie" 
            :disabled="!cookie_user"
            :icon="Delete"
          >
            清除 Cookie
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 二维码登录区域 -->
    <el-card class="qr-login-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Grid /></el-icon>
            <span>Bilibili 扫码登录</span>
          </div>
          <el-tag v-if="pollingStatus === 'success'" type="success" effect="dark">
            <el-icon><CircleCheck /></el-icon> 登录成功
          </el-tag>
        </div>
      </template>

      <div class="qr-content">
        <!-- 初始状态：显示登录按钮 -->
        <div v-if="!qrcodeUrl && !pollingStatus" class="qr-initial">
          <div class="qr-icon-large">
            <el-icon><Cellphone /></el-icon>
          </div>
          <h3>扫码快速登录</h3>
          <p class="qr-description">
            使用 Bilibili App 扫描二维码，即可自动获取 Cookie<br>
            无需手动复制粘贴，安全又便捷
          </p>
          <el-button
            type="success"
            size="large"
            @click="startQRCodeLogin"
            :loading="generatingQRCode"
            :icon="RefreshRight"
          >
            {{ generatingQRCode ? '生成中...' : '生成登录二维码' }}
          </el-button>
        </div>

        <!-- 二维码显示状态 -->
        <div v-if="qrcodeUrl" class="qr-active">
          <div class="qr-main-area">
            <div class="qr-image-wrapper" :class="{ 'expired': pollingStatus === 'failed' }">
              <el-image
                :src="`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrcodeUrl)}`"
                style="width: 200px; height: 200px;"
                fit="contain"
              />
              <div v-if="pollingStatus === 'failed'" class="expired-overlay">
                <el-icon><CircleClose /></el-icon>
                <span>已过期</span>
              </div>
            </div>
            
            <div class="qr-status-panel">
              <!-- 状态指示器 -->
              <div class="status-steps">
                <div class="step" :class="{ 'active': pollingStatus === 'checking', 'completed': pollingStatus !== 'checking' && pollingStatus !== '' }">
                  <div class="step-icon">1</div>
                  <div class="step-text">扫描二维码</div>
                </div>
                <div class="step-line" :class="{ 'completed': pollingStatus === 'scanned' || pollingStatus === 'success' }"></div>
                <div class="step" :class="{ 'active': pollingStatus === 'scanned', 'completed': pollingStatus === 'success' }">
                  <div class="step-icon">2</div>
                  <div class="step-text">确认登录</div>
                </div>
                <div class="step-line" :class="{ 'completed': pollingStatus === 'success' }"></div>
                <div class="step" :class="{ 'active': pollingStatus === 'success' }">
                  <div class="step-icon">3</div>
                  <div class="step-text">登录成功</div>
                </div>
              </div>

              <!-- 当前状态提示 -->
              <div class="current-status">
                <el-alert
                  v-if="pollingStatus === 'checking'"
                  title="等待扫码..."
                  type="info"
                  :description="'请使用 Bilibili App 扫描左侧二维码'"
                  show-icon
                  :closable="false"
                />
                <el-alert
                  v-if="pollingStatus === 'scanned'"
                  title="扫码成功"
                  type="warning"
                  :description="'请在手机上确认登录操作'"
                  show-icon
                  :closable="false"
                />
                <el-alert
                  v-if="pollingStatus === 'success'"
                  title="登录成功！"
                  type="success"
                  :description="'Cookie 已自动保存，可以开始使用功能了'"
                  show-icon
                  :closable="false"
                />
                <el-alert
                  v-if="pollingStatus === 'failed'"
                  title="登录失败"
                  type="error"
                  :description="'二维码已过期，请重新生成'"
                  show-icon
                  :closable="false"
                />
              </div>

              <!-- 操作按钮 -->
              <div class="qr-actions">
                <el-button
                  v-if="pollingStatus === 'pending'"
                  type="primary"
                  @click="startPolling"
                  :loading="polling"
                  size="large"
                >
                  <el-icon v-if="!polling"><Check /></el-icon>
                  {{ polling ? '检查中...' : '我已扫码' }}
                </el-button>
                
                <el-button
                  v-if="pollingStatus === 'failed' || pollingStatus === 'success'"
                  type="info"
                  @click="resetQRCodeLogin"
                  :icon="RefreshRight"
                >
                  重新生成二维码
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 使用说明 -->
    <el-card class="tips-card" shadow="never">
      <template #header>
        <div class="tips-header">
          <el-icon><InfoFilled /></el-icon>
          <span>使用提示</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <div class="tip-item">
            <el-icon color="#065f46"><CircleCheck /></el-icon>
            <div class="tip-content">
              <div class="tip-title">自动获取 Cookie</div>
              <div class="tip-desc">扫码登录后会自动获取并保存 Cookie，无需手动操作</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="tip-item">
            <el-icon color="#065f46"><Lock /></el-icon>
            <div class="tip-content">
              <div class="tip-title">安全存储</div>
              <div class="tip-desc">Cookie 仅保存在本地服务器，不会上传到任何第三方</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="tip-item">
            <el-icon color="#065f46"><Timer /></el-icon>
            <div class="tip-content">
              <div class="tip-title">定期更新</div>
              <div class="tip-desc">建议定期重新登录以更新 Cookie，确保功能正常使用</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12">
          <div class="tip-item">
            <el-icon color="#065f46"><User /></el-icon>
            <div class="tip-content">
              <div class="tip-title">账号安全</div>
              <div class="tip-desc">请确保是您本人的 Bilibili 账号，避免使用他人账号登录</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 修改 Cookie 对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="手动修改 Cookie"
      width="600px"
      :close-on-click-modal="false"
      class="cookie-dialog"
    >
      <div class="dialog-content">
        <el-alert
          title="高级操作"
          type="warning"
          description="手动修改 Cookie 需要您了解 Cookie 格式。建议普通用户使用扫码登录功能。"
          show-icon
          :closable="false"
          style="margin-bottom: 16px;"
        />
        <el-form label-position="top">
          <el-form-item label="Cookie 值">
            <el-input
              v-model="newCookieValue"
              type="textarea"
              :rows="6"
              placeholder="请输入新的 Cookie 值..."
              resize="none"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmChangeCookie" :disabled="!newCookieValue.trim()">
            <el-icon><Check /></el-icon> 确认修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Cookie 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="Cookie 详情"
      width="700px"
    >
      <div class="cookie-detail-content">
        <div class="detail-section">
          <div class="detail-label">完整 Cookie 值</div>
          <pre class="cookie-full-code">{{ cookie_user }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { changeUserCookie, getCookies, generateBilibiliQRCode, pollBilibiliLogin } from '@/api/bilibili';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  User, 
  Timer, 
  Lock, 
  Key, 
  Edit, 
  View, 
  Delete,
  Warning,
  RefreshRight,
  Cellphone,
  Grid,
  CircleCheck,
  CircleClose,
  Check,
  InfoFilled
} from '@element-plus/icons-vue';

const cookie_user = ref('');
const lastUpdateTime = ref('');
const dialogVisible = ref(false);
const detailDialogVisible = ref(false);
const newCookieValue = ref('');

// QR Code Login State
const qrcodeUrl = ref('');
const generatingQRCode = ref(false);
const polling = ref(false);
const pollingStatus = ref(''); // 'pending', 'checking', 'scanned', 'success', 'failed'
const pollingInterval = ref<number | null>(null);

// 计算属性：是否有 cookie
const hasCookie = computed(() => {
  return !!cookie_user.value && cookie_user.value !== '暂无cookie' && cookie_user.value !== '获取Cookie失败';
});

// 获取 Cookie
const getCookie = async () => {
  try {
    const cookie_all = await getCookies();
    if (cookie_all.data && cookie_all.data.cookie) {
      cookie_user.value = cookie_all.data.cookie;
      lastUpdateTime.value = new Date().toLocaleString('zh-CN');
    } else {
      cookie_user.value = '';
    }
  } catch (error) {
    console.error('Failed to fetch cookies:', error);
    cookie_user.value = '';
  }
};

// 打开编辑对话框
const openEditDialog = () => {
  newCookieValue.value = cookie_user.value || '';
  dialogVisible.value = true;
};

// 显示 Cookie 详情
const showCookieDetail = () => {
  detailDialogVisible.value = true;
};

// 清除 Cookie
const clearCookie = () => {
  ElMessageBox.confirm(
    '确定要清除当前 Cookie 吗？清除后将需要重新登录',
    '确认清除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await changeUserCookie('');
      cookie_user.value = '';
      ElMessage.success('Cookie 已清除');
      await getCookie();
    } catch (error) {
      console.error('Failed to clear cookie:', error);
      ElMessage.error('清除 Cookie 失败');
    }
  }).catch(() => {
    // 取消操作
  });
};

// 确认修改 Cookie
const confirmChangeCookie = async () => {
  if (!newCookieValue.value.trim()) {
    ElMessage.error('请输入 Cookie 值');
    return;
  }

  try {
    await changeUserCookie(newCookieValue.value.trim());
    ElMessage.success('Cookie 修改成功');
    await getCookie();
    dialogVisible.value = false;
    newCookieValue.value = '';
  } catch (error) {
    console.error('Failed to change cookie:', error);
    ElMessage.error('修改 Cookie 失败');
  }
};

// 开始二维码登录
const startQRCodeLogin = async () => {
  generatingQRCode.value = true;
  pollingStatus.value = '';
  qrcodeUrl.value = '';

  try {
    const response = await generateBilibiliQRCode();
    if (response.code === 200) {
      qrcodeUrl.value = response.data.url;
      pollingStatus.value = 'pending';
      ElMessage.success('二维码生成成功');
    } else {
      ElMessage.error(response.message || '二维码生成失败');
    }
  } catch (error: any) {
    console.error('Failed to generate QR code:', error);
    ElMessage.error(error?.message || '生成二维码失败');
  } finally {
    generatingQRCode.value = false;
  }
};

// 开始轮询
const startPolling = async () => {
  polling.value = true;
  pollingStatus.value = 'checking';

  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
  }

  await pollLoginStatus();

  pollingInterval.value = window.setInterval(async () => {
    await pollLoginStatus();
  }, 2000);
};

// 轮询登录状态
const pollLoginStatus = async () => {
  try {
    const response = await pollBilibiliLogin();

    if (response.code === 200) {
      const loginData = response.data;

      if (loginData.code === 0) {
        clearInterval(pollingInterval.value as number);
        pollingInterval.value = null;
        polling.value = false;
        pollingStatus.value = 'success';
        await getCookie();
        ElMessage.success('Bilibili 登录成功！');
      } else if (loginData.code === 86101) {
        pollingStatus.value = 'checking';
      } else if (loginData.code === 86090) {
        pollingStatus.value = 'scanned';
      } else if (loginData.code === 86038) {
        clearInterval(pollingInterval.value as number);
        pollingInterval.value = null;
        polling.value = false;
        pollingStatus.value = 'failed';
        ElMessage.warning('二维码已过期，请重新生成');
      } else {
        clearInterval(pollingInterval.value as number);
        pollingInterval.value = null;
        polling.value = false;
        pollingStatus.value = 'failed';
      }
    } else {
      clearInterval(pollingInterval.value as number);
      pollingInterval.value = null;
      polling.value = false;
      pollingStatus.value = 'failed';
    }
  } catch (error) {
    console.error('Failed to poll login status:', error);
    clearInterval(pollingInterval.value as number);
    pollingInterval.value = null;
    polling.value = false;
    pollingStatus.value = 'failed';
  }
};

// 重置二维码登录
const resetQRCodeLogin = () => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
  qrcodeUrl.value = '';
  pollingStatus.value = '';
  polling.value = false;
  generatingQRCode.value = false;
};

// 初始化
onMounted(() => {
  getCookie();
});
</script>

<style scoped>
.cookie-management-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #065f46;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 状态概览卡片 */
.status-overview {
  margin-bottom: 24px;
}

.status-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.status-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.status-card.active {
  border-color: #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), #ffffff);
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.08), rgba(0, 0, 0, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #4b5563;
}

.status-icon.update {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1));
  color: #065f46;
}

.status-icon.security {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(0, 0, 0, 0.1));
  color: #10b981;
}

.status-card.active .status-icon {
  background: linear-gradient(135deg, #065f46, #047857);
  color: #ffffff;
}

.status-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.status-value {
  font-size: 16px;
  font-weight: 500;
  color: #374151;
}

.status-value.success {
  color: #059669;
}

.status-value.warning {
  color: #d97706;
}

/* 管理卡片 */
.management-card {
  margin-bottom: 24px;
  border-radius: var(--radius-lg);
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-title .el-icon {
  font-size: 16px;
  color: #065f46;
}

/* Cookie 显示区域 */
.cookie-display-section {
  padding: 8px 0;
}

.section-label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 12px;
}

.cookie-value-box {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: var(--radius-md);
  padding: 16px;
  min-height: 100px;
  word-break: break-all;
  margin-bottom: 16px;
}

.cookie-value-box.empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.cookie-code {
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #4b5563;
  background: transparent;
  margin: 0;
}

.empty-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #6b7280;
}

.empty-placeholder .el-icon {
  font-size: 32px;
}

.cookie-actions-row {
  display: flex;
  gap: 12px;
}

/* 二维码登录卡片 */
.qr-login-card {
  margin-bottom: 24px;
  border-radius: var(--radius-lg);
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.qr-content {
  padding: 16px 0;
}

/* 二维码初始状态 */
.qr-initial {
  text-align: center;
  padding: 40px 16px;
}

.qr-icon-large {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1));
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: #065f46;
}

.qr-initial h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.qr-description {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
  margin: 0 0 24px 0;
}

/* 二维码激活状态 */
.qr-active {
  padding: 20px;
}

.qr-main-area {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  justify-content: center;
  flex-wrap: wrap;
}

.qr-image-wrapper {
  position: relative;
  padding: 16px;
  background: #ffffff;
  border-radius: var(--radius-lg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #d1d5db;
}

.qr-image-wrapper.expired {
  filter: grayscale(100%);
  opacity: 0.6;
}

.expired-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  gap: 8px;
}

.expired-overlay .el-icon {
  font-size: 48px;
}

.qr-status-panel {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
}

/* 状态步骤 */
.status-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-xl);
  background: rgba(0, 0, 0, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.3s ease;
}

.step.active .step-icon {
  background: #065f46;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.step.completed .step-icon {
  background: #10b981;
  color: #ffffff;
}

.step-text {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.step.active .step-text,
.step.completed .step-text {
  color: #065f46;
  font-weight: 600;
}

.step-line {
  width: 40px;
  height: 2px;
  background: rgba(0, 0, 0, 0.15);
  margin: 0 8px;
  transition: all 0.3s ease;
}

.step-line.completed {
  background: #10b981;
}

/* 当前状态 */
.current-status {
  margin-bottom: 16px;
}

/* 二维码操作 */
.qr-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* 提示卡片 */
.tips-card {
  border-radius: var(--radius-lg);
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #065f46;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #ffffff;
  border-radius: var(--radius-md);
  margin-bottom: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(6, 95, 70, 0.03);
}

.tip-item .el-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.tip-content {
  flex: 1;
}

.tip-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.tip-desc {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.5;
}

/* 对话框样式 */
.cookie-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 16px;
  margin-right: 0;
}

.dialog-content {
  padding: 8px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Cookie 详情 */
.cookie-detail-content {
  padding: 8px 0;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 8px;
}

.cookie-full-code {
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-md);
  padding: 16px;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #4b5563;
  word-break: break-all;
  white-space: pre-wrap;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .cookie-management-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .qr-main-area {
    flex-direction: column;
    align-items: center;
  }
  
  .qr-status-panel {
    min-width: 100%;
    max-width: 100%;
  }
  
  .status-steps {
    transform: scale(0.9);
  }
  
  .tip-item {
    margin-bottom: 8px;
  }
  
  .cookie-actions-row {
    flex-direction: column;
  }
}
</style>
