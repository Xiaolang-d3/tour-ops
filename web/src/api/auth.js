import request from '@/utils/request'

export const login = (data) => request.post('/auth/login', data)
export const register = (data) => request.post('/auth/register', data)
export const getMe = () => request.get('/auth/me')
export const updateProfile = (data) => request.put('/auth/profile', data)
export const getUsers = () => request.get('/auth/users')
export const updateUserRole = (userId, data) => request.put(`/auth/users/${userId}/role`, data)
export const deleteUser = (userId, force = false) => request.delete(`/auth/users/${userId}?force=${force}`)
export const createUser = (data) => request.post('/auth/create-user', data)
export const getAdminStats = () => request.get('/auth/admin/stats')
