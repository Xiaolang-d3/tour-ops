import request from '@/utils/request'

// 公开接口（无需登录）
export const submitPublicReview = (shareCode, data) => request.post(`/public/trips/${shareCode}/reviews`, data)
export const getPublicReviews = (shareCode) => request.get(`/public/trips/${shareCode}/reviews`)

// 登录用户接口
export const getTripReviews = (tripId) => request.get(`/trips/${tripId}/reviews`)
export const getTripReviewStats = (tripId) => request.get(`/trips/${tripId}/reviews/stats`)

// 管理员接口
export const getAdminReviewStats = () => request.get('/admin/reviews/stats')
