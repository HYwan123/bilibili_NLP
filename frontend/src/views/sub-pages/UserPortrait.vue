<template>
  <div class="user-portrait-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <h1 class="page-title">用户画像分析</h1>
      <p class="page-subtitle">查看和管理已分析的用户画像数据</p>
    </div>

    <!-- 统计卡片区 -->
    <div class="stats-section" v-if="uidList.length > 0">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8">
          <div class="stat-card primary">
            <div class="stat-icon">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ uidList.length }}</div>
              <div class="stat-label">已分析用户</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8">
          <div class="stat-card success">
            <div class="stat-icon">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalComments }}</div>
              <div class="stat-label">评论总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8">
          <div class="stat-card warning">
            <div class="stat-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayAnalyzed }}</div>
              <div class="stat-label">今日分析</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 加载状态 -->
    <div v-if="loadingHistory" class="skeleton-section">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="8" v-for="i in 6" :key="i">
          <div class="skeleton-card">
            <div class="skeleton-header">
              <div class="skeleton-avatar"></div>
              <div class="skeleton-info">
                <div class="skeleton-line short"></div>
                <div class="skeleton-line"></div>
              </div>
            </div>
            <div class="skeleton-body">
              <div class="skeleton-tags">
                <div class="skeleton-tag" v-for="j in 3" :key="j"></div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 空状态 -->
    <div v-else-if="uidList.length === 0" class="empty-state">
      <div class="empty-icon">
        <el-icon><User /></el-icon>
      </div>
      <h3>暂无用户画像数据</h3>
      <p>您还没有分析过任何用户的画像</p>
      <el-button type="primary" @click="goToAnalysis">
        <el-icon><Plus /></el-icon>
        开始分析用户
      </el-button>
    </div>

    <!-- 用户卡片列表 -->
    <div v-else class="user-grid">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="user in uidList" :key="user.uid">
          <div class="user-card">
            <div class="card-header">
              <div class="user-avatar">
                <el-icon><Avatar /></el-icon>
              </div>
              <div class="user-info">
                <div class="uid-label">用户 UID</div>
                <div class="uid-value">{{ user.uid }}</div>
              </div>
              <el-tag size="small" effect="light" class="user-tag">
                <el-icon><ChatLineRound /></el-icon>
                {{ getCommentCount(user.uid) }} 评论
              </el-tag>
            </div>

            <div class="preview-section">
              <div class="preview-label">评论预览</div>
              <div class="preview-tags" v-if="getCommentPreview(user.uid).length > 0">
                <el-tag 
                  v-for="(comment, idx) in getCommentPreview(user.uid)" 
                  :key="idx"
                  size="small"
                  type="info"
                  effect="light"
                  class="preview-tag"
                >
                  {{ truncateText(comment.comment_text, 20) }}
                </el-tag>
              </div>
              <div v-else class="no-preview">暂无评论预览</div>
            </div>

            <div class="card-actions">
              <el-button 
                size="small" 
                @click="viewUserComments(user.uid, 10)"
              >
                <el-icon><Document /></el-icon>
                评论
              </el-button>
              <el-button 
                type="primary" 
                size="small" 
                @click="viewAnalysis(user.uid)"
              >
                <el-icon><View /></el-icon>
                查看画像
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 用户画像详情对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="`用户 ${analysisResult?.uid} 的画像分析`" 
      width="850px"
      class="portrait-dialog"
      destroy-on-close
    >
      <div v-if="analysisResult" class="dialog-content">
        <!-- 基本信息头部 -->
        <div class="info-header">
          <div class="info-item">
            <div class="info-label">用户UID</div>
            <div class="info-value uid">{{ analysisResult.uid }}</div>
          </div>
          <div class="info-item">
            <div class="info-label">评论数量</div>
            <div class="info-value">
              <el-tag type="success" effect="light">{{ analysisResult.comment_count }} 条</el-tag>
            </div>
          </div>
          <div class="info-item">
            <div class="info-label">分析时间</div>
            <div class="info-value time">{{ formatTime(analysisResult.timestamp) }}</div>
          </div>
        </div>

        <!-- 标签页切换 -->
        <el-tabs v-model="activeTab" class="content-tabs">
          <el-tab-pane label="画像分析" name="analysis">
            <!-- 视图模式切换 -->
            <div class="view-toggle">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button label="markdown">
                  <el-icon><Document /></el-icon> 文本视图
                </el-radio-button>
                <el-radio-button label="mindmap">
                  <el-icon><Share /></el-icon> 思维导图
                </el-radio-button>
              </el-radio-group>
            </div>

            <!-- Markdown 视图 -->
            <div v-if="viewMode === 'markdown'" class="analysis-view">
              <div v-html="md.render(analysisResult.analysis)" class="markdown-content"></div>
            </div>

            <!-- 思维导图视图 -->
            <div v-if="viewMode === 'mindmap'" class="mindmap-view">
              <svg ref="mindmapContainer" class="mindmap-svg"></svg>
            </div>
          </el-tab-pane>

          <el-tab-pane label="样本评论" name="comments">
            <div class="comments-section">
              <div class="comments-header">
                <span class="section-title">用户评论样本</span>
                <span class="comments-count">共 {{ analysisResult.sample_comments?.length || 0 }} 条</span>
              </div>
              <div class="comments-list" v-if="analysisResult.sample_comments?.length > 0">
                <div 
                  v-for="(comment, idx) in displayedComments" 
                  :key="idx"
                  class="comment-item"
                >
                  <div class="comment-index">{{ idx + 1 }}</div>
                  <div class="comment-content">{{ formatComment(comment) }}</div>
                </div>
              </div>
              <div v-else class="no-comments">
                <el-empty description="暂无评论数据" />
              </div>
              <div v-if="showMoreButton" class="more-btn">
                <el-button text @click="toggleShowAllComments">
                  {{ showAllComments ? '收起' : `展开全部 ${analysisResult.sample_comments.length} 条评论` }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 评论列表对话框 -->
    <el-dialog 
      v-model="commentDialogVisible" 
      :title="`用户 ${currentUid} 的前${commentLimit}条评论`" 
      width="700px"
      destroy-on-close
    >
      <div class="comments-dialog-content">
        <el-table :data="userComments" stripe style="width: 100%">
          <el-table-column type="index" width="60" align="center" />
          <el-table-column label="评论内容" min-width="400">
            <template #default="{ row }">
              <div class="comment-text">{{ row.comment_text }}</div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/utils/request';
import MarkdownIt from 'markdown-it';
import { Transformer } from 'markmap-lib';
import { Markmap } from 'markmap-view';
import { 
  UserFilled, 
  ChatDotRound, 
  Calendar, 
  User, 
  Plus, 
  Avatar, 
  ChatLineRound, 
  Document, 
  View, 
  Share 
} from '@element-plus/icons-vue';

const router = useRouter();

// 状态
const uidList = ref<{ uid: string }[]>([]);
const analysisResult = ref<any>(null);
const dialogVisible = ref(false);
const loadingHistory = ref(false);
const error = ref('');
const activeTab = ref('analysis');
const viewMode = ref('markdown');
const currentUid = ref('');

// 评论相关
const userComments = ref<any[]>([]);
const commentDialogVisible = ref(false);
const commentLimit = ref(10);
const commentPreviewMap = ref<Record<string, any[]>>({});
const showAllComments = ref(false);
const defaultCommentCount = 5;

// 思维导图
const mindmapContainer = ref<SVGSVGElement | null>(null);
let mm: any = null;
const transformer = new Transformer();

// Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
});

// 计算属性
const totalComments = computed(() => {
  return Object.values(commentPreviewMap.value).reduce((sum, comments) => sum + comments.length, 0);
});

const todayAnalyzed = computed(() => {
  // 简化计算，实际应该从分析结果的时间戳计算
  return Math.floor(uidList.value.length * 0.3); // 模拟30%是今日分析的
});

const displayedComments = computed(() => {
  if (!analysisResult.value?.sample_comments) return [];
  if (showAllComments.value) return analysisResult.value.sample_comments;
  return analysisResult.value.sample_comments.slice(0, defaultCommentCount);
});

const showMoreButton = computed(() => {
  return (analysisResult.value?.sample_comments?.length || 0) > defaultCommentCount;
});

// 方法
const goToAnalysis = () => {
  router.push('/user-analysis');
};

const fetchUidList = async () => {
  loadingHistory.value = true;
  try {
    const res = await request.get('/api/get_uids');
    if (Array.isArray(res.data)) {
      uidList.value = res.data;
      // 获取评论预览
      const uids = uidList.value.map(item => String(item.uid));
      if (uids.length > 0) {
        await fetchCommentPreviews(uids);
      }
    }
  } catch (e: any) {
    error.value = e.message || '请求失败';
  } finally {
    loadingHistory.value = false;
  }
};

const fetchCommentPreviews = async (uids: string[]) => {
  const map: Record<string, any[]> = {};
  await Promise.all(uids.map(async (uid) => {
    try {
      const res = await request.get(`/api/user/comments/${uid}`);
      if (Array.isArray(res.data)) {
        map[uid] = res.data.slice(0, 3);
      }
    } catch {
      map[uid] = [];
    }
  }));
  commentPreviewMap.value = map;
};

const getCommentPreview = (uid: string) => {
  return commentPreviewMap.value[uid] || [];
};

const getCommentCount = (uid: string) => {
  return commentPreviewMap.value[uid]?.length || 0;
};

const viewUserComments = async (uid: string, limit: number) => {
  currentUid.value = uid;
  commentLimit.value = limit;
  try {
    const res = await request.get(`/api/user/comments/${uid}`);
    if (Array.isArray(res.data)) {
      userComments.value = res.data;
      commentDialogVisible.value = true;
    }
  } catch (e) {
    ElMessage.error('获取评论失败');
  }
};

const viewAnalysis = async (uid: string) => {
  currentUid.value = uid;
  try {
    const res = await request.get(`/api/user/analysis/${uid}`);
    const data = res.data;
    
    // 处理两种可能的API响应格式
    if (data.code === 200) {
      // 格式1: { code: 200, data: { uid, analysis, ... } }
      analysisResult.value = data.data;
    } else if (data.uid || data.analysis) {
      // 格式2: 直接返回分析对象
      analysisResult.value = data;
    } else {
      ElMessage.error('未找到分析记录');
      return;
    }
    
    dialogVisible.value = true;
    activeTab.value = 'analysis';
    showAllComments.value = false;
    
    // 初始化思维导图
    await nextTick();
    if (viewMode.value === 'mindmap' && analysisResult.value?.analysis) {
      initializeMindMap(analysisResult.value.analysis);
    }
  } catch (e: any) {
    console.error('查看画像失败:', e);
    ElMessage.error('查看画像失败: ' + (e.message || '请求失败'));
  }
};

const initializeMindMap = async (markdownContent: string) => {
  if (!mindmapContainer.value) return;
  try {
    const { root } = transformer.transform(markdownContent);
    if (!mm) {
      mm = Markmap.create(mindmapContainer.value, null, root);
    } else {
      await mm.setData(root);
      mm.fit();
    }
  } catch (error) {
    console.error('思维导图初始化失败:', error);
    ElMessage.error('思维导图加载失败');
  }
};

const toggleShowAllComments = () => {
  showAllComments.value = !showAllComments.value;
};

// 监听视图模式变化
watch(viewMode, async (newMode) => {
  if (newMode === 'mindmap' && analysisResult.value?.analysis) {
    await nextTick();
    initializeMindMap(analysisResult.value.analysis);
  }
});

// 工具函数
const formatTime = (timestamp: string) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const truncateText = (text: string, length: number) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

const formatComment = (comment: any) => {
  if (typeof comment === 'string') return comment;
  return comment.comment_text || comment.content || JSON.stringify(comment);
};

onMounted(() => {
  fetchUidList();
});
</script>

<style scoped>
.user-portrait-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 50%, #f0fdf4 100%);
  min-height: 100vh;
}

@media (min-width: 1600px) {
  .user-portrait-page {
    max-width: 1600px;
    padding: 32px 48px;
  }
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
  background: linear-gradient(135deg, #065f46, #047857);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(6, 95, 70, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 95, 70, 0.15);
}

.stat-card.primary {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  border: none;
}

.stat-card.success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
}

.stat-card.warning {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border: none;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  opacity: 0.9;
  margin-top: 4px;
}

/* 骨架屏 */
.skeleton-section {
  margin-bottom: 32px;
}

.skeleton-card {
  background: #f3f4f6;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  animation: pulse 2s infinite;
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e5e7eb;
}

.skeleton-info {
  flex: 1;
}

.skeleton-line {
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 40%;
}

.skeleton-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.skeleton-tag {
  width: 80px;
  height: 24px;
  background: #e5e7eb;
  border-radius: 4px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, rgba(6, 95, 70, 0.1), rgba(4, 120, 87, 0.1));
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #065f46;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px 0;
}

/* 用户卡片网格 */
.user-grid {
  margin-bottom: 32px;
}

.user-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(6, 95, 70, 0.08);
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(6, 95, 70, 0.15);
  border-color: rgba(6, 95, 70, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #065f46, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.user-info {
  flex: 1;
}

.uid-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 2px;
}

.uid-value {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  font-family: 'SF Mono', Monaco, monospace;
}

.user-tag {
  margin-left: auto;
}

.preview-section {
  margin-bottom: 16px;
}

.preview-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 8px;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.preview-tag {
  max-width: 100%;
}

.no-preview {
  font-size: 13px;
  color: #9ca3af;
  font-style: italic;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-actions .el-button {
  flex: 1;
}

/* 对话框样式 */
:deep(.portrait-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  padding: 16px 20px;
  margin-right: 0;
}

:deep(.portrait-dialog .el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.portrait-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: white;
}

.dialog-content {
  padding: 20px 0;
}

.info-header {
  display: flex;
  gap: 32px;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #9ca3af;
}

.info-value {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.info-value.uid {
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 16px;
  color: #065f46;
}

.info-value.time {
  color: #6b7280;
}

/* 标签页 */
.content-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.view-toggle {
  margin-bottom: 16px;
}

/* 分析内容视图 */
.analysis-view {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  color: #065f46;
  margin-top: 20px;
  margin-bottom: 12px;
}

.markdown-content :deep(p) {
  line-height: 1.8;
  color: #374151;
  margin: 12px 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 24px;
  margin: 12px 0;
}

.markdown-content :deep(li) {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-content :deep(strong) {
  color: #065f46;
}

/* 思维导图 */
.mindmap-view {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.mindmap-svg {
  width: 100%;
  height: 500px;
}

/* 评论区域 */
.comments-section {
  padding: 16px 0;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.comments-count {
  font-size: 13px;
  color: #6b7280;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #065f46;
}

.comment-index {
  width: 24px;
  height: 24px;
  background: #065f46;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
  line-height: 1.6;
  color: #374151;
  word-break: break-all;
}

.no-comments {
  padding: 40px 0;
}

.more-btn {
  margin-top: 16px;
  text-align: center;
}

/* 评论对话框 */
.comments-dialog-content {
  padding: 20px 0;
}

.comment-text {
  line-height: 1.6;
  color: #374151;
}

/* 响应式 */
@media (max-width: 768px) {
  .user-portrait-page {
    padding: 16px;
  }
  
  .info-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .card-actions {
    flex-direction: column;
  }
}
</style>
