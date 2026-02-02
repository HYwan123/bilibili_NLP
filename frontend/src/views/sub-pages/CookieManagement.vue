<template>
  <div class="cookie-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>Cookie 管理</h2>
          <el-button type="primary" @click="fetchCookies">刷新 Cookie 信息</el-button>
        </div>
      </template>

      <!-- Cookie 列表 -->
      <div class="cookie-list">
        <el-card v-for="cookieType in cookieTypes" :key="cookieType.key" class="cookie-item">
          <template #header>
            <div class="cookie-header">
              <h3>{{ cookieType.name }}</h3>
              <el-tag :type="cookieStatus[cookieType.key] ? 'success' : 'danger'">
                {{ cookieStatus[cookieType.key] ? '有效' : '无效' }}
              </el-tag>
            </div>
          </template>

          <div class="cookie-content">
            <el-input
              v-model="cookieValues[cookieType.key]"
              type="textarea"
              :rows="4"
              :placeholder="`请输入 ${cookieType.name}`"
              @input="handleCookieInput(cookieType.key, $event)"
            />
            
            <div class="cookie-actions">
              <el-button 
                type="primary" 
                :loading="validating[cookieType.key]"
                @click="validateCookie(cookieType.key)"
              >
                {{ validating[cookieType.key] ? '验证中...' : '验证 Cookie' }}
              </el-button>
              <el-button 
                type="success" 
                :disabled="!cookieValues[cookieType.key] || !cookieStatus[cookieType.key]"
                @click="updateCookie(cookieType.key)"
              >
                保存 Cookie
              </el-button>
            </div>

            <div v-if="validationResults[cookieType.key]" class="validation-result">
              <el-alert
                :title="validationResults[cookieType.key].success ? '验证成功' : '验证失败'"
                :type="validationResults[cookieType.key].success ? 'success' : 'error'"
                :description="validationResults[cookieType.key].message"
                show-icon
                :closable="false"
              />
            </div>
          </div>
        </el-card>
      </div>

      <!-- 批量操作 -->
      <div class="batch-actions">
        <el-button type="primary" @click="validateAllCookies" :loading="validatingAll">
          批量验证所有 Cookie
        </el-button>
        <el-button type="success" @click="updateAllCookies" :disabled="!allCookiesValid">
          批量保存所有 Cookie
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCookies, validateCookie as validateCookieApi, updateCookie as updateCookieApi } from '@/api/bilibili'

interface CookieData {
  [key: string]: string
}

interface ValidationResult {
  success: boolean
  message: string
}

// 定义3个cookie类型
const cookieTypes = [
  { key: 'comment_cookie', name: '评论爬虫 Cookie' },
  { key: 'video_cookie', name: '视频爬虫 Cookie' },
  { key: 'user_cookie', name: '用户爬虫 Cookie' }
]

const cookies = ref<CookieData>({})
const cookieValues = ref<CookieData>({})
const cookieStatus = ref<{ [key: string]: boolean }>({})
const validating = ref<{ [key: string]: boolean }>({})
const validatingAll = ref(false)
const validationResults = ref<{ [key: string]: ValidationResult }>({})
const message_ = ref('')

// 计算属性：检查所有cookie是否都有效
const allCookiesValid = computed(() => {
  return Object.values(cookieStatus.value).every(status => status)
})

// 获取cookie信息
const fetchCookies = async () => {
  try {
    const response = await getCookies()
    if (response.data.code === 200) {
      cookies.value = response.data.data
      // 初始化cookie值
      Object.keys(cookies.value).forEach(key => {
        cookieValues.value[key] = cookies.value[key]
      })
      ElMessage.success('Cookie 信息获取成功')
    } else {
      ElMessage.error('获取 Cookie 信息失败')
    }
  } catch (error) {
    console.error('获取 Cookie 失败:', error)
    ElMessage.error('获取 Cookie 失败')
  }
}

// 处理cookie输入
const handleCookieInput = (key: string, value: string) => {
  cookieValues.value[key] = value
  // 输入时重置验证状态
  cookieStatus.value[key] = false
  validationResults.value[key] = { success: false, message: '' }
}

// 验证单个cookie
const validateCookie = async (key: string) => {
  const cookieValue = cookieValues.value[key]
  if (!cookieValue) {
    ElMessage.warning('请先输入 Cookie')
    return
  }

  validating.value[key] = true
  validationResults.value[key] = { success: false, message: '验证中...' }

  try {
    // 调用后端API进行真实cookie验证
    const response = await validateCookieApi(key, cookieValue)
    const isValid = response.data.data.valid
    
    cookieStatus.value[key] = isValid
    validationResults.value[key] = {
      success: isValid,
      message: isValid ? 'Cookie 验证成功，可以正常使用' : 'Cookie 验证失败，请检查格式或重新获取'
    }

    if (isValid) {
      ElMessage.success(`${cookieTypes.find(t => t.key === key)?.name} 验证成功`)
    } else {
      ElMessage.error(`${cookieTypes.find(t => t.key === key)?.name} 验证失败`)
    }
  } catch (error: any) {
    console.error('Cookie 验证失败:', error)
    cookieStatus.value[key] = false
    const errorMessage = error.response?.data?.message || '验证过程中发生错误'
    validationResults.value[key] = {
      success: false,
      message: errorMessage
    }
    ElMessage.error(`${cookieTypes.find(t => t.key === key)?.name} 验证失败: ${errorMessage}`)
  } finally {
    validating.value[key] = false
  }
}

// 更新单个cookie - 使用ElMessageBox.prompt，参照CommentQuery.vue
const updateCookie = (key: string) => {
  const cookieTypeName = cookieTypes.find(t => t.key === key)?.name || key
  
  ElMessageBox.prompt(`请输入新的${cookieTypeName}`, '修改 Cookie', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputErrorMessage: 'Cookie格式错误',
    inputValue: cookieValues.value[key] || ''
  })
    .then(async ({ value }) => {
      try {
        await updateCookieApi(key, value)
        ElMessage.success(`${cookieTypeName} 更新成功`)
        cookieValues.value[key] = value
        message_.value = `${cookieTypeName} 更新成功`
        // 刷新cookie信息
        await fetchCookies()
      } catch (error) {
        console.error('更新 Cookie 失败:', error)
        ElMessage.error('更新 Cookie 失败')
      }
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '取消修改',
      })
    })
}

// 批量验证所有cookie
const validateAllCookies = async () => {
  validatingAll.value = true
  const keys = Object.keys(cookieValues.value)
  
  for (const key of keys) {
    if (cookieValues.value[key]) {
      await validateCookie(key)
    }
  }
  
  validatingAll.value = false
  ElMessage.success('批量验证完成')
}

// 批量更新所有cookie
const updateAllCookies = async () => {
  if (!allCookiesValid.value) {
    ElMessage.warning('请确保所有 Cookie 都验证通过')
    return
  }

  try {
    for (const key of Object.keys(cookieValues.value)) {
      if (cookieValues.value[key] && cookieStatus.value[key]) {
        await updateCookieApi(key, cookieValues.value[key])
      }
    }
    ElMessage.success('所有 Cookie 更新成功')
    await fetchCookies()
  } catch (error) {
    console.error('批量更新 Cookie 失败:', error)
    ElMessage.error('批量更新 Cookie 失败')
  }
}

// 初始化
onMounted(() => {
  fetchCookies()
})
</script>

<style scoped>
.cookie-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cookie-list {
  display: grid;
  gap: 20px;
  margin-bottom: 20px;
}

.cookie-item {
  margin-bottom: 16px;
}

.cookie-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cookie-content {
  padding: 16px 0;
}

.cookie-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.validation-result {
  margin-top: 16px;
}

.batch-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

:deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}
</style>
