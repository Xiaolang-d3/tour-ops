<template>
  <div class="admin-dash" v-loading="loading">
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
              <h2>{{ greeting }}，{{ userStore.user?.name || '管理员' }}</h2>
              <p class="welcome-sub">系统运行概览，一切尽在掌控</p>
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

    <!-- 核心指标 -->
    <div class="stat-grid">
      <div class="stat-card" @click="router.push('/admin/users')">
        <div class="stat-top">
          <div class="stat-icon" style="background:linear-gradient(135deg,#e6a23c,#f59e0b)">
            <el-icon :size="20" color="#fff"><User /></el-icon>
          </div>
          <div class="stat-badge" v-if="stats.users.new_this_week">+{{ stats.users.new_this_week }} 本周</div>
        </div>
        <div class="stat-value">{{ stats.users.total }}</div>
        <div class="stat-label">注册用户</div>
      </div>
      <div class="stat-card">
        <div class="stat-top">
          <div class="stat-icon" style="background:linear-gradient(135deg,#3b82f6,#06b6d4)">
            <el-icon :size="20" color="#fff"><Suitcase /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ stats.trips.total }}</div>
        <div class="stat-label">总行程数</div>
      </div>
      <div class="stat-card" @click="router.push('/admin/resources')">
        <div class="stat-top">
          <div class="stat-icon" style="background:linear-gradient(135deg,#10b981,#059669)">
            <el-icon :size="20" color="#fff"><OfficeBuilding /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ stats.resources.total }}</div>
        <div class="stat-label">资源总数</div>
      </div>
      <div class="stat-card" @click="router.push('/admin/templates')">
        <div class="stat-top">
          <div class="stat-icon" style="background:linear-gradient(135deg,#8b5cf6,#6366f1)">
            <el-icon :size="20" color="#fff"><Files /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ stats.templates }}</div>
        <div class="stat-label">模板数量</div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="dashboard-row">
      <!-- 左侧 -->
      <div class="dash-left">
        <!-- 行程状态分布 -->
        <div class="dash-card">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">📊</span>
              <span class="dash-card-title">行程状态分布</span>
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

        <!-- 资源概览 -->
        <div class="dash-card">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">🏢</span>
              <span class="dash-card-title">资源概览</span>
            </div>
            <el-button text size="small" @click="router.push('/admin/resources')">
              管理 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <div class="resource-grid">
            <div class="resource-item">
              <div class="resource-icon guides">🧑‍🏫</div>
              <div class="resource-value">{{ stats.resources.guides }}</div>
              <div class="resource-label">导游</div>
            </div>
            <div class="resource-item">
              <div class="resource-icon vehicles">🚐</div>
              <div class="resource-value">{{ stats.resources.vehicles }}</div>
              <div class="resource-label">车辆</div>
            </div>
            <div class="resource-item">
              <div class="resource-icon hotels">🏨</div>
              <div class="resource-value">{{ stats.resources.hotels }}</div>
              <div class="resource-label">酒店</div>
            </div>
            <div class="resource-item">
              <div class="resource-icon restaurants">🍽️</div>
              <div class="resource-value">{{ stats.resources.restaurants }}</div>
              <div class="resource-label">餐厅</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧 -->
      <div class="dash-right">
        <!-- 用户构成 -->
        <div class="dash-card">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">👥</span>
              <span class="dash-card-title">用户构成</span>
            </div>
            <el-button text size="small" @click="router.push('/admin/users')">
              管理 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <div class="user-composition">
            <div class="comp-ring">
              <svg viewBox="0 0 100 100" class="comp-svg">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#f3f4f6" stroke-width="12" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#f59e0b" stroke-width="12"
                  :stroke-dasharray="`${adminPct * 2.51} 251`" stroke-dashoffset="0"
                  stroke-linecap="round" transform="rotate(-90 50 50)" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#10b981" stroke-width="12"
                  :stroke-dasharray="`${plannerPct * 2.51} 251`"
                  :stroke-dashoffset="`-${adminPct * 2.51}`"
                  stroke-linecap="round" transform="rotate(-90 50 50)" />
              </svg>
              <div class="comp-center">
                <span class="comp-total">{{ stats.users.total }}</span>
                <span class="comp-unit">人</span>
              </div>
            </div>
            <div class="comp-legend">
              <div class="legend-item">
                <div class="legend-dot" style="background:#f59e0b"></div>
                <span class="legend-label">管理员</span>
                <span class="legend-value">{{ stats.users.admins }}</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot" style="background:#10b981"></div>
                <span class="legend-label">计划员</span>
                <span class="legend-value">{{ stats.users.planners }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 最近注册 -->
        <div class="dash-card">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">🆕</span>
              <span class="dash-card-title">最近注册</span>
            </div>
          </div>
          <div v-if="stats.recent_users.length === 0" class="empty-hint">暂无用户</div>
          <div v-else class="recent-list">
            <div class="recent-row" v-for="u in stats.recent_users" :key="u.id">
              <el-avatar :size="32" class="recent-avatar" :style="getAvatarStyle(u.avatar)">
                <span v-if="getAvatarEmoji(u.avatar)">{{ getAvatarEmoji(u.avatar) }}</span>
                <span v-else>{{ (u.name || u.username).charAt(0) }}</span>
              </el-avatar>
              <div class="recent-info">
                <span class="recent-name">{{ u.name || u.username }}</span>
                <span class="recent-time">{{ formatTime(u.created_at) }}</span>
              </div>
              <div class="recent-role" :class="u.role">
                {{ u.role === 'admin' ? '管理员' : '计划员' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="dash-card">
          <div class="dash-card-header">
            <div class="card-title-group">
              <span class="card-title-icon">⚡</span>
              <span class="dash-card-title">快捷操作</span>
            </div>
          </div>
          <div class="quick-actions">
            <div class="quick-action-item" @click="router.push('/admin/users')">
              <div class="qa-icon" style="background:linear-gradient(135deg,#e6a23c,#f59e0b)"><el-icon size="18" color="#fff"><User /></el-icon></div>
              <div class="qa-text"><span class="qa-title">用户管理</span><span class="qa-desc">管理系统用户</span></div>
              <el-icon size="14" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
            <div class="quick-action-item" @click="router.push('/admin/resources')">
              <div class="qa-icon" style="background:linear-gradient(135deg,#10b981,#059669)"><el-icon size="18" color="#fff"><OfficeBuilding /></el-icon></div>
              <div class="qa-text"><span class="qa-title">资源管理</span><span class="qa-desc">导游、车辆、酒店、餐厅</span></div>
              <el-icon size="14" color="#c0c4cc"><ArrowRight /></el-icon>
            </div>
            <div class="quick-action-item" @click="router.push('/admin/templates')">
              <div class="qa-icon" style="background:linear-gradient(135deg,#8b5cf6,#6366f1)"><el-icon size="18" color="#fff"><Files /></el-icon></div>
              <div class="qa-text"><span class="qa-title">模板库</span><span class="qa-desc">管理行程模板</span></div>
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
import { getAdminStats } from '@/api/auth'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const defaultStats = {
  users: { total: 0, admins: 0, planners: 0, new_this_week: 0 },
  trips: { total: 0, by_status: {} },
  resources: { guides: 0, vehicles: 0, hotels: 0, restaurants: 0, total: 0 },
  templates: 0,
  recent_users: [],
}
const stats = ref({ ...defaultStats })

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

const adminPct = computed(() => {
  const t = stats.value.users.total || 1
  return Math.round((stats.value.users.admins / t) * 100)
})
const plannerPct = computed(() => {
  const t = stats.value.users.total || 1
  return Math.round((stats.value.users.planners / t) * 100)
})

const statusDist = computed(() => {
  const total = stats.value.trips.total || 1
  const bs = stats.value.trips.by_status || {}
  const map = [
    { status: 'draft', label: '草稿', color: '#8b5cf6' },
    { status: 'confirmed', label: '已确认', color: '#3b82f6' },
    { status: 'completed', label: '已完成', color: '#10b981' },
    { status: 'cancelled', label: '已取消', color: '#ef4444' },
  ]
  return map.map(m => ({
    ...m,
    count: bs[m.status] || 0,
    pct: Math.round(((bs[m.status] || 0) / total) * 100),
  }))
})

const avatarOptions = [
  { id: 'avatar-1', emoji: '😊', bg: 'linear-gradient(135deg, #8b5cf6, #6366f1)' },
  { id: 'avatar-2', emoji: '🚀', bg: 'linear-gradient(135deg, #3b82f6, #06b6d4)' },
  { id: 'avatar-3', emoji: '🌸', bg: 'linear-gradient(135deg, #ec4899, #f43f5e)' },
  { id: 'avatar-4', emoji: '🌿', bg: 'linear-gradient(135deg, #10b981, #059669)' },
  { id: 'avatar-5', emoji: '🔥', bg: 'linear-gradient(135deg, #f97316, #ef4444)' },
  { id: 'avatar-6', emoji: '⭐', bg: 'linear-gradient(135deg, #f59e0b, #eab308)' },
  { id: 'avatar-7', emoji: '🎵', bg: 'linear-gradient(135deg, #8b5cf6, #ec4899)' },
  { id: 'avatar-8', emoji: '🌊', bg: 'linear-gradient(135deg, #0ea5e9, #6366f1)' },
]
function getAvatarStyle(id) {
  const av = avatarOptions.find(a => a.id === id)
  return av ? { background: av.bg } : {}
}
function getAvatarEmoji(id) {
  const av = avatarOptions.find(a => a.id === id)
  return av ? av.emoji : null
}
function formatTime(dt) {
  if (!dt) return ''
  return dayjs(dt).format('M月D日')
}

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await getAdminStats()
  } catch { stats.value = { ...defaultStats } }
  finally { loading.value = false }
})
</script>

<style scoped>
.admin-dash { max-width: 1200px; }

/* 欢迎横幅 */
.welcome-banner {
  position: relative; border-radius: 18px; overflow: hidden;
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #e6a23c 100%);
  padding: 32px 36px; margin-bottom: 24px; color: #fff;
}
.welcome-bg { position: absolute; inset: 0; overflow: hidden; pointer-events: none; }
.welcome-orb {
  position: absolute; border-radius: 50%; opacity: 0.18; background: #fff;
  animation: orbFloat 8s ease-in-out infinite;
}
.orb-1 { width: 200px; height: 200px; top: -60px; right: -40px; }
.orb-2 { width: 120px; height: 120px; bottom: -30px; left: 20%; animation-delay: -3s; }
@keyframes orbFloat {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-18px) scale(1.08); }
}
.welcome-content {
  position: relative; display: flex; align-items: center;
  justify-content: space-between; gap: 20px;
}
.welcome-greeting { display: flex; align-items: center; gap: 16px; }
.greeting-emoji { font-size: 40px; line-height: 1; }
.welcome-greeting h2 { margin: 0; font-size: 22px; font-weight: 700; }
.welcome-sub { margin: 6px 0 0; font-size: 14px; opacity: 0.85; }
.welcome-date-card {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.18); backdrop-filter: blur(8px);
  border-radius: 14px; padding: 12px 20px;
}
.date-day { font-size: 36px; font-weight: 800; line-height: 1; }
.date-detail { display: flex; flex-direction: column; font-size: 13px; opacity: 0.9; line-height: 1.5; }

/* 统计卡片 */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card {
  background: #fff; border-radius: 14px; padding: 20px;
  cursor: pointer; transition: all 0.25s; border: 1px solid #f0f0f0;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(230,162,60,0.10); border-color: #fef3c7; }
.stat-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.stat-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.stat-badge {
  font-size: 11px; color: #d97706; background: #fffbeb;
  padding: 2px 10px; border-radius: 20px; font-weight: 600;
}
.stat-value { font-size: 30px; font-weight: 800; color: #1e1b4b; line-height: 1.1; }
.stat-label { font-size: 13px; color: #9ca3af; margin-top: 4px; }

/* 主内容区 */
.dashboard-row { display: grid; grid-template-columns: 1fr 340px; gap: 20px; }
.dash-left { display: flex; flex-direction: column; gap: 20px; }
.dash-right { display: flex; flex-direction: column; gap: 20px; }
.dash-card { background: #fff; border-radius: 14px; padding: 20px; border: 1px solid #f0f0f0; }
.dash-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.card-title-group { display: flex; align-items: center; gap: 8px; }
.card-title-icon { font-size: 18px; }
.dash-card-title { font-size: 15px; font-weight: 600; color: #1e1b4b; }

/* 状态分布 */
.status-bars { display: flex; flex-direction: column; gap: 14px; }
.status-bar-item { display: flex; flex-direction: column; gap: 6px; }
.status-bar-label { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #4b5563; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.status-bar-count { margin-left: auto; font-weight: 600; color: #1e1b4b; font-size: 13px; }
.status-bar-track { height: 6px; background: #f3f4f6; border-radius: 3px; overflow: hidden; }
.status-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }

/* 资源概览 */
.resource-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.resource-item { text-align: center; padding: 16px 8px; border-radius: 12px; background: #fafafa; }
.resource-icon { font-size: 28px; margin-bottom: 8px; }
.resource-value { font-size: 22px; font-weight: 800; color: #1e1b4b; }
.resource-label { font-size: 12px; color: #9ca3af; margin-top: 2px; }

/* 用户构成 */
.user-composition { display: flex; align-items: center; gap: 24px; padding: 8px 0; }
.comp-ring { position: relative; width: 100px; height: 100px; flex-shrink: 0; }
.comp-svg { width: 100%; height: 100%; }
.comp-center {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.comp-total { font-size: 22px; font-weight: 800; color: #1e1b4b; line-height: 1; }
.comp-unit { font-size: 11px; color: #9ca3af; }
.comp-legend { display: flex; flex-direction: column; gap: 10px; }
.legend-item { display: flex; align-items: center; gap: 8px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-label { font-size: 13px; color: #4b5563; }
.legend-value { font-size: 14px; font-weight: 700; color: #1e1b4b; margin-left: auto; min-width: 24px; text-align: right; }

/* 最近注册 */
.recent-list { display: flex; flex-direction: column; gap: 4px; }
.recent-row { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 10px; transition: background 0.2s; }
.recent-row:hover { background: #fffbeb; }
.recent-avatar { background: linear-gradient(135deg, #e6a23c, #f59e0b); color: #fff; font-weight: 600; font-size: 12px; flex-shrink: 0; }
.recent-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.recent-name { font-size: 13px; font-weight: 600; color: #1e1b4b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-time { font-size: 11px; color: #9ca3af; }
.recent-role {
  font-size: 11px; padding: 2px 8px; border-radius: 6px; font-weight: 600; flex-shrink: 0;
}
.recent-role.admin { background: #fef2f2; color: #dc2626; }
.recent-role.planner { background: #ecfdf5; color: #059669; }

/* 快捷操作 */
.quick-actions { display: flex; flex-direction: column; gap: 6px; }
.quick-action-item {
  display: flex; align-items: center; gap: 12px; padding: 12px;
  border-radius: 10px; cursor: pointer; transition: background 0.2s;
}
.quick-action-item:hover { background: #fffbeb; }
.qa-icon { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.qa-text { flex: 1; display: flex; flex-direction: column; }
.qa-title { font-size: 14px; font-weight: 500; color: #1e1b4b; }
.qa-desc { font-size: 12px; color: #9ca3af; margin-top: 2px; }

.empty-hint { text-align: center; padding: 20px 0; color: #9ca3af; font-size: 13px; }

/* 响应式 */
@media (max-width: 1024px) {
  .dashboard-row { grid-template-columns: 1fr; }
  .dash-right { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
}
@media (max-width: 768px) {
  .welcome-banner { padding: 24px 20px; border-radius: 14px; }
  .welcome-greeting h2 { font-size: 18px; }
  .greeting-emoji { font-size: 32px; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .dash-right { grid-template-columns: 1fr; }
  .resource-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .welcome-content { flex-direction: column; align-items: flex-start; }
  .welcome-date-card { align-self: flex-end; }
  .stat-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .stat-card { padding: 14px; }
  .stat-value { font-size: 24px; }
  .date-day { font-size: 28px; }
  .resource-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
}
</style>
