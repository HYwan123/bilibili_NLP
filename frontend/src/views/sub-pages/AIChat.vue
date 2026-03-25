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
                <!-- 流式输出光标 -->
                <span v-if="message.isStreaming" class="streaming-cursor">▊</span>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>

          <!-- 快捷问题 - 仅在只有初始消息或清空后显示 -->
          <div v-if="messages.length <= 1 && !loading" class="quick-questions-container">
            <p class="quick-questions-title">您可以试着这样问我：</p>
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
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <!-- 系统提示词设置 -->
        <div class="system-prompt-section" v-if="showSystemPrompt">
          <div class="system-prompt-header">
            <el-icon><Setting /></el-icon>
            <span>系统提示词</span>
            <el-button type="primary" link size="small" @click="saveSystemPrompt">保存</el-button>
          </div>
          <el-input
            v-model="systemPrompt"
            type="textarea"
            :rows="2"
            placeholder="设置AI助手的系统提示词，用于定义AI的角色和行为..."
            resize="none"
          />
        </div>
        
        <div class="input-wrapper">
          <div class="input-toolbar">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="showSystemPrompt = !showSystemPrompt"
            >
              <el-icon><Setting /></el-icon>
              {{ showSystemPrompt ? '收起设置' : '系统提示词' }}
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="clearMessages"
              v-if="messages.length > 0"
            >
              <el-icon><Delete /></el-icon>
              清空对话
            </el-button>
          </div>
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入您的问题，按 Enter 发送，Shift + Enter 换行..."
            resize="none"
            :disabled="loading"
            @keydown.enter.prevent="(e: KeyboardEvent) => handleEnter(e)"
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
import MarkdownIt from 'markdown-it'
import { 
  ChatDotRound, 
  ChatLineRound, 
  User, 
  Cpu, 
  Promotion, 
  ArrowRight,
  InfoFilled,
  Setting,
  Delete
} from '@element-plus/icons-vue'
import { chatWithAIStream } from '@/api/bilibili'

// 初始化 markdown-it
const md = new MarkdownIt({
  html: false, // 禁用HTML标签，防止XSS
  breaks: true, // 转换换行符为<br>
  linkify: true // 自动转换URL为链接
})

// 消息类型定义
interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  isLoading?: boolean
  isStreaming?: boolean
}

// 响应式数据
const messages = ref<Message[]>([
  {
    role: 'assistant',
    content: '你好！我是 **B 站视频分析系统** 的 AI 助手。很高兴为你服务！\n\n我可以帮你：\n- 分析视频评论的情感和关键词\n- 解读 B 站用户画像和互动偏好\n- 提供视频内容推荐和运营建议\n- 洞察弹幕趋势和社区热点\n\n你可以直接问我问题，或者点击下方的快捷问题。',
    timestamp: Date.now()
  }
])
const inputMessage = ref('')
const loading = ref(false)
const messagesWrapper = ref<HTMLElement | null>(null)
const showSystemPrompt = ref(false)
const systemPrompt = ref('# 角色\n你是一个专门针对 B 站（Bilibili）数据分析的资深 NLP 专家助手。你拥有深厚的内容理解、用户画像构建、情感分析以及推荐系统领域的知识。\n\n# 交互准则\n1. 专业性：使用行业术语并确保易懂。\n2. 场景化建议：结合 B 站社区氛围给出建议。\n3. 简洁高效：回答控制在 300 字以内。\n4. 准确性：基于已知功能回答。')

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
  e.preventDefault()
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 格式化消息内容（使用markdown-it渲染）
const formatMessage = (content: string) => {
  // 使用 markdown-it 渲染 markdown
  return md.render(content)
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesWrapper.value) {
    messagesWrapper.value.scrollTop = messagesWrapper.value.scrollHeight
  }
}

// 保存系统提示词
const saveSystemPrompt = () => {
  ElMessage.success('系统提示词已保存')
  showSystemPrompt.value = false
}

// 清空消息
const clearMessages = () => {
  messages.value = [
    {
      role: 'assistant',
      content: '对话已重置。你好！我是 **B 站视频分析系统** 的 AI 助手。有什么我可以帮你的吗？',
      timestamp: Date.now()
    }
  ]
  ElMessage.success('对话已清空')
}

// 发送消息（流式输出）
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
  
  // 添加流式输出的 AI 消息
  const aiMessage: Message = {
    role: 'assistant',
    content: '',
    timestamp: Date.now(),
    isLoading: true, // 初始显示加载中
    isStreaming: true
  }
  messages.value.push(aiMessage)
  
  loading.value = true
  await scrollToBottom()

  try {
    // 准备对话消息 - 包含之前的完整对话和刚发送的用户消息
    // 排除掉当前正在等待回复的这个AI消息占位符
    const chatMessages = messages.value
      .filter(m => m.role === 'user' || (m.role === 'assistant' && !m.isLoading && !m.isStreaming))
      .map(m => ({ role: m.role, content: m.content }))
    
    // 获取当前AI消息引用
    const lastMessage = messages.value[messages.value.length - 1]
    
    // 调用流式API
    await chatWithAIStream(
      chatMessages,
      (content: string, done: boolean) => {
        // 只要收到任何回调，哪怕是空字符串或完成信号，都应该处理加载状态
        if (lastMessage.isLoading) {
          lastMessage.isLoading = false
        }
        
        if (content !== undefined && content !== null) {
          lastMessage.content += content
        }
        
        if (done) {
          lastMessage.isStreaming = false
        }
        // 每次接收到内容都滚动到底部
        scrollToBottom()
      },
      'glm-4.7-flash',  // 使用GLM模型
      systemPrompt.value || undefined
    )
    
  } catch (error) {
    // 发生错误时，确保取消加载状态并显示错误信息
    const lastMessage = messages.value[messages.value.length - 1]
    lastMessage.isLoading = false
    lastMessage.isStreaming = false
    lastMessage.content = '抱歉，对话请求失败。请检查网络连接或稍后重试。'
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
  padding: 24px;
  background: var(--bg-secondary);
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 6px 0;
  letter-spacing: -0.02em;
}

.page-title .el-icon {
  color: var(--primary-color);
  font-size: 28px;
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  border: 1px solid var(--border-light);
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

/* 快捷问题区域 */
.quick-questions-container {
  margin: 20px 0 20px 48px;
  animation: fadeIn 0.5s ease 0.3s both;
}

.quick-questions-title {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 12px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-question-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--border-light);
}

.quick-question-item:hover {
  background: var(--bg-card);
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.quick-question-item .el-icon {
  color: var(--primary-color);
  font-size: 14px;
}

.quick-question-item span {
  font-size: 14px;
  color: var(--text-primary);
}

/* 消息样式 - Apple 风格 */
.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
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
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.avatar-icon.user {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.avatar-icon.assistant {
  background: var(--primary-color);
  color: white;
}

.message-content {
  max-width: 75%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.5;
}

.user-message .message-bubble {
  background: var(--primary-color);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message .message-bubble {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 4px;
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

/* 输入区域 - Apple 风格 */
.input-section {
  padding: 20px 24px;
  background: var(--bg-card);
  border-top: 1px solid var(--separator-color);
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

/* 系统提示词区域 */
.system-prompt-section {
  max-width: 900px;
  margin: 0 auto 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.system-prompt-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.system-prompt-header .el-button {
  margin-left: auto;
}

/* 输入工具栏 */
.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

/* 流式输出光标 */
.streaming-cursor {
  display: inline-block;
  animation: blink 1s infinite;
  color: var(--primary-color);
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

.input-wrapper :deep(.el-textarea__inner) {
  border-radius: 12px;
  border-color: var(--separator-color);
  padding: 14px 18px;
  font-size: 15px;
  resize: none;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.input-wrapper :deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

.input-wrapper :deep(.el-textarea__inner::placeholder) {
  color: var(--text-tertiary);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
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

/* 代码块样式 - Apple 风格 */
.message-text :deep(.code-block) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  padding: 16px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 8px 0;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
  border: 1px solid var(--border-light);
}

.message-text :deep(.inline-code) {
  background: var(--bg-tertiary);
  color: var(--primary-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  border: 1px solid var(--border-light);
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3),
.message-text :deep(h4),
.message-text :deep(h5),
.message-text :deep(h6) {
  margin: 12px 0 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.message-text :deep(h1) { font-size: 1.3em; }
.message-text :deep(h2) { font-size: 1.2em; }
.message-text :deep(h3) { font-size: 1.1em; }
.message-text :deep(h4), .message-text :deep(h5), .message-text :deep(h6) { font-size: 1em; }

.message-text :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.message-text :deep(ul), .message-text :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 4px 0;
}

.message-text :deep(strong) {
  font-weight: 600;
  color: var(--text-primary);
}

.message-text :deep(em) {
  font-style: italic;
}

.message-text :deep(a) {
  color: var(--primary-color);
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

.message-text :deep(blockquote) {
  border-left: 3px solid var(--primary-color);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.message-text :deep(pre) {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
  overflow-x: auto;
}

.message-text :deep(pre code) {
  background: transparent;
  padding: 0;
  border: none;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.message-text :deep(code) {
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  border: 1px solid var(--border-light);
}

.message-text :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-light);
  margin: 12px 0;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.message-text :deep(th), .message-text :deep(td) {
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  text-align: left;
}

.message-text :deep(th) {
  background: var(--bg-tertiary);
  font-weight: 600;
}

/* 滚动条样式 */
.messages-wrapper::-webkit-scrollbar {
  width: 6px;
}

.messages-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.messages-wrapper::-webkit-scrollbar-thumb {
  background: var(--border-light);
  border-radius: 3px;
}

.messages-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .message-text :deep(.code-block) {
    background: var(--bg-dark);
    border-color: var(--border-light);
  }

  .message-text :deep(.inline-code) {
    background: var(--bg-tertiary);
    border-color: var(--border-light);
  }

  .user-message .message-bubble {
    background: var(--primary-color);
  }

  .ai-message .message-bubble {
    background: var(--bg-secondary);
  }

  .system-prompt-section {
    background: var(--bg-secondary);
    border-color: var(--border-light);
  }

  .input-wrapper :deep(.el-textarea__inner) {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-color: var(--border-light);
  }
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
