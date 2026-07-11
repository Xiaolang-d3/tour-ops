<template>
  <div class="trip-list-page">
    <!-- 顶部统计卡片 -->
    <div class="stats-grid" v-if="trips.length">
      <div class="stat-card" @click="filterStatus = ''" :class="{ active: !filterStatus }">
        <div class="stat-icon all"><el-icon size="20"><Suitcase /></el-icon></div>
        <div class="stat-content">
          <span class="stat-num">{{ trips.length }}</span>
          <span class="stat-label">全部行程</span>
        </div>
      </div>
      <div class="stat-card" @click="filterStatus = 'draft'" :class="{ active: filterStatus === 'draft' }">
        <div class="stat-icon draft"><el-icon size="20"><EditPen /></el-icon></div>
        <div class="stat-content">
          <span class="stat-num">{{ trips.filter(t => t.status === 'draft').length }}</span>
          <span class="stat-label">草稿</span>
        </div>
      </div>
      <div class="stat-card" @click="filterStatus = 'confirmed'" :class="{ active: filterStatus === 'confirmed' }">
        <div class="stat-icon confirmed"><el-icon size="20"><CircleCheck /></el-icon></div>
        <div class="stat-content">
          <span class="stat-num">{{ trips.filter(t => t.status === 'confirmed').length }}</span>
          <span class="stat-label">已确认</span>
        </div>
      </div>
      <div class="stat-card" @click="filterStatus = 'completed'" :class="{ active: filterStatus === 'completed' }">
        <div class="stat-icon completed"><el-icon size="20"><Trophy /></el-icon></div>
        <div class="stat-content">
          <span class="stat-num">{{ trips.filter(t => t.status === 'completed').length }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="page-toolbar">
      <div class="toolbar-left">
        <el-input v-model="searchText" placeholder="搜索行程..." prefix-icon="Search" clearable class="search-input" />
        <el-select v-model="sortBy" style="width:150px" placeholder="排序">
          <el-option label="最近创建" value="created_desc" />
          <el-option label="出发日期↑" value="start_asc" />
          <el-option label="出发日期↓" value="start_desc" />
        </el-select>
      </div>
      <el-button type="primary" @click="openCreateDialog" round size="large">
        <el-icon><Plus /></el-icon> 新建行程
      </el-button>
    </div>

    <!-- 加载态 -->
    <div v-if="loading" class="trip-grid">
      <div v-for="i in 6" :key="i" class="trip-grid-item">
        <div class="trip-card"><div class="card-inner"><el-skeleton :rows="4" animated /></div></div>
      </div>
    </div>

    <!-- 行程卡片 -->
    <transition-group v-else-if="sortedTrips.length" name="card-list" tag="div" class="trip-grid">
      <div v-for="trip in sortedTrips" :key="trip.id" class="trip-grid-item">
        <div class="trip-card" :class="trip.status" @click="router.push(`/trips/${trip.id}`)">
          <!-- 顶部彩条 -->
          <div class="card-status-bar" :class="trip.status"></div>
          <div class="card-inner">
            <!-- 标题行 -->
            <div class="card-header">
              <h3 class="trip-name">{{ trip.name }}</h3>
              <el-tag :type="statusType(trip.status)" size="small" effect="plain" round>{{ statusLabel(trip.status) }}</el-tag>
            </div>

            <!-- 日期 + 倒计时 -->
            <div class="card-date-row">
              <div class="card-date">
                <el-icon size="14"><Calendar /></el-icon>
                <span>{{ trip.start_date }} ~ {{ trip.end_date }}</span>
              </div>
              <span class="days-badge">{{ getDays(trip) }}天</span>
            </div>

            <!-- 时间状态提示 -->
            <div class="card-time-hint" v-if="getTimeHint(trip)">
              <span class="time-hint-dot" :class="getTimeHint(trip).type"></span>
              {{ getTimeHint(trip).text }}
            </div>

            <!-- 进度条（已确认/进行中的行程） -->
            <div class="card-progress" v-if="trip.status === 'confirmed' && getTripProgress(trip) !== null">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: getTripProgress(trip) + '%' }"></div>
              </div>
              <span class="progress-text">行程进度 {{ getTripProgress(trip) }}%</span>
            </div>

            <!-- 信息标签 -->
            <div class="card-tags">
              <div class="info-chip">
                <el-icon size="13"><User /></el-icon>
                {{ trip.guest_count }}人
              </div>
              <div v-if="trip.budget" class="info-chip budget">
                <el-icon size="13"><Money /></el-icon>
                ¥{{ Number(trip.budget).toLocaleString() }}
              </div>
            </div>

            <!-- 底部操作 -->
            <div class="card-bottom" @click.stop>
              <div class="card-bottom-left">
                <span class="card-id">#{{ trip.id }}</span>
              </div>
              <div class="card-bottom-right">
                <el-tooltip content="分享" placement="top">
                  <el-button text size="small" @click="handleShare(trip)">
                    <el-icon><Share /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-dropdown trigger="click" @command="(cmd) => handleExport(trip.id, cmd)" @click.stop>
                  <el-tooltip content="导出" placement="top">
                    <el-button text size="small" @click.stop>
                      <el-icon><Download /></el-icon>
                    </el-button>
                  </el-tooltip>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
                      <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-tooltip content="删除" placement="top">
                  <el-button text size="small" type="danger" @click="handleDelete(trip.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition-group>

    <!-- 空状态 -->
    <div v-else class="empty-wrap">
      <div class="empty-illustration">📋</div>
      <p class="empty-title">{{ searchText || filterStatus ? '没有匹配的行程' : '还没有行程' }}</p>
      <p class="empty-desc">{{ searchText || filterStatus ? '试试调整筛选条件' : '创建你的第一个行程，开始规划旅途吧' }}</p>
      <el-button v-if="!searchText && !filterStatus" type="primary" round size="large" @click="openCreateDialog">
        <el-icon><Plus /></el-icon> 创建行程
      </el-button>
      <el-button v-else text @click="searchText = ''; filterStatus = ''">清除筛选</el-button>
    </div>

    <!-- 分享对话框 -->
    <el-dialog v-model="showShare" title="分享行程" width="400px">
      <div v-if="shareUrl" style="text-align:center">
        <p style="margin-bottom:12px;color:#606266">将链接发送给他人即可查看行程（无需登录）</p>
        <el-input :model-value="shareUrl" readonly>
          <template #append>
            <el-button @click="copyShareUrl">复制</el-button>
          </template>
        </el-input>
      </div>
      <div v-else style="text-align:center;padding:20px 0">
        <el-icon class="is-loading" size="24"><Loading /></el-icon>
      </div>
    </el-dialog>

    <!-- 新建行程对话框 -->
    <el-dialog v-model="showCreate" title="新建行程" width="600px" destroy-on-close top="8vh">
      <el-steps :active="step" finish-status="success" simple style="margin-bottom:28px">
        <el-step title="基本信息" />
        <el-step title="偏好设置" />
      </el-steps>

      <el-form v-show="step === 0" :model="form" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="行程类型" prop="trip_type">
          <div class="type-picker">
            <div v-for="t in tripTypes" :key="t.value" class="type-option" :class="{ active: form.trip_type === t.value }" @click="form.trip_type = t.value">
              <span class="type-emoji">{{ t.icon }}</span>
              <span class="type-name">{{ t.label }}</span>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="行程名称" prop="name">
          <el-input v-model="form.name" placeholder="如：云南7日游" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="出行日期" prop="dateRange">
          <el-date-picker v-model="form.dateRange" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" :disabled-date="(d) => d < new Date(new Date().setHours(0,0,0,0))" style="width:100%" />
        </el-form-item>
        <el-form-item v-if="form.dateRange" label="">
          <el-tag type="info" effect="plain" round>共 {{ calcDays }} 天</el-tag>
        </el-form-item>
        <el-form-item label="出行人数" prop="guest_count">
          <el-input-number v-model="form.guest_count" :min="1" :max="999" />
        </el-form-item>
        <el-form-item label="预算">
          <el-input v-model.number="form.budget" placeholder="选填，单位：元" type="number">
            <template #prefix>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="兴趣方向">
          <div class="interest-picker">
            <span v-for="tag in interestOptions" :key="tag" class="interest-chip" :class="{ active: form.interests.includes(tag) }" @click="toggleInterest(tag)">{{ tag }}</span>
          </div>
        </el-form-item>
      </el-form>

      <div v-show="step === 1" class="pref-step">
        <p class="pref-hint">以下为选填项，可帮助 AI 更好地生成行程建议</p>
        <el-form :model="form" label-width="80px">
          <el-form-item label="行程节奏">
            <el-radio-group v-model="form.pace">
              <el-radio-button value="tight">紧凑</el-radio-button>
              <el-radio-button value="moderate">适中</el-radio-button>
              <el-radio-button value="relaxed">休闲</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="住宿偏好">
            <el-radio-group v-model="form.accommodation">
              <el-radio-button value="budget">经济型</el-radio-button>
              <el-radio-button value="comfort">舒适型</el-radio-button>
              <el-radio-button value="luxury">豪华型</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="餐饮偏好">
            <el-checkbox-group v-model="form.dining">
              <el-checkbox value="local">当地特色</el-checkbox>
              <el-checkbox value="halal">清真</el-checkbox>
              <el-checkbox value="vegetarian">素食</el-checkbox>
              <el-checkbox value="none">无特殊</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="交通偏好">
            <el-radio-group v-model="form.transport">
              <el-radio-button value="bus">大巴</el-radio-button>
              <el-radio-button value="business_car">商务车</el-radio-button>
              <el-radio-button value="self_drive">自驾</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <!-- 场景专属字段 -->
          <template v-if="form.trip_type === 'team_building'">
            <el-form-item label="团建主题">
              <el-input v-model="form.custom1" placeholder="如：年度团建、新人融入、部门拓展" />
            </el-form-item>
            <el-form-item label="公司名称">
              <el-input v-model="form.custom2" placeholder="选填" />
            </el-form-item>
          </template>
          <template v-else-if="form.trip_type === 'study_tour'">
            <el-form-item label="研学主题">
              <el-input v-model="form.custom1" placeholder="如：历史文化、自然科学、红色教育" />
            </el-form-item>
            <el-form-item label="学生年龄">
              <el-input v-model="form.custom2" placeholder="如：10-12岁" />
            </el-form-item>
          </template>
          <template v-else-if="form.trip_type === 'business'">
            <el-form-item label="商务目的">
              <el-input v-model="form.custom1" placeholder="如：客户考察、会议接待" />
            </el-form-item>
          </template>
          <el-form-item label="自定义备注">
            <el-input v-model="form.custom3" placeholder="其他补充需求" />
          </el-form-item>
          <el-form-item label="特殊需求">
            <el-input v-model="form.special" type="textarea" :rows="2" placeholder="如：有老人小孩、需要轮椅通道等" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div style="display:flex;justify-content:space-between;width:100%">
          <div><el-button v-if="step === 1" @click="step = 0">上一步</el-button></div>
          <div style="display:flex;gap:8px">
            <el-button @click="showCreate = false">取消</el-button>
            <el-button v-if="step === 0" @click="handleNextStep">下一步</el-button>
            <el-button v-if="step === 0" type="primary" :loading="creating" @click="handleCreate(false)">直接创建</el-button>
            <el-button v-if="step === 1" type="primary" :loading="creating" @click="handleCreate(true)">创建行程</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { getTrips, createTrip, deleteTrip, exportPdf, exportExcel, getShareInfo } from '@/api/trips'

const router = useRouter()
const trips = ref([])
const loading = ref(true)
const showCreate = ref(false)
const creating = ref(false)
const searchText = ref('')
const filterStatus = ref('')
const sortBy = ref('created_desc')
const formRef = ref(null)
const step = ref(0)
const showShare = ref(false)
const shareUrl = ref('')

const form = reactive({
  name: '', dateRange: null, guest_count: 1, budget: null, trip_type: 'leisure',
  interests: [],
  pace: 'moderate', accommodation: 'comfort', dining: [], transport: 'bus', special: '',
  custom1: '', custom2: '', custom3: ''
})

const tripTypes = [
  { value: 'leisure', label: '常规旅游', icon: '🏖️' },
  { value: 'team_building', label: '企业团建', icon: '🤝' },
  { value: 'study_tour', label: '主题研学', icon: '📚' },
  { value: 'business', label: '商务考察', icon: '💼' },
]

const interestOptions = ['自然风光', '历史文化', '美食体验', '户外运动', '休闲度假', '亲子互动', '摄影打卡', '民俗体验']

function toggleInterest(tag) {
  const idx = form.interests.indexOf(tag)
  if (idx >= 0) form.interests.splice(idx, 1)
  else form.interests.push(tag)
}

const formRules = {
  name: [{ required: true, message: '请输入行程名称', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择出行日期', trigger: 'change' }],
  guest_count: [{ required: true, message: '请输入人数', trigger: 'change' }]
}

const calcDays = computed(() => {
  if (!form.dateRange) return 0
  return dayjs(form.dateRange[1]).diff(dayjs(form.dateRange[0]), 'day') + 1
})

const getDays = (trip) => dayjs(trip.end_date).diff(dayjs(trip.start_date), 'day') + 1

const filteredTrips = computed(() => {
  let list = trips.value
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    list = list.filter(t => t.name.toLowerCase().includes(kw))
  }
  if (filterStatus.value) list = list.filter(t => t.status === filterStatus.value)
  return list
})

const sortedTrips = computed(() => {
  const list = [...filteredTrips.value]
  switch (sortBy.value) {
    case 'start_asc': return list.sort((a, b) => a.start_date.localeCompare(b.start_date))
    case 'start_desc': return list.sort((a, b) => b.start_date.localeCompare(a.start_date))
    default: return list.sort((a, b) => (b.id || 0) - (a.id || 0))
  }
})

const statusLabel = (s) => ({ draft: '草稿', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ draft: 'info', confirmed: 'success', completed: '', cancelled: 'danger' }[s] || 'info')

function getTimeHint(trip) {
  const today = dayjs().startOf('day')
  const start = dayjs(trip.start_date)
  const end = dayjs(trip.end_date)
  if (trip.status === 'cancelled') return null
  if (trip.status === 'completed') return null
  if (today.isBefore(start)) {
    const diff = start.diff(today, 'day')
    if (diff <= 7) return { type: 'soon', text: `${diff}天后出发` }
    if (diff <= 30) return { type: 'upcoming', text: `${diff}天后出发` }
    return null
  }
  if ((today.isSame(start) || today.isAfter(start)) && (today.isSame(end) || today.isBefore(end))) {
    const dayNum = today.diff(start, 'day') + 1
    return { type: 'ongoing', text: `进行中 · 第${dayNum}天` }
  }
  if (today.isAfter(end) && trip.status !== 'completed') {
    return { type: 'overdue', text: '已过期未完成' }
  }
  return null
}

function getTripProgress(trip) {
  const today = dayjs().startOf('day')
  const start = dayjs(trip.start_date)
  const end = dayjs(trip.end_date)
  const total = end.diff(start, 'day') + 1
  if (today.isBefore(start)) return 0
  if (today.isAfter(end)) return 100
  const elapsed = today.diff(start, 'day') + 1
  return Math.round((elapsed / total) * 100)
}

function openCreateDialog() {
  step.value = 0
  Object.assign(form, {
    name: '', dateRange: null, guest_count: 1, budget: null, trip_type: 'leisure',
    interests: [],
    pace: 'moderate', accommodation: 'comfort', dining: [], transport: 'bus', special: '',
    custom1: '', custom2: '', custom3: ''
  })
  showCreate.value = true
}

async function loadTrips() {
  loading.value = true
  try { trips.value = await getTrips() } finally { loading.value = false }
}

async function handleNextStep() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  step.value = 1
}

async function handleCreate(withPrefs) {
  if (step.value === 0) {
    const valid = await formRef.value?.validate().catch(() => false)
    if (!valid) return
  }
  creating.value = true
  try {
    const payload = {
      name: form.name, start_date: form.dateRange[0], end_date: form.dateRange[1],
      guest_count: form.guest_count, budget: form.budget || null,
      trip_type: form.trip_type || null,
    }
    if (withPrefs) {
      payload.preferences = {
        pace: form.pace, accommodation: form.accommodation,
        dining: form.dining, transport: form.transport,
        interests: form.interests,
      }
      const customFields = {}
      if (form.custom1) customFields.custom1 = form.custom1
      if (form.custom2) customFields.custom2 = form.custom2
      if (form.custom3) customFields.custom3 = form.custom3
      if (form.special) customFields.notes = form.special
      if (Object.keys(customFields).length) payload.special_requirements = customFields
    } else {
      if (form.interests.length) {
        payload.preferences = { interests: form.interests }
      }
    }
    const res = await createTrip(payload)
    showCreate.value = false
    ElMessage.success('创建成功')
    router.push(`/trips/${res.id}`)
  } finally { creating.value = false }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除该行程？删除后不可恢复。', '删除确认', { type: 'warning', confirmButtonText: '删除', confirmButtonClass: 'el-button--danger' })
  await deleteTrip(id)
  ElMessage.success('已删除')
  loadTrips()
}

async function handleShare(trip) {
  shareUrl.value = ''
  showShare.value = true
  try {
    const info = await getShareInfo(trip.id)
    shareUrl.value = `${window.location.origin}/share/${info.share_code}`
  } catch {
    ElMessage.error('获取分享信息失败')
    showShare.value = false
  }
}

async function copyShareUrl() {
  await navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('链接已复制')
}

async function handleExport(tripId, type) {
  const token = localStorage.getItem('token')
  const url = type === 'pdf' ? exportPdf(tripId) : exportExcel(tripId)
  const typeName = type === 'pdf' ? 'PDF' : 'Excel'
  try {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) {
      ElMessage.error(`导出${typeName}失败`)
      return
    }
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `trip_${tripId}.${type === 'pdf' ? 'pdf' : 'xlsx'}`
    a.click()
    URL.revokeObjectURL(a.href)
    ElMessage.success(`${typeName}导出成功`)
  } catch {
    ElMessage.error(`导出${typeName}失败`)
  }
}

onMounted(loadTrips)
</script>

<style scoped>
.trip-list-page { max-width: 1200px; }

/* 统计卡片 */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card {
  background: #fff; border-radius: 16px; padding: 20px 22px;
  display: flex; align-items: center; gap: 16px;
  border: 1px solid rgba(0,0,0,0.04); box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  cursor: pointer; transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  position: relative; overflow: hidden;
}
.stat-card::before {
  content: ''; position: absolute; inset: 0; border-radius: 16px;
  border: 2px solid transparent; transition: border-color 0.3s; pointer-events: none;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.stat-card.active::before { border-color: #8b5cf6; }
.stat-card.active { box-shadow: 0 4px 16px rgba(139,92,246,0.12); }
.stat-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon.all { background: linear-gradient(135deg, #ede9fe, #ddd6fe); color: #7c3aed; }
.stat-icon.draft { background: linear-gradient(135deg, #f3f4f6, #e5e7eb); color: #9ca3af; }
.stat-icon.confirmed { background: linear-gradient(135deg, #ecfdf5, #d1fae5); color: #10b981; }
.stat-icon.completed { background: linear-gradient(135deg, #f5f3ff, #ede9fe); color: #8b5cf6; }
.stat-content { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 28px; font-weight: 800; color: #1a1a2e; line-height: 1.1; letter-spacing: -0.5px; }
.stat-label { font-size: 13px; color: #a8abb2; font-weight: 500; }

/* 工具栏 */
.page-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.toolbar-left { display: flex; gap: 12px; }
.search-input { width: 260px; }

/* 卡片网格 */
.trip-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.trip-grid-item { display: flex; }
.trip-card {
  background: #fff; border-radius: 18px; overflow: hidden; cursor: pointer;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 1px 2px rgba(0,0,0,0.02);
  transition: all 0.35s cubic-bezier(0.4,0,0.2,1); position: relative;
  width: 100%; display: flex; flex-direction: column;
}
.trip-card:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,0.06); }

.card-status-bar { height: 3px; }
.card-status-bar.draft { background: linear-gradient(90deg, #d1d5db, #e5e7eb); }
.card-status-bar.confirmed { background: linear-gradient(90deg, #10b981, #34d399); }
.card-status-bar.completed { background: linear-gradient(90deg, #8b5cf6, #6366f1); }
.card-status-bar.cancelled { background: linear-gradient(90deg, #f87171, #fca5a5); }

.card-inner { padding: 20px 22px 16px; flex: 1; display: flex; flex-direction: column; }

/* 标题 */
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 8px; }
.trip-name { font-size: 16px; font-weight: 700; color: #1a1a2e; line-height: 1.4; margin: 0; letter-spacing: -0.2px; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 日期行 */
.card-date-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.card-date { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #909399; }
.days-badge {
  display: inline-block; padding: 2px 10px; font-size: 11px; font-weight: 600;
  background: linear-gradient(135deg, #ede9fe, #ddd6fe); color: #7c3aed; border-radius: 10px;
}

/* 时间提示 */
.card-time-hint {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600; margin-bottom: 10px;
  padding: 6px 12px; border-radius: 8px; background: #f8f9fc;
}
.time-hint-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.time-hint-dot.soon { background: #f59e0b; animation: pulse-dot 1.5s infinite; }
.time-hint-dot.upcoming { background: #3b82f6; }
.time-hint-dot.ongoing { background: #10b981; animation: pulse-dot 1.5s infinite; }
.time-hint-dot.overdue { background: #ef4444; }
.card-time-hint:has(.soon) { color: #d97706; background: #fffbeb; }
.card-time-hint:has(.upcoming) { color: #2563eb; background: #eff6ff; }
.card-time-hint:has(.ongoing) { color: #059669; background: #ecfdf5; }
.card-time-hint:has(.overdue) { color: #dc2626; background: #fef2f2; }

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.4); }
}

/* 进度条 */
.card-progress { margin-bottom: 10px; }
.progress-bar { height: 4px; background: #f0f2f5; border-radius: 2px; overflow: hidden; }
.progress-fill {
  height: 100%; border-radius: 2px;
  background: linear-gradient(90deg, #10b981, #34d399);
  transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
}
.progress-text { font-size: 11px; color: #a8abb2; margin-top: 4px; display: block; }

/* 信息标签 */
.card-tags { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.info-chip {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 12px; font-size: 12px; color: #606266;
  background: #f8f9fc; border-radius: 8px; font-weight: 500;
}
.info-chip.budget { color: #d97706; background: #fffbeb; }

/* 底部操作 */
.card-bottom {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 1px solid #f5f6fa; margin-top: auto;
}
.card-bottom-left { display: flex; align-items: center; }
.card-id { font-size: 11px; color: #d0d3d9; font-weight: 600; font-family: monospace; }
.card-bottom-right { display: flex; gap: 2px; opacity: 0; transition: opacity 0.25s; }
.trip-card:hover .card-bottom-right { opacity: 1; }

/* 空状态 */
.empty-wrap { text-align: center; padding: 100px 0; }
.empty-illustration { font-size: 64px; margin-bottom: 16px; filter: grayscale(0.2); }
.empty-title { font-size: 18px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; }
.empty-desc { font-size: 14px; color: #909399; margin-bottom: 24px; }

/* 偏好步骤 */
.pref-step { padding: 0 10px; }
.pref-hint { color: #909399; font-size: 13px; margin-bottom: 20px; }

/* 行程类型选择 */
.type-picker { display: flex; gap: 10px; flex-wrap: wrap; }
.type-option {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 20px; border-radius: 14px; cursor: pointer;
  background: #f8f9fc; border: 2px solid transparent;
  transition: all 0.25s ease; min-width: 80px;
}
.type-option:hover { background: #f0f2f8; }
.type-option.active {
  background: #ede9fe; border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.12);
}
.type-emoji { font-size: 24px; }
.type-name { font-size: 12px; font-weight: 600; color: #606266; }
.type-option.active .type-name { color: #7c3aed; }

/* 兴趣标签 */
.interest-picker { display: flex; flex-wrap: wrap; gap: 8px; }
.interest-chip {
  padding: 6px 14px; border-radius: 20px; font-size: 13px;
  background: #f5f7fa; color: #606266; cursor: pointer;
  border: 1px solid transparent; transition: all 0.2s ease;
  user-select: none;
}
.interest-chip:hover { border-color: #c0c4cc; }
.interest-chip.active {
  background: #ede9fe; color: #7c3aed; border-color: #c4b5fd;
  font-weight: 500;
}

/* 动画 */
.card-list-enter-active { transition: all 0.4s cubic-bezier(0.4,0,0.2,1); }
.card-list-leave-active { transition: all 0.3s ease; }
.card-list-enter-from { opacity: 0; transform: translateY(20px) scale(0.97); }
.card-list-leave-to { opacity: 0; transform: scale(0.95); }

@media (max-width: 1024px) { .trip-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-card { padding: 14px 16px; }
  .stat-num { font-size: 22px; }
  .page-toolbar { flex-direction: column; gap: 12px; align-items: stretch; }
  .toolbar-left { flex-direction: column; gap: 8px; }
  .search-input { width: 100%; }
  .trip-grid { grid-template-columns: 1fr; gap: 14px; }
  .card-bottom-right { opacity: 1; }
}
@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .stat-card { padding: 12px 14px; gap: 10px; }
  .stat-icon { width: 40px; height: 40px; }
  .stat-num { font-size: 20px; }
  .card-inner { padding: 16px 18px 14px; }
  .trip-name { font-size: 15px; }
  .empty-wrap { padding: 60px 0; }
  .empty-illustration { font-size: 48px; }
  .empty-title { font-size: 16px; }
}
</style>
