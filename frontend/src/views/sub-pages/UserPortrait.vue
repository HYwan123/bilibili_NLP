<template>
  <div class="user-portrait">
    <h2>历史用户画像分析记录</h2>

    <!-- 历史 UID 列表 -->
    <el-table :data="uidList" style="width: 100%; margin-top: 20px;" v-loading="loadingHistory">
      <el-table-column prop="uid" label="用户UID" width="200" />
      <el-table-column label="评论预览">
        <template #default="{ row }">
          <div v-if="commentPreviewMap[row.uid] && commentPreviewMap[row.uid].length > 0">
            <div v-for="(comment, idx) in commentPreviewMap[row.uid]" :key="idx" class="preview-comment">
              <span style="color: #999;">{{ idx + 1 }}.</span> {{ comment.comment_text }}
            </div>
          </div>
          <div v-else style="color: #ccc;">无</div>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="viewUserComments(row.uid, 10)">前10条评论</el-button>
          <el-button type="primary" size="small" @click="viewAnalysis(row.uid)">
            查看画像
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 弹出用户画像分析结果 -->
    <el-dialog v-model="dialogVisible" title="用户画像分析结果" width="600px" :before-close="handleCloseDialog">
      <div v-if="analysisResult" class="analysis-content">
        <p><strong>用户UID:</strong> {{ analysisResult.uid }}</p>
        <p><strong>评论数量:</strong> {{ analysisResult.comment_count }}</p>
        <p><strong>分析时间:</strong> {{ formatTime(analysisResult.timestamp) }}</p>
        <div class="analysis-section">
          <h4>分析内容:</h4>
          <div v-html="md.render(analysisResult.analysis)" class="markdown-content"></div>
        </div>
        <div v-if="sampleCommentsToShow.length > 0" style="margin-top: 15px;">
          <h4>样本评论:</h4>
          <el-table :data="sampleCommentsToShow" style="width: 100%;">
            <el-table-column type="index" width="50" />
            <el-table-column v-if="isStringArray" label="评论内容">
              <template #default="scope">{{ scope.row }}</template>
            </el-table-column>
            <el-table-column v-else prop="comment_text" label="评论内容" />
          </el-table>
          <div v-if="showExpandBtn" style="margin-top: 8px; text-align: right;">
            <el-button size="small" @click="toggleExpand">{{ expanded ? '收起' : '展开全部' }}</el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="commentDialogVisible" title="用户前10条评论" width="600px">
      <el-table :data="commentsToShow" style="width: 100%;">
        <el-table-column type="index" width="50" />
        <el-table-column prop="comment_text" label="评论内容" />
      </el-table>
      <template #footer>
        <el-button @click="commentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import request from '@/utils/request';
import MarkdownIt from 'markdown-it';

const uidList = ref<{ uid: string }[]>([]);
const analysisResult = ref<any>(null);
const dialogVisible = ref(false);
const loadingHistory = ref(false);

const error = ref('');

const expanded = ref(false);
const maxShow = 3;

const isStringArray = computed(() => {
  const arr = analysisResult.value?.sample_comments;
  return Array.isArray(arr) && arr.length > 0 && typeof arr[0] === 'string';
});

const sampleCommentsToShow = computed(() => {
  const arr = analysisResult.value?.sample_comments || [];
  if (!expanded.value) {
    return arr.slice(0, maxShow);
  }
  return arr;
});

const showExpandBtn = computed(() => {
  const arr = analysisResult.value?.sample_comments || [];
  return arr.length > maxShow;
});

const toggleExpand = () => {
  expanded.value = !expanded.value;
};

const userComments = ref<any[]>([]);
const commentDialogVisible = ref(false);
const commentLimit = ref(10);

const viewUserComments = async (uid: string, limit: number) => {
  commentLimit.value = limit;
  try {
    const res = await request.get(`/api/user/comments/${uid}`);
    if (Array.isArray(res.data)) {
      userComments.value = res.data;
      commentDialogVisible.value = true;
    } else {
      userComments.value = [];
      commentDialogVisible.value = true;
    }
  } catch (e) {
    userComments.value = [];
    commentDialogVisible.value = true;
  }
};

const commentsToShow = computed(() => {
  if (commentLimit.value > 0) {
    return userComments.value.slice(0, commentLimit.value);
  }
  return userComments.value;
});

const commentPreviewMap = ref<Record<string, any[]>>({});

const fetchCommentPreviews = async (uids: string[]) => {
  const map: Record<string, any[]> = {};
  await Promise.all(uids.map(async (uid) => {
    try {
      const res = await request.get(`/api/user/comments/${uid}`);
      if (Array.isArray(res.data)) {
        map[uid] = res.data.slice(0, 3);
      } else {
        map[uid] = [];
      }
    } catch {
      map[uid] = [];
    }
  }));
  commentPreviewMap.value = map;
};

// 获取 UID 列表
const fetchUidList = async () => {
  loadingHistory.value = true;
  try {
    const res = await request.get('/api/get_uids'); // res.data 就是数组了
    const uidArray = res.data; // 直接就是 [{uid: 15133257}, ...]
    if (Array.isArray(uidArray)) {
      uidList.value = uidArray;  // 直接赋值，数组格式已经符合 el-table 要求
    } else {
      error.value = '未获取到UID列表';
    }
  } catch (e: any) {
    error.value = e.message || '请求失败';
  } finally {
    loadingHistory.value = false;
  }
};


// 查看某个 UID 的分析结果
const viewAnalysis = async (uid: string) => {
  try {
    const res = await request.get(`/api/user/analysis/${uid}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
      dialogVisible.value = true;
      expanded.value = false;
    } else {
      error.value = res.message || '未找到分析记录';
    }
  } catch (e: any) {
    error.value = e.message || '请求失败';
  }
};

const handleCloseDialog = () => {
  dialogVisible.value = false;
  analysisResult.value = null;
};

const md = new MarkdownIt();

const formatTime = (timestamp: string) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
};

// 页面加载时请求 UID 列表
onMounted(async () => {
  await fetchUidList();
  // 获取所有UID的前3条评论
  const uids = uidList.value.map(item => String(item.uid));
  if (uids.length > 0) {
    await fetchCommentPreviews(uids);
  }
});
</script>
<style scoped>
.user-analysis-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-section {
  margin-top: 20px;
}

.comments-section {
  margin-top: 20px;
}

.preview-comment {
  font-size: 13px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 2px;
  word-break: break-all;
}

.analysis-content {
  padding: 15px;
}

.analysis-section {
  margin-top: 15px;
}

.markdown-content {
  line-height: 1.6;
  padding: 10px 0;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: bold;
}

.markdown-content p {
  margin: 8px 0;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-content li {
  margin: 4px 0;
}

.markdown-content code {
  background-color: #f4f4f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}

.markdown-content pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

.markdown-content blockquote {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  margin: 8px 0;
  color: #666;
}
</style>