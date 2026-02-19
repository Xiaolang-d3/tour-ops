import request from '@/utils/request'

export const getSharedTrip = (shareCode) => request.get(`/public/trips/${shareCode}`)

export const submitPartnerConfirm = (shareCode, data) => request.post(`/public/trips/${shareCode}/confirm`, data)

export const getPartnerConfirmations = (shareCode) => request.get(`/public/trips/${shareCode}/confirmations`)
