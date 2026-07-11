import request from '@/utils/request'

export const getSharedTrip = (shareCode) => request.get(`/public/trips/${shareCode}`)
