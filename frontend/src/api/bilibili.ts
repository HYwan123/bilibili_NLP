import request from '@/utils/request'
import type { BaseResponse } from '@/types/request'

export function getComments(bv: string) {
  return request({
    url: `/api/select/${bv}`,
    method: 'get'
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