<template>
  <div class="user-portrait-page">
    <div class="content-container">
      <!-- 只有存在结果时才显示头部 -->
      <header v-if="analysisResult" class="profile-header">
        <div class="user-main-info">
          <div class="avatar-box">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="info-text">
            <div class="uid-row">
              <span class="uid-label">档案编号</span>
              <span class="uid-value">{{ uid }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-item"><el-icon><Clock /></el-icon> 存档于：{{ formatTime(analysisResult.timestamp) }}</span>
              <span class="meta-divider">|</span>
              <span class="meta-item"><el-icon><ChatLineRound /></el-icon> 样本规模：{{ analysisResult.comment_count }} </span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button @click="copyAnalysis" plain icon="CopyDocument">提取报告文本</el-button>
          <el-button @click="router.push('/history')" icon="Back">返回历史</el-button>
        </div>
      </header>

      <!-- 主要内容区 -->
      <div v-loading="loading" class="main-body">
        <div v-if="analysisResult" class="report-layout">
          <!-- 左侧：核心报告 -->
          <div class="report-container">
            <div class="section-title">
              <el-icon><Memo /></el-icon>
              <span>专家级分析结论</span>
            </div>
            <div class="markdown-content">
              <div v-html="renderMarkdown(analysisResult.analysis)"></div>
            </div>
          </div>

          <!-- 右侧：侧边信息 -->
          <div class="sidebar">
            <div class="sidebar-card">
              <div class="card-title">样本溯源</div>
              <div class="comments-scroll">
                <div 
                  v-for="(comment, idx) in analysisResult.sample_comments" 
                  :key="idx"
                  class="mini-comment"
                >
                  <div class="comment-content">{{ comment }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态：仅提供返回历史的入口 -->
        <div v-else-if="!loading" class="empty-state">
          <div class="empty-inner">
            <el-icon class="empty-icon"><Files /></el-icon>
            <h3>未调取到画像档案</h3>
            <p>该页面仅用于查阅已完成的分析报告，请从历史记录中选择一项进入。</p>
            <el-button type="primary" @click="router.push('/history')">前往历史足迹</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import MarkdownIt from 'markdown-it';
import { 
  UserFilled, Clock, ChatLineRound, CopyDocument, 
  Memo, Back, Files 
} from '@element-plus/icons-vue';
import request from '@/utils/request';

const route = useRoute();
const router = useRouter();
const md = new MarkdownIt({ html: true, breaks: true, linkify: true });

const uid = ref(route.query.uid);
const loading = ref(false);
const analysisResult = ref(null);

const loadAnalysis = async () => {
  if (!uid.value) return;
  loading.value = true;
  try {
    const res = await request.get(`/api/user/analysis/${uid.value}`);
    if (res.code === 200 && res.data) {
      analysisResult.value = res.data;
    } else {
      ElMessage.warning('档案不存在或已被清理');
    }
  } catch (error) {
    ElMessage.error('调取档案失败');
  } finally {
    loading.value = false;
  }
};

const renderMarkdown = (content) => md.render(content || '');

const formatTime = (timeStr) => {
  if (!timeStr) return '-';
  return new Date(timeStr).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  });
};

const copyAnalysis = () => {
  if (analysisResult.value?.analysis) {
    navigator.clipboard.writeText(analysisResult.value.analysis);
    ElMessage.success('已存入剪贴板');
  }
};

onMounted(() => loadAnalysis());
</script>

<style scoped>
.user-portrait-page {
  background-color: var(--bg-secondary);
  min-height: 100vh;
  padding: 40px 24px;
}

.content-container {
  max-width: 1100px;
  margin: 0 auto;
}

/* 头部样式 */
.profile-header {
  background: var(--bg-card);
  padding: 20px 32px;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  box-shadow: var(--shadow-sm);
}

.user-main-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-box {
  width: 56px;
  height: 56px;
  background: var(--bg-secondary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: var(--primary-color);
  border: 1px solid var(--border-light);
}

.info-text {
  display: flex;
  flex-direction: column;
}

.uid-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.uid-label {
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 700;
  letter-spacing: 0.5px;
}

.uid-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: 'SF Mono', monospace;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.meta-divider {
  opacity: 0.3;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 布局结构 */
.report-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 32px;
}

/* 左侧报告 */
.report-container {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-light);
  padding: 40px;
  box-shadow: var(--shadow-sm);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.markdown-content {
  color: var(--text-primary);
  line-height: 1.8;
  font-size: 15px;
}

.markdown-content :deep(h1), .markdown-content :deep(h2) {
  font-size: 18px;
  border-left: 4px solid var(--primary-color);
  padding-left: 12px;
  margin: 32px 0 16px;
}

.markdown-content :deep(p) {
  margin-bottom: 16px;
  color: var(--text-secondary);
}

/* 右侧侧边栏 */
.sidebar {
  display: flex;
  flex-direction: column;
}

.sidebar-card {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-light);
  padding: 24px;
}

.card-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-tertiary);
  margin-bottom: 20px;
}

.comments-scroll {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mini-comment {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 14px;
  background: var(--bg-secondary);
  border-radius: 10px;
  border: 1px solid var(--border-light);
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  padding: 100px 0;
}

.empty-inner {
  text-align: center;
  background: var(--bg-card);
  padding: 60px;
  border-radius: 24px;
  border: 1px solid var(--border-light);
  max-width: 400px;
}

.empty-icon {
  font-size: 56px;
  color: var(--text-light);
  margin-bottom: 20px;
}

.empty-inner h3 {
  margin-bottom: 12px;
}

.empty-inner p {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 32px;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .report-layout { grid-template-columns: 1fr; }
  .profile-header { flex-direction: column; gap: 20px; }
}
</style>
