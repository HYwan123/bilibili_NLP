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
 */
export function getHistory() {
  return request({
    url: '/api/history',
    method: 'get'
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
