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

    <!-- 优化的用户画像详情模态框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="用户画像分析详情" 
      width="1000px"
      class="portrait-dialog"
      destroy-on-close
      :close-on-click-modal="false"
      align-center
    >
      <div v-if="analysisResult" class="dialog-wrapper">
        <!-- 用户信息卡片头部 -->
        <div class="user-profile-header">
          <div class="profile-avatar">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="profile-info">
            <div class="profile-main">
              <span class="profile-label">用户 UID</span>
              <span class="profile-uid">{{ analysisResult.uid }}</span>
            </div>
            <div class="profile-meta">
              <div class="meta-item">
                <el-icon><ChatLineRound /></el-icon>
                <span>{{ analysisResult.comment_count }} 条评论</span>
              </div>
              <div class="meta-divider"></div>
              <div class="meta-item">
                <el-icon><Clock /></el-icon>
                <span>{{ formatTime(analysisResult.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 视图切换工具栏 -->
        <div class="toolbar-section">
          <div class="view-switcher">
            <button 
              class="switch-btn" 
              :class="{ active: activeTab === 'analysis' }"
              @click="activeTab = 'analysis'"
            >
              <el-icon><Document /></el-icon>
              <span>画像分析</span>
            </button>
            <button 
              class="switch-btn" 
              :class="{ active: activeTab === 'comments' }"
              @click="activeTab = 'comments'"
            >
              <el-icon><ChatDotRound /></el-icon>
              <span>评论样本</span>
              <span class="count-badge" v-if="analysisResult.sample_comments?.length">
                {{ analysisResult.sample_comments.length }}
              </span>
            </button>
          </div>

          <div class="display-mode" v-if="activeTab === 'analysis'">
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

        <!-- 内容展示区 -->
        <div class="content-display">
          <!-- 分析内容 -->
          <div v-show="activeTab === 'analysis'" class="analysis-panel">
            <div v-if="viewMode === 'markdown'" class="markdown-wrapper">
              <div class="content-scroll">
                <div v-html="md.render(analysisResult.analysis)" class="markdown-body"></div>
              </div>
            </div>
            <div v-else class="mindmap-wrapper">
              <div class="mindmap-container">
                <svg ref="mindmapContainer" class="mindmap-svg"></svg>
              </div>
              <div class="mindmap-hint">
                <el-icon><InfoFilled /></el-icon>
                <span>支持缩放和拖拽查看</span>
              </div>
            </div>
          </div>

          <!-- 评论样本 -->
          <div v-show="activeTab === 'comments'" class="comments-panel">
            <div class="comments-scroll">
              <div v-if="analysisResult.sample_comments?.length > 0" class="comments-timeline">
                <div 
                  v-for="(comment, idx) in displayedComments" 
                  :key="idx"
                  class="timeline-comment"
                >
                  <div class="timeline-marker">
                    <div class="marker-number">{{ idx + 1 }}</div>
                    <div class="marker-line" v-if="idx !== displayedComments.length - 1"></div>
                  </div>
                  <div class="comment-card">
                    <div class="comment-text">{{ formatComment(comment) }}</div>
                  </div>
                </div>
              </div>
              <div v-else class="comments-empty">
                <el-empty description="暂无评论样本">
                  <template #image>
                    <div class="empty-comments-icon">
                      <el-icon><ChatLineRound /></el-icon>
                    </div>
                  </template>
                </el-empty>
              </div>

              <div v-if="showMoreButton" class="load-more">
                <el-button 
                  type="primary" 
                  plain
                  @click="toggleShowAllComments"
                  :icon="showAllComments ? 'ArrowUp' : 'ArrowDown'"
                >
                  {{ showAllComments ? '收起评论' : `展开全部 ${analysisResult.sample_comments.length} 条评论` }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 评论列表对话框 -->
    <el-dialog 
      v-model="commentDialogVisible" 
      :title="`用户 ${currentUid} 的前${commentLimit}条评论`" 
      width="700px"
      destroy-on-close
      align-center
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
  Share,
  Clock,
  InfoFilled,
  ArrowUp,
  ArrowDown
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
  return Math.floor(uidList.value.length * 0.3);
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
    
    if (data.code === 200) {
      analysisResult.value = data.data;
    } else if (data.uid || data.analysis) {
      analysisResult.value = data;
    } else {
      ElMessage.error('未找到分析记录');
      return;
    }
    
    dialogVisible.value = true;
    activeTab.value = 'analysis';
    showAllComments.value = false;
    
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
  }
};

const toggleShowAllComments = () => {
  showAllComments.value = !showAllComments.value;
};

watch(viewMode, async (newMode) => {
  if (newMode === 'mindmap' && analysisResult.value?.analysis) {
    await nextTick();
    initializeMindMap(analysisResult.value.analysis);
  }
});

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

/* 用户卡片 */
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

.user-card .card-header {
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

.card-actions {
  display: flex;
  gap: 8px;
}

.card-actions .el-button {
  flex: 1;
}

/* ==================== 优化的模态框样式 ==================== */

:deep(.portrait-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.portrait-dialog .el-dialog__header) {
  background: linear-gradient(135deg, #065f46, #047857);
  padding: 20px 24px;
  margin-right: 0;
}

:deep(.portrait-dialog .el-dialog__title) {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

:deep(.portrait-dialog .el-dialog__headerbtn) {
  top: 20px;
  right: 20px;
}

:deep(.portrait-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: white;
  font-size: 20px;
}

:deep(.portrait-dialog .el-dialog__body) {
  padding: 0;
  max-height: 70vh;
  overflow: hidden;
}

.dialog-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 70vh;
}

/* 用户信息头部 */
.user-profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #f0fdf4, #ffffff);
  border-bottom: 1px solid rgba(6, 95, 70, 0.1);
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #065f46, #047857);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  box-shadow: 0 4px 12px rgba(6, 95, 70, 0.3);
}

.profile-info {
  flex: 1;
}

.profile-main {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.profile-label {
  font-size: 13px;
  color: #6b7280;
}

.profile-uid {
  font-size: 24px;
  font-weight: 700;
  color: #065f46;
  font-family: 'SF Mono', Monaco, monospace;
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.meta-divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #d1d5db;
}

/* 工具栏 */
.toolbar-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid rgba(6, 95, 70, 0.1);
}

.view-switcher {
  display: flex;
  gap: 8px;
}

.switch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch-btn:hover {
  border-color: #065f46;
  color: #065f46;
}

.switch-btn.active {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(6, 95, 70, 0.3);
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

/* 内容展示区 */
.content-display {
  flex: 1;
  overflow: hidden;
  background: white;
}

/* Markdown 内容 */
.markdown-wrapper {
  height: 100%;
  max-height: calc(70vh - 200px);
}

.content-scroll {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
}

.markdown-body {
  line-height: 1.8;
  color: #374151;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  color: #065f46;
  margin-top: 24px;
  margin-bottom: 12px;
  font-weight: 600;
}

.markdown-body :deep(h1) { font-size: 22px; }
.markdown-body :deep(h2) { font-size: 18px; }
.markdown-body :deep(h3) { font-size: 16px; }

.markdown-body :deep(p) {
  margin: 12px 0;
  line-height: 1.8;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
  margin: 12px 0;
}

.markdown-body :deep(li) {
  margin: 8px 0;
}

.markdown-body :deep(strong) {
  color: #065f46;
  font-weight: 600;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #065f46;
  padding-left: 16px;
  margin: 16px 0;
  color: #4b5563;
  background: #f0fdf4;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
}

/* 思维导图 */
.mindmap-wrapper {
  height: 100%;
  max-height: calc(70vh - 200px);
  display: flex;
  flex-direction: column;
}

.mindmap-container {
  flex: 1;
  padding: 20px;
  background: #f9fafb;
}

.mindmap-svg {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.mindmap-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  background: #f0fdf4;
  color: #065f46;
  font-size: 13px;
  border-top: 1px solid rgba(6, 95, 70, 0.1);
}

/* 评论面板 */
.comments-panel {
  height: 100%;
  max-height: calc(70vh - 200px);
}

.comments-scroll {
  height: 100%;
  overflow-y: auto;
  padding: 24px;
}

.comments-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.timeline-comment {
  display: flex;
  gap: 12px;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.marker-line {
  width: 2px;
  flex: 1;
  background: linear-gradient(180deg, rgba(6, 95, 70, 0.3), transparent);
  margin-top: 8px;
  min-height: 40px;
}

.comment-card {
  flex: 1;
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  border-left: 3px solid #065f46;
}

.comment-text {
  line-height: 1.6;
  color: #374151;
  word-break: break-all;
}

.comments-empty {
  padding: 40px 0;
}

.empty-comments-icon {
  font-size: 64px;
  color: #d1d5db;
  margin-bottom: 16px;
}

.load-more {
  margin-top: 24px;
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
  
  .toolbar-section {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .view-switcher {
    justify-content: center;
  }
  
  .user-profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-meta {
    justify-content: center;
  }
}
</style>
