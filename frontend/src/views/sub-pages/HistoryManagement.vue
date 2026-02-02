<template>
  <div class="history-management-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">查询历史</h1>
      <p class="page-subtitle">查看和管理您的B站数据分析记录</p>
    </div>

    <!-- 统计卡片区 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6">
          <div class="stat-card total">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ total }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card bv">
            <div class="stat-icon">
              <el-icon><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ bvCount }}</div>
              <div class="stat-label">BV查询</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card uid">
            <div class="stat-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ uidCount }}</div>
              <div class="stat-label">UID分析</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card today">
            <div class="stat-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayCount }}</div>
              <div class="stat-label">今日查询</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 类型筛选标签 -->
    <div class="filter-section">
      <div class="filter-tabs">
        <div 
          class="filter-tab" 
          :class="{ active: activeTab === 'all' }"
          @click="switchTab('all')"
        >
          <el-icon><Grid /></el-icon>
          <span>全部</span>
          <el-tag size="small" class="count-tag">{{ total }}</el-tag>
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: activeTab === 'bv' }"
          @click="switchTab('bv')"
        >
          <el-icon><VideoPlay /></el-icon>
          <span>BV查询</span>
          <el-tag size="small" type="primary" class="count-tag">{{ bvCount }}</el-tag>
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: activeTab === 'uuid' }"
          @click="switchTab('uuid')"
        >
          <el-icon><User /></el-icon>
          <span>UID分析</span>
          <el-tag size="small" type="success" class="count-tag">{{ uidCount }}</el-tag>
        </div>
      </div>
    </div>

    <!-- 历史记录列表 -->
    <div class="history-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="skeleton-loading">
        <div v-for="i in 3" :key="i" class="skeleton-item">
          <div class="skeleton-header">
            <div class="skeleton-avatar"></div>
            <div class="skeleton-lines">
              <div class="skeleton-line short"></div>
              <div class="skeleton-line"></div>
            </div>
          </div>
          <div class="skeleton-body">
            <div class="skeleton-line"></div>
            <div class="skeleton-line medium"></div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="historyList.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><DocumentDelete /></el-icon>
        </div>
        <h3>暂无历史记录</h3>
        <p>您还没有进行过任何查询或分析</p>
        <div class="empty-actions">
          <el-button type="primary" @click="goToQuery">
            <el-icon><VideoPlay /></el-icon>
            开始BV查询
          </el-button>
          <el-button @click="goToAnalysis">
            <el-icon><User /></el-icon>
            进行UID分析
          </el-button>
        </div>
      </div>

      <!-- 时间轴列表 -->
      <div v-else class="timeline-list">
        <div 
          v-for="(group, date) in groupedHistory" 
          :key="date"
          class="timeline-group"
        >
          <div class="timeline-date">
            <div class="date-badge">{{ formatGroupDate(date) }}</div>
            <div class="date-line"></div>
          </div>
          
          <div class="timeline-items">
            <div 
              v-for="item in group" 
              :key="item.bv || item.uid + item.query_time"
              class="timeline-card"
              :class="item.type"
            >
              <div class="card-left">
                <div class="type-icon" :class="item.type">
                  <el-icon v-if="item.type === 'bv'"><VideoPlay /></el-icon>
                  <el-icon v-else><User /></el-icon>
                </div>
                <div class="time-line">
                  <div class="time-dot"></div>
                  <div class="time-connector"></div>
                </div>
              </div>
              
              <div class="card-content">
                <div class="card-header">
                  <div class="header-main">
                    <el-tag :type="item.type === 'bv' ? 'primary' : 'success'" size="small" effect="light">
                      {{ item.type === 'bv' ? 'BV视频' : '用户分析' }}
                    </el-tag>
                    <span class="item-id">{{ item.bv || item.uid }}</span>
                  </div>
                  <span class="time-ago">{{ formatTimeAgo(item.query_time) }}</span>
                </div>
                
                <div class="card-body">
                  <div v-if="item.type === 'bv' && item.data" class="summary-text">
                    <el-icon><InfoFilled /></el-icon>
                    <span>{{ item.data }}</span>
                  </div>
                  
                  <div v-if="item.type === 'uuid' && item.sample_comments?.length" class="comments-preview">
                    <div class="preview-label">样本评论：</div>
                    <div class="comments-list">
                      <div 
                        v-for="(comment, idx) in item.sample_comments.slice(0, 2)" 
                        :key="idx"
                        class="comment-item"
                      >
                        <span class="quote-mark">"</span>
                        <span class="comment-text">{{ truncateText(comment, 50) }}</span>
                        <span class="quote-mark">"</span>
                      </div>
                      <div v-if="item.sample_comments.length > 2" class="more-comments">
                        +{{ item.sample_comments.length - 2 }} 条更多评论
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="card-footer">
                  <span class="exact-time">
                    <el-icon><Clock /></el-icon>
                    {{ formatExactTime(item.query_time) }}
                  </span>
                  <div class="card-actions">
                    <el-button 
                      v-if="item.type === 'bv'"
                      type="primary"
                      size="small"
                      :loading="loadingBV === item.bv"
                      @click="handleInsertVector(item.bv)"
                    >
                      <el-icon><Plus /></el-icon>
                      插入向量
                    </el-button>
                    <el-button 
                      v-else
                      type="success"
                      size="small"
                      @click="viewUidDetail(item.uid)"
                    >
                      <el-icon><View /></el-icon>
                      查看详情
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页器 -->
      <div v-if="historyList.length > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { 
  Document, 
  VideoPlay, 
  User, 
  Calendar,
  Grid,
  DocumentDelete,
  InfoFilled,
  Clock,
  Plus,
  View
} from '@element-plus/icons-vue';
import { getHistory, insertVectorByBV } from '@/api/bilibili';

const router = useRouter();

// 状态
const activeTab = ref('all');
const historyList = ref([]);
const loadingBV = ref('');
const loading = ref(false);

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 统计数据
const bvCount = ref(0);
const uidCount = ref(0);
const todayCount = ref(0);

// 加载历史
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
      // 计算统计数据
      calculateStats();
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
    ElMessage.error('加载历史记录失败');
  } finally {
    loading.value = false;
  }
};

// 计算统计数据
const calculateStats = () => {
  const allItems = historyList.value;
  bvCount.value = allItems.filter(item => item.type === 'bv').length;
  uidCount.value = allItems.filter(item => item.type === 'uuid').length;
  
  const today = new Date().toDateString();
  todayCount.value = allItems.filter(item => {
    const itemDate = new Date(item.query_time).toDateString();
    return itemDate === today;
  }).length;
};

// 按日期分组
const groupedHistory = computed(() => {
  const groups = {};
  historyList.value.forEach(item => {
    const date = new Date(item.query_time).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(item);
  });
  return groups;
});

// 切换标签
const switchTab = (tab) => {
  activeTab.value = tab;
  currentPage.value = 1;
  loadHistory();
};

// 分页处理
const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  currentPage.value = 1;
  loadHistory();
};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  loadHistory();
};

// 操作
const handleInsertVector = async (bvId) => {
  loadingBV.value = bvId;
  try {
    const response = await insertVectorByBV(bvId);
    if (response.code === 200) {
      ElMessage.success(`BV${bvId} 向量插入成功`);
    } else {
      ElMessage.error(response.message || '插入向量失败');
    }
  } catch (error) {
    console.error('插入向量失败:', error);
    ElMessage.error('插入向量失败，请检查网络连接或后端服务');
  } finally {
    loadingBV.value = '';
  }
};

const viewUidDetail = (uid) => {
  router.push(`/user-portrait?uid=${uid}`);
};

// 导航
const goToQuery = () => {
  router.push('/query');
};

const goToAnalysis = () => {
  router.push('/user-analysis');
};

// 格式化
const formatGroupDate = (dateStr) => {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  if (date.toDateString() === today.toDateString()) {
    return '今天';
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天';
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
  }
};

const formatTimeAgo = (timeStr) => {
  const date = new Date(timeStr);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 30) return `${days}天前`;
  return date.toLocaleDateString('zh-CN');
};

const formatExactTime = (timeStr) => {
  return new Date(timeStr).toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

const truncateText = (text, length) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

onMounted(() => {
  loadHistory();
});
</script>

<style scoped>
.history-management-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #065f46;
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

/* 统计卡片区 */
.stats-section {
  margin-bottom: 24px;
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

.stat-card.total {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  border: none;
}

.stat-card.bv {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
}

.stat-card.uid {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
}

.stat-card.today {
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

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  opacity: 0.9;
}

/* 筛选标签区 */
.filter-section {
  margin-bottom: 24px;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  background: white;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #6b7280;
}

.filter-tab:hover {
  background: #f3f4f6;
  color: #374151;
}

.filter-tab.active {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  box-shadow: 0 2px 8px rgba(6, 95, 70, 0.3);
}

.count-tag {
  margin-left: 4px;
}

.filter-tab.active .count-tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-color: transparent;
}

/* 历史内容区 */
.history-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

/* 骨架屏 */
.skeleton-loading {
  padding: 20px 0;
}

.skeleton-item {
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
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
}

.skeleton-lines {
  flex: 1;
}

.skeleton-line {
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.skeleton-line.short {
  width: 30%;
}

.skeleton-line.medium {
  width: 60%;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, rgba(6, 95, 70, 0.1), rgba(4, 120, 87, 0.1));
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
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

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 时间轴列表 */
.timeline-list {
  padding: 20px 0;
}

.timeline-group {
  margin-bottom: 32px;
}

.timeline-date {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.date-badge {
  background: linear-gradient(135deg, #065f46, #047857);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

.date-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(6, 95, 70, 0.3), transparent);
}

.timeline-items {
  padding-left: 20px;
  border-left: 2px solid rgba(6, 95, 70, 0.1);
  margin-left: 8px;
}

.timeline-card {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  position: relative;
}

.card-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.type-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  z-index: 2;
}

.type-icon.bv {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.type-icon.uuid {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.time-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: absolute;
  top: 40px;
  bottom: -20px;
}

.time-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(6, 95, 70, 0.3);
  margin-top: 8px;
}

.time-connector {
  flex: 1;
  width: 2px;
  background: rgba(6, 95, 70, 0.1);
  margin-top: 4px;
}

.card-content {
  flex: 1;
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(6, 95, 70, 0.08);
  transition: all 0.3s ease;
}

.card-content:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(6, 95, 70, 0.1);
  transform: translateX(4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-id {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  font-family: 'SF Mono', Monaco, monospace;
}

.time-ago {
  font-size: 13px;
  color: #9ca3af;
}

.card-body {
  margin-bottom: 12px;
}

.summary-text {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #4b5563;
  font-size: 14px;
}

.summary-text .el-icon {
  color: #065f46;
  margin-top: 2px;
}

.comments-preview {
  background: white;
  border-radius: 8px;
  padding: 12px;
}

.preview-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-item {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

.quote-mark {
  color: #065f46;
  font-weight: 600;
}

.comment-text {
  color: #4b5563;
}

.more-comments {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(6, 95, 70, 0.08);
}

.exact-time {
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* 分页器 */
.pagination-wrapper {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(6, 95, 70, 0.1);
  display: flex;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .history-management-page {
    padding: 16px;
  }
  
  .filter-tabs {
    flex-direction: column;
  }
  
  .timeline-items {
    padding-left: 12px;
    margin-left: 4px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
