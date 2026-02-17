<template>
  <div v-if="trip" class="trip-detail-page">
    <!-- 顶部信息卡片 -->
    <div class="detail-hero">
      <div class="hero-top">
        <div class="hero-back" @click="router.push('/trips')">
          <el-icon size="18"><ArrowLeft /></el-icon>
          <span>返回列表</span>
        </div>
        <div class="hero-actions">
          <el-dropdown @command="handleExport">
            <el-button round>
              <el-icon><Download /></el-icon> 导出
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
                <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button round @click="showShare = true">
            <el-icon><Share /></el-icon> 分享
          </el-button>
          <el-dropdown @command="handleStatus" trigger="click">
            <el-button round>
              <span class="status-btn-dot" :style="{ background: statusColor(trip.status) }"></span>
              {{ statusLabel(trip.status) }}
              <el-icon style="margin-left:4px"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="s in statusOptions" :key="s.value" :command="s.value" :disabled="trip.status === s.value">
                  <span class="status-option">
                    <span class="status-option-dot" :style="{ background: s.color }"></span>
                    {{ s.label }}
                    <el-icon v-if="trip.status === s.value" size="14" style="margin-left:auto;color:#8b5cf6"><Check /></el-icon>
                  </span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div class="hero-body">
        <div class="hero-title-row">
          <h1 class="hero-title">{{ trip.name }}</h1>
          <el-tag :type="statusType(trip.status)" size="large" effect="plain" round class="status-tag">
            {{ statusLabel(trip.status) }}
          </el-tag>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="detail-stats">
        <div class="detail-stat-card">
          <div class="detail-stat-icon date">
            <el-icon size="18"><Calendar /></el-icon>
          </div>
          <div class="detail-stat-body">
            <span class="detail-stat-value">{{ trip.start_date }} ~ {{ trip.end_date }}</span>
            <span class="detail-stat-label">出行日期 · {{ totalDays }}天</span>
          </div>
        </div>
        <div class="detail-stat-card">
          <div class="detail-stat-icon people">
            <el-icon size="18"><User /></el-icon>
          </div>
          <div class="detail-stat-body">
            <span class="detail-stat-value">{{ trip.guest_count }} 人</span>
            <span class="detail-stat-label">出行人数</span>
          </div>
        </div>
        <div class="detail-stat-card" v-if="trip.budget">
          <div class="detail-stat-icon budget">
            <el-icon size="18"><Money /></el-icon>
          </div>
          <div class="detail-stat-body">
            <span class="detail-stat-value">¥{{ Number(trip.budget).toLocaleString() }}</span>
            <span class="detail-stat-label">预算总额</span>
          </div>
        </div>
        <div class="detail-stat-card" v-if="totalCost > 0">
          <div class="detail-stat-icon cost" :class="{ over: budgetPercent > 100 }">
            <el-icon size="18"><Coin /></el-icon>
          </div>
          <div class="detail-stat-body">
            <span class="detail-stat-value">¥{{ totalCost.toLocaleString() }}</span>
            <span class="detail-stat-label">已花费{{ trip.budget ? ` · ${budgetPercent}%` : '' }}</span>
          </div>
          <div v-if="trip.budget" class="detail-stat-bar">
            <div class="detail-stat-bar-fill" :style="{ width: Math.min(budgetPercent, 100) + '%' }" :class="{ over: budgetPercent > 100 }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 活动安排区域 -->
    <div class="activities-section">
      <div class="section-toolbar">
        <h3 class="section-title">
          <span class="title-icon">📋</span> 活动安排
          <span class="act-count" v-if="activities.length">{{ activities.length }}项</span>
        </h3>
        <div class="toolbar-right">
          <el-switch v-model="continuousMode" active-text="连续添加" size="small" />
          <el-button type="primary" round @click="openActivityDialog()">
            <el-icon><Plus /></el-icon> 添加活动
          </el-button>
        </div>
      </div>

      <!-- 加载态 -->
      <div v-if="loading" style="padding:20px 0">
        <el-skeleton :rows="4" animated />
      </div>

      <!-- 按天分组 -->
      <template v-else-if="activities.length">
        <div v-for="(dayActs, dayLabel) in groupedActivities" :key="dayLabel" class="day-group">
          <div class="day-header">
            <div class="day-indicator">
              <div class="day-dot"></div>
              <div class="day-line"></div>
            </div>
            <div class="day-info">
              <span class="day-title">{{ dayLabel }}</span>
              <span class="day-cost" v-if="getDayCost(dayActs) > 0">
                <el-icon size="12"><Coin /></el-icon> ¥{{ getDayCost(dayActs).toLocaleString() }}
              </span>
            </div>
            <el-button text size="small" class="day-add-btn" @click="openActivityForDay(dayLabel)">
              <el-icon><Plus /></el-icon> 添加
            </el-button>
          </div>

          <div class="day-activities">
            <div v-for="act in dayActs" :key="act.id" class="activity-card" @click="openActivityDialog(act)">
              <div class="act-type-badge" :class="act.type">
                {{ actTypeIcon(act.type) }}
              </div>
              <div class="act-body">
                <div class="act-main-row">
                  <span class="act-name">{{ act.name }}</span>
                  <span v-if="act.cost" class="act-cost">¥{{ act.cost }}</span>
                </div>
                <div class="act-detail-row">
                  <span class="act-time" v-if="formatHour(act.start_time)">
                    <el-icon size="12"><Clock /></el-icon>
                    {{ formatHour(act.start_time) }} - {{ formatHour(act.end_time) }}
                  </span>
                  <span class="act-location" v-if="act.location">
                    <el-icon size="12"><Location /></el-icon>
                    {{ act.location }}
                  </span>
                </div>
                <div v-if="act.notes" class="act-notes">{{ act.notes }}</div>
              </div>
              <div class="act-actions" @click.stop>
                <el-button text size="small" circle type="danger" @click="handleDeleteActivity(act.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else class="empty-activities">
        <div class="empty-icon">🗓️</div>
        <p class="empty-title">暂无活动安排</p>
        <p class="empty-desc">添加第一个活动，开始规划行程吧</p>
        <el-button type="primary" round @click="openActivityDialog()">
          <el-icon><Plus /></el-icon> 添加活动
        </el-button>
      </div>
    </div>

    <!-- 活动编辑对话框 -->
    <el-dialog v-model="showActivity" :title="editingActivity ? '编辑活动' : '添加活动'" width="580px" :close-on-click-modal="false">
      <el-form :model="actForm" :rules="actRules" ref="actFormRef" label-width="80px">
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="actForm.type" @change="onTypeChange">
            <el-radio-button value="transport">🚌 交通</el-radio-button>
            <el-radio-button value="attraction">🏛️ 景点</el-radio-button>
            <el-radio-button value="meal">🍽️ 餐饮</el-radio-button>
            <el-radio-button value="hotel">🏨 住宿</el-radio-button>
            <el-radio-button value="free">🎯 自由</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="actForm.name" :placeholder="namePlaceholder" />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker v-model="actForm.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" :disabled-date="disableDate" style="width:100%" />
        </el-form-item>
        <el-form-item label="时间段">
          <div style="display:flex;gap:12px;align-items:center;width:100%">
            <el-time-picker v-model="actForm.startHour" placeholder="开始" format="HH:mm" style="flex:1" />
            <span style="color:#909399">至</span>
            <el-time-picker v-model="actForm.endHour" placeholder="结束" format="HH:mm" style="flex:1" />
          </div>
        </el-form-item>
        <el-form-item label="地点">
          <el-input v-model="actForm.location" :placeholder="locationPlaceholder" />
        </el-form-item>
        <el-form-item label="费用">
          <el-input v-model.number="actForm.cost" placeholder="选填" type="number">
            <template #prefix>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="actForm.notes" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showActivity = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveActivity">
          {{ continuousMode && !editingActivity ? '保存并继续' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 分享对话框 -->
    <el-dialog v-model="showShare" title="分享行程" width="400px">
      <div v-if="shareInfo" style="text-align:center">
        <p style="margin-bottom:12px;color:#606266">将链接发送给他人即可查看行程</p>
        <el-input :model-value="shareUrl" readonly>
          <template #append>
            <el-button @click="copyShareUrl">复制</el-button>
          </template>
        </el-input>
        <img :src="qrcodeUrl" alt="二维码" style="width:180px;margin-top:16px;border-radius:12px" />
      </div>
    </el-dialog>
  </div>

  <div v-else style="padding:40px 0">
    <el-skeleton :rows="6" animated />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import {
  getTrip, updateTrip, getActivities, createActivity, updateActivity,
  deleteActivity, exportPdf, exportExcel, getShareInfo, getQrcodeUrl
} from '@/api/trips'

const route = useRoute()
const router = useRouter()
const tripId = computed(() => Number(route.params.id))

const trip = ref(null)
const activities = ref([])
const loading = ref(true)
const showActivity = ref(false)
const showShare = ref(false)
const editingActivity = ref(null)
const saving = ref(false)
const shareInfo = ref(null)
const actFormRef = ref(null)
const continuousMode = ref(false)

const actForm = reactive({
  type: 'attraction', name: '', date: null, startHour: null, endHour: null,
  location: '', cost: null, notes: ''
})

const actRules = {
  name: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const namePlaceholder = computed(() => ({
  transport: '如：昆明→大理 高铁', attraction: '如：洱海骑行',
  meal: '如：午餐·云南过桥米线', hotel: '如：大理洱海边酒店', free: '如：自由活动'
}[actForm.type] || '活动名称'))

const locationPlaceholder = computed(() => ({
  transport: '出发地 → 目的地', attraction: '景点地址',
  meal: '餐厅名称/地址', hotel: '酒店地址', free: '活动区域'
}[actForm.type] || '选填'))

const statusLabel = (s) => ({ draft: '草稿', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', confirmed: 'success', completed: '', cancelled: 'danger' }[s] || 'info')
const statusColor = (s) => ({ draft: '#909399', confirmed: '#10b981', completed: '#8b5cf6', cancelled: '#ef4444' }[s] || '#909399')
const statusOptions = [
  { value: 'draft', label: '草稿', color: '#909399' },
  { value: 'confirmed', label: '已确认', color: '#10b981' },
  { value: 'completed', label: '已完成', color: '#8b5cf6' },
  { value: 'cancelled', label: '已取消', color: '#ef4444' },
]
const actTypeIcon = (t) => ({ transport: '🚌', attraction: '🏛️', meal: '🍽️', hotel: '🏨', free: '🎯' }[t] || '📌')
const formatHour = (t) => t ? dayjs(t).format('HH:mm') : ''

const totalDays = computed(() => {
  if (!trip.value) return 0
  return dayjs(trip.value.end_date).diff(dayjs(trip.value.start_date), 'day') + 1
})

const totalCost = computed(() => activities.value.reduce((sum, a) => sum + Number(a.cost || 0), 0))
const budgetPercent = computed(() => trip.value?.budget ? Math.round(totalCost.value / Number(trip.value.budget) * 100) : 0)
const getDayCost = (dayActs) => dayActs.reduce((sum, a) => sum + Number(a.cost || 0), 0)

const groupedActivities = computed(() => {
  const groups = {}
  const sorted = [...activities.value].sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  for (const act of sorted) {
    const date = dayjs(act.start_time).format('YYYY-MM-DD')
    const dayNum = trip.value ? dayjs(date).diff(dayjs(trip.value.start_date), 'day') + 1 : 0
    const label = `第${dayNum}天 · ${date}`
    if (!groups[label]) groups[label] = []
    groups[label].push(act)
  }
  return groups
})

const shareUrl = computed(() => shareInfo.value ? `${window.location.origin}/share/${shareInfo.value.share_code}` : '')
const qrcodeUrl = computed(() => getQrcodeUrl(tripId.value))

function disableDate(date) {
  if (!trip.value) return false
  const d = dayjs(date).format('YYYY-MM-DD')
  return d < trip.value.start_date || d > trip.value.end_date
}

function onTypeChange(type) {
  const defaults = {
    transport: { start: '08:00', end: '12:00' }, attraction: { start: '09:00', end: '12:00' },
    meal: { start: '12:00', end: '13:30' }, hotel: { start: '20:00', end: '08:00' },
    free: { start: '14:00', end: '17:00' }
  }
  const d = defaults[type]
  if (d && !editingActivity.value) {
    actForm.startHour = new Date(`2000-01-01T${d.start}`)
    actForm.endHour = new Date(`2000-01-01T${d.end}`)
  }
}

async function loadData() {
  loading.value = true
  try {
    trip.value = await getTrip(tripId.value)
    activities.value = await getActivities(tripId.value)
  } finally { loading.value = false }
}

function openActivityDialog(act = null) {
  editingActivity.value = act
  if (act) {
    Object.assign(actForm, {
      type: act.type, name: act.name,
      date: dayjs(act.start_time).format('YYYY-MM-DD'),
      startHour: new Date(act.start_time), endHour: new Date(act.end_time),
      location: act.location || '', cost: act.cost, notes: act.notes || ''
    })
  } else {
    Object.assign(actForm, {
      type: 'attraction', name: '', date: trip.value?.start_date || null,
      startHour: new Date('2000-01-01T09:00'), endHour: new Date('2000-01-01T12:00'),
      location: '', cost: null, notes: ''
    })
  }
  showActivity.value = true
}

function openActivityForDay(dayLabel) {
  const match = dayLabel.match(/\d{4}-\d{2}-\d{2}/)
  const date = match ? match[0] : trip.value?.start_date
  editingActivity.value = null
  Object.assign(actForm, {
    type: 'attraction', name: '', date,
    startHour: new Date('2000-01-01T09:00'), endHour: new Date('2000-01-01T12:00'),
    location: '', cost: null, notes: ''
  })
  showActivity.value = true
}

async function handleSaveActivity() {
  const valid = await actFormRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!actForm.startHour || !actForm.endHour) { ElMessage.warning('请选择时间段'); return }
  saving.value = true
  try {
    const date = actForm.date
    const sh = dayjs(actForm.startHour).format('HH:mm')
    const eh = dayjs(actForm.endHour).format('HH:mm')
    const data = {
      type: actForm.type, name: actForm.name,
      start_time: `${date}T${sh}:00`, end_time: `${date}T${eh}:00`,
      location: actForm.location || null, cost: actForm.cost || null, notes: actForm.notes || null
    }
    if (editingActivity.value) {
      await updateActivity(tripId.value, editingActivity.value.id, data)
      showActivity.value = false
      ElMessage.success('已更新')
    } else {
      await createActivity(tripId.value, data)
      ElMessage.success('已添加')
      if (continuousMode.value) {
        const keepDate = actForm.date, keepType = actForm.type
        Object.assign(actForm, {
          type: keepType, name: '', date: keepDate,
          startHour: actForm.endHour, endHour: null,
          location: '', cost: null, notes: ''
        })
        actFormRef.value?.clearValidate()
      } else { showActivity.value = false }
    }
    activities.value = await getActivities(tripId.value)
  } finally { saving.value = false }
}

async function handleDeleteActivity(actId) {
  await ElMessageBox.confirm('确定删除该活动？', '删除确认', {
    type: 'warning', confirmButtonText: '删除', confirmButtonClass: 'el-button--danger'
  })
  await deleteActivity(tripId.value, actId)
  ElMessage.success('已删除')
  activities.value = await getActivities(tripId.value)
}

async function handleStatus(status) {
  if (trip.value.status === status) return
  const label = statusLabel(status)
  try {
    await ElMessageBox.confirm(
      `确定将行程状态改为「${label}」？`,
      '更改状态',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
  } catch { return }
  try {
    await updateTrip(tripId.value, { status })
    trip.value = await getTrip(tripId.value)
    ElMessage.success(`状态已更新为「${label}」`)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '状态更新失败')
  }
}

async function handleExport(type) {
  const token = localStorage.getItem('token')
  const url = type === 'pdf' ? exportPdf(tripId.value) : exportExcel(tripId.value)
  const typeName = type === 'pdf' ? 'PDF' : 'Excel'
  try {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) {
      let msg = `导出${typeName}失败`
      try {
        const err = await res.json()
        if (err.detail) msg = err.detail
      } catch {}
      ElMessage.error(msg)
      return
    }
    const blob = await res.blob()
    if (!blob.size) {
      ElMessage.error(`导出${typeName}失败：文件为空`)
      return
    }
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${trip.value?.name || 'trip'}_${tripId.value}.${type === 'pdf' ? 'pdf' : 'xlsx'}`
    a.click()
    URL.revokeObjectURL(a.href)
    ElMessage.success(`${typeName}导出成功`)
  } catch (e) {
    ElMessage.error(`导出${typeName}失败，请检查网络连接`)
  }
}

async function copyShareUrl() {
  await navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('已复制')
}

onMounted(async () => {
  await loadData()
  shareInfo.value = await getShareInfo(tripId.value)
})
</script>

<style scoped>
.trip-detail-page { max-width: 960px; }

/* ===== Hero 顶部卡片 ===== */
.detail-hero {
  background: #fff;
  border-radius: 20px;
  padding: 26px 30px;
  margin-bottom: 24px;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 1px 2px rgba(0,0,0,0.02);
}
.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.hero-back {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 10px;
  transition: all 0.25s ease;
  font-weight: 500;
}
.hero-back:hover { color: #7c3aed; background: #ede9fe; }
.hero-actions { display: flex; gap: 8px; }

.hero-body { margin-bottom: 0; }
.hero-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 0;
}
.hero-title {
  font-size: 24px;
  font-weight: 800;
  color: #1a1a2e;
  letter-spacing: -0.5px;
  margin: 0;
}
.status-tag { font-size: 13px; }
.status-btn-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-width: 100px;
}
.status-option-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 统计卡片 */
.detail-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
}
.detail-stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #f8f9fc;
  border-radius: 14px;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
}
.detail-stat-card:hover {
  background: #f0f2f8;
}
.detail-stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.detail-stat-icon.date {
  background: linear-gradient(135deg, #ede9fe, #ddd6fe);
  color: #7c3aed;
}
.detail-stat-icon.people {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  color: #10b981;
}
.detail-stat-icon.budget {
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  color: #d97706;
}
.detail-stat-icon.cost {
  background: linear-gradient(135deg, #f5f3ff, #ede9fe);
  color: #8b5cf6;
}
.detail-stat-icon.cost.over {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #ef4444;
}
.detail-stat-body {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  flex: 1;
}
.detail-stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.detail-stat-label {
  font-size: 12px;
  color: #a8abb2;
  font-weight: 500;
}
.detail-stat-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #f0f0f5;
}
.detail-stat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6, #6366f1);
  border-radius: 0 2px 2px 0;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.detail-stat-bar-fill.over {
  background: linear-gradient(90deg, #f87171, #fbbf24);
}

/* ===== 活动区域 ===== */
.activities-section {
  background: #fff;
  border-radius: 20px;
  padding: 26px 30px;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 1px 2px rgba(0,0,0,0.02);
}
.section-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.section-title {
  font-size: 17px;
  font-weight: 800;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  letter-spacing: -0.3px;
}
.title-icon { font-size: 20px; }
.act-count {
  font-size: 12px;
  font-weight: 500;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 10px;
  border-radius: 10px;
}
.toolbar-right { display: flex; align-items: center; gap: 12px; }

/* ===== 天分组 ===== */
.day-group { margin-bottom: 28px; }
.day-group:last-child { margin-bottom: 0; }

.day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.day-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}
.day-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
  flex-shrink: 0;
}
.day-info { display: flex; align-items: center; gap: 12px; flex: 1; }
.day-title {
  font-size: 15px;
  font-weight: 600;
  color: #7c3aed;
}
.day-cost {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #d97706;
  font-weight: 500;
  background: #fffbeb;
  padding: 2px 10px;
  border-radius: 10px;
}
.day-add-btn {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: auto;
}
.day-add-btn:hover { color: #7c3aed; }

/* ===== 活动卡片 ===== */
.day-activities {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-left: 4px;
  padding-left: 20px;
  border-left: 2px solid #eef0f4;
}

.activity-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 20px;
  background: #fafbfd;
  border-radius: 14px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.activity-card:hover {
  background: #fff;
  border-color: rgba(14, 165, 233, 0.12);
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.06);
  transform: translateX(4px);
}

.act-type-badge {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.act-type-badge.transport { background: linear-gradient(135deg, #fff7ed, #ffedd5); }
.act-type-badge.attraction { background: linear-gradient(135deg, #ecfdf5, #d1fae5); }
.act-type-badge.meal { background: linear-gradient(135deg, #fef2f2, #fee2e2); }
.act-type-badge.hotel { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.act-type-badge.free { background: linear-gradient(135deg, #eff6ff, #dbeafe); }

.act-body { flex: 1; min-width: 0; }
.act-main-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.act-name {
  font-weight: 600;
  font-size: 14px;
  color: #1a1a2e;
}
.act-cost {
  color: #d97706;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}
.act-detail-row {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}
.act-time, .act-location {
  display: flex;
  align-items: center;
  gap: 3px;
}
.act-notes {
  font-size: 12px;
  color: #a8abb2;
  margin-top: 4px;
  line-height: 1.5;
}
.act-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.activity-card:hover .act-actions { opacity: 1; }

/* ===== 空状态 ===== */
.empty-activities {
  text-align: center;
  padding: 60px 0;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-title { font-size: 16px; font-weight: 600; color: #303133; margin-bottom: 6px; }
.empty-desc { font-size: 13px; color: #909399; margin-bottom: 20px; }

@media (max-width: 768px) {
  .detail-hero { padding: 20px; border-radius: 16px; }
  .hero-top { flex-direction: column; gap: 12px; align-items: flex-start; }
  .hero-actions { width: 100%; display: flex; flex-wrap: wrap; gap: 8px; }
  .hero-actions .el-button { flex: 1; min-width: 0; }
  .hero-title { font-size: 20px; }
  .detail-stats { grid-template-columns: 1fr 1fr; }
  .activities-section { padding: 20px; border-radius: 16px; }
  .section-toolbar { flex-direction: column; gap: 12px; align-items: flex-start; }
  .toolbar-right { width: 100%; justify-content: space-between; }
  .day-activities { padding-left: 14px; }
  .activity-card { padding: 14px 16px; gap: 10px; }
  .act-type-badge { width: 36px; height: 36px; font-size: 16px; }
  .act-actions { opacity: 1; }
}

@media (max-width: 480px) {
  .detail-hero { padding: 16px; }
  .hero-title { font-size: 18px; }
  .hero-actions .el-button { font-size: 12px; }
  .detail-stats { grid-template-columns: 1fr; }
  .detail-stat-card { padding: 12px 14px; }
  .activities-section { padding: 16px; }
  .activity-card { flex-direction: column; gap: 8px; padding: 12px 14px; }
  .act-main-row { flex-direction: column; align-items: flex-start; gap: 4px; }
  .act-detail-row { flex-direction: column; gap: 4px; }
}
</style>
