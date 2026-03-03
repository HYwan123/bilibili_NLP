<template>
  <div class="history-page-wrapper">
    <!-- 头部区域 -->
    <header class="history-header">
      <div class="header-left">
        <h1 class="page-title">探索足迹</h1>
        <p class="page-subtitle">回顾您在 Bilibili 数据海洋中的每一次深度挖掘</p>
      </div>
      <div class="header-right">
        <div class="stat-group">
          <div class="stat-pill">
            <span class="pill-label">总计</span>
            <span class="pill-value">{{ total }}</span>
          </div>
          <div class="stat-pill primary">
            <span class="pill-label">视频</span>
            <span class="pill-value">{{ bvCount }}</span>
          </div>
          <div class="stat-pill success">
            <span class="pill-label">画像</span>
            <span class="pill-value">{{ uidCount }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 顶部筛选器 -->
    <nav class="filter-nav">
      <div class="tabs-container">
        <div 
          v-for="tab in tabs" 
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          <el-icon><component :is="tab.icon" /></el-icon>
          <span>{{ tab.label }}</span>
        </div>
      </div>
    </nav>

    <!-- 主列表区域 -->
    <main class="history-main">
      <div v-if="loading" class="loading-container">
        <div class="apple-spinner"></div>
      </div>

      <div v-else-if="historyList.length === 0" class="empty-state">
        <div class="empty-glass-card">
          <el-icon class="empty-icon"><Compass /></el-icon>
          <h3>尚无探索记录</h3>
          <p>开始您的第一次数据分析旅程吧</p>
          <div class="empty-btns">
            <el-button round type="primary" @click="goToQuery">分析视频</el-button>
            <el-button round @click="goToAnalysis">透视用户</el-button>
          </div>
        </div>
      </div>

      <div v-else class="history-grid">
        <div 
          v-for="(group, date) in groupedHistory" 
          :key="date"
          class="date-group"
        >
          <div class="date-header">
            <span class="date-text">{{ formatGroupDate(date) }}</span>
            <div class="date-line"></div>
          </div>
          
          <div class="cards-stack">
            <div 
              v-for="item in group" 
              :key="getItemKey(item)"
              class="history-card"
              :class="item.type"
            >
              <div class="card-glass-effect"></div>
              
              <div class="card-inner">
                <div class="card-top">
                  <div class="type-indicator">
                    <div class="icon-orb" :class="item.type">
                      <el-icon v-if="item.type === 'bv'"><VideoPlay /></el-icon>
                      <el-icon v-else><User /></el-icon>
                    </div>
                    <div class="id-info">
                      <span class="id-tag">{{ item.type === 'bv' ? 'VIDEO' : 'USER' }}</span>
                      <span class="id-value">{{ item.bv || item.uid }}</span>
                    </div>
                  </div>
                  <time class="card-time">{{ formatExactTime(item.query_time) }}</time>
                </div>

                <div class="card-body">
                  <!-- 视频摘要样式 -->
                  <div v-if="item.type === 'bv' && item.data" class="content-preview bv-content">
                    <p class="summary-text">{{ item.data }}</p>
                  </div>

                  <!-- 用户评论样板样式 -->
                  <div v-if="item.type === 'uuid' && item.sample_comments?.length" class="content-preview user-content">
                    <div class="comment-scroller">
                      <div 
                        v-for="(comment, idx) in item.sample_comments.slice(0, 3)" 
                        :key="idx"
                        class="mini-comment"
                      >
                        <span class="quote-char">“</span>
                        {{ truncateText(comment, 80) }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="card-footer">
                  <span class="time-relative">{{ formatTimeAgo(item.query_time) }}</span>
                  <div class="actions">
                    <el-button 
                      v-if="item.type === 'bv'"
                      class="apple-action-btn"
                      @click="viewBvDetail(item.bv)"
                    >
                      <span>分析详情</span>
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                    <el-button 
                      v-else
                      class="apple-action-btn success"
                      @click="viewUidDetail(item.uid)"
                    >
                      <span>查看画像</span>
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页区域 -->
      <footer v-if="historyList.length > 0" class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="handleCurrentChange"
          class="apple-pagination"
        />
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  VideoPlay, User, Grid, Compass, 
  ArrowRight, Clock, ChatDotRound, Ticket
} from '@element-plus/icons-vue';
import { getHistory } from '@/api/bilibili';

const router = useRouter();

// 状态
const activeTab = ref('all');
const historyList = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(12); // 改为12，更适合栅格布局
const total = ref(0);
const bvCount = ref(0);
const uidCount = ref(0);
const todayCount = ref(0);

const tabs = [
  { key: 'all', label: '全部记录', icon: 'Grid' },
  { key: 'bv', label: '视频分析', icon: 'VideoPlay' },
  { key: 'uuid', label: '用户画像', icon: 'User' }
];

// 核心加载逻辑
const loadHistory = async () => {
  loading.value = true;
  try {
    const response = await getHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      type: activeTab.value
    });
    
    if (response.data) {
      historyList.value = response.data.items || [];
      total.value = response.data.total || 0;
      
      // 更新计数
      if (activeTab.value === 'all') {
        bvCount.value = response.data.bv_total || 0;
        uidCount.value = response.data.uuid_total || 0;
      } else if (activeTab.value === 'bv') {
        bvCount.value = response.data.total || 0;
      } else if (activeTab.value === 'uuid') {
        uidCount.value = response.data.total || 0;
      }
      
      calculateTodayCount();
    }
  } catch (error) {
    ElMessage.error('无法同步您的历史足迹');
  } finally {
    loading.value = false;
  }
};

const calculateTodayCount = () => {
  const today = new Date().toDateString();
  todayCount.value = historyList.value.filter(item => 
    new Date(item.query_time).toDateString() === today
  ).length;
};

// 辅助方法
const getItemKey = (item) => `${item.type}_${item.bv || item.uid}_${item.query_time}`;

const groupedHistory = computed(() => {
  const groups = {};
  historyList.value.forEach(item => {
    const date = new Date(item.query_time).toDateString();
    if (!groups[date]) groups[date] = [];
    groups[date].push(item);
  });
  return groups;
});

const switchTab = (tab) => {
  activeTab.value = tab;
  currentPage.value = 1;
  loadHistory();
};

const handleCurrentChange = (page) => {
  currentPage.value = page;
  loadHistory();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const viewBvDetail = (bvId) => router.push({ path: '/comment-analysis', query: { bv: bvId } });
const viewUidDetail = (uid) => router.push(`/user-portrait?uid=${uid}`);
const goToQuery = () => router.push('/query');
const goToAnalysis = () => router.push('/user-analysis');

const formatGroupDate = (dateStr) => {
  const date = new Date(dateStr);
  const now = new Date();
  if (date.toDateString() === now.toDateString()) return '今日探索';
  const yesterday = new Date(now.setDate(now.getDate() - 1));
  if (date.toDateString() === yesterday.toDateString()) return '昨日记录';
  return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', year: 'numeric' });
};

const formatExactTime = (timeStr) => {
  return new Date(timeStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const formatTimeAgo = (timeStr) => {
  const diff = new Date() - new Date(timeStr);
  const min = Math.floor(diff / 60000);
  const hr = Math.floor(diff / 3600000);
  if (min < 1) return '刚刚';
  if (min < 60) return `${min}m 前`;
  if (hr < 24) return `${hr}h 前`;
  return '已归档';
};

const truncateText = (text, len) => text && text.length > len ? text.slice(0, len) + '...' : text;

onMounted(() => loadHistory());
</script>

<style scoped>
.history-page-wrapper {
  padding: 40px 60px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: var(--bg-secondary);
}

/* Header设计 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
}

.page-title {
  font-size: 34px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.03em;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--text-secondary);
}

.stat-group {
  display: flex;
  gap: 12px;
}

.stat-pill {
  background: var(--bg-card);
  padding: 8px 16px;
  border-radius: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
}

.stat-pill.primary { border-color: rgba(0, 122, 255, 0.3); }
.stat-pill.success { border-color: rgba(52, 199, 89, 0.3); }

.pill-label { font-size: 12px; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; }
.pill-value { font-size: 16px; font-weight: 700; color: var(--text-primary); }

/* 导航标签 */
.filter-nav {
  margin-bottom: 40px;
}

.tabs-container {
  display: flex;
  gap: 8px;
  background: rgba(0, 0, 0, 0.03);
  padding: 6px;
  border-radius: 14px;
  width: fit-content;
}

.tab-item {
  padding: 10px 24px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-item:hover { color: var(--text-primary); }
.tab-item.active {
  background: var(--bg-card);
  color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

/* 时间轴逻辑 */
.date-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 40px 0 24px;
}

.date-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
}

.date-line {
  height: 1px;
  background: var(--separator-color);
  flex: 1;
  opacity: 0.4;
}

.cards-stack {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

/* 卡片极致设计 */
.history-card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
}

.history-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-color);
}

.card-inner {
  padding: 24px;
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.type-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-orb {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.icon-orb.bv { background: linear-gradient(135deg, #007AFF, #0051D5); }
.icon-orb.uuid { background: linear-gradient(135deg, #34C759, #248A3D); }

.id-info { display: flex; flex-direction: column; }
.id-tag { font-size: 10px; font-weight: 800; color: var(--text-tertiary); letter-spacing: 0.1em; }
.id-value { font-size: 16px; font-weight: 700; color: var(--text-primary); font-family: 'SF Mono', monospace; }

.card-time { font-size: 13px; font-weight: 600; color: var(--text-tertiary); }

.card-body {
  flex: 1;
  margin-bottom: 24px;
}

.content-preview {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 16px;
  height: 100%;
}

.summary-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.comment-scroller {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mini-comment {
  font-size: 13px;
  color: var(--text-secondary);
  position: relative;
  padding-left: 14px;
  line-height: 1.4;
}

.quote-char {
  position: absolute;
  left: 0;
  color: var(--primary-color);
  font-family: Georgia, serif;
  font-size: 18px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time-relative { font-size: 12px; font-weight: 600; color: var(--text-tertiary); text-transform: uppercase; }

.apple-action-btn {
  border: none;
  background: rgba(0, 122, 255, 0.1);
  color: var(--primary-color);
  font-weight: 700;
  border-radius: 12px;
  padding: 8px 16px;
  transition: all 0.2s ease;
}

.apple-action-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: scale(1.05);
}

.apple-action-btn.success {
  background: rgba(52, 199, 89, 0.1);
  color: var(--success-color);
}

.apple-action-btn.success:hover {
  background: var(--success-color);
  color: white;
}

/* 分页 */
.pagination-footer {
  margin-top: 60px;
  display: flex;
  justify-content: center;
}

.apple-pagination :deep(.el-pager li) {
  background: transparent;
  font-weight: 700;
}

.apple-pagination :deep(.el-pager li.is-active) {
  color: var(--primary-color);
  font-size: 18px;
}

/* 空状态 */
.empty-glass-card {
  background: var(--bg-card);
  padding: 80px 40px;
  border-radius: 32px;
  text-align: center;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-lg);
}

.empty-icon { font-size: 64px; color: var(--text-light); margin-bottom: 24px; }

/* 响应式 */
@media (max-width: 1024px) {
  .cards-stack { grid-template-columns: 1fr; }
  .history-page-wrapper { padding: 24px; }
  .history-header { flex-direction: column; align-items: flex-start; gap: 20px; }
}

/* 深色模式微调 */
html.dark .history-card { background: #1C1C1E; }
html.dark .content-preview { background: #2C2C2E; }
html.dark .tab-item.active { background: #2C2C2E; }

html.dark .summary-text { color: #E1E1E6; }
html.dark .mini-comment { color: #D1D1D6; }
html.dark .card-time, 
html.dark .time-relative { color: #A1A1A6; }
html.dark .id-tag { color: #8E8E93; }
html.dark .pill-label { color: #A1A1A6; }

</style>
