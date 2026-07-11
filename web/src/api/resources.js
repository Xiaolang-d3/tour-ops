import request from '@/utils/request'

export const getGuides = () => request.get('/resources/guides')
export const createGuide = (data) => request.post('/resources/guides', data)
export const deleteGuide = (id) => request.delete(`/resources/guides/${id}`)
export const getAvailableGuides = (start, end) => request.get('/resources/guides/available', { params: { start, end } })

export const getVehicles = () => request.get('/resources/vehicles')
export const createVehicle = (data) => request.post('/resources/vehicles', data)
export const deleteVehicle = (id) => request.delete(`/resources/vehicles/${id}`)
export const getAvailableVehicles = (start, end) => request.get('/resources/vehicles/available', { params: { start, end } })

export const getHotels = () => request.get('/resources/hotels')
export const createHotel = (data) => request.post('/resources/hotels', data)
export const deleteHotel = (id) => request.delete(`/resources/hotels/${id}`)

export const getRestaurants = () => request.get('/resources/restaurants')
export const createRestaurant = (data) => request.post('/resources/restaurants', data)
export const deleteRestaurant = (id) => request.delete(`/resources/restaurants/${id}`)

export const getResourceSchedule = (type, id, start, end) =>
  request.get(`/resources/${type}/${id}/schedule`, { params: { start, end } })
