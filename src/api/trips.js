import request from '@/utils/request'

export const getTrips = () => request.get('/trips')
export const getTrip = (id) => request.get(`/trips/${id}`)
export const createTrip = (data) => request.post('/trips', data)
export const updateTrip = (id, data) => request.put(`/trips/${id}`, data)
export const deleteTrip = (id) => request.delete(`/trips/${id}`)
export const copyTrip = (id) => request.post(`/trips/${id}/copy`)
export const checkDateConflict = (params) => request.get('/trips/check-date-conflict', { params })

// 管理员行程管理
export const getAdminTrips = (params) => request.get('/trips/admin/all', { params })
export const adminUpdateTripStatus = (id, data) => request.put(`/trips/admin/${id}/status`, data)
export const adminDeleteTrip = (id) => request.delete(`/trips/admin/${id}`)

// 活动
export const getActivities = (tripId) => request.get(`/trips/${tripId}/activities`)
export const createActivity = (tripId, data) => request.post(`/trips/${tripId}/activities`, data)
export const updateActivity = (tripId, actId, data) => request.put(`/trips/${tripId}/activities/${actId}`, data)
export const deleteActivity = (tripId, actId) => request.delete(`/trips/${tripId}/activities/${actId}`)
export const reorderActivities = (tripId, items) => request.put(`/trips/${tripId}/activities/reorder`, { items })
export const checkTimeConflict = (tripId, data) => request.post(`/trips/${tripId}/activities/check-conflict`, data)

// 导出
export const exportPdf = (tripId) => `/api/v1/trips/${tripId}/export/pdf`
export const exportExcel = (tripId) => `/api/v1/trips/${tripId}/export/excel`

// 分享
export const getShareInfo = (tripId) => request.get(`/trips/${tripId}/share-info`)
export const getQrcodeUrl = (tripId) => `/api/v1/trips/${tripId}/qrcode?base_url=${window.location.origin}`
