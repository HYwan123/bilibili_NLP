<template>
  <div class="user-analysis-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Orange /></el-icon>
        智能用户画像分析
      </h1>
      <p class="page-subtitle">基于AI大模型，深度分析B站用户行为特征和兴趣偏好</p>
    </div>

    <!-- 步骤引导 -->
    <div class="steps-section">
      <el-steps :active="currentStep" finish-status="success" simple>
        <el-step title="输入UID">
          <template #icon>
            <el-icon><EditPen /></el-icon>
          </template>
        </el-step>
        <el-step title="获取评论">
          <template #icon>
            <el-icon><Download /></el-icon>
          </template>
        </el-step>
        <el-step title="AI分析">
          <template #icon>
            <el-icon><Cpu /></el-icon>
          </template>
        </el-step>
        <el-step title="查看结果">
          <template #icon>
            <el-icon><View /></el-icon>
          </template>
        </el-step>
      </el-steps>
    </div>

    <!-- 主操作区 -->
    <div class="main-operation">
      <el-card class="operation-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="header-title">第一步：输入用户UID</span>
            <el-tooltip content="B站用户空间URL中的数字部分" placement="top">
              <el-icon class="help-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
        </template>

        <div class="uid-input-section">
          <div class="input-wrapper">
            <el-input
              v-model="form.uid"
              placeholder="请输入B站用户UID，例如：66143532"
              size="large"
              clearable
              :disabled="loading || analyzing"
              @keyup.enter="fetchComments"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
              <template #append>
                <el-button 
                  type="primary" 
                  @click="fetchComments"
                  :loading="loading"
                  :disabled="!form.uid || loading || analyzing"
                >
                  <el-icon><Download /></el-icon>
                  获取评论
                </el-button>
              </template>
            </el-input>
          </div>

          <div class="quick-actions" v-if="!retrievedComments.length && !analysisResult">
            <span class="quick-label">快速尝试：</span>
            <el-tag 
              v-for="sample in sampleUids" 
              :key="sample"
              class="sample-tag"
              @click="form.uid = sample; fetchComments()"
              effect="light"
              type="info"
            >
              UID: {{ sample }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 获取评论后显示操作区 -->
      <transition name="fade-up">
        <div v-if="retrievedComments.length > 0" class="analysis-section">
          <!-- 评论预览卡片 -->
          <el-card class="comments-preview-card" shadow="hover">
            <template #header>
              <div class="preview-header">
                <div class="preview-title">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>已获取 {{ retrievedComments.length }} 条评论</span>
                </div>
                <div class="preview-actions">
                  <el-button 
                    type="success" 
                    @click="getSavedComments"
                    :loading="loadingSaved"
                    size="small"
                  >
                    <el-icon><Refresh /></el-icon>
                    重新获取已保存
                  </el-button>
                  <el-button 
                    @click="clearComments"
                    size="small"
                  >
                    <el-icon><Delete /></el-icon>
                    清空
                  </el-button>
                </div>
              </div>
            </template>

            <div class="comments-scroll">
              <div class="comment-timeline">
                <div 
                  v-for="(comment, idx) in displayedComments" 
                  :key="idx"
                  class="timeline-item"
                >
                  <div class="timeline-marker">
                    <div class="marker-number">{{ idx + 1 }}</div>
                    <div class="marker-line" v-if="idx !== displayedComments.length - 1"></div>
                  </div>
                  <div class="comment-box">
                    <div class="comment-text">{{ comment.comment_text }}</div>
                  </div>
                </div>
              </div>
              
              <div v-if="showMoreComments" class="show-more">
                <el-button text @click="toggleShowAll">
                  {{ showAll ? '收起' : `显示全部 ${retrievedComments.length} 条` }}
                </el-button>
              </div>
            </div>
          </el-card>

          <!-- AI分析按钮 -->
          <div class="analyze-action">
            <el-button 
              type="primary" 
              size="large"
              @click="analyzeUser"
              :loading="analyzing"
              :disabled="analyzing"
              class="analyze-btn"
            >
              <el-icon><Orange /></el-icon>
              <span v-if="analyzing">AI分析中...</span>
              <span v-else>开始AI画像分析</span>
            </el-button>
            
            <div class="config-hint">
              <el-icon><InfoFilled /></el-icon>
              <span>使用系统预设的专家级分析模型进行处理</span>
            </div>
          </div>
        </div>
      </transition>

      <!-- 消息提示 -->
      <transition name="fade">
        <div v-if="message" class="message-section">
          <el-alert 
            :title="message" 
            :type="messageType" 
            :closable="true"
            @close="message = ''"
            show-icon 
          />
        </div>
      </transition>

      <!-- 分析结果展示 -->
      <transition name="fade-up">
        <div v-if="analysisResult" class="result-section">
          <div class="result-header">
            <div class="result-title">
              <el-icon><CircleCheck /></el-icon>
              <span>分析完成</span>
            </div>
            <div class="result-meta">
              <el-tag type="success" effect="light">
                <el-icon><ChatLineRound /></el-icon>
                {{ analysisResult.comment_count }} 条评论
              </el-tag>
              <el-tag type="info" effect="light">
                <el-icon><Clock /></el-icon>
                {{ formatTime(analysisResult.timestamp) }}
              </el-tag>
            </div>
          </div>

          <!-- 结果展示卡片 -->
          <el-card class="result-card" shadow="hover">
            <template #header>
              <div class="result-card-header">
                <span class="user-info">
                  <el-icon><UserFilled /></el-icon>
                  用户 {{ analysisResult.uid }} 的画像分析
                </span>
                <div class="view-switcher">
                  <el-radio-group v-model="viewMode" size="small">
                    <el-radio-button label="markdown">
                      <el-icon><Document /></el-icon> 文本
                    </el-radio-button>
                    <el-radio-button label="mindmap">
                      <el-icon><Share /></el-icon> 导图
                    </el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>

            <div class="result-content">
              <!-- Markdown 视图 -->
              <div v-if="viewMode === 'markdown'" class="markdown-view">
                <div class="content-scroll">
                  <div v-html="md.render(analysisResult.analysis)" class="markdown-body"></div>
                </div>
              </div>

              <!-- 思维导图视图 -->
              <div v-else class="mindmap-view">
                <div class="mindmap-container">
                  <svg ref="mindmapContainer" class="mindmap-svg"></svg>
                </div>
                <div class="mindmap-hint">
                  <el-icon><InfoFilled /></el-icon>
                  <span>支持鼠标滚轮缩放、拖拽移动查看</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 保存到历史 -->
          <div class="save-action">
            <el-button type="success" @click="saveToHistory" :icon="Star">
              <el-icon><Star /></el-icon>
              保存到历史记录
            </el-button>
            <el-button @click="resetAnalysis">
              <el-icon><RefreshLeft /></el-icon>
              重新分析
            </el-button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import request from '@/utils/request';
import MarkdownIt from 'markdown-it';
import { Transformer } from 'markmap-lib';
import { Markmap } from 'markmap-view';
import { 
  Orange, EditPen, Download, Cpu, View, Setting,
  User, QuestionFilled, ChatDotRound, Refresh, Delete, Warning,
  CircleCheck, Clock, UserFilled, Document, Share, InfoFilled,
  Star, RefreshLeft, ChatLineRound
} from '@element-plus/icons-vue';

const router = useRouter();

// 状态
const form = ref({ uid: '' });
const currentStep = ref(0);
const loading = ref(false);
const loadingSaved = ref(false);
const analyzing = ref(false);
const retrievedComments = ref([]);
const analysisResult = ref(null);
const message = ref('');
const messageType = ref('info');
const viewMode = ref('markdown');
const showAll = ref(false);
const defaultCommentDisplay = 5;

// 思维导图
const mindmapContainer = ref(null);
let mm = null;
const transformer = new Transformer();

// Markdown
const md = new MarkdownIt({ html: true, breaks: true, linkify: true });

// 快速尝试UID
const sampleUids = ['66143532', '208259', '2'];

// 计算属性
const displayedComments = computed(() => {
  if (showAll.value) return retrievedComments.value;
  return retrievedComments.value.slice(0, defaultCommentDisplay);
});

const showMoreComments = computed(() => {
  return retrievedComments.value.length > defaultCommentDisplay;
});

// 方法
const fetchComments = async () => {
  const uid = parseInt(form.value.uid);
  if (!uid || uid <= 0) {
    ElMessage.error('请输入有效的用户UID');
    return;
  }

  loading.value = true;
  message.value = '';
  
  try {
    const res = await request.get(`/api/user/comments/${uid}`);
    const data = res.data;
    
    // 处理两种可能的响应格式
    let comments = [];
    let count = 0;
    
    if (Array.isArray(data)) {
      // 格式1: 直接返回数组
      comments = data;
      count = data.length;
    } else if (data && data.comments && Array.isArray(data.comments)) {
      // 格式2: { comments: [], comment_count: number }
      comments = data.comments;
      count = data.comment_count || data.comments.length;
    } else if (data && Array.isArray(data.data)) {
      // 格式3: { data: [] }
      comments = data.data;
      count = data.data.length;
    }
    
    if (comments.length > 0) {
      retrievedComments.value = comments;
      currentStep.value = 1;
      message.value = `成功获取 ${count} 条评论`;
      messageType.value = 'success';
    } else {
      message.value = '未获取到评论数据，该用户可能没有公开评论';
      messageType.value = 'warning';
    }
  } catch (error: any) {
    message.value = `获取评论失败: ${error.message || '网络错误'}`;
    messageType.value = 'error';
  } finally {
    loading.value = false;
  }
};

const getSavedComments = async () => {
  const uid = parseInt(form.value.uid);
  if (!uid || uid <= 0) {
    ElMessage.error('请输入有效的用户UID');
    return;
  }

  loadingSaved.value = true;
  try {
    const res = await request.get(`/api/user/comments/${uid}`);
    
    // 检查是否有数据
    let comments = [];
    if (Array.isArray(res.data)) {
      comments = res.data;
    } else if (res.data && Array.isArray(res.data.data)) {
      comments = res.data.data;
    }
    
    if (comments.length > 0) {
      retrievedComments.value = comments;
      currentStep.value = 1;
      message.value = `从数据库获取到 ${comments.length} 条已保存评论`;
      messageType.value = 'success';
    } else {
      // 数据库中没有，自动尝试实时获取
      message.value = '数据库中未找到，正在尝试实时获取...';
      messageType.value = 'info';
      await fetchComments();
    }
  } catch (error: any) {
    // 404错误表示数据库中没有，尝试实时获取
    if (error.response?.status === 404 || error.message?.includes('404')) {
      message.value = '数据库中未找到，正在尝试实时获取...';
      messageType.value = 'info';
      await fetchComments();
    } else {
      message.value = `获取失败: ${error.message || '网络错误'}`;
      messageType.value = 'error';
    }
  } finally {
    loadingSaved.value = false;
  }
};

const clearComments = () => {
  retrievedComments.value = [];
  analysisResult.value = null;
  currentStep.value = 0;
  destroyMindMap();
  ElMessage.success('已清空数据');
};

const toggleShowAll = () => {
  showAll.value = !showAll.value;
};

const analyzeUser = async () => {
  if (retrievedComments.value.length === 0) {
    ElMessage.warning('请先获取用户评论');
    return;
  }

  analyzing.value = true;
  currentStep.value = 2;
  
  try {
    const data = await request.post(`/api/user/analyze/${form.value.uid}`);
    
    // 处理API响应
    if (data.code === 200 || data.code === 201) {
      // 如果已经分析过，直接显示结果
      analysisResult.value = data.data || data;
      currentStep.value = 3;
      message.value = data.message === '分析过了' ? '已获取历史分析结果' : '用户画像分析成功！';
      messageType.value = 'success';
      
      // 初始化思维导图
      await nextTick();
      if (viewMode.value === 'mindmap' && analysisResult.value?.analysis) {
        initializeMindMap(analysisResult.value.analysis);
      }
    } else {
      message.value = data.message || '分析失败';
      messageType.value = 'error';
      currentStep.value = 1;
    }
  } catch (e: any) {
    message.value = e.message || '分析请求失败';
    messageType.value = 'error';
    currentStep.value = 1;
  } finally {
    analyzing.value = false;
  }
};

const initializeMindMap = async (content) => {
  if (!mindmapContainer.value) return;
  
  try {
    destroyMindMap();
    const { root } = transformer.transform(content);
    mm = Markmap.create(mindmapContainer.value, null, root);
  } catch (error) {
    console.error('思维导图初始化失败:', error);
  }
};

const destroyMindMap = () => {
  if (mm) {
    try {
      mm.destroy();
    } catch (e) {
      console.error('销毁思维导图失败:', e);
    }
    mm = null;
  }
};

const saveToHistory = () => {
  ElMessage.success('已保存到历史记录');
  router.push('/user-portrait');
};

const resetAnalysis = () => {
  analysisResult.value = null;
  destroyMindMap();
  currentStep.value = 1;
  viewMode.value = 'markdown';
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 监听视图模式变化
watch(viewMode, async (newMode) => {
  if (newMode === 'mindmap' && analysisResult.value?.analysis) {
    await nextTick();
    initializeMindMap(analysisResult.value.analysis);
  }
});

// 初始化
onMounted(() => {
  // 不再需要加载本地API配置
});
</script>

<style scoped>
.user-analysis-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-secondary);
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-title .el-icon {
  font-size: 36px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 步骤引导 */
.steps-section {
  margin-bottom: 32px;
  background: var(--bg-card);
  padding: 24px 32px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.steps-section :deep(.el-steps--simple) {
  background: transparent !important;
  border: none !important;
}

/* 主操作区 */
.main-operation {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.operation-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.help-icon {
  color: var(--text-tertiary);
  cursor: help;
}

/* UID输入 */
.uid-input-section {
  padding: 20px 0;
}

.input-wrapper {
  margin-bottom: 16px;
}

/* 修复下拉框被遮挡问题 */
:deep(.el-input__wrapper) {
  z-index: 1;
}

:deep(.el-input-group__append) {
  z-index: 2;
}

/* 确保弹出层不被裁剪 */
:deep(.el-overlay) {
  z-index: 2000 !important;
}

:deep(.el-popper) {
  z-index: 2001 !important;
}

:deep(.el-select__popper) {
  z-index: 2001 !important;
}

:deep(.el-dropdown__popper) {
  z-index: 2001 !important;
}

/* 防止el-input的append裁剪 */
:deep(.el-input-group) {
  display: flex;
}

:deep(.el-input-group__append) {
  flex-shrink: 0;
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.quick-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.sample-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.sample-tag:hover {
  background: var(--primary-color);
  color: white;
}

/* 分析区 */
.analysis-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.comments-preview-card {
  border-radius: 12px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--primary-color);
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.comments-scroll {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.comment-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  display: flex;
  gap: 12px;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.marker-line {
  width: 2px;
  flex: 1;
  background: linear-gradient(180deg, var(--primary-color), transparent);
  opacity: 0.3;
  margin-top: 4px;
  min-height: 20px;
}

.comment-box {
  flex: 1;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px 16px;
  border-left: 3px solid var(--primary-color);
}

.comment-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  word-break: break-all;
}

.show-more {
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--separator-color);
}

/* AI分析按钮 */
.analyze-action {
  text-align: center;
  padding: 32px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.analyze-btn {
  padding: 16px 48px;
  font-size: 16px;
  font-weight: 600;
}

.analyze-btn .el-icon {
  font-size: 20px;
  margin-right: 8px;
}

.config-hint {
  margin-top: 12px;
  color: var(--text-secondary);
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

/* 消息提示 */
.message-section {
  margin-top: 8px;
}

/* 结果区 */
.result-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--primary-color);
  color: white;
  padding: 16px 24px;
  border-radius: 12px;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.result-meta {
  display: flex;
  gap: 8px;
}

.result-card {
  border-radius: 12px;
}

.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--primary-color);
}

.result-content {
  min-height: 400px;
}

.markdown-view {
  max-height: 500px;
}

.content-scroll {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 16px;
}

.markdown-body {
  line-height: 1.8;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  color: var(--primary-color);
  margin-top: 20px;
  margin-bottom: 12px;
}

.markdown-body :deep(p) {
  margin: 12px 0;
}

.markdown-body :deep(strong) {
  color: var(--primary-color);
}

.mindmap-view {
  display: flex;
  flex-direction: column;
}

.mindmap-container {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
}

.mindmap-svg {
  width: 100%;
  height: 450px;
}

.mindmap-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  background: var(--bg-secondary);
  color: var(--primary-color);
  font-size: 13px;
  border-radius: 0 0 8px 8px;
}

.save-action {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-up-enter-active {
  transition: all 0.4s ease;
}

.fade-up-leave-active {
  transition: all 0.3s ease;
}

.fade-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-up-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .steps-section {
    background: var(--bg-card);
  }

  .comment-box {
    background: var(--bg-secondary);
  }

  .analyze-action {
    background: var(--bg-card);
  }

  .mindmap-container {
    background: var(--bg-secondary);
  }

  .mindmap-hint {
    background: var(--bg-secondary);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .user-analysis-page {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .result-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .result-card-header {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
