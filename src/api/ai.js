import request from '@/utils/request'

export const generateTrip = (data) => request.post('/ai/generate', data, { timeout: 180000 })

// 流式生成行程（SSE）
export const generateTripStream = (data, token) => {
  return fetch('/api/v1/ai/generate/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
}
export const aiChat = (data) => request.post('/ai/chat', data)
export const getChatHistory = (limit = 50) => request.get('/ai/chat/history', { params: { limit } })
export const clearChatHistory = () => request.delete('/ai/chat/history')

export const saveTripFromAI = (data) => request.post('/ai/save-trip', data)

export const recommendActivities = (data) => request.post('/ai/recommend-activities', data, { timeout: 120000 })

export const chatGenerateTrip = (data) => request.post('/ai/chat/generate-trip', data, { timeout: 120000 })

// SSE 流式对话
export const aiChatStream = (data, token) => {
  return fetch('/api/v1/ai/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(data)
  })
}
