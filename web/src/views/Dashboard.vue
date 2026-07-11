<template>
  <div class="dashboard" v-loading="loading">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-bg">
        <div class="welcome-orb orb-1"></div>
        <div class="welcome-orb orb-2"></div>
      </div>
      <div class="welcome-content">
        <div class="welcome-left">
          <div class="welcome-greeting">
            <span class="greeting-emoji">{{ greetingEmoji }}</span>
            <div>
              <h2>{{ greeting }}，{{ userStore.user?.name || '旅行规划师' }}</h2>
              <p class="welcome-sub">这是你的工作台概览，祝你今天工作顺利</p>
            </div>
          </div>
        </div>
        <div class="welcome-right">
          <div class="welcome-date-card">
            <span class="date-day">{{ todayDay }}</span>
            <div class="date-detail">
              <span class="date-month">{{ todayMonth }}</span>
              <span class="date-weekday">{{ todayWeekday }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div class="stat-card" v-for="s in stats" :key="s.label" @click="s.action?.()">
        <div class="stat-top">
          <div class="stat-icon" :style="{ background: s.iconBg }">
            <el-icon :size="20" color="#fff"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-trend" v-if="s.trend">
            <el-icon size="12"><Top /></el-icon> {{ s.trend }}
          </div>
        </div>
        <div class="stat-value">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-row">
      <!-- 最近行程 -->
      <div class="dash-card recent-trips">
        <div class="dash-card-header">
          <div class="card-title-group">
            <span class="card-title-icon">📋</span>
            <span class="dash-card-title">最近行程</span>
          </div>
          <el-button text size="small" @click="router.push('/trips')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div v-if="recentTrips.length === 0" class="empty-hint">
          <div class="empty-icon">🗺️</div>
          <p>暂无行程</p>
          <el-button type="primary" size="small" round @click="router.push('/trips')">去创建</el-button>
        </div>
        <div v-else class="trip-list">
          <div class="trip-row" v-for="(t, idx) in recentTrips" :key="t.id" @click="router.push(`/trips/${t.id}`)">
            <div class="trip-index">{{ idx + 1 }}</div>
            <div class="trip-row-body">
              <span class="trip-name">{{ t.title }}</span>
              <div class="trip-meta">
                <span class="trip-date">
                  <el-icon size="12"><Calendar /></el-icon>
                  {{ t.start_date || '未设置日期' }}
                </span>
                <span v-if="t.guest_count" class="trip-people">
                  <el-icon size="12"><User /></el-icon>
                  {{ t.guest_count }}人
                </span>
              </div>
            </div>
            <el-tag :type="statusType(t.status)" size="small" effect="plain" round>{{ statusLabel(t.status) }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="dash-right">
        <!-- 状态分布 -->
        <div class="dash-card status-dist">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">📊</span>
              <span class="dash-card-title">行程状态</span>
            </div>
          </div>
          <div class="status-bars">
            <div class="status-bar-item" v-for="s in statusDist" :key="s.status">
              <div class="status-bar-label">
                <div class="status-dot" :style="{ background: s.color }"></div>
                <span>{{ s.label }}</span>
                <span class="status-bar-count">{{ s.count }}</span>
              </div>
              <div class="status-bar-track">
                <div class="status-bar-fill" :style="{ width: s.pct + '%', background: s.color }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="dash-card quick-card">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">⚡</span>
              <span class="dash-card-title">快捷操作</span>
            </div>
          </div>
          <div class="quick-actions">
            <div class="quick-action-item" @click="router.push('/trips')">
              <div class="qa-icon" style="background:linear-gradient(135deg,#8b5cf6,#6366f1)">
                <el-icon size="18" color="#fff"><Suitcase /></el-icon>
              </div>
              <div class="qa-text">
                <span class="qa-title">行程管理</span>
                <span class="qa-desc">创建和管理行程</span>
              </div>
              <el-icon size="14" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
            <div class="quick-action-item" @click="router.push('/ai')">
              <div class="qa-icon" style="background:linear-gradient(135deg,#3b82f6,#06b6d4)">
                <el-icon size="18" color="#fff"><ChatDotRound /></el-icon>
              </div>
              <div class="qa-text">
                <span class="qa-title">AI 助手</span>
                <span class="qa-desc">智能规划行程</span>
              </div>
              <el-icon size="14" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
            <div class="quick-action-item" @click="router.push('/templates')">
              <div class="qa-icon" style="background:linear-gradient(135deg,#f59e0b,#f97316)">
                <el-icon size="18" color="#fff"><Files /></el-icon>
              </div>
              <div class="qa-text">
                <span class="qa-title">模板库</span>
                <span class="qa-desc">使用模板快速创建</span>
              </div>
              <el-icon size="14" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getTrips } from '@/api/trips'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const trips = ref([])

const greeting = computed(() => {
  const h = dayjs().hour()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const greetingEmoji = computed(() => {
  const h = dayjs().hour()
  if (h < 6) return '🌙'
  if (h < 12) return '☀️'
  if (h < 14) return '🌤️'
  if (h < 18) return '🌅'
  return '🌆'
})

const todayDay = computed(() => dayjs().format('D'))
const todayMonth = computed(() => dayjs().format('YYYY年M月'))
const todayWeekday = computed(() => dayjs().format('dddd'))

const recentTrips = computed(() =>
  [...trips.value]
    .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
    .slice(0, 5)
)

const stats = computed(() => {
  const total = trips.value.length
  const activities = trips.value.reduce((s, t) => s + (t.activity_count || 0), 0)
  const planning = trips.value.filter(t => t.status === 'draft').length
  const completed = trips.value.filter(t => t.status === 'completed').length
  return [
    { label: '总行程', value: total, icon: 'Suitcase', iconBg: 'linear-gradient(135deg,#8b5cf6,#6366f1)', action: () => router.push('/trips') },
    { label: '活动数', value: activities, icon: 'Location', iconBg: 'linear-gradient(135deg,#3b82f6,#06b6d4)' },
    { label: '草稿', value: planning, icon: 'EditPen', iconBg: 'linear-gradient(135deg,#f59e0b,#f97316)' },
    { label: '已完成', value: completed, icon: 'CircleCheck', iconBg: 'linear-gradient(135deg,#10b981,#059669)' },
  ]
})

const statusDist = computed(() => {
  const total = trips.value.length || 1
  const map = [
    { status: 'draft', label: '草稿', color: '#8b5cf6' },
    { status: 'confirmed', label: '已确认', color: '#3b82f6' },
    { status: 'completed', label: '已完成', color: '#10b981' },
    { status: 'cancelled', label: '已取消', color: '#ef4444' },
  ]
  return map.map(m => {
    const count = trips.value.filter(t => t.status === m.status).length
    return { ...m, count, pct: Math.round((count / total) * 100) }
  })
})

function statusType(s) {
  const m = { draft: 'info', confirmed: 'success', completed: '', cancelled: 'danger' }
  return m[s] || 'info'
}
function statusLabel(s) {
  const m = { draft: '草稿', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }
  return m[s] || s
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getTrips()
    trips.value = res.items || res || []
  } catch { trips.value = [] }
  finally { loading.value = false }
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎横幅 */
.welcome-banner {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #4f46e5 100%);
  padding: 32px 36px;
  margin-bottom: 24px;
  color: #fff;
}
.welcome-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.welcome-orb {
  position: absolute;
  border-radius: 50%;
  opacity: 0.18;
  background: #fff;
  animation: orbFloat 8s ease-in-out infinite;
}
.orb-1 { width: 200px; height: 200px; top: -60px; right: -40px; }
.orb-2 { width: 120px; height: 120px; bottom: -30px; left: 20%; animation-delay: -3s; }
@keyframes orbFloat {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-18px) scale(1.08); }
}
.welcome-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.welcome-greeting {
  display: flex;
  align-items: center;
  gap: 16px;
}
.greeting-emoji {
  font-size: 40px;
  line-height: 1;
}
.welcome-greeting h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}
.welcome-sub {
  margin: 6px 0 0;
  font-size: 14px;
  opacity: 0.85;
}
.welcome-date-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(8px);
  border-radius: 14px;
  padding: 12px 20px;
}
.date-day {
  font-size: 36px;
  font-weight: 800;
  line-height: 1;
}
.date-detail {
  display: flex;
  flex-direction: column;
  font-size: 13px;
  opacity: 0.9;
  line-height: 1.5;
}

/* 统计卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.25s;
  border: 1px solid #f0f0f0;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(139,92,246,0.10);
  border-color: #ede9fe;
}
.stat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: #10b981;
  background: #ecfdf5;
  padding: 2px 8px;
  border-radius: 20px;
}
.stat-value {
  font-size: 30px;
  font-weight: 800;
  color: #1e1b4b;
  line-height: 1.1;
}
.stat-label {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 4px;
}

/* 主内容区 */
.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
}
.dash-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px;
  border: 1px solid #f0f0f0;
}
.dash-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.card-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-title-icon {
  font-size: 18px;
}
.dash-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e1b4b;
}

/* 最近行程列表 */
.trip-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.trip-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.trip-row:hover {
  background: #f5f3ff;
}
.trip-index {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: #f5f3ff;
  color: #8b5cf6;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.trip-row-body {
  flex: 1;
  min-width: 0;
}
.trip-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e1b4b;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.trip-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
  font-size: 12px;
  color: #9ca3af;
}
.trip-meta .el-icon {
  margin-right: 2px;
}

/* 右侧面板 */
.dash-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 状态分布 */
.status-bars {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.status-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.status-bar-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #4b5563;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-bar-count {
  margin-left: auto;
  font-weight: 600;
  color: #1e1b4b;
  font-size: 13px;
}
.status-bar-track {
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}
.status-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.quick-action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}
.quick-action-item:hover {
  background: #f5f3ff;
}
.qa-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.qa-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.qa-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e1b4b;
}
.qa-desc {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

/* 空状态 */
.empty-hint {
  text-align: center;
  padding: 40px 0;
  color: #9ca3af;
}
.empty-icon {
  font-size: 40px;
  margin-bottom: 8px;
}
.empty-hint p {
  margin: 0 0 12px;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }
  .dash-right {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
}
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  .welcome-banner {
    padding: 24px 20px;
    border-radius: 14px;
  }
  .welcome-greeting h2 {
    font-size: 18px;
  }
  .greeting-emoji {
    font-size: 32px;
  }
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  .dash-right {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 480px) {
  .dashboard {
    padding: 12px;
  }
  .welcome-banner {
    padding: 20px 16px;
  }
  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
  }
  .welcome-date-card {
    align-self: flex-end;
  }
  .stat-grid {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  .stat-card {
    padding: 14px;
  }
  .stat-value {
    font-size: 24px;
  }
  .date-day {
    font-size: 28px;
  }
  .trip-row {
    padding: 10px;
  }
}
</style>
