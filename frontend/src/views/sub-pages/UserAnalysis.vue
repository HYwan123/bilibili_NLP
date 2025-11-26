<template>
  <div class="user-analysis-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户画像分析系统</span>
        </div>
      </template>

      <!-- API配置 -->
      <el-form :model="apiConfig" label-width="100px" style="margin-bottom: 20px;">
        <el-form-item label="API Key">
          <el-input
            v-model="apiConfig.apiKey"
            type="password"
            placeholder="请输入API Key"
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item label="API 网址">
          <el-input
            v-model="apiConfig.apiUrl"
            placeholder="请输入API网址，例如：https://api.openai.com/v1"
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item label="模型ID">
          <el-input
            v-model="apiConfig.modelId"
            placeholder="请输入模型ID，例如：gpt-4o"
            clearable
          ></el-input>
        </el-form-item>
      </el-form>

      <!-- 输入 UID -->
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户UID">
          <el-input
            v-model="form.uid"
            placeholder="请输入B站用户UID"
            :disabled="loading"
            clearable
          ></el-input>
        </el-form-item>

        <!-- 按钮操作区 -->
        <el-form-item>
          <el-button type="primary" @click="fetchComments" :loading="loading" :disabled="!form.uid">
            {{ loading ? '获取中...' : '获取用户评论' }}
          </el-button>
          <el-button type="success" @click="getSavedComments" :loading="loadingSaved" :disabled="!form.uid">
            {{ loadingSaved ? '加载中...' : '查看已保存评论' }}
          </el-button>
          <el-button type="warning" @click="analyzeUser" :loading="analyzing" :disabled="!form.uid">
            分析用户画像
          </el-button>

        </el-form-item>
      </el-form>

      <!-- 消息展示 -->
      <div v-if="message" class="message-section">
        <el-alert :title="message" :type="messageType" :closable="false" show-icon />
      </div>

      <!-- 评论表格 -->
      <div v-if="retrievedComments.length > 0" class="comments-section">
        <h3>用户评论列表 (共{{ retrievedComments.length }}条)</h3>
        <el-table :data="retrievedComments" stripe style="width: 100%" height="300">
          <el-table-column type="index" width="50" />
          <el-table-column prop="comment_text" label="评论内容" />
        </el-table>
      </div>

      <!-- 用户画像分析结果 -->
      <div v-if="analysisResult" style="margin-top: 20px;">
        <h3>用户画像分析结果</h3>

          <div v-if="analysisResult.uid">
            <p><strong>用户UID:</strong> {{ analysisResult.uid }}</p>
            <p><strong>评论数量:</strong> {{ analysisResult.comment_count }}</p>
            <p><strong>分析时间:</strong> {{ formatTime(analysisResult.timestamp) }}</p>
          </div>
          <div v-if="analysisResult.analysis" style="margin-top: 15px;">
            <h4>分析内容:</h4>
            <!-- View mode toggle -->
            <div style="margin-bottom: 10px;">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button label="markdown">Markdown</el-radio-button>
                <el-radio-button label="mindmap">思维导图</el-radio-button>
              </el-radio-group>
            </div>

            <!-- Markdown view -->
            <div v-if="viewMode === 'markdown'" v-html="md.render(analysisResult.analysis)" class="markdown-content"></div>

            <!-- Mind map view -->
            <svg v-if="viewMode === 'mindmap'" ref="mindmapContainer" class="mindmap-container"></svg>
          </div>

      </div>
    </el-card>
  </div>
</template>


<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { getUserComments, getSavedUserComments } from '@/api/bilibili';
import request from '@/utils/request';
import MarkdownIt from 'markdown-it';

// Import markmap libraries
import { Transformer } from 'markmap-lib';
import { Markmap } from 'markmap-view';

const form = ref({
  uid: '66143532',
});

const apiConfig = ref({
  apiKey: '',
  apiUrl: '',
  modelId: ''
});

const loading = ref(false);
const loadingSaved = ref(false);
const loadingHistory = ref(false);
const analyzing = ref(false);

const retrievedComments = ref([]);
const analysisResult = ref(null);

const message = ref('');
const messageType = ref('info');

// View mode toggle
const viewMode = ref('markdown');

// Mind map refs
const mindmapContainer = ref(null);
let mm = null; // Markmap instance

const md = new MarkdownIt();

// Initialize markmap transformer
const transformer = new Transformer();

// Load saved API config from localStorage on component mount
onMounted(() => {
  const savedConfig = localStorage.getItem('userAnalysisApiConfig');
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig);
      apiConfig.value = {
        ...apiConfig.value,
        ...config
      };
    } catch (e) {
      console.error('Failed to parse saved API config:', e);
    }
  }
});

// Save API config to localStorage whenever it changes
watch(apiConfig.value, (newConfig) => {
  try {
    localStorage.setItem('userAnalysisApiConfig', JSON.stringify(newConfig));
  } catch (e) {
    console.error('Failed to save API config:', e);
  }
}, { deep: true });

// 获取评论（实时）
const fetchComments = async () => {
  const uid = parseInt(form.value.uid);
  if (!uid || uid <= 0) {
    ElMessage.error('请输入有效的用户UID');
    return;
  }

  loading.value = true;
  retrievedComments.value = [];
  message.value = '';

  try {
    const response = await getUserComments(uid);
    if (response.data && response.data.comments) {
      retrievedComments.value = response.data.comments;
      message.value = `成功获取 ${response.data.comment_count} 条评论`;
      messageType.value = 'success';
    } else {
      message.value = '未获取到评论数据';
      messageType.value = 'warning';
    }
  } catch (error) {
    message.value = `获取评论失败: ${error.message}`;
    messageType.value = 'error';
  } finally {
    loading.value = false;
  }
};

// 获取已保存评论
const getSavedComments = async () => {
  const uid = parseInt(form.value.uid);
  if (!uid || uid <= 0) {
    ElMessage.error('请输入有效的用户UID');
    return;
  }

  loadingSaved.value = true;
  retrievedComments.value = [];
  message.value = '';

  try {
    const response = await getSavedUserComments(uid);
    if (response.data && response.data.length > 0) {
      retrievedComments.value = response.data;
      message.value = `数据库中获取到 ${response.data.length} 条评论`;
      messageType.value = 'success';
    } else {
      message.value = '数据库中未找到评论，请先获取评论';
      messageType.value = 'info';
    }
  } catch (error) {
    message.value = `获取失败: ${error.message}`;
    messageType.value = 'error';
  } finally {
    loadingSaved.value = false;
  }
};

// 分析用户画像
const analyzeUser = async () => {
  const uid = form.value.uid;
  if (!uid) {
    ElMessage.error('请输入UID');
    return;
  }

  // 检查API配置
  if (!apiConfig.value.apiKey || !apiConfig.value.apiUrl) {
    ElMessage.warning('请先配置API Key和API网址');
    return;
  }

  analyzing.value = true;
  try {
    const res = await request.post(`/api/user/analyze/${uid}`, {
      api_key: apiConfig.value.apiKey,
      api_url: apiConfig.value.apiUrl,
      model_id: apiConfig.value.modelId
    });
    if (res.code === 200) {
      analysisResult.value = res.data;
      ElMessage.success('用户画像分析成功');
      // Initialize mind map when analysis result is available
      await nextTick();
      if (viewMode.value === 'mindmap' && analysisResult.value.analysis) {
        initializeMindMap(analysisResult.value.analysis);
      }
    } else {
      ElMessage.error(res.message || '分析失败');
    }
  } catch (e) {
    ElMessage.error(e.message || '分析请求失败');
  } finally {
    analyzing.value = false;
  }
};

// 获取历史分析结果
const getHistoryAnalysis = async () => {
  const uid = form.value.uid;
  if (!uid) {
    ElMessage.error('请输入UID');
    return;
  }

  loadingHistory.value = true;
  try {
    const res = await request.get(`/api/user/analysis/${uid}`);
    if (res.code === 200) {
      analysisResult.value = res.data;
      ElMessage.success('历史分析结果加载成功');
      // Initialize mind map when analysis result is available
      await nextTick();
      if (viewMode.value === 'mindmap' && analysisResult.value.analysis) {
        initializeMindMap(analysisResult.value.analysis);
      }
    } else {
      ElMessage.warning(res.message || '未找到历史记录');
    }
  } catch (e) {
    ElMessage.error(e.message || '请求失败');
  } finally {
    loadingHistory.value = false;
  }
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN');
};

// Initialize mind map with markdown content
const initializeMindMap = async (markdownContent) => {
  if (!mindmapContainer.value) return;

  try {
    // Transform markdown to markmap data
    const { root } = transformer.transform(markdownContent);

    if (!mm) {
      // Create new markmap instance if it doesn't exist
      mm = Markmap.create(mindmapContainer.value, null, root);
    } else {
      // Update existing markmap instance
      await mm.setData(root);
      mm.fit();
    }
  } catch (error) {
    console.error('Error initializing mind map:', error);
    ElMessage.error('思维导图初始化失败: ' + error.message);
  }
};

// Watch for view mode changes
watch(viewMode, async (newMode) => {
  if (newMode === 'mindmap' && analysisResult.value && analysisResult.value.analysis) {
    await nextTick();
    initializeMindMap(analysisResult.value.analysis);
  }
});

// Watch for analysis result changes
watch(analysisResult, async (newResult) => {
  if (viewMode.value === 'mindmap' && newResult && newResult.analysis) {
    await nextTick();
    initializeMindMap(newResult.analysis);
  }
});

// Handle window resize for mind map
onMounted(() => {
  const handleResize = () => {
    if (mm && viewMode.value === 'mindmap') {
      mm.fit(); // Adjust mind map to fit container
    }
  };

  window.addEventListener('resize', handleResize);

  // Cleanup event listener
  return () => {
    window.removeEventListener('resize', handleResize);
  };
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

.mindmap-container {
  width: 100%;
  height: 600px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background: white;
  margin-top: 10px;
}
</style>
