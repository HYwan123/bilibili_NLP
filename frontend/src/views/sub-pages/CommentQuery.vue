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

    <!-- Bilibili QR Code Login Card -->
    <el-card class="qr-login-container">
      <template #header>
        <div class="card-header">
          <span>Bilibili 登录</span>
        </div>
      </template>

      <div class="qr-login-content">
        <el-button
          v-if="!qrcodeUrl && !pollingStatus"
          type="success"
          @click="startQRCodeLogin"
          :loading="generatingQRCode"
        >
          {{ generatingQRCode ? '生成中...' : '使用二维码登录Bilibili' }}
        </el-button>

        <div v-if="qrcodeUrl" class="qrcode-display">
          <div class="qrcode-image">
            <el-image
              :src="`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrcodeUrl)}`"
              :preview-src-list="[`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrcodeUrl)}`]"
              :preview-teleported="true"
              style="width: 200px; height: 200px;"
            />
          </div>
          <p>请使用 Bilibili APP 扫码登录</p>

          <el-button
            v-if="pollingStatus === 'pending'"
            type="primary"
            @click="startPolling"
            :loading="polling"
          >
            {{ polling ? '登录中...' : '开始检查登录状态' }}
          </el-button>

          <div v-if="pollingStatus === 'checking'" class="polling-status">
            <el-tag type="warning" effect="dark">等待扫码中...</el-tag>
          </div>

          <div v-if="pollingStatus === 'scanned'" class="polling-status">
            <el-tag type="warning" effect="dark">已扫码，请在手机上确认登录</el-tag>
          </div>

          <div v-if="pollingStatus === 'success'" class="polling-status">
            <el-tag type="success" effect="dark">登录成功！</el-tag>
          </div>

          <div v-if="pollingStatus === 'failed'" class="polling-status">
            <el-tag type="danger" effect="dark">登录失败或已过期</el-tag>
          </div>

          <el-button
            type="info"
            @click="resetQRCodeLogin"
            size="small"
          >
            重新开始
          </el-button>
        </div>
      </div>
    </el-card>



  <!-- Cookie Modification Dialog -->
  <el-dialog
    v-model="dialogVisible"
    title="修改Cookie"
    width="500px"
    @close="cancelChangeCookie"
  >
    <el-form>
      <el-form-item label="Cookie值">
        <el-input
          v-model="newCookieValue"
          type="textarea"
          :rows="4"
          placeholder="请输入新的Cookie值"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="cancelChangeCookie">取消</el-button>
        <el-button type="primary" @click="confirmChangeCookie">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { changeUserCookie, getComments, getCookies, generateBilibiliQRCode, pollBilibiliLogin } from '@/api/bilibili';
import { ElMessage, ElMessageBox } from 'element-plus';

const bv = ref('');
const comments = ref([]);
const cookie_user = ref('');
const viewUserCookie = ref(0)
const message_ = ref('')

// QR Code Login State
const qrcodeUrl = ref('')
const generatingQRCode = ref(false)
const polling = ref(false)
const pollingStatus = ref('') // 'pending', 'checking', 'scanned', 'success', 'failed'
const pollingInterval = ref<number | null>(null)

const getCookie = async () => {
  try {
    const cookie_all = await getCookies();
    cookie_user.value = cookie_all.data.cookie || "暂无cookie";

  } catch (error) {
    console.error('Failed to fetch cookies:', error);
    ElMessage.error('获取Cookie失败');
    cookie_user.value = "获取Cookie失败";
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

// Cookie modification dialog state
const dialogVisible = ref(false);
const newCookieValue = ref('');

const open = () => {
  dialogVisible.value = true;
  newCookieValue.value = '';
};

const confirmChangeCookie = async () => {
  if (!newCookieValue.value.trim()) {
    ElMessage.error('请输入Cookie值');
    return;
  }

  try {
    const result = await changeUserCookie(newCookieValue.value);
    message_.value = result.message || 'Cookie修改成功';
    ElMessage.success('Cookie修改成功');

    // Refresh the cookie display
    await getCookie();

    // Close dialog
    dialogVisible.value = false;
    newCookieValue.value = '';
  } catch (error) {
    console.error('Failed to change cookie:', error);
    ElMessage.error('修改Cookie失败');
  }
};

const cancelChangeCookie = () => {
  dialogVisible.value = false;
  newCookieValue.value = '';
};

// Bilibili QR Code Login Methods
const startQRCodeLogin = async () => {
  generatingQRCode.value = true;
  pollingStatus.value = '';
  qrcodeUrl.value = '';

  try {
    const response = await generateBilibiliQRCode();
    if (response.code === 200) {
      qrcodeUrl.value = response.data.url;
      pollingStatus.value = 'pending';
      ElMessage.success('二维码生成成功，请扫码登录');
    } else {
      ElMessage.error(response.message || '二维码生成失败');
    }
  } catch (error) {
    console.error('Failed to generate QR code:', error);
    ElMessage.error('生成二维码失败');
  } finally {
    generatingQRCode.value = false;
  }
};

const startPolling = async () => {
  polling.value = true;
  pollingStatus.value = 'checking';

  // Start periodic polling
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
  }

  // Initial check
  await pollLoginStatus();

  // Set up interval to check every 2 seconds
  pollingInterval.value = window.setInterval(async () => {
    await pollLoginStatus();
  }, 2000);
};

const pollLoginStatus = async () => {
  try {
    const response = await pollBilibiliLogin();

    if (response.code === 200) {
      const loginData = response.data;

      // Check login status based on Bilibili's response codes
      // 0 = success, 86038 = expired, 86101 = not scanned yet, 86090 = scanned but not confirmed
      if (loginData.code === 0) {
        // Login successful
        clearInterval(pollingInterval.value as number);
        pollingInterval.value = null;
        polling.value = false;
        pollingStatus.value = 'success';

        // Refresh cookies to show updated login status
        await getCookie();

        ElMessage.success('Bilibili 登录成功！');
      } else if (loginData.code === 86101) {
        // Not scanned yet
        pollingStatus.value = 'checking';
      } else if (loginData.code === 86090) {
        // Scanned but not confirmed
        pollingStatus.value = 'scanned';
      } else if (loginData.code === 86038) {
        // Expired QR code
        clearInterval(pollingInterval.value as number);
        pollingInterval.value = null;
        polling.value = false;
        pollingStatus.value = 'failed';
        ElMessage.warning('二维码已过期，请重新生成');
      } else {
        // Other error
        clearInterval(pollingInterval.value as number);
        pollingInterval.value = null;
        polling.value = false;
        pollingStatus.value = 'failed';
        ElMessage.warning('登录状态检查出现问题，请重试');
      }
    } else {
      // Handle API error
      clearInterval(pollingInterval.value as number);
      pollingInterval.value = null;
      polling.value = false;
      pollingStatus.value = 'failed';
      ElMessage.error(response.message || '登录状态检查失败');
    }
  } catch (error) {
    console.error('Failed to poll login status:', error);
    clearInterval(pollingInterval.value as number);
    pollingInterval.value = null;
    polling.value = false;
    pollingStatus.value = 'failed';
    ElMessage.error('登录状态检查失败');
  }
};

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





</script>

<style scoped>
.page-container {
  height: 100%;
}
.card-header {
  font-size: 18px;
  font-weight: bold;
}

.qr-login-container {
  margin-bottom: 20px;
}

.qr-login-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.qrcode-display {
  text-align: center;
  padding: 20px;
}

.qrcode-image {
  margin-bottom: 20px;
}

.polling-status {
  margin: 15px 0;
}

.qr-login-container .el-card__body {
  padding: 20px;
}
</style> 