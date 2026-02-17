import request from '@/utils/request'

export const getTemplates = (category) => request.get('/templates', { params: category ? { category } : {} })
export const getTemplate = (id) => request.get(`/templates/${id}`)
export const createTemplate = (data) => request.post('/templates', data)
export const updateTemplate = (id, data) => request.put(`/templates/${id}`, data)
export const deleteTemplate = (id) => request.delete(`/templates/${id}`)
export const createTemplateFromTrip = (tripId, data) => request.post(`/templates/from-trip/${tripId}`, data)
export const createTripFromTemplate = (templateId, data) => request.post(`/templates/${templateId}/create-trip`, data)
