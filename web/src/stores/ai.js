import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import { getChatHistory, clearChatHistory, generateTripStream, aiChatStream, saveTripFromAI } from '@/api/ai'

export const useAiStore = defineStore('ai', () => {
  // ===== 聊天状态 =====
  const messages = ref([])
  const streaming = ref(false)
  const streamContent = ref('')
  const historyLoaded = ref(false)

  // 流式请求的 reader，用于切走时中断
  let _reader = null
  let _abortController = null

  async function loadHistory() {
    if (historyLoaded.value) return
    const history = await getChatHistory()
    messages.value = history
    historyLoaded.value = true
  }

  async function sendMessage(text) {
    if (!text.trim() || streaming.value) return
    messages.value.push({ role: 'user', content: text })
    streaming.value = true
    streamContent.value = ''
    _abortController = new AbortController()
    try {
      const token = localStorage.getItem('token')
      const history = messages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))
      const res = await aiChatStream({ message: text, history }, token)
      _reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await _reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') break
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) streamContent.value += parsed.content
            } catch {}
          }
        }
      }
      messages.value.push({ role: 'assistant', content: streamContent.value })
    } catch {
      // 如果有已接收的内容，保留它
      if (streamContent.value) {
        messages.value.push({ role: 'assistant', content: streamContent.value })
      } else {
        messages.value.push({ role: 'assistant', content: '抱歉，AI 暂时无法响应，请稍后再试。' })
      }
    } finally {
      streaming.value = false
      streamContent.value = ''
      _reader = null
      _abortController = null
    }
  }

  async function clearHistory() {
    await clearChatHistory()
    messages.value = []
  }

  // ===== 行程生成状态 =====
  const generating = ref(false)
  const suggestion = ref(null)
  const genStep = ref(0)
  const expandedDays = ref(new Set())
  let _genStepTimer = null

  const genForm = reactive({
    destination: '', trip_type: 'regular_tour', dateRange: null,
    participants: 2, budget_min: 3000, budget_max: 8000
  })

  const groupedSuggestionDays = computed(() => {
    if (!suggestion.value?.activities) return {}
    const groups = {}
    for (const act of suggestion.value.activities) {
      const d = act.day || 1
      if (!groups[d]) groups[d] = []
      groups[d].push(act)
    }
    return groups
  })

  function toggleDay(dayNum) {
    const s = new Set(expandedDays.value)
    if (s.has(dayNum)) s.delete(dayNum)
    else s.add(dayNum)
    expandedDays.value = s
  }

  function startGenSteps() {
    genStep.value = 0
    let step = 0
    _genStepTimer = setInterval(() => {
      step++
      genStep.value = step
      if (step >= 4) clearInterval(_genStepTimer)
    }, 2500)
  }

  function stopGenSteps() {
    if (_genStepTimer) clearInterval(_genStepTimer)
    genStep.value = 4
  }

  async function generate() {
    if (!genForm.destination || !genForm.dateRange) return false
    generating.value = true
    suggestion.value = null
    startGenSteps()
    try {
      const token = localStorage.getItem('token')
      const res = await generateTripStream({
        ...genForm,
        start_date: genForm.dateRange[0],
        end_date: genForm.dateRange[1],
        interests: []
      }, token)

      if (!res.ok) {
        stopGenSteps()
        return false
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let result = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') break
            try {
              const parsed = JSON.parse(data)
              if (parsed.type === 'result' && parsed.data) {
                result = parsed.data
              }
              // chunk 类型不需要处理，只是保持连接活跃
            } catch {}
          }
        }
      }

      stopGenSteps()
      if (result) {
        suggestion.value = result
        expandedDays.value = new Set(Object.keys(groupedSuggestionDays.value).map(Number))
        return true
      }
      return false
    } catch {
      stopGenSteps()
      return false
    } finally {
      generating.value = false
    }
  }

  function resetGenForm() {
    suggestion.value = null
  }

  return {
    // 聊天
    messages, streaming, streamContent, historyLoaded,
    loadHistory, sendMessage, clearHistory,
    // 生成
    generating, suggestion, genStep, expandedDays, genForm,
    groupedSuggestionDays, toggleDay, generate, resetGenForm,
  }
})
