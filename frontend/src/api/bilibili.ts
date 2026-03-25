import request from '@/utils/request'
import type { BaseResponse } from '@/types/request'

export function getComments(bv: string) {
  return request({
    url: `/api/select/${bv}`,
    method: 'get'
  })
}

export function getCookies() {
  return request({
    url: `/api/get_cookies`,
    method: 'get'
  })
}

export function changeUserCookie(cookie: string) {
  return request({
    url: `/api/change_cookie_user`,
    method: 'post' ,
    data: { cookie }
  })
}

export function getuids() {
  return request({
    url: `/api/get_uids`,
    method: 'get'
  })
}
/**
 * 获取用户评论并保存到数据库
 * @param uid 用户ID
 */
export function getUserComments(uid: number) {
  return request({
    url: `/api/user/comments/${uid}`,
    method: 'post'
  })
}

/**
 * 从数据库获取已保存的用户评论
 * @param uid 用户ID
 */
export function getSavedUserComments(uid: number) {
  return request({
    url: `/api/user/comments/${uid}`,
    method: 'get'
  })
}

/**
 * 获取查询历史记录
 * @param params 分页参数 { page, page_size, type }
 */
export function getHistory(params?: { page?: number; page_size?: number; type?: string }) {
  return request({
    url: '/api/history',
    method: 'get',
    params
  })
}

export function getJobStatus(jobId: string) {
  return request({
    url: `/api/job/status/${jobId}`,
    method: 'get'
  })
}

/**
 * 提交用户评论获取任务
 * @param uid 用户ID
 */
export function userAnalysis(uid: string | number) {
  return request({
    url: `/api/user/analysis/${uid}`,
    method: 'post'
  })
} 

/**
 * 提交评论分析任务
 * @param bv_id BV视频ID
 */
export function submitCommentAnalysis(bv_id: string) {
  return request({
    url: `/api/comments/analyze/submit/${bv_id}`,
    method: 'post'
  })
}

/**
 * 获取指定BV视频的评论分析结果 (从缓存中)
 * @param bv_id BV视频ID
 */
export function getCommentAnalysis(bv_id: string) {
  return request({
    url: `/api/comments/analysis/${bv_id}`,
    method: 'get'
  })
}


export function get_history_data() {
  return request({
    url: `/api/history_data`,
    method: 'get'
  })
}

/**
 * 为指定用户生成内容推荐
 * @param uid 用户ID
 */
export function generateUserRecommendations(uid: number) {
  return request({
    url: `/api/recommendations/generate/${uid}`,
    method: 'post'
  })
}

/**
 * 获取用户的推荐结果
 * @param uid 用户ID
 */
export function getUserRecommendations(uid: number) {
  return request({
    url: `/api/recommendations/${uid}`,
    method: 'get'
  })
}

/**
 * 获取用户偏好分析结果
 * @param uid 用户ID
 */
export function getUserPreferences(uid: number) {
  return request({
    url: `/api/recommendations/preferences/${uid}`,
    method: 'get'
  })
}

/**
 * 获取可用的用户ID列表
 */
export function getAvailableUids() {
  return request({
    url: '/api/get_uids',
    method: 'get'
  })
}

/**
 * 获取示例视频数据
 */
export function getSampleVideos() {
  return request({
    url: '/api/recommendations/sample-videos',
    method: 'get'
  })
}

/**
 * 为用户生成推荐视频BV号 (新API)
 * @param uid 用户ID
 */
export function generateVideoRecommendations(uid: string) {
  return request({
    url: `/api/start_tuijian/${uid}`,
    method: 'post'
  })
}

/**
 * 获取推荐视频的详细信息 (新API)
 * @param uid 用户ID
 */
export function getRecommendedVideosInfo(uid: number) {
  return request({
    url: `/api/get_tuijian_video_info/${uid}`,
    method: 'get'
  })
}

/**
 * 将指定BV号的视频标签向量插入到向量数据库
 * @param bv_id BV视频ID
 */
export function insertVectorByBV(bv_id: string) {
  return request({
    url: `/api/insert_vector/${bv_id}`,
    method: 'post'
  })
}

/**
 * 获取单个视频的详细信息
 * @param bv_id BV视频ID
 */
export function getVideoInfo(bv_id: string) {
  return request({
    url: `/api/video/info/${bv_id}`,
    method: 'get'
  })
}

/**
 * Generate Bilibili login QR code
 */
export function generateBilibiliQRCode() {
  return request({
    url: `/api/bilibili/qrcode/generate`,
    method: 'post'
  })
}

/**
 * Poll Bilibili login status
 */
export function pollBilibiliLogin() {
  return request({
    url: `/api/bilibili/qrcode/poll`,
    method: 'post'
  })
}

/**
 * AI问答 - 完整对话模式
 * @param messages 对话消息列表 [{role: 'user'|'assistant', content: string}]
 * @param model 模型名称，默认 kimi-k2
 */
export function chatWithAI(messages: Array<{role: string, content: string}>, model?: string) {
  return request({
    url: `/api/chat`,
    method: 'post',
    data: { messages, model }
  })
}

/**
 * AI简单问答 - 单条消息快速回复
 * @param text 用户输入的消息
 */
export function chatWithAISimple(text: string) {
  return request({
    url: `/api/chat/simple`,
    method: 'post',
    params: { text }
  })
}

/**
 * AI问答 - 流式输出模式
 * @param messages 对话消息列表 [{role: 'user'|'assistant', content: string}]
 * @param onMessage 流式消息回调函数
 * @param model 模型名称，默认 glm-4.7-flash
 * @param systemPrompt 系统提示词
 */
export async function chatWithAIStream(
  messages: Array<{role: string, content: string}>,
  onMessage: (content: string, done: boolean) => void,
  model?: string,
  systemPrompt?: string
) {
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''
  const token = localStorage.getItem('token')
  
  // 如果没有提供model，则使用默认的GLM模型
  const modelToSend = model || 'glm-4.7-flash'
  
  const response = await fetch(`${baseURL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    },
    body: JSON.stringify({ messages, model: modelToSend, system_prompt: systemPrompt })
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  if (!reader) {
    throw new Error('无法获取响应流')
  }

  try {
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        onMessage('', true)
        break
      }

      buffer += decoder.decode(value, { stream: true })
      
      // 处理SSE格式：按两个换行符分割
      const messages = buffer.split('\n\n')
      // 保留最后一个可能未完成的片段
      buffer = messages.pop() || ''
      
      for (const message of messages) {
        if (!message.trim()) continue;
        // 检查是否是 'data:' 开头的SSE消息
        const dataMatch = message.match(/^data: (.*)$/m)
        if (dataMatch) {
          const data = dataMatch[1].trim()
          console.log('SSE data received:', data)
          
          if (data === '[DONE]') {
            onMessage('', true)
            return
          }
          
          try {
            const parsed = JSON.parse(data)
            console.log('Parsed:', parsed)
            if (parsed.content) {
              onMessage(parsed.content, false)
            } else if (parsed.error) {
              console.error('Stream error:', parsed.error)
              onMessage(`错误: ${parsed.error}`, true)
              return
            }
          } catch (e) {
            console.error('JSON parse error:', e, 'Raw:', data)
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
