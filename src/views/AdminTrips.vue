<template>
  <div class="admin-trips">
    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card" :class="{ active: !filterStatus }" @click="filterStatus = ''; loadTrips()">
        <div class="stat-icon all"><el-icon size="20"><Suitcase /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ allTrips.length }}</div>
          <div class="stat-label">全部行程</div>
        </div>
      </div>
      <div class="stat-card" :class="{ active: filterStatus === 'draft' }" @click="filterStatus = 'draft'; loadTrips()">
        <div class="stat-icon draft"><el-icon size="20"><EditPen /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ countByStatus('draft') }}</div>
          <div class="stat-label">草稿</div>
        </div>
      </div>
      <div class="stat-card" :class="{ active: filterStatus === 'confirmed' }" @click="filterStatus = 'confirmed'; loadTrips()">
        <div class="stat-icon confirmed"><el-icon size="20"><CircleCheck /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ countByStatus('confirmed') }}</div>
          <div class="stat-label">已确认</div>
        </div>
      </div>
      <div class="stat-card" :class="{ active: filterStatus === 'completed' }" @click="filterStatus = 'completed'; loadTrips()">
        <div class="stat-icon completed"><el-icon size="20"><SuccessFilled /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ countByStatus('completed') }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="page-toolbar">
      <el-input v-model="searchText" placeholder="搜索行程名称..." prefix-icon="Search" clearable class="search-input" @keyup.enter="loadTrips" @clear="loadTrips" />
      <el-button :icon="Refresh" circle @click="loadTrips" />
    </div>

    <!-- 行程表格 -->
    <div class="table-wrap">
      <el-table v-loading="loading" :data="trips" stripe class="trip-table" @sort-change="handleSort">
        <el-table-column label="行程" min-width="240">
          <template #default="{ row }">
            <div class="trip-cell">
              <div class="trip-cell-main">
                <span class="trip-name">{{ row.name }}</span>
                <span class="trip-id">#{{ row.id }}</span>
              </div>
              <div class="trip-cell-meta">
                <span class="trip-date">
                  <el-icon size="12"><Calendar /></el-icon>
                  {{ row.start_date }} ~ {{ row.end_date }}
                </span>
                <span v-if="row.guest_count" class="trip-people">{{ row.guest_count }}人</span>
                <span v-if="row.activity_count" class="trip-acts">{{ row.activity_count }}项活动</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="创建者" width="160">
          <template #default="{ row }">
            <div v-if="row.creator" class="creator-cell">
              <el-avatar :size="28" class="creator-avatar" :style="getAvatarStyle(row.creator.avatar)">
                <span v-if="getAvatarEmoji(row.creator.avatar)">{{ getAvatarEmoji(row.creator.avatar) }}</span>
                <span v-else>{{ (row.creator.name || row.creator.username).charAt(0) }}</span>
              </el-avatar>
              <span class="creator-name">{{ row.creator.name || row.creator.username }}</span>
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light" round size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="120" sortable="custom" prop="created_at">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(cmd) => handleStatusChange(row, cmd)">
              <el-button text size="small" class="action-btn">
                <el-icon><Switch /></el-icon> 状态
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="s in statusOptions" :key="s.value" :command="s.value" :disabled="row.status === s.value">
                    {{ s.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-popconfirm title="确定删除该行程？活动数据将一并删除。" confirm-button-text="删除" confirm-button-type="danger" @confirm="handleDelete(row)">
              <template #reference>
                <el-button text size="small" type="danger"><el-icon><Delete /></el-icon></el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && trips.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p class="empty-title">{{ searchText ? '未找到匹配的行程' : '暂无行程数据' }}</p>
      <p class="empty-desc">{{ searchText ? '试试其他关键词' : '计划员创建的行程将在这里显示' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getAdminTrips, adminUpdateTripStatus, adminDeleteTrip } from '@/api/trips'

const trips = ref([])
const allTrips = ref([])
const loading = ref(true)
const searchText = ref('')
const filterStatus = ref('')
const sortOrder = ref('')

const statusOptions = [
  { value: 'draft', label: '草稿' },
  { value: 'confirmed', label: '已确认' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
]

function countByStatus(s) {
  return allTrips.value.filter(t => t.status === s).length
}

function statusType(s) {
  return { draft: 'info', confirmed: '', completed: 'success', cancelled: 'danger' }[s] || 'info'
}
function statusLabel(s) {
  return { draft: '草稿', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }[s] || s
}
function formatDate(dt) {
  if (!dt) return '-'
  return dt.slice(0, 10)
}

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

function handleSort({ prop, order }) {
  if (prop === 'created_at') {
    sortOrder.value = order
    if (order === 'ascending') {
      trips.value.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    } else if (order === 'descending') {
      trips.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }
  }
}

async function loadTrips() {
  loading.value = true
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (searchText.value) params.keyword = searchText.value
    trips.value = await getAdminTrips(params)
    // 首次或无筛选时更新全量数据用于统计
    if (!filterStatus.value && !searchText.value) {
      allTrips.value = [...trips.value]
    }
  } finally { loading.value = false }
}

async function handleStatusChange(row, newStatus) {
  try {
    await adminUpdateTripStatus(row.id, { status: newStatus })
    ElMessage.success('状态已更新')
    // 更新本地数据
    row.status = newStatus
    // 同步 allTrips
    const at = allTrips.value.find(t => t.id === row.id)
    if (at) at.status = newStatus
  } catch {
    ElMessage.error('更新失败')
  }
}

async function handleDelete(row) {
  try {
    await adminDeleteTrip(row.id)
    ElMessage.success('已删除')
    trips.value = trips.value.filter(t => t.id !== row.id)
    allTrips.value = allTrips.value.filter(t => t.id !== row.id)
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(async () => {
  // 先加载全量用于统计
  loading.value = true
  try {
    allTrips.value = await getAdminTrips({})
    trips.value = [...allTrips.value]
  } finally { loading.value = false }
})
</script>

<style scoped>
.admin-trips { max-width: 1100px; }

/* 统计卡片 */
.stat-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.stat-card {
  background: #fff; border-radius: 16px; padding: 18px;
  display: flex; align-items: center; gap: 14px;
  border: 2px solid transparent; cursor: pointer; transition: all 0.3s ease;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.stat-card.active { border-color: #f59e0b; background: #fffbeb; box-shadow: 0 4px 16px rgba(245,158,11,0.15); }
.stat-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0;
}
.stat-icon.all { background: linear-gradient(135deg, #e6a23c, #f59e0b); }
.stat-icon.draft { background: linear-gradient(135deg, #8b5cf6, #6366f1); }
.stat-icon.confirmed { background: linear-gradient(135deg, #3b82f6, #06b6d4); }
.stat-icon.completed { background: linear-gradient(135deg, #10b981, #059669); }
.stat-value { font-size: 24px; font-weight: 800; color: #1a1a2e; line-height: 1.2; }
.stat-label { font-size: 13px; color: #909399; font-weight: 500; margin-top: 2px; }

/* 工具栏 */
.page-toolbar { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
.search-input { width: 280px; }

/* 表格 */
.table-wrap {
  background: #fff; border-radius: 18px; overflow: hidden;
  border: 1px solid rgba(0,0,0,0.04);
}
.trip-table :deep(.el-table__header th) {
  background: #fefce8 !important; color: #92400e; font-weight: 600; font-size: 13px;
}

.trip-cell { display: flex; flex-direction: column; gap: 4px; }
.trip-cell-main { display: flex; align-items: center; gap: 8px; }
.trip-name { font-weight: 600; font-size: 14px; color: #1a1a2e; }
.trip-id { font-size: 11px; color: #c0c4cc; background: #f5f7fa; padding: 1px 6px; border-radius: 4px; }
.trip-cell-meta { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #909399; }
.trip-date { display: flex; align-items: center; gap: 3px; }
.trip-people { color: #d97706; }
.trip-acts { color: #8b5cf6; }

.creator-cell { display: flex; align-items: center; gap: 8px; }
.creator-avatar {
  background: linear-gradient(135deg, #e6a23c, #f59e0b);
  color: #fff; font-weight: 600; font-size: 11px; flex-shrink: 0;
}
.creator-name { font-size: 13px; color: #1a1a2e; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.time-text { font-size: 13px; color: #909399; }
.text-muted { color: #c0c4cc; }
.action-btn { color: #d97706; }
.action-btn:hover { color: #b45309; }

/* 空状态 */
.empty-state { text-align: center; padding: 60px 0; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-title { font-size: 16px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.empty-desc { font-size: 13px; color: #909399; }

@media (max-width: 1024px) { .stat-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 14px; }
  .stat-value { font-size: 20px; }
  .page-toolbar { flex-wrap: wrap; }
  .search-input { flex: 1; width: auto !important; min-width: 180px; }
  .table-wrap { overflow-x: auto; }
  .table-wrap :deep(.el-table) { min-width: 700px; }
}
@media (max-width: 480px) {
  .stat-cards { grid-template-columns: 1fr 1fr; gap: 8px; }
  .stat-card { padding: 12px; gap: 10px; }
  .stat-icon { width: 36px; height: 36px; }
  .stat-value { font-size: 18px; }
}
</style>
