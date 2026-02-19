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
          <el-dropdown @command="handleExport" :disabled="!canShareExport">
            <el-button round :disabled="!canShareExport">
              <el-icon><Download /></el-icon> 导出
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
                <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button round :disabled="!canShareExport" @click="openShareDialog">
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
          <!-- 视图切换 -->
          <div class="view-toggle">
            <el-tooltip content="时间线视图" placement="top">
              <div class="view-toggle-btn" :class="{ active: viewMode === 'timeline' }" @click="viewMode = 'timeline'">
                <el-icon size="16"><List /></el-icon>
              </div>
            </el-tooltip>
            <el-tooltip content="日历视图" placement="top">
              <div class="view-toggle-btn" :class="{ active: viewMode === 'calendar' }" @click="viewMode = 'calendar'">
                <el-icon size="16"><Calendar /></el-icon>
              </div>
            </el-tooltip>
          </div>
          <el-switch v-model="continuousMode" active-text="连续添加" size="small" />
          <el-button round @click="handleRecommend" :loading="recommending">
            ✨ AI 推荐
          </el-button>
          <el-button type="primary" round @click="openActivityDialog()">
            <el-icon><Plus /></el-icon> 添加活动
          </el-button>
        </div>
      </div>

      <!-- 加载态 -->
      <div v-if="loading" style="padding:20px 0">
        <el-skeleton :rows="4" animated />
      </div>

      <!-- ========== 时间线视图（支持拖拽） ========== -->
      <template v-else-if="activities.length && viewMode === 'timeline'">
        <div class="drag-hint" v-if="activities.length > 1">
          <el-icon size="14"><Rank /></el-icon> 拖拽活动卡片可调整顺序
        </div>
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

          <draggable
            :list="dayActs"
            item-key="id"
            class="day-activities"
            ghost-class="drag-ghost"
            chosen-class="drag-chosen"
            drag-class="drag-active"
            handle=".drag-handle"
            animation="250"
            @end="onDragEnd(dayLabel)"
          >
            <template #item="{ element: act }">
              <div class="activity-card" @click="openActivityDialog(act)">
                <div class="drag-handle" @click.stop title="拖拽排序">
                  <el-icon size="14"><Rank /></el-icon>
                </div>
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
                  <div class="act-resources" v-if="act.guide_id || act.vehicle_id || act.hotel_id || act.restaurant_id">
                    <span v-if="act.guide_id" class="act-resource-tag guide">👤 {{ getResourceName('guide', act.guide_id) }}</span>
                    <span v-if="act.vehicle_id" class="act-resource-tag vehicle">🚌 {{ getResourceName('vehicle', act.vehicle_id) }}</span>
                    <span v-if="act.hotel_id" class="act-resource-tag hotel">🏨 {{ getResourceName('hotel', act.hotel_id) }}</span>
                    <span v-if="act.restaurant_id" class="act-resource-tag restaurant">🍽️ {{ getResourceName('restaurant', act.restaurant_id) }}</span>
                  </div>
                </div>
                <div class="act-actions" @click.stop>
                  <el-button text size="small" circle type="danger" @click="handleDeleteActivity(act.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </template>

      <!-- ========== 日历视图 ========== -->
      <template v-else-if="activities.length && viewMode === 'calendar'">
        <div class="calendar-view">
          <div v-for="day in calendarDays" :key="day.date" class="calendar-day" :class="{ today: day.isToday, empty: !day.acts.length }">
            <div class="calendar-day-header">
              <span class="calendar-day-num">{{ day.dayNum }}</span>
              <span class="calendar-day-label">第{{ day.tripDay }}天</span>
              <span class="calendar-day-date">{{ day.dateLabel }}</span>
              <el-button text size="small" class="calendar-day-add" @click="openActivityForDate(day.date)">
                <el-icon size="12"><Plus /></el-icon>
              </el-button>
            </div>
            <div class="calendar-day-body">
              <div v-for="act in day.acts" :key="act.id" class="calendar-act" :class="act.type" @click="openActivityDialog(act)">
                <span class="calendar-act-icon">{{ actTypeIcon(act.type) }}</span>
                <div class="calendar-act-info">
                  <span class="calendar-act-name">{{ act.name }}</span>
                  <span class="calendar-act-time">{{ formatHour(act.start_time) }}-{{ formatHour(act.end_time) }}</span>
                </div>
              </div>
              <div v-if="!day.acts.length" class="calendar-empty">
                <span>暂无安排</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 空状态 -->
      <div v-else-if="!activities.length" class="empty-activities">
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
        <!-- 资源关联 -->
        <el-form-item label="导游">
          <el-select v-model="actForm.guide_id" placeholder="选择导游（选填）" clearable filterable style="width:100%">
            <el-option v-for="g in guides" :key="g.id" :label="`${g.name}${g.contact_phone ? ' · ' + g.contact_phone : ''}`" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="actForm.type === 'transport'" label="车辆">
          <el-select v-model="actForm.vehicle_id" placeholder="选择车辆（选填）" clearable filterable style="width:100%">
            <el-option v-for="v in vehicles" :key="v.id" :label="`${v.name}${v.plate_number ? ' · ' + v.plate_number : ''}${v.seats ? ' · ' + v.seats + '座' : ''}`" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="actForm.type === 'hotel'" label="酒店">
          <el-select v-model="actForm.hotel_id" placeholder="选择酒店（选填）" clearable filterable style="width:100%">
            <el-option v-for="h in hotels" :key="h.id" :label="`${h.name}${h.star_rating ? ' · ' + h.star_rating + '星' : ''}`" :value="h.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="actForm.type === 'meal'" label="餐厅">
          <el-select v-model="actForm.restaurant_id" placeholder="选择餐厅（选填）" clearable filterable style="width:100%">
            <el-option v-for="r in restaurants" :key="r.id" :label="`${r.name}${r.cuisine ? ' · ' + r.cuisine : ''}`" :value="r.id" />
          </el-select>
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
        <img v-if="qrcodeBlobUrl" :src="qrcodeBlobUrl" alt="二维码" style="width:180px;margin-top:16px;border-radius:12px" />
        <div v-else style="margin-top:16px;color:#909399;font-size:13px">二维码加载中...</div>
      </div>
    </el-dialog>

    <!-- AI 推荐活动对话框 -->
    <el-dialog v-model="showRecommend" title="✨ AI 推荐活动" width="680px" :close-on-click-modal="false">
      <div v-if="recommending" style="text-align:center;padding:40px 0">
        <el-icon class="is-loading" size="32" color="#8b5cf6"><Loading /></el-icon>
        <p style="margin-top:12px;color:#909399;font-size:14px">AI 正在分析行程并生成推荐...</p>
      </div>
      <div v-else-if="recommendList.length">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <span style="font-size:13px;color:#909399">共推荐 {{ recommendList.length }} 项活动，点击添加到行程</span>
          <el-button size="small" type="primary" plain round @click="addAllRecommended" :disabled="recommendList.every(a => a.added)">
            全部添加
          </el-button>
        </div>
        <div class="recommend-list">
          <div v-for="(act, idx) in recommendList" :key="idx" class="recommend-card" :class="{ added: act.added }">
            <div class="rec-left">
              <div class="rec-type-badge" :class="act.type">
                {{ actTypeIcon(act.type) }}
              </div>
              <div class="rec-info">
                <div class="rec-name">{{ act.name }}</div>
                <div class="rec-meta">
                  <span>第{{ act.day }}天</span>
                  <span>{{ act.time }}</span>
                  <span v-if="act.duration">{{ act.duration }}</span>
                  <span v-if="act.location">📍 {{ act.location }}</span>
                </div>
                <div v-if="act.notes" class="rec-notes">{{ act.notes }}</div>
              </div>
            </div>
            <div class="rec-right">
              <span v-if="act.estimated_cost" class="rec-cost">¥{{ act.estimated_cost }}</span>
              <el-button v-if="!act.added" size="small" type="primary" round :loading="addingIdx === idx" @click="addRecommendedActivity(act, idx)">
                添加
              </el-button>
              <el-tag v-else type="success" size="small" round>已添加</el-tag>
            </div>
          </div>
        </div>
      </div>
      <div v-else style="text-align:center;padding:30px 0;color:#909399">
        暂无推荐结果
      </div>
      <template #footer>
        <el-button @click="showRecommend = false">关闭</el-button>
        <el-button type="primary" plain @click="handleRecommend" :loading="recommending">重新推荐</el-button>
      </template>
    </el-dialog>

    <!-- 合作伙伴确认状态 -->
    <div v-if="trip.partner_confirmations?.length" class="partner-status-section">
      <div class="section-toolbar">
        <h3 class="section-title">
          <span class="title-icon">🤝</span> 合作伙伴确认
          <span class="act-count">{{ trip.partner_confirmations.length }}个</span>
        </h3>
      </div>
      <div class="partner-cards">
        <div v-for="(c, i) in trip.partner_confirmations" :key="i" class="partner-card">
          <div class="partner-card-icon">✅</div>
          <div class="partner-card-body">
            <div class="partner-card-top">
              <span class="partner-card-name">{{ c.name }}</span>
              <el-tag size="small" effect="plain" round>{{ c.role }}</el-tag>
            </div>
            <div class="partner-card-meta">
              <span v-if="c.note" class="partner-card-note">{{ c.note }}</span>
              <span class="partner-card-time">{{ c.confirmed_at?.slice(0, 16).replace('T', ' ') }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 评价统计区域 -->
    <div v-if="reviewStats && reviewStats.total > 0" class="review-stats-section">
      <div class="section-toolbar">
        <h3 class="section-title">
          <span class="title-icon">📊</span> 客户评价
          <span class="act-count">{{ reviewStats.total }}条</span>
        </h3>
      </div>

      <div class="review-overview">
        <div class="review-score-card">
          <div class="score-big">{{ reviewStats.avg_rating }}</div>
          <div class="score-stars">
            <span v-for="s in 5" :key="s" class="star-icon" :class="{ active: s <= Math.round(reviewStats.avg_rating) }">★</span>
          </div>
          <div class="score-total">{{ reviewStats.total }} 条评价</div>
        </div>

        <div class="review-dist">
          <div v-for="i in [5,4,3,2,1]" :key="i" class="dist-row">
            <span class="dist-label">{{ i }}星</span>
            <div class="dist-bar">
              <div class="dist-fill" :style="{ width: (reviewStats.rating_dist[String(i)] || 0) / reviewStats.total * 100 + '%' }"></div>
            </div>
            <span class="dist-count">{{ reviewStats.rating_dist[String(i)] || 0 }}</span>
          </div>
        </div>

        <div class="review-tags-cloud" v-if="Object.keys(reviewStats.tag_stats || {}).length">
          <div class="tags-title">热门标签</div>
          <div class="tags-wrap">
            <span v-for="(count, tag) in reviewStats.tag_stats" :key="tag" class="cloud-tag">
              {{ tag }} <span class="tag-num">{{ count }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- 最近评价 -->
      <div v-if="reviewList.length" class="recent-reviews">
        <div v-for="r in reviewList.slice(0, 5)" :key="r.id" class="review-item">
          <div class="review-item-top">
            <span class="reviewer-name">{{ r.reviewer_name }}</span>
            <span class="review-stars-sm">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
            <span class="review-date">{{ r.created_at ? r.created_at.slice(0, 10) : '' }}</span>
          </div>
          <div class="review-item-tags" v-if="r.tags?.length">
            <span v-for="t in r.tags" :key="t" class="review-tag-sm">{{ t }}</span>
          </div>
          <p v-if="r.comment" class="review-comment-sm">{{ r.comment }}</p>
        </div>
      </div>
    </div>
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
import draggable from 'vuedraggable'
import {
  getTrip, updateTrip, getActivities, createActivity, updateActivity,
  deleteActivity, reorderActivities, exportPdf, exportExcel, getShareInfo, getQrcodeUrl
} from '@/api/trips'
import { getTripReviews, getTripReviewStats } from '@/api/reviews'
import { getGuides, getVehicles, getHotels, getRestaurants } from '@/api/resources'
import { recommendActivities } from '@/api/ai'

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

// 视图模式：timeline | calendar
const viewMode = ref('timeline')

const guides = ref([])
const vehicles = ref([])
const hotels = ref([])
const restaurants = ref([])

const actForm = reactive({
  type: 'attraction', name: '', date: null, startHour: null, endHour: null,
  location: '', cost: null, notes: '',
  guide_id: null, vehicle_id: null, hotel_id: null, restaurant_id: null
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

const canShareExport = computed(() => {
  const s = trip.value?.status
  return s === 'confirmed' || s === 'completed'
})
const formatHour = (t) => t ? dayjs(t).format('HH:mm') : ''

const totalDays = computed(() => {
  if (!trip.value) return 0
  return dayjs(trip.value.end_date).diff(dayjs(trip.value.start_date), 'day') + 1
})

const totalCost = computed(() => activities.value.reduce((sum, a) => sum + Number(a.cost || 0), 0))
const budgetPercent = computed(() => trip.value?.budget ? Math.round(totalCost.value / Number(trip.value.budget) * 100) : 0)
const getDayCost = (dayActs) => dayActs.reduce((sum, a) => sum + Number(a.cost || 0), 0)

const getResourceName = (type, id) => {
  if (!id) return ''
  const map = { guide: guides, vehicle: vehicles, hotel: hotels, restaurant: restaurants }
  const list = map[type]?.value || []
  const item = list.find(r => r.id === id)
  return item?.name || ''
}

const groupedActivities = computed(() => {
  const groups = {}
  const sorted = [...activities.value].sort((a, b) => {
    // 先按 sort_order，再按 start_time
    if (a.sort_order !== b.sort_order) return a.sort_order - b.sort_order
    return new Date(a.start_time) - new Date(b.start_time)
  })
  for (const act of sorted) {
    const date = dayjs(act.start_time).format('YYYY-MM-DD')
    const dayNum = trip.value ? dayjs(date).diff(dayjs(trip.value.start_date), 'day') + 1 : 0
    const label = `第${dayNum}天 · ${date}`
    if (!groups[label]) groups[label] = []
    groups[label].push(act)
  }
  return groups
})

// 日历视图数据：生成行程每一天的格子
const calendarDays = computed(() => {
  if (!trip.value) return []
  const days = []
  const start = dayjs(trip.value.start_date)
  const end = dayjs(trip.value.end_date)
  const today = dayjs().format('YYYY-MM-DD')
  let cur = start
  while (cur.isBefore(end) || cur.isSame(end, 'day')) {
    const dateStr = cur.format('YYYY-MM-DD')
    const dayActs = activities.value
      .filter(a => dayjs(a.start_time).format('YYYY-MM-DD') === dateStr)
      .sort((a, b) => {
        if (a.sort_order !== b.sort_order) return a.sort_order - b.sort_order
        return new Date(a.start_time) - new Date(b.start_time)
      })
    days.push({
      date: dateStr,
      dayNum: cur.format('D'),
      tripDay: cur.diff(start, 'day') + 1,
      dateLabel: cur.format('M月D日'),
      isToday: dateStr === today,
      acts: dayActs,
    })
    cur = cur.add(1, 'day')
  }
  return days
})

// 拖拽结束后同步排序到后端
async function onDragEnd(dayLabel) {
  const dayActs = groupedActivities.value[dayLabel]
  if (!dayActs) return
  const items = dayActs.map((act, idx) => ({ id: act.id, sort_order: idx }))
  try {
    await reorderActivities(tripId.value, items)
    // 同步本地 sort_order
    items.forEach(item => {
      const act = activities.value.find(a => a.id === item.id)
      if (act) act.sort_order = item.sort_order
    })
  } catch {
    ElMessage.error('排序保存失败')
    // 回滚：重新加载
    activities.value = await getActivities(tripId.value)
  }
}

// 日历视图中按日期添加活动
function openActivityForDate(dateStr) {
  editingActivity.value = null
  Object.assign(actForm, {
    type: 'attraction', name: '', date: dateStr,
    startHour: new Date('2000-01-01T09:00'), endHour: new Date('2000-01-01T12:00'),
    location: '', cost: null, notes: '',
    guide_id: null, vehicle_id: null, hotel_id: null, restaurant_id: null
  })
  showActivity.value = true
}

const shareUrl = computed(() => shareInfo.value ? `${window.location.origin}/share/${shareInfo.value.share_code}` : '')
const qrcodeBlobUrl = ref(null)

async function loadQrcode() {
  try {
    const url = getQrcodeUrl(tripId.value)
    const token = localStorage.getItem('token')
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) return
    const blob = await res.blob()
    qrcodeBlobUrl.value = URL.createObjectURL(blob)
  } catch {}
}

const reviewStats = ref(null)
const reviewList = ref([])

async function loadReviews() {
  try {
    const [stats, list] = await Promise.all([
      getTripReviewStats(tripId.value),
      getTripReviews(tripId.value),
    ])
    reviewStats.value = stats
    reviewList.value = list
  } catch {}
}

// AI 推荐活动
const showRecommend = ref(false)
const recommending = ref(false)
const recommendList = ref([])
const addingIdx = ref(-1)

async function handleRecommend() {
  showRecommend.value = true
  recommending.value = true
  recommendList.value = []
  try {
    const res = await recommendActivities({ trip_id: tripId.value })
    recommendList.value = (res.activities || []).map(a => ({ ...a, added: false }))
    if (!recommendList.value.length) {
      ElMessage.info(res.message || 'AI 暂无推荐，请稍后重试')
    }
  } catch (e) {
    ElMessage.error('AI 推荐失败，请检查网络或稍后重试')
  } finally { recommending.value = false }
}

async function addRecommendedActivity(act, idx) {
  if (!trip.value || act.added) return
  addingIdx.value = idx
  try {
    const actDate = dayjs(trip.value.start_date).add(act.day - 1, 'day').format('YYYY-MM-DD')
    const sh = act.time || '09:00'
    // 解析 duration 为分钟
    let mins = 60
    const hm = act.duration?.match(/(\d+)\s*[小时hH]/)
    const mm = act.duration?.match(/(\d+)\s*[分钟mM]/)
    if (hm) mins = parseInt(hm[1]) * 60
    if (mm) mins += parseInt(mm[1])
    const endTime = dayjs(`${actDate}T${sh}`).add(mins, 'minute').format('HH:mm')

    await createActivity(tripId.value, {
      type: act.type, name: act.name,
      start_time: `${actDate}T${sh}:00`,
      end_time: `${actDate}T${endTime}:00`,
      location: act.location || null,
      cost: act.estimated_cost || null,
      notes: act.notes || null,
    })
    act.added = true
    ElMessage.success(`已添加「${act.name}」`)
    activities.value = await getActivities(tripId.value)
  } catch (e) {
    ElMessage.error('添加失败')
  } finally { addingIdx.value = -1 }
}

async function addAllRecommended() {
  const toAdd = recommendList.value.filter(a => !a.added)
  if (!toAdd.length) return
  for (let i = 0; i < toAdd.length; i++) {
    const act = toAdd[i]
    const idx = recommendList.value.indexOf(act)
    await addRecommendedActivity(act, idx)
  }
  ElMessage.success('全部添加完成')
}

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

async function loadResources() {
  try {
    const [g, v, h, r] = await Promise.all([getGuides(), getVehicles(), getHotels(), getRestaurants()])
    guides.value = g
    vehicles.value = v
    hotels.value = h
    restaurants.value = r
  } catch {}
}

function openActivityDialog(act = null) {
  editingActivity.value = act
  if (act) {
    Object.assign(actForm, {
      type: act.type, name: act.name,
      date: dayjs(act.start_time).format('YYYY-MM-DD'),
      startHour: new Date(act.start_time), endHour: new Date(act.end_time),
      location: act.location || '', cost: act.cost, notes: act.notes || '',
      guide_id: act.guide_id || null, vehicle_id: act.vehicle_id || null,
      hotel_id: act.hotel_id || null, restaurant_id: act.restaurant_id || null
    })
  } else {
    Object.assign(actForm, {
      type: 'attraction', name: '', date: trip.value?.start_date || null,
      startHour: new Date('2000-01-01T09:00'), endHour: new Date('2000-01-01T12:00'),
      location: '', cost: null, notes: '',
      guide_id: null, vehicle_id: null, hotel_id: null, restaurant_id: null
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
    location: '', cost: null, notes: '',
    guide_id: null, vehicle_id: null, hotel_id: null, restaurant_id: null
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
      location: actForm.location || null, cost: actForm.cost || null, notes: actForm.notes || null,
      guide_id: actForm.guide_id || null, vehicle_id: actForm.vehicle_id || null,
      hotel_id: actForm.hotel_id || null, restaurant_id: actForm.restaurant_id || null
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
          location: '', cost: null, notes: '',
          guide_id: null, vehicle_id: null, hotel_id: null, restaurant_id: null
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

async function openShareDialog() {
  showShare.value = true
  if (!qrcodeBlobUrl.value) {
    await loadQrcode()
  }
}

async function copyShareUrl() {
  await navigator.clipboard.writeText(shareUrl.value)
  ElMessage.success('已复制')
}

onMounted(async () => {
  await loadData()
  loadResources()
  shareInfo.value = await getShareInfo(tripId.value)
  loadReviews()
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
.act-resources {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.act-resource-tag {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 8px;
  font-weight: 500;
}
.act-resource-tag.guide { background: #ecfdf5; color: #059669; }
.act-resource-tag.vehicle { background: #fff7ed; color: #c2410c; }
.act-resource-tag.hotel { background: #ede9fe; color: #7c3aed; }
.act-resource-tag.restaurant { background: #fef2f2; color: #dc2626; }
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

/* ===== 视图切换 ===== */
.view-toggle {
  display: flex;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 2px;
  gap: 2px;
}
.view-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  color: #909399;
  transition: all 0.2s;
}
.view-toggle-btn:hover { color: #606266; background: #eef0f4; }
.view-toggle-btn.active {
  background: #fff;
  color: #7c3aed;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

/* ===== 拖拽相关 ===== */
.drag-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #c0c4cc;
  margin-bottom: 16px;
  padding: 6px 12px;
  background: #fafbfd;
  border-radius: 8px;
  border: 1px dashed #e8e8ed;
}
.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  flex-shrink: 0;
  color: #dcdfe6;
  cursor: grab;
  transition: color 0.2s;
  margin-right: 4px;
}
.drag-handle:hover { color: #8b5cf6; }
.drag-handle:active { cursor: grabbing; }
.drag-ghost {
  opacity: 0.4;
  background: #f5f3ff;
  border: 2px dashed #a78bfa;
  border-radius: 14px;
}
.drag-chosen {
  box-shadow: 0 8px 24px rgba(139,92,246,0.15);
  border-color: #a78bfa;
}
.drag-active {
  opacity: 0.9;
  transform: rotate(1deg);
}

/* ===== 日历视图 ===== */
.calendar-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}
.calendar-day {
  background: #fafbfd;
  border-radius: 14px;
  border: 1px solid #f0f2f5;
  overflow: hidden;
  transition: all 0.2s;
}
.calendar-day:hover { border-color: #e0e0e8; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.calendar-day.today { border-color: #a78bfa; background: #faf8ff; }
.calendar-day.empty { opacity: 0.7; }
.calendar-day-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #fff;
  border-bottom: 1px solid #f0f2f5;
}
.calendar-day.today .calendar-day-header { background: #f5f3ff; }
.calendar-day-num {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a2e;
  line-height: 1;
}
.calendar-day.today .calendar-day-num { color: #7c3aed; }
.calendar-day-label {
  font-size: 12px;
  font-weight: 600;
  color: #7c3aed;
  background: #ede9fe;
  padding: 1px 8px;
  border-radius: 6px;
}
.calendar-day-date {
  font-size: 11px;
  color: #a8abb2;
}
.calendar-day-add {
  margin-left: auto;
  color: #c0c4cc;
  padding: 2px;
}
.calendar-day-add:hover { color: #7c3aed; }
.calendar-day-body {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 60px;
}
.calendar-act {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  border: 1px solid #f0f2f5;
}
.calendar-act:hover { transform: translateX(2px); box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.calendar-act.transport { border-left: 3px solid #f97316; }
.calendar-act.attraction { border-left: 3px solid #10b981; }
.calendar-act.meal { border-left: 3px solid #ef4444; }
.calendar-act.hotel { border-left: 3px solid #8b5cf6; }
.calendar-act.free { border-left: 3px solid #3b82f6; }
.calendar-act-icon { font-size: 16px; flex-shrink: 0; }
.calendar-act-info { flex: 1; min-width: 0; }
.calendar-act-name {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a2e;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.calendar-act-time {
  font-size: 11px;
  color: #a8abb2;
}
.calendar-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  font-size: 12px;
  color: #dcdfe6;
}

/* ===== AI 推荐列表 ===== */
.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 450px;
  overflow-y: auto;
}
.recommend-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: #fafbfd;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.recommend-card:hover { background: #f5f3ff; border-color: rgba(139,92,246,0.12); }
.recommend-card.added { opacity: 0.55; }
.rec-left { display: flex; align-items: flex-start; gap: 12px; flex: 1; min-width: 0; }
.rec-type-badge {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.rec-type-badge.transport { background: #fff7ed; }
.rec-type-badge.attraction { background: #ecfdf5; }
.rec-type-badge.meal { background: #fef2f2; }
.rec-type-badge.hotel { background: #ede9fe; }
.rec-type-badge.free { background: #eff6ff; }
.rec-info { flex: 1; min-width: 0; }
.rec-name { font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 4px; }
.rec-meta {
  display: flex; flex-wrap: wrap; gap: 8px;
  font-size: 12px; color: #909399;
}
.rec-notes { font-size: 12px; color: #a8abb2; margin-top: 3px; }
.rec-right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.rec-cost { font-size: 13px; font-weight: 600; color: #d97706; }

/* ===== 评价统计 ===== */
.review-stats-section {
  background: #fff;
  border-radius: 20px;
  padding: 26px 30px;
  margin-top: 24px;
  border: 1px solid rgba(0,0,0,0.04);
  box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 1px 2px rgba(0,0,0,0.02);
}
.review-overview {
  display: grid;
  grid-template-columns: 140px 1fr 1fr;
  gap: 24px;
  margin-bottom: 20px;
}
.review-score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.score-big {
  font-size: 42px;
  font-weight: 800;
  color: #1a1a2e;
  line-height: 1;
}
.score-stars { display: flex; gap: 2px; }
.star-icon { font-size: 16px; color: #dcdfe6; }
.star-icon.active { color: #f59e0b; }
.score-total { font-size: 12px; color: #909399; margin-top: 4px; }

.review-dist { display: flex; flex-direction: column; gap: 6px; justify-content: center; }
.dist-row { display: flex; align-items: center; gap: 8px; }
.dist-label { font-size: 12px; color: #909399; width: 28px; text-align: right; flex-shrink: 0; }
.dist-bar { flex: 1; height: 8px; background: #f5f7fa; border-radius: 4px; overflow: hidden; }
.dist-fill { height: 100%; background: linear-gradient(90deg, #f59e0b, #fbbf24); border-radius: 4px; transition: width 0.6s ease; }
.dist-count { font-size: 12px; color: #c0c4cc; width: 20px; flex-shrink: 0; }

.review-tags-cloud { display: flex; flex-direction: column; gap: 10px; justify-content: center; }
.tags-title { font-size: 14px; font-weight: 700; color: #303133; }
.tags-wrap { display: flex; flex-wrap: wrap; gap: 8px; }
.cloud-tag {
  padding: 6px 14px; border-radius: 14px; font-size: 13px;
  background: linear-gradient(135deg, #f5f3ff, #ede9fe); color: #6d28d9;
  display: flex; align-items: center; gap: 6px;
  border: 1px solid #ddd6fe; font-weight: 500;
  transition: all 0.2s; cursor: default;
}
.cloud-tag:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(139,92,246,0.15); }
.tag-num {
  font-weight: 800; color: #fff; font-size: 11px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  padding: 1px 7px; border-radius: 10px; min-width: 20px; text-align: center;
}

.recent-reviews { border-top: 1px solid #f0f2f5; padding-top: 16px; }
.review-item {
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fc;
}
.review-item:last-child { border-bottom: none; }
.review-item-top { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.reviewer-name { font-size: 13px; font-weight: 600; color: #303133; }
.review-stars-sm { color: #f59e0b; font-size: 12px; }
.review-date { font-size: 11px; color: #c0c4cc; margin-left: auto; }
.review-item-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 6px; }
.review-tag-sm {
  padding: 2px 10px; border-radius: 10px; font-size: 12px;
  background: linear-gradient(135deg, #f5f3ff, #ede9fe); color: #6d28d9;
  border: 1px solid #e9e5f5; font-weight: 500;
}
.review-comment-sm { font-size: 13px; color: #606266; line-height: 1.5; margin: 0; }

@media (max-width: 768px) {
  .detail-hero { padding: 20px; border-radius: 16px; }
  .hero-top { flex-direction: column; gap: 12px; align-items: flex-start; }
  .hero-actions { width: 100%; display: flex; flex-wrap: wrap; gap: 8px; }
  .hero-actions .el-button { flex: 1; min-width: 0; }
  .hero-title { font-size: 20px; }
  .detail-stats { grid-template-columns: 1fr 1fr; }
  .activities-section { padding: 20px; border-radius: 16px; }
  .section-toolbar { flex-direction: column; gap: 12px; align-items: flex-start; }
  .toolbar-right { width: 100%; justify-content: space-between; flex-wrap: wrap; }
  .day-activities { padding-left: 14px; }
  .activity-card { padding: 14px 16px; gap: 10px; }
  .act-type-badge { width: 36px; height: 36px; font-size: 16px; }
  .act-actions { opacity: 1; }
  .review-overview { grid-template-columns: 1fr; }
  .review-stats-section { padding: 20px; border-radius: 16px; }
  .calendar-view { grid-template-columns: 1fr 1fr; }
  .drag-handle { display: none; }
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
  .calendar-view { grid-template-columns: 1fr; }
}

/* ========== 合作伙伴确认状态 ========== */
.partner-status-section {
  background: #fff; border-radius: 18px; padding: 24px 28px;
  border: 1px solid #eef0f4; margin-top: 20px;
}
.partner-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.partner-card {
  display: flex; gap: 12px; align-items: center;
  padding: 14px 16px; background: #f0fdf4; border-radius: 12px; border: 1px solid #d1fae5;
}
.partner-card-icon { font-size: 20px; flex-shrink: 0; }
.partner-card-body { flex: 1; min-width: 0; }
.partner-card-top { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.partner-card-name { font-size: 14px; font-weight: 600; color: #303133; }
.partner-card-meta { display: flex; flex-wrap: wrap; gap: 8px; }
.partner-card-note { font-size: 12px; color: #606266; }
.partner-card-time { font-size: 11px; color: #c0c4cc; }
</style>
