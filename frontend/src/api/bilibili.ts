import request from '@/utils/request'
import type { BaseResponse } from '@/types/request'

export function getComments(bv: string) {
  return request({
    url: `/api/select/${bv}`,
    method: 'get'
  })
}

/**
 * 提交用户分析任务
 * @param uid 用户ID
 */
export function userAnalysis(uid: number) {
  return request({
    url: `/api/user/analysis/${uid}`,
    method: 'post'
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
 * 获取用户评论数据
 * @param uid 用户ID
 */
export function getUserComments(uid: number) {
  return request({
    url: `/api/user/comments/${uid}`,
    method: 'get'
  })
} 