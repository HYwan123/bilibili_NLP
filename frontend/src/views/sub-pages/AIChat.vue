<template>
  <div class="ai-chat-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><ChatDotRound /></el-icon>
        AI 智能问答
      </h1>
      <p class="page-subtitle">基于大语言模型的智能对话助手，为您解答各类问题</p>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="messages-wrapper" ref="messagesWrapper">
        <div class="messages-list">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-section">
            <div class="welcome-icon">
              <el-icon><ChatLineRound /></el-icon>
            </div>
            <h2 class="welcome-title">你好！我是 AI 助手</h2>
            <p class="welcome-desc">我可以帮你解答问题、分析数据、提供建议。试着问我点什么吧！</p>
            
            <!-- 快捷问题 -->
            <div class="quick-questions">
              <div 
                v-for="question in quickQuestions" 
                :key="question"
                class="quick-question-item"
                @click="sendQuickQuestion(question)"
              >
                <el-icon><ArrowRight /></el-icon>
                <span>{{ question }}</span>
              </div>
            </div>
          </div>

          <!-- 消息气泡 -->
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            class="message-item"
            :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'assistant' }"
          >
            <div class="message-avatar">
              <div class="avatar-icon" :class="message.role">
                <el-icon v-if="message.role === 'user'"><User /></el-icon>
                <el-icon v-else><Cpu /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="message-bubble">
                <div v-if="message.isLoading" class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <div v-else class="message-text" v-html="formatMessage(message.content)"></div>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入您的问题，按 Enter 发送，Shift + Enter 换行..."
            resize="none"
            :disabled="loading"
            @keydown.enter.prevent="handleEnter"
          />
          <div class="input-actions">
            <div class="input-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>Enter 发送 · Shift + Enter 换行</span>
            </div>
            <el-button
              type="primary"
              :loading="loading"
              :disabled="!inputMessage.trim() || loading"
              @click="sendMessage"
            >
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ChatDotRound, 
  ChatLineRound, 
  User, 
  Cpu, 
  Promotion, 
  ArrowRight,
  InfoFilled
} from '@element-plus/icons-vue'
import { chatWithAI } from '@/api/bilibili'

// 消息类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  isLoading?: boolean
}

// 响应式数据
const messages = ref<Message[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesWrapper = ref<HTMLElement | null>(null)

// 快捷问题
const quickQuestions = [
  '如何分析B站视频评论？',
  '怎样获取用户画像数据？',
  '内容推荐功能如何使用？',
  '系统支持哪些数据分析功能？'
]

// 发送快捷问题
const sendQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

// 处理 Enter 键
const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    sendMessage()
  }
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 格式化消息内容（支持简单的换行和代码块）
const formatMessage = (content: string) => {
  // 转义 HTML 特殊字符
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // 处理代码块
  formatted = formatted.replace(
    /```(\w+)?\n([\s\S]*?)```/g,
    '<pre class="code-block"><code>$2</code></pre>'
  )
  
  // 处理行内代码
  formatted = formatted.replace(
    /`([^`]+)`/g,
    '<code class="inline-code">$1</code>'
  )
  
  // 处理换行
  formatted = formatted.replace(/\n/g, '<br>')
  
  return formatted
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesWrapper.value) {
    messagesWrapper.value.scrollTop = messagesWrapper.value.scrollHeight
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  // 添加用户消息
  const userMessage: Message = {
    role: 'user',
    content: message,
    timestamp: Date.now()
  }
  messages.value.push(userMessage)
  inputMessage.value = ''
  
  // 添加加载中的 AI 消息
  const aiMessage: Message = {
    role: 'assistant',
    content: '',
    timestamp: Date.now(),
    isLoading: true
  }
  messages.value.push(aiMessage)
  
  loading.value = true
  await scrollToBottom()

  try {
    // 调用 API
    const chatMessages = messages.value
      .filter(m => !m.isLoading)
      .map(m => ({ role: m.role, content: m.content }))
    
    const response: any = await chatWithAI(chatMessages)
    
    // 更新 AI 消息
    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.isLoading = false
    
    if (response.code === 200 && response.data) {
      lastMessage.content = response.data.content || '抱歉，我暂时无法回答这个问题。'
    } else {
      lastMessage.content = '抱歉，请求失败，请稍后重试。'
    }
  } catch (error) {
    // 更新错误消息
    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.isLoading = false
    lastMessage.content = '抱歉，网络连接失败，请检查网络后重试。'
    ElMessage.error('发送消息失败，请稍后重试')
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

// 页面加载时聚焦输入框
onMounted(() => {
  // 可以在这里添加一些初始化逻辑
})
</script>

<style scoped>
.ai-chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: var(--bg-light);
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 8px 0;
}

.page-title .el-icon {
  color: var(--primary-color);
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.messages-list {
  max-width: 900px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: white;
  font-size: 36px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.welcome-desc {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0 0 40px 0;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 500px;
  margin: 0 auto;
}

.quick-question-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  background: var(--bg-light);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  border: 1px solid transparent;
}

.quick-question-item:hover {
  background: white;
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(6, 95, 70, 0.1);
  transform: translateX(4px);
}

.quick-question-item .el-icon {
  color: var(--primary-color);
  font-size: 16px;
}

.quick-question-item span {
  font-size: 14px;
  color: var(--text-primary);
}

/* 消息样式 */
.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.avatar-icon.user {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
}

.avatar-icon.assistant {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message .message-bubble {
  background: var(--bg-light);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
  text-align: right;
}

.ai-message .message-time {
  text-align: left;
}

/* 加载动画 */
.loading-dots {
  display: flex;
  gap: 6px;
  padding: 8px 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 输入区域 */
.input-section {
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.input-wrapper :deep(.el-textarea__inner) {
  border-radius: 12px;
  border-color: #e5e7eb;
  padding: 12px 16px;
  font-size: 14px;
  resize: none;
}

.input-wrapper :deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.input-hint .el-icon {
  font-size: 14px;
}

/* 代码块样式 */
.message-text :deep(.code-block) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.message-text :deep(.inline-code) {
  background: rgba(6, 95, 70, 0.1);
  color: var(--primary-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

/* 滚动条样式 */
.messages-wrapper::-webkit-scrollbar {
  width: 6px;
}

.messages-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.messages-wrapper::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.messages-wrapper::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .ai-chat-page {
    padding: 12px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .welcome-title {
    font-size: 22px;
  }
  
  .quick-questions {
    padding: 0 10px;
  }
}
</style>