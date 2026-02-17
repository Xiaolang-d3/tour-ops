import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getMe } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isAdmin = computed(() => user.value?.role === 'admin')
  let fetchPromise = null

  async function fetchUser() {
    // 避免重复请求
    if (fetchPromise) return fetchPromise
    fetchPromise = getMe()
      .then(res => { user.value = res })
      .catch(() => { user.value = null })
      .finally(() => { fetchPromise = null })
    return fetchPromise
  }

  function logout() {
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, isAdmin, fetchUser, logout }
})
