<template>
  <div class="share-page">
    <el-card v-if="trip" class="share-card">
      <template #header>
        <div class="share-header">
          <h2>{{ trip.name }}</h2>
          <p>{{ trip.start_date }} ~ {{ trip.end_date }} · {{ trip.guest_count }}人</p>
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          v-for="act in trip.activities"
          :key="act.id"
          :timestamp="formatTime(act.start_time)"
          placement="top"
        >
          <el-card shadow="never" class="share-act-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <el-tag size="small" :type="actTypeTag(act.type)" round style="margin-right:8px">{{ actTypeLabel(act.type) }}</el-tag>
                <span style="font-weight:600;color:#1a1a2e">{{ act.name }}</span>
              </div>
              <span style="color:#909399;font-size:13px">{{ formatTime(act.start_time) }} ~ {{ formatTime(act.end_time) }}</span>
            </div>
            <p v-if="act.location" style="color:#606266;font-size:13px;margin-top:8px">📍 {{ act.location }}</p>
            <p v-if="act.notes" style="color:#909399;font-size:13px;margin-top:4px">{{ act.notes }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-empty v-if="!trip.activities.length" description="暂无活动安排" />
    </el-card>

    <div v-if="error" style="text-align:center;margin-top:100px">
      <el-result icon="warning" title="行程不存在" sub-title="链接可能已失效" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'
import { getSharedTrip } from '@/api/public'

const route = useRoute()
const trip = ref(null)
const error = ref(false)

const actTypeLabel = (t) => ({ transport: '交通', attraction: '景点', meal: '餐饮', hotel: '住宿', free: '自由' }[t] || t)
const actTypeTag = (t) => ({ transport: 'warning', attraction: 'success', meal: 'danger', hotel: '', free: 'info' }[t] || 'info')
const formatTime = (t) => t ? dayjs(t).format('MM-DD HH:mm') : ''

onMounted(async () => {
  try {
    trip.value = await getSharedTrip(route.params.code)
  } catch {
    error.value = true
  }
})
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f2f5 0%, #e8eaf0 100%);
  padding: 24px;
}
.share-card {
  max-width: 800px;
  margin: 40px auto;
}
.share-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}
.share-header p {
  color: #909399;
  font-size: 14px;
}
.share-act-card {
  border: 1px solid #f0f2f5 !important;
  box-shadow: none !important;
}

@media (max-width: 768px) {
  .share-page { padding: 16px; }
  .share-card { margin: 16px auto; }
  .share-header h2 { font-size: 18px; }
}

@media (max-width: 480px) {
  .share-page { padding: 12px; }
  .share-card { margin: 8px auto; }
  .share-header h2 { font-size: 16px; }
}
</style>
