m<template>
  <div class="ai-page">
    <!-- 左侧：AI 对话 -->
    <div class="chat-panel" :class="{ 'mobile-show': mobileTab === 'chat' }">
      <div class="chat-panel-header">
        <div class="chat-title">
          <div class="chat-title-icon">
            <el-icon size="18" color="#fff"><ChatDotRound /></el-icon>
          </div>
          <div class="chat-title-text">
            <span class="chat-title-name">AI 旅行助手</span>
            <span class="chat-title-status">
              <span class="status-dot" :class="{ active: streaming }"></span>
              {{ streaming ? '正在回复...' : '在线' }}
            </span>
          </div>
        </div>
        <el-button class="clear-btn" text size="small" @click="handleClear" :disabled="!messages.length && !streaming">
          <el-icon><Delete /></el-icon> 清空对话
        </el-button>
      </div>

      <div ref="chatBox" class="chat-box">
        <!-- 欢迎页 -->
        <div v-if="!messages.length && !streaming" class="welcome">
          <div class="welcome-glow"></div>
          <div class="welcome-emoji">🧳</div>
          <h3>你好，我是 AI 旅行助手</h3>
          <p>我可以帮你规划行程、推荐景点、解答旅行问题</p>
          <div class="quick-prompts">
            <div v-for="(p, idx) in quickPrompts" :key="idx" class="quick-card" @click="sendQuick(p.text)">
              <span class="quick-icon">{{ p.icon }}</span>
              <span class="quick-text">{{ p.text }}</span>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <template v-for="(msg, i) in messages" :key="i">
          <div :class="['msg', msg.role]">
            <div class="msg-avatar">
              <div v-if="msg.role === 'user'" class="avatar avatar-user">
                <el-icon size="16"><User /></el-icon>
              </div>
              <div v-else class="avatar avatar-ai">AI</div>
            </div>
            <div class="msg-body">
              <div class="bubble" v-if="msg.role === 'user'">{{ msg.content }}</div>
              <div class="bubble md-content" v-else v-html="renderMd(getDisplayContent(msg.content))"></div>
              <div v-if="msg.role === 'assistant' && extractTripJson(msg.content)" class="bubble-action">
                <el-button size="small" type="primary" round @click="openChatTripDialog(msg.content)">
                  <el-icon><FolderAdd /></el-icon> 添加到行程
                </el-button>
              </div>
            </div>
          </div>
        </template>

        <!-- 流式输出 -->
        <div v-if="streaming" class="msg assistant">
          <div class="msg-avatar"><div class="avatar avatar-ai">AI</div></div>
          <div class="msg-body">
            <div class="bubble md-content streaming-bubble" v-if="streamContent" v-html="renderMd(streamContent)"></div>
            <div class="bubble typing-bubble" v-else>
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-area">
        <div class="chat-input-bar">
          <input
            ref="chatInput"
            v-model="input"
            class="chat-input"
            placeholder="输入你的旅行问题..."
            @keyup.enter="handleSend"
            :disabled="streaming"
          />
          <button class="send-btn" :class="{ active: input.trim() && !streaming, loading: streaming }" @click="handleSend" :disabled="!input.trim() || streaming">
            <el-icon v-if="!streaming" size="18"><Promotion /></el-icon>
            <div v-else class="send-loading">
              <span></span><span></span><span></span>
            </div>
          </button>
        </div>
        <div class="input-hint">按 Enter 发送 · AI 回复仅供参考</div>
      </div>
    </div>

    <!-- 移动端切换按钮 -->
    <div class="mobile-tab-bar">
      <button class="mobile-tab" :class="{ active: mobileTab === 'chat' }" @click="mobileTab = 'chat'">
        <el-icon size="16"><ChatDotRound /></el-icon> 对话
      </button>
      <button class="mobile-tab" :class="{ active: mobileTab === 'gen' }" @click="mobileTab = 'gen'">
        <el-icon size="16"><MagicStick /></el-icon> 生成行程
      </button>
    </div>

    <!-- 右侧：AI 生成行程 -->
    <div class="gen-panel" :class="{ 'mobile-show': mobileTab === 'gen' }">
      <div class="gen-panel-header">
        <div class="chat-title">
          <div class="gen-title-icon">
            <el-icon size="18" color="#fff"><MagicStick /></el-icon>
          </div>
          <span class="chat-title-name">智能行程生成</span>
        </div>
        <el-button v-if="suggestion && !generating" class="clear-btn" text size="small" @click="aiStore.resetGenForm()">
          <el-icon><RefreshLeft /></el-icon> 重新填写
        </el-button>
      </div>

      <div class="gen-panel-body">
        <!-- 生成中状态 -->
        <div v-if="generating" class="gen-loading-state">
          <div class="gen-loading-orb">
            <div class="orb-ring"></div>
            <el-icon size="28" color="#8b5cf6"><MagicStick /></el-icon>
          </div>
          <h4>AI 正在规划行程...</h4>
          <p>正在为「{{ genForm.destination }}」生成最佳方案</p>
          <div class="gen-loading-steps">
            <div class="step" :class="{ done: genStep >= 1 }"><span class="step-dot"></span> 分析需求</div>
            <div class="step" :class="{ done: genStep >= 2 }"><span class="step-dot"></span> 规划路线</div>
            <div class="step" :class="{ done: genStep >= 3 }"><span class="step-dot"></span> 安排活动</div>
            <div class="step" :class="{ done: genStep >= 4 }"><span class="step-dot"></span> 优化方案</div>
          </div>
        </div>

        <!-- 生成结果 -->
        <div v-else-if="suggestion" class="suggestion-result">
          <div class="suggestion-header">
            <div class="suggestion-title-row">
              <span class="suggestion-icon">🎯</span>
              <h4>{{ suggestion.title }}</h4>
            </div>
            <p class="suggestion-summary">{{ suggestion.summary }}</p>
            <div class="suggestion-tags">
              <span class="stag days"><el-icon size="12"><Calendar /></el-icon> {{ suggestion.total_days }}天</span>
              <span class="stag budget"><el-icon size="12"><Money /></el-icon> ¥{{ suggestion.estimated_budget }}/人</span>
              <span class="stag acts"><el-icon size="12"><List /></el-icon> {{ suggestion.activities.length }}个活动</span>
            </div>
          </div>

          <!-- 按天分组的活动 -->
          <div class="suggestion-days">
            <template v-for="(dayActs, dayNum) in groupedSuggestionDays" :key="dayNum">
              <div v-if="showAllDays || Number(dayNum) <= 3" class="sug-day">
                <div class="sug-day-header" @click="toggleDay(dayNum)">
                  <span class="sug-day-label">第{{ dayNum }}天</span>
                  <span class="sug-day-count">{{ dayActs.length }}项活动</span>
                  <el-icon size="12" :class="{ 'is-rotate': expandedDays.has(dayNum) }"><ArrowDown /></el-icon>
                </div>
                <div v-show="expandedDays.has(dayNum)" class="sug-day-acts">
                  <div v-for="act in dayActs" :key="`${act.day}-${act.time}`" class="tl-item">
                    <div class="tl-type-icon" :class="act.type">{{ actTypeEmoji(act.type) }}</div>
                    <div class="tl-content">
                      <div class="tl-name">{{ act.name }}</div>
                      <div class="tl-meta">
                        <span class="tl-time">{{ act.time }}</span>
                        <span v-if="act.duration" class="tl-dur">{{ act.duration }}</span>
                      </div>
                    </div>
                    <span v-if="act.estimated_cost" class="tl-cost">¥{{ act.estimated_cost }}</span>
                  </div>
                </div>
              </div>
            </template>
            <button v-if="!showAllDays && totalSuggestionDays > 3" class="show-more-days" @click="showAllDays = true">
              查看剩余 {{ totalSuggestionDays - 3 }} 天 <el-icon size="12"><ArrowDown /></el-icon>
            </button>
            <button v-if="showAllDays && totalSuggestionDays > 3" class="show-more-days" @click="showAllDays = false">
              收起 <el-icon size="12"><ArrowUp /></el-icon>
            </button>
          </div>

          <!-- 贴士 -->
          <div v-if="suggestion.tips && suggestion.tips.length" class="suggestion-tips">
            <div class="tips-title">💡 出行贴士</div>
            <div v-for="(tip, i) in suggestion.tips" :key="i" class="tip-item">{{ tip }}</div>
          </div>
        </div>

        <!-- 表单（默认状态） -->
        <div v-else class="gen-form">
          <!-- 目的地 + 热门标签 -->
          <div class="form-group">
            <label class="form-label">
              <el-icon size="14"><Location /></el-icon> 目的地
            </label>
            <el-input v-model="genForm.destination" placeholder="输入目的地..." clearable class="dest-input" />
            <div class="hot-tags">
              <span class="hot-tag" v-for="t in hotDests" :key="t" :class="{ active: genForm.destination === t }" @click="genForm.destination = t">{{ t }}</span>
            </div>
          </div>

          <!-- 出行类型：图标卡片 -->
          <div class="form-group">
            <label class="form-label">
              <el-icon size="14"><Suitcase /></el-icon> 出行类型
            </label>
            <div class="type-cards">
              <div v-for="tp in tripTypes" :key="tp.value" class="type-card" :class="{ active: genForm.trip_type === tp.value }" @click="genForm.trip_type = tp.value">
                <span class="type-card-icon">{{ tp.icon }}</span>
                <span class="type-card-label">{{ tp.label }}</span>
              </div>
            </div>
          </div>

          <!-- 日期 + 人数 同一行 -->
          <div class="form-row-2">
            <div class="form-group" style="flex:1.4;min-width:0">
              <label class="form-label">
                <el-icon size="14"><Calendar /></el-icon> 出行日期
              </label>
              <el-date-picker v-model="genForm.dateRange" type="daterange" value-format="YYYY-MM-DD" style="width:100%" start-placeholder="出发" end-placeholder="返回" />
            </div>
            <div class="form-group" style="flex:0.6;min-width:0">
              <label class="form-label">
                <el-icon size="14"><User /></el-icon> 人数
              </label>
              <el-input-number v-model="genForm.participants" :min="1" :max="100" style="width:100%" controls-position="right" />
            </div>
          </div>

          <!-- 预算滑块 -->
          <div class="form-group">
            <label class="form-label">
              <el-icon size="14"><Money /></el-icon> 预算
              <span class="budget-display">¥{{ genForm.budget_min }} — ¥{{ genForm.budget_max }}/人</span>
            </label>
            <div class="budget-slider-wrap">
              <el-slider v-model="budgetSlider" range :min="0" :max="30000" :step="500" :marks="budgetMarks" :format-tooltip="v => `¥${v}`" />
            </div>
          </div>

          <button class="gen-btn" @click="handleGenerate">
            <el-icon><MagicStick /></el-icon>
            ✨ 一键生成行程
          </button>
        </div>
      </div>

      <!-- 固定底部操作栏 -->
      <div v-if="suggestion && !generating" class="gen-panel-footer">
        <button class="save-btn" :class="{ loading: saving }" :disabled="saving" @click="handleSaveTrip">
          <el-icon v-if="!saving"><FolderAdd /></el-icon>
          <el-icon v-else class="is-loading"><Loading /></el-icon>
          {{ saving ? '保存中...' : '保存为行程' }}
        </button>
        <button class="regen-btn" :disabled="generating" @click="handleGenerate">
          <el-icon><Refresh /></el-icon> 重新生成
        </button>
      </div>
    </div>

    <!-- 聊天行程保存对话框 -->
    <el-dialog v-model="chatTripDialogVisible" title="保存为行程" width="420px" :close-on-click-modal="false" class="trip-save-dialog">
      <div v-if="chatTripData" class="dialog-trip-info">
        <span class="dialog-trip-icon">🎯</span>
        <div>
          <div class="dialog-trip-title">{{ chatTripData.title }}</div>
          <div class="dialog-trip-meta">共 {{ chatTripData.total_days }} 天 · {{ chatTripData.activities?.length || 0 }} 个活动</div>
        </div>
      </div>
      <el-form label-width="70px">
        <el-form-item label="出行日期" required>
          <el-date-picker v-model="chatTripDateRange" type="daterange" value-format="YYYY-MM-DD" style="width:100%" start-placeholder="开始" end-placeholder="结束" />
        </el-form-item>
        <el-form-item label="人数">
          <el-input-number v-model="chatTripParticipants" :min="1" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="chatTripDialogVisible = false" round>取消</el-button>
        <el-button type="primary" :loading="chatTripSaving" @click="saveChatTrip" round>保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getChatHistory, clearChatHistory, aiChatStream, saveTripFromAI } from '@/api/ai'
import { useAiStore } from '@/stores/ai'

const router = useRouter()
const aiStore = useAiStore()
const messages = ref([])
const input = ref('')
const streaming = ref(false)
const streamContent = ref('')
const chatBox = ref(null)
const chatInput = ref(null)
const generating = computed(() => aiStore.generating)
const suggestion = computed(() => aiStore.suggestion)
const saving = ref(false)
const genStep = computed(() => aiStore.genStep)
const expandedDays = computed(() => aiStore.expandedDays)
const chatTripDialogVisible = ref(false)
const chatTripData = ref(null)
const chatTripDateRange = ref(null)
const chatTripParticipants = ref(2)
const chatTripSaving = ref(false)
const mobileTab = ref('chat')
const showAllDays = ref(false)
const genForm = aiStore.genForm

const hotDests = ['云南', '三亚', '成都', '西安', '厦门', '桂林', '重庆', '杭州', '北京', '大理']

const tripTypes = [
  { value: 'regular_tour', icon: '🌍', label: '常规旅游' },
  { value: 'family', icon: '👨‍👩‍👧', label: '亲子游' },
  { value: 'business', icon: '💼', label: '商务考察' },
  { value: 'team_building', icon: '🤝', label: '团建拓展' },
  { value: 'adventure', icon: '🏔️', label: '探险之旅' },
  { value: 'leisure', icon: '🏖️', label: '休闲度假' },
]

const budgetSlider = computed({
  get: () => [genForm.budget_min, genForm.budget_max],
  set: (v) => { genForm.budget_min = v[0]; genForm.budget_max = v[1] }
})

const budgetMarks = { 0: '0', 5000: '5k', 10000: '1w', 20000: '2w', 30000: '3w' }

const quickPrompts = [
  { icon: '🏖️', text: '推荐一个适合亲子游的目的地' },
  { icon: '🗺️', text: '云南5天行程怎么安排？' },
  { icon: '✈️', text: '出国旅行需要准备什么？' },
  { icon: '💰', text: '预算3000元能去哪里？' },
]

function extractTripJson(content) {
  if (!content) return null
  const match = content.match(/<!--TRIP_JSON:([\s\S]*?)-->/)
  if (!match) return null
  try { return JSON.parse(match[1]) } catch { return null }
}

function getDisplayContent(content) {
  if (!content) return ''
  return content.replace(/<!--TRIP_JSON:[\s\S]*?-->/g, '').trim()
}

function renderMd(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^#### (.+)$/gm, '<h5>$1</h5>')
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
    .replace(/\n/g, '<br>')
    .replace(/<br><\/ul>/g, '</ul>')
    .replace(/<ul><br>/g, '<ul>')
    .replace(/<\/h([2345])><br>/g, '</h$1>')
    .replace(/<br><h([2345])>/g, '<h$1>')
    .replace(/<\/pre><br>/g, '</pre>')
    .replace(/<br><pre>/g, '<pre>')
  return html
}

function openChatTripDialog(content) {
  const data = extractTripJson(content)
  if (!data) return
  chatTripData.value = data
  chatTripDateRange.value = null
  chatTripParticipants.value = 2
  chatTripDialogVisible.value = true
}

async function saveChatTrip() {
  if (!chatTripDateRange.value) return ElMessage.warning('请选择出行日期')
  if (!chatTripData.value) return
  chatTripSaving.value = true
  try {
    const res = await saveTripFromAI({
      title: chatTripData.value.title,
      start_date: chatTripDateRange.value[0],
      end_date: chatTripDateRange.value[1],
      participants: chatTripParticipants.value,
      budget: chatTripData.value.estimated_budget || null,
      activities: chatTripData.value.activities || [],
    })
    ElMessage.success('行程已保存')
    chatTripDialogVisible.value = false
    router.push(`/trips/${res.trip_id}`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally { chatTripSaving.value = false }
}

async function loadHistory() {
  const history = await getChatHistory()
  messages.value = history
  scrollBottom()
}

function sendQuick(text) { input.value = text; handleSend() }

async function handleSend() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  scrollBottom()
  streaming.value = true
  streamContent.value = ''
  try {
    const token = localStorage.getItem('token')
    const history = messages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))
    const res = await aiChatStream({ message: text, history }, token)
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
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
            if (parsed.content) { streamContent.value += parsed.content; scrollBottom() }
          } catch {}
        }
      }
    }
    messages.value.push({ role: 'assistant', content: streamContent.value })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，AI 暂时无法响应，请稍后再试。' })
  } finally {
    streaming.value = false
    streamContent.value = ''
  }
}

async function handleClear() { await clearChatHistory(); messages.value = []; ElMessage.success('已清空') }

const actTypeEmoji = (t) => ({ transport: '🚌', attraction: '🏛️', meal: '🍽️', hotel: '🏨', free: '🎯' }[t] || '📌')

const groupedSuggestionDays = computed(() => aiStore.groupedSuggestionDays)
const totalSuggestionDays = computed(() => Object.keys(aiStore.groupedSuggestionDays).length)

function toggleDay(dayNum) {
  aiStore.toggleDay(dayNum)
}

async function handleGenerate() {
  if (!genForm.destination) return ElMessage.warning('请输入目的地')
  if (!genForm.dateRange) return ElMessage.warning('请选择日期')
  showAllDays.value = false
  const ok = await aiStore.generate()
  if (!ok) ElMessage.error('生成失败，请稍后重试')
}

async function handleSaveTrip() {
  if (!suggestion.value || !genForm.dateRange) return
  saving.value = true
  try {
    const res = await saveTripFromAI({
      title: suggestion.value.title,
      start_date: genForm.dateRange[0],
      end_date: genForm.dateRange[1],
      participants: genForm.participants,
      budget: suggestion.value.estimated_budget,
      activities: suggestion.value.activities,
    })
    ElMessage.success('行程已保存')
    router.push(`/trips/${res.trip_id}`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally { saving.value = false }
}

function scrollBottom() { nextTick(() => { if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight }) }

onMounted(loadHistory)
</script>

<style scoped>
/* ===== 页面布局 ===== */
.ai-page {
  display: flex;
  gap: 20px;
  height: calc(100vh - 136px);
}

/* ===== 左侧聊天面板 ===== */
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 20px;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  overflow: hidden;
}
.chat-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f1f5;
}
.chat-title {
  display: flex;
  align-items: center;
  gap: 12px;
}
.chat-title-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.25);
}
.chat-title-text {
  display: flex;
  flex-direction: column;
}
.chat-title-name {
  font-weight: 700;
  font-size: 15px;
  color: #1a1a2e;
}
.chat-title-status {
  font-size: 12px;
  color: #a8abb2;
  display: flex;
  align-items: center;
  gap: 5px;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c0c4cc;
  transition: background 0.3s;
}
.status-dot.active {
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
  animation: pulse-dot 1.5s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.clear-btn {
  color: #a8abb2;
  font-size: 13px;
  transition: color 0.2s;
}
.clear-btn:hover { color: #ef4444; }

/* ===== 聊天区域 ===== */
.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  scroll-behavior: smooth;
}
.chat-box::-webkit-scrollbar { width: 4px; }
.chat-box::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 4px; }
.chat-box::-webkit-scrollbar-thumb:hover { background: #c0c0c0; }

/* ===== 欢迎页 ===== */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
}
.welcome-glow {
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -65%);
  pointer-events: none;
}
.welcome-emoji {
  font-size: 64px;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
.welcome h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
}
.welcome p {
  font-size: 14px;
  color: #909399;
  margin-bottom: 32px;
}
.quick-prompts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  max-width: 480px;
  width: 100%;
}
.quick-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #f8f9fc;
  border: 1px solid #eef0f4;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 13px;
  color: #606266;
}
.quick-card:hover {
  background: #f5f3ff;
  border-color: rgba(139, 92, 246, 0.2);
  color: #7c3aed;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.08);
}
.quick-icon { font-size: 20px; flex-shrink: 0; }
.quick-text { line-height: 1.4; }

/* ===== 消息 ===== */
.msg {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: flex-start;
  animation: msg-in 0.3s ease;
}
@keyframes msg-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.msg.user { flex-direction: row-reverse; }
.msg-avatar { flex-shrink: 0; }
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
}
.avatar-user {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
}
.avatar-ai {
  background: #f0f1f5;
  color: #7c3aed;
}
.msg-body { max-width: 72%; min-width: 0; }
.bubble {
  padding: 12px 18px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}
.msg.user .bubble {
  background: linear-gradient(135deg, #8b5cf6, #818cf8);
  color: #fff;
  border-bottom-right-radius: 6px;
  white-space: pre-wrap;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.15);
}
.msg.assistant .bubble {
  background: #f5f6fa;
  color: #303133;
  border-bottom-left-radius: 6px;
}

/* 流式输出光标 */
.streaming-bubble::after {
  content: '▍';
  color: #8b5cf6;
  animation: blink-cursor 0.8s infinite;
  font-weight: 300;
}
@keyframes blink-cursor {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 打字动画 */
.typing-bubble {
  background: #f5f6fa;
  border-bottom-left-radius: 6px;
  padding: 16px 22px;
}
.typing-dots {
  display: flex;
  gap: 5px;
  align-items: center;
}
.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #c0c4cc;
  animation: typing-bounce 1.4s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.bubble-action { margin-top: 8px; }
.bubble-action :deep(.el-button) {
  font-size: 12px;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.15);
}

/* ===== 输入区 ===== */
.chat-input-area {
  padding: 16px 24px 18px;
  border-top: 1px solid #f0f1f5;
}
.chat-input-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f5f6fa;
  border-radius: 16px;
  padding: 6px 6px 6px 18px;
  border: 2px solid transparent;
  transition: all 0.25s ease;
}
.chat-input-bar:focus-within {
  background: #fff;
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.06);
}
.chat-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}
.chat-input::placeholder { color: #c0c4cc; }
.chat-input:disabled { opacity: 0.5; }
.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: #e0e0e6;
  color: #a8abb2;
  cursor: not-allowed;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
  flex-shrink: 0;
}
.send-btn.active {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}
.send-btn.active:hover {
  transform: scale(1.05);
}
.send-loading span {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #fff;
  margin: 0 1.5px;
  animation: typing-bounce 1.4s infinite;
}
.send-loading span:nth-child(2) { animation-delay: 0.2s; }
.send-loading span:nth-child(3) { animation-delay: 0.4s; }
.input-hint {
  text-align: center;
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 8px;
}

/* ===== Markdown 渲染 ===== */
.md-content :deep(h2), .md-content :deep(h3), .md-content :deep(h4), .md-content :deep(h5) {
  margin: 10px 0 6px;
  font-weight: 700;
  line-height: 1.4;
  color: #1a1a2e;
}
.md-content :deep(h2) { font-size: 16px; }
.md-content :deep(h3) { font-size: 15px; }
.md-content :deep(h4) { font-size: 14px; }
.md-content :deep(h5) { font-size: 13px; }
.md-content :deep(strong) { font-weight: 700; color: #1a1a2e; }
.md-content :deep(em) { font-style: italic; }
.md-content :deep(ul) {
  margin: 6px 0;
  padding-left: 18px;
  list-style: disc;
}
.md-content :deep(li) {
  margin: 3px 0;
  line-height: 1.6;
}
.md-content :deep(code) {
  background: rgba(139, 92, 246, 0.08);
  padding: 2px 6px;
  border-radius: 5px;
  font-size: 13px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  color: #7c3aed;
}
.md-content :deep(pre) {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 14px 16px;
  border-radius: 12px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
  line-height: 1.5;
}
.md-content :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

/* ===== 右侧生成面板 ===== */
.gen-panel {
  width: 380px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 20px;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  overflow: hidden;
}
.gen-panel-header {
  padding: 16px 22px;
  border-bottom: 1px solid #f0f1f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.gen-title-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
}
.gen-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 22px;
}
.gen-panel-body::-webkit-scrollbar { width: 4px; }
.gen-panel-body::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 4px; }

/* ===== 表单 ===== */
.gen-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}
.form-label .el-icon { color: #a8abb2; }

/* 热门标签 */
.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}
.hot-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}
.hot-tag:hover {
  color: #7c3aed;
  background: #f5f3ff;
  border-color: rgba(139, 92, 246, 0.15);
}
.hot-tag.active {
  color: #fff;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  border-color: transparent;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.25);
}

/* 类型卡片 */
.type-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.type-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  border-radius: 12px;
  border: 1.5px solid #eef0f4;
  background: #fafbfd;
  cursor: pointer;
  transition: all 0.25s;
  user-select: none;
}
.type-card:hover {
  border-color: rgba(139, 92, 246, 0.2);
  background: #f5f3ff;
}
.type-card.active {
  border-color: #8b5cf6;
  background: #f5f3ff;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.08);
}
.type-card-icon {
  font-size: 20px;
  line-height: 1;
}
.type-card-label {
  font-size: 11px;
  color: #606266;
  font-weight: 500;
}
.type-card.active .type-card-label {
  color: #7c3aed;
  font-weight: 600;
}

/* 日期+人数同行 */
.form-row-2 {
  display: flex;
  gap: 10px;
}

/* 预算滑块 */
.budget-display {
  margin-left: auto;
  font-size: 12px;
  font-weight: 700;
  color: #8b5cf6;
}
.budget-slider-wrap {
  padding: 0 6px;
}
.budget-slider-wrap :deep(.el-slider__runway) {
  height: 4px;
  background: #eef0f4;
}
.budget-slider-wrap :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #8b5cf6, #6366f1);
  height: 4px;
}
.budget-slider-wrap :deep(.el-slider__button) {
  width: 16px;
  height: 16px;
  border: 2px solid #8b5cf6;
  box-shadow: 0 2px 6px rgba(139, 92, 246, 0.25);
}
.budget-slider-wrap :deep(.el-slider__marks-text) {
  font-size: 10px;
  color: #c0c4cc;
}

.gen-btn {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
  margin-top: 4px;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.25);
}
.gen-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.35);
}
.gen-btn:active:not(:disabled) {
  transform: translateY(0);
}
.gen-btn.loading {
  opacity: 0.8;
  cursor: wait;
}
.gen-btn:disabled {
  cursor: not-allowed;
}

/* ===== 生成结果 ===== */
.suggestion-result {
  animation: fade-up 0.4s ease;
}
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.suggestion-header {
  margin-bottom: 16px;
}
.suggestion-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.suggestion-icon { font-size: 20px; }
.suggestion-title-row h4 {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}
.suggestion-summary {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  margin-bottom: 10px;
}
.suggestion-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.stag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}
.stag.days { background: #ede9fe; color: #7c3aed; }
.stag.budget { background: #fff7ed; color: #d97706; }
.stag.acts { background: #ecfdf5; color: #059669; }

/* ===== 按天分组 ===== */
.suggestion-days {
  max-height: 380px;
  overflow-y: auto;
  margin-bottom: 12px;
}
.suggestion-days::-webkit-scrollbar { width: 3px; }
.suggestion-days::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 3px; }
.show-more-days {
  width: 100%;
  padding: 10px 0;
  border: 1px dashed #e4e7ed;
  border-radius: 10px;
  background: transparent;
  color: #8b5cf6;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.2s;
  margin-top: 2px;
}
.show-more-days:hover {
  background: #f5f3ff;
  border-color: #8b5cf6;
}
.sug-day {
  margin-bottom: 6px;
  border: 1px solid #f0f1f5;
  border-radius: 12px;
  overflow: hidden;
}
.sug-day-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #fafbfd;
  cursor: pointer;
  transition: background 0.2s;
  user-select: none;
}
.sug-day-header:hover { background: #f5f3ff; }
.sug-day-label {
  font-size: 13px;
  font-weight: 700;
  color: #7c3aed;
}
.sug-day-count {
  font-size: 11px;
  color: #a8abb2;
  margin-left: auto;
}
.sug-day-header .el-icon {
  color: #c0c4cc;
  transition: transform 0.25s;
}
.sug-day-header .el-icon.is-rotate {
  transform: rotate(180deg);
}
.sug-day-acts {
  padding: 6px 10px 10px;
}
.tl-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 6px;
  border-radius: 8px;
  transition: background 0.2s;
}
.tl-item:hover { background: #f8f9fc; }
.tl-type-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}
.tl-type-icon.transport { background: #fff7ed; }
.tl-type-icon.attraction { background: #ede9fe; }
.tl-type-icon.meal { background: #fef2f2; }
.tl-type-icon.hotel { background: #eff6ff; }
.tl-type-icon.free { background: #ecfdf5; }
.tl-content {
  flex: 1;
  min-width: 0;
}
.tl-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tl-meta {
  display: flex;
  gap: 8px;
  margin-top: 2px;
}
.tl-time {
  font-size: 11px;
  color: #a8abb2;
  font-weight: 500;
}
.tl-dur {
  font-size: 11px;
  color: #c0c4cc;
}
.tl-cost {
  font-size: 12px;
  color: #d97706;
  font-weight: 600;
  flex-shrink: 0;
}

/* ===== 贴士 ===== */
.suggestion-tips {
  background: #fffbeb;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 14px;
}
.tips-title {
  font-size: 13px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 6px;
}
.tip-item {
  font-size: 12px;
  color: #a16207;
  line-height: 1.6;
  padding-left: 12px;
  position: relative;
}
.tip-item::before {
  content: '·';
  position: absolute;
  left: 2px;
  font-weight: 700;
}

/* ===== 底部固定操作栏 ===== */
.gen-panel-footer {
  display: flex;
  gap: 10px;
  padding: 14px 22px;
  border-top: 1px solid #f0f1f5;
  background: #fff;
  flex-shrink: 0;
}

.save-btn {
  flex: 1;
  height: 42px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}
.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35);
}
.save-btn.loading {
  opacity: 0.8;
  cursor: wait;
}
.regen-btn {
  height: 42px;
  padding: 0 18px;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  background: #fff;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.25s;
  flex-shrink: 0;
}
.regen-btn:hover:not(:disabled) {
  border-color: #8b5cf6;
  color: #8b5cf6;
  background: #f5f3ff;
}

/* ===== 生成中动画 ===== */
.gen-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  animation: fade-up 0.3s ease;
}
.gen-loading-orb {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.orb-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #8b5cf6;
  border-right-color: #6366f1;
  animation: spin 1.2s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.gen-loading-state h4 {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}
.gen-loading-state p {
  font-size: 13px;
  color: #909399;
  margin: 0 0 24px;
}
.gen-loading-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 200px;
}
.gen-loading-steps .step {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #c0c4cc;
  transition: color 0.3s;
}
.gen-loading-steps .step.done {
  color: #8b5cf6;
}
.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e4e7ed;
  transition: all 0.3s;
  flex-shrink: 0;
}
.step.done .step-dot {
  background: #8b5cf6;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.4);
}

/* ===== 对话框 ===== */
.dialog-trip-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #f5f3ff;
  border-radius: 12px;
  margin-bottom: 20px;
}
.dialog-trip-icon { font-size: 28px; }
.dialog-trip-title {
  font-weight: 700;
  font-size: 15px;
  color: #1a1a2e;
  margin-bottom: 2px;
}
.dialog-trip-meta {
  font-size: 13px;
  color: #909399;
}

/* ===== Element Plus 覆盖 ===== */
.gen-form :deep(.el-input__wrapper),
.gen-form :deep(.el-select .el-input__wrapper) {
  border-radius: 10px;
}
.gen-form :deep(.el-input-number) {
  width: 100%;
}
.gen-form :deep(.el-date-editor) {
  --el-date-editor-width: 100%;
}

/* ===== 移动端切换栏（默认隐藏） ===== */
.mobile-tab-bar {
  display: none;
}

/* ===== 响应式：平板 ≤1024px ===== */
@media (max-width: 1024px) {
  .gen-panel { width: 320px; }
  .gen-panel-body { padding: 16px 18px; }
  .msg-body { max-width: 78%; }
  .quick-prompts { max-width: 420px; }
}

/* ===== 响应式：小平板 ≤768px ===== */
@media (max-width: 768px) {
  .ai-page {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 136px);
    gap: 0;
    position: relative;
  }
  .mobile-tab-bar {
    display: flex;
    gap: 0;
    background: #fff;
    border-radius: 14px;
    padding: 4px;
    margin-bottom: 12px;
    border: 1px solid #f0f1f5;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  }
  .mobile-tab {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px 0;
    border: none;
    background: transparent;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    color: #909399;
    cursor: pointer;
    transition: all 0.25s ease;
  }
  .mobile-tab.active {
    background: linear-gradient(135deg, #8b5cf6, #6366f1);
    color: #fff;
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25);
  }
  .chat-panel,
  .gen-panel {
    display: none;
    width: 100%;
    height: calc(100vh - 200px);
    min-height: 500px;
  }
  .chat-panel.mobile-show,
  .gen-panel.mobile-show {
    display: flex;
  }
  .gen-panel.mobile-show {
    height: auto;
    min-height: auto;
  }
  .msg-body { max-width: 80%; }
  .quick-prompts {
    grid-template-columns: 1fr;
    max-width: 100%;
    padding: 0 8px;
  }
  .chat-box { padding: 16px; }
  .chat-panel-header { padding: 14px 16px; }
  .chat-input-area { padding: 12px 16px 14px; }
}

/* ===== 响应式：手机 ≤480px ===== */
@media (max-width: 480px) {
  .ai-page {
    gap: 0;
  }
  .chat-panel,
  .gen-panel {
    border-radius: 14px;
    height: calc(100vh - 190px);
    min-height: 420px;
  }
  .chat-panel-header { padding: 12px 14px; }
  .chat-title-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
  }
  .chat-title-name { font-size: 14px; }
  .chat-title-status { font-size: 11px; }
  .chat-box { padding: 12px; }
  .chat-input-area { padding: 10px 12px 12px; }
  .chat-input-bar { padding: 4px 4px 4px 14px; border-radius: 14px; }
  .chat-input { font-size: 13px; }
  .send-btn { width: 36px; height: 36px; border-radius: 10px; }
  .input-hint { font-size: 10px; margin-top: 6px; }
  .msg { gap: 8px; margin-bottom: 14px; }
  .avatar { width: 30px; height: 30px; border-radius: 10px; font-size: 11px; }
  .bubble { padding: 10px 14px; font-size: 13px; border-radius: 16px; }
  .msg-body { max-width: 82%; }
  .msg.user .bubble { border-bottom-right-radius: 5px; }
  .msg.assistant .bubble { border-bottom-left-radius: 5px; }
  .welcome-emoji { font-size: 48px; }
  .welcome h3 { font-size: 17px; }
  .welcome p { font-size: 13px; margin-bottom: 24px; }
  .quick-card { padding: 12px 14px; font-size: 12px; }
  .quick-icon { font-size: 18px; }
  .gen-panel-header { padding: 14px 16px; }
  .gen-title-icon { width: 32px; height: 32px; border-radius: 10px; }
  .gen-panel-body { padding: 16px; }
  .gen-form { gap: 14px; }
  .form-label { font-size: 12px; }
  .type-cards { grid-template-columns: repeat(3, 1fr); gap: 6px; }
  .type-card { padding: 8px 2px; }
  .type-card-icon { font-size: 18px; }
  .type-card-label { font-size: 10px; }
  .form-row-2 { flex-direction: column; gap: 12px; }
  .hot-tag { padding: 3px 10px; font-size: 11px; }
  .gen-btn { height: 40px; font-size: 14px; border-radius: 12px; }
  .save-btn { height: 38px; font-size: 13px; border-radius: 10px; }
  .suggestion-title-row h4 { font-size: 15px; }
  .suggestion-timeline { max-height: 260px; }
  .dialog-trip-info { padding: 12px 14px; }
  .mobile-tab { padding: 8px 0; font-size: 13px; }
}
</style>
