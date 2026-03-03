<template>
  <div class="history-management-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">查询历史</h1>
      <p class="page-subtitle">查看和管理您的B站数据分析记录</p>
    </div>

    <!-- 统计卡片区 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-card total">
            <div class="stat-icon"><el-icon><Document /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ total }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-card bv">
            <div class="stat-icon"><el-icon><VideoPlay /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ bvCount }}</div>
              <div class="stat-label">BV查询</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-card uid">
            <div class="stat-icon"><el-icon><User /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">{{ uidCount }}</div>
              <div class="stat-label">UID分析</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6" :md="6">
          <div class="stat-card today">
            <div class="stat-icon"><el-icon><Calendar /></el-icon></div>
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

      <div v-else-if="historyList.length === 0" class="empty-state">
        <div class="empty-icon"><el-icon><DocumentDelete /></el-icon></div>
        <h3>暂无历史记录</h3>
        <p>您还没有进行过任何查询或分析</p>
        <div class="empty-actions">
          <el-button type="primary" @click="goToQuery">开始BV查询</el-button>
          <el-button @click="goToAnalysis">进行UID分析</el-button>
        </div>
      </div>

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
              :key="getItemKey(item)"
              class="timeline-card"
              :class="[item.type, { 'is-expanded': isExpanded(item) }]"
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
                    <div class="type-tag" :class="item.type">
                      {{ item.type === 'bv' ? '视频查询' : '用户画像' }}
                    </div>
                    <span class="item-id">{{ item.bv || item.uid }}</span>
                  </div>
                  <span class="time-ago">{{ formatTimeAgo(item.query_time) }}</span>
                </div>
                
                <div class="card-body">
                  <!-- BV 视频摘要 -->
                  <div v-if="item.type === 'bv' && item.data" class="summary-container">
                    <div class="summary-text">
                      {{ item.data }}
                    </div>
                    <div class="expand-action">
                      <el-button 
                        type="primary" 
                        link 
                        size="small" 
                        class="expand-btn"
                        @click="viewBvDetail(item.bv)"
                      >
                        <el-icon><View /></el-icon>
                        查看视频详细分析
                      </el-button>
                    </div>
                  </div>
                  
                  <!-- UID 用户评论样板 -->
                  <div v-if="item.type === 'uuid' && item.sample_comments?.length" class="comments-preview">
                    <div class="preview-label">
                      <el-icon><ChatDotRound /></el-icon>
                      核心样本评论
                    </div>
                    <div class="comments-list">
                      <div 
                        v-for="(comment, idx) in (isExpanded(item) ? item.sample_comments : item.sample_comments.slice(0, 2))" 
                        :key="idx"
                        class="comment-item"
                      >
                        <span class="quote-mark">“</span>
                        <span class="comment-text">{{ truncateText(comment, isExpanded(item) ? 500 : 150) }}</span>
                        <span class="quote-mark">”</span>
                      </div>
                      
                      <div v-if="item.sample_comments.length > 2" class="comments-toggle">
                        <el-button 
                          type="primary" 
                          link 
                          size="small" 
                          @click="toggleExpand(item)"
                        >
                          <el-icon>
                            <ArrowDown v-if="!isExpanded(item)" />
                            <ArrowUp v-else />
                          </el-icon>
                          {{ isExpanded(item) ? '收起评论' : `展开全部 ${item.sample_comments.length} 条评论` }}
                        </el-button>
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
  Document, VideoPlay, User, Calendar, Grid, DocumentDelete,
  InfoFilled, Clock, Plus, View, ArrowDown, ArrowUp, ChatDotRound
} from '@element-plus/icons-vue';
import { getHistory, insertVectorByBV } from '@/api/bilibili';

const router = useRouter();

// 状态
const activeTab = ref('all');
const historyList = ref([]);
const loadingBV = ref('');
const loading = ref(false);
const expandedIds = ref(new Set());

// 分页
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

const bvCount = ref(0);
const uidCount = ref(0);
const todayCount = ref(0);

// 获取项的唯一Key
const getItemKey = (item) => {
  const time = item.query_time || '';
  const id = item.bv || item.uid || '';
  return `${item.type}_${id}_${time}`;
};

const isExpanded = (item) => {
  return expandedIds.value.has(getItemKey(item));
};

const toggleExpand = (item) => {
  const key = getItemKey(item);
  if (expandedIds.value.has(key)) {
    expandedIds.value.delete(key);
  } else {
    expandedIds.value.add(key);
  }
  // Vue Set 响应式触发技巧
  expandedIds.value = new Set(expandedIds.value);
};

// 加载历史
const loadHistory = async () => {
  loading.value = true;
  expandedIds.value.clear();
  expandedIds.value = new Set();
  
  try {
    const response = await getHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      type: activeTab.value
    });
    
    if (response.data) {
      historyList.value = response.data.items || [];
      total.value = response.data.total || 0;
      
      if (activeTab.value === 'all') {
        bvCount.value = response.data.bv_total || 0;
        uidCount.value = response.data.uuid_total || 0;
      } else if (activeTab.value === 'bv') {
        bvCount.value = response.data.total || 0;
      } else if (activeTab.value === 'uuid') {
        uidCount.value = response.data.total || 0;
      }
      
      calculateTodayStats();
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
    ElMessage.error('加载历史记录失败');
  } finally {
    loading.value = false;
  }
};

const calculateTodayStats = () => {
  const today = new Date().toDateString();
  todayCount.value = historyList.value.filter(item => {
    return new Date(item.query_time).toDateString() === today;
  }).length;
};

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

const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  currentPage.value = 1;
  loadHistory();
};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  loadHistory();
};

const handleInsertVector = async (bvId) => {
  loadingBV.value = bvId;
  try {
    const response = await insertVectorByBV(bvId);
    if (response.code === 200) ElMessage.success(`BV${bvId} 向量插入成功`);
    else ElMessage.error(response.message || '插入向量失败');
  } catch (error) {
    ElMessage.error('插入向量失败，请检查网络连接或后端服务');
  } finally {
    loadingBV.value = '';
  }
};

const viewUidDetail = (uid) => {
  router.push(`/user-portrait?uid=${uid}`);
};

const viewBvDetail = (bvId) => {
  router.push({ path: '/comment-analysis', query: { bv: bvId } });
};

const goToQuery = () => router.push('/query');
const goToAnalysis = () => router.push('/user-analysis');

const formatGroupDate = (dateStr) => {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return '今天';
  if (date.toDateString() === yesterday.toDateString()) return '昨天';
  return date.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
};

const formatTimeAgo = (timeStr) => {
  const diff = new Date() - new Date(timeStr);
  const min = Math.floor(diff / 60000);
  const hr = Math.floor(diff / 3600000);
  if (min < 1) return '刚刚';
  if (min < 60) return `${min}分钟前`;
  if (hr < 24) return `${hr}小时前`;
  return new Date(timeStr).toLocaleDateString('zh-CN');
};

const formatExactTime = (timeStr) => {
  return new Date(timeStr).toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit' });
};

const truncateText = (text, length) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

onMounted(() => loadHistory());
</script>

<style scoped>
.history-management-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--bg-secondary);
  min-height: 100vh;
}

.page-header { margin-bottom: 32px; text-align: center; }
.page-title { font-size: 32px; font-weight: 700; color: var(--primary-color); margin: 0 0 8px 0; }
.page-subtitle { font-size: 15px; color: var(--text-secondary); }

.stats-section { margin-bottom: 32px; }
.stat-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
.stat-card.total { background: linear-gradient(135deg, #007AFF, #0051D5); color: white; border: none; }
.stat-card.bv { background: linear-gradient(135deg, #5E5CE6, #3634A3); color: white; border: none; }
.stat-card.uid { background: linear-gradient(135deg, #34C759, #248A3D); color: white; border: none; }
.stat-card.today { background: linear-gradient(135deg, #FF9500, #C97300); color: white; border: none; }

.stat-icon { width: 56px; height: 56px; border-radius: 14px; background: rgba(255, 255, 255, 0.2); display: flex; align-items: center; justify-content: center; font-size: 28px; }
.stat-value { font-size: 32px; font-weight: 700; margin-bottom: 6px; }
.stat-label { font-size: 14px; opacity: 0.9; }

.filter-section { margin-bottom: 32px; }
.filter-tabs { display: flex; gap: 12px; background: var(--bg-card); padding: 8px; border-radius: 14px; border: 1px solid var(--border-light); }
.filter-tab { flex: 1; display: flex; align-items: center; justify-content: center; gap: 10px; padding: 12px 24px; border-radius: 10px; cursor: pointer; transition: all 0.25s ease; font-weight: 600; color: var(--text-secondary); }
.filter-tab.active { background: var(--primary-color); color: white; box-shadow: 0 4px 12px rgba(0, 122, 255, 0.25); }

.timeline-group { margin-bottom: 40px; }
.timeline-date { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.date-badge { background: var(--bg-card); padding: 8px 20px; border-radius: 20px; font-weight: 700; box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); }
.date-line { flex: 1; height: 1px; background: var(--separator-color); opacity: 0.5; }

.timeline-items { padding-left: 24px; border-left: 2px solid var(--border-light); margin-left: 8px; }
.timeline-card { display: flex; gap: 20px; margin-bottom: 24px; }

.type-icon { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; color: white; z-index: 2; }
.type-icon.bv { background: var(--primary-color); }
.type-icon.uuid { background: var(--success-color); }

.card-content { flex: 1; background: var(--bg-card); border-radius: 16px; padding: 24px; border: 1px solid var(--border-light); transition: all 0.3s ease; box-shadow: var(--shadow-sm); min-width: 0; }
.card-content:hover { border-color: var(--primary-color); transform: translateX(6px); }

.type-tag { padding: 4px 12px; border-radius: 8px; font-size: 12px; font-weight: 700; }
.type-tag.bv { background: rgba(0, 122, 255, 0.1); color: var(--primary-color); }
.type-tag.uuid { background: rgba(52, 199, 89, 0.1); color: var(--success-color); }

.summary-container, .comments-preview { background: var(--bg-secondary); border-radius: 12px; padding: 16px; border: 1px solid var(--border-light); margin-top: 12px; }

.summary-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 关键修复：展开状态下的样式 */
.summary-text.is-expanded {
  display: block !important;
  -webkit-line-clamp: unset !important;
  overflow: visible !important;
}

.expand-action { margin-top: 10px; }
.comment-item { font-size: 14px; color: var(--text-secondary); line-height: 1.6; padding-left: 12px; position: relative; margin-bottom: 8px; }
.quote-mark { color: var(--primary-color); font-size: 20px; font-family: Georgia, serif; }

.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px solid var(--border-light); margin-top: 16px; }
.pagination-wrapper { margin-top: 40px; padding: 24px; background: var(--bg-card); border-radius: 16px; display: flex; justify-content: center; }

html.dark .summary-container, html.dark .comments-preview { background: rgba(255, 255, 255, 0.03); }
</style>
