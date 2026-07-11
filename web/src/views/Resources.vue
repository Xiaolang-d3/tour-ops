<template>
  <div class="resources-page">
    <!-- 资源总览卡片 -->
    <div class="stat-cards">
      <div class="stat-card" :class="{ active: activeTab === 'guides' }" @click="activeTab = 'guides'">
        <div class="stat-icon guides"><span class="stat-emoji">🧑‍🏫</span></div>
        <div class="stat-body">
          <div class="stat-value">{{ guides.length }}</div>
          <div class="stat-label">导游</div>
        </div>
      </div>
      <div class="stat-card" :class="{ active: activeTab === 'vehicles' }" @click="activeTab = 'vehicles'">
        <div class="stat-icon vehicles"><span class="stat-emoji">🚐</span></div>
        <div class="stat-body">
          <div class="stat-value">{{ vehicles.length }}</div>
          <div class="stat-label">车辆</div>
        </div>
      </div>
      <div class="stat-card" :class="{ active: activeTab === 'hotels' }" @click="activeTab = 'hotels'">
        <div class="stat-icon hotels"><span class="stat-emoji">🏨</span></div>
        <div class="stat-body">
          <div class="stat-value">{{ hotels.length }}</div>
          <div class="stat-label">酒店</div>
        </div>
      </div>
      <div class="stat-card" :class="{ active: activeTab === 'restaurants' }" @click="activeTab = 'restaurants'">
        <div class="stat-icon restaurants"><span class="stat-emoji">🍽️</span></div>
        <div class="stat-body">
          <div class="stat-value">{{ restaurants.length }}</div>
          <div class="stat-label">餐厅</div>
        </div>
      </div>
    </div>

    <!-- 当前分类内容 -->
    <div class="section-header">
      <div class="section-title-row">
        <h3 class="section-title">{{ sectionTitle }}</h3>
        <span class="section-count">共 {{ currentList.length }} 项</span>
      </div>
      <div class="section-actions">
        <el-input v-model="searchText" placeholder="搜索..." prefix-icon="Search" clearable class="search-input" />
        <el-button type="primary" round size="small" @click="openDialog(activeTab.slice(0, -1))">
          <el-icon><Plus /></el-icon> {{ addBtnText }}
        </el-button>
      </div>
    </div>

    <!-- 导游列表 -->
    <div v-if="activeTab === 'guides'" class="table-wrap">
      <el-table v-loading="loading" :data="filteredGuides" stripe>
        <el-table-column label="导游" min-width="180">
          <template #default="{ row }">
            <div class="res-cell">
              <div class="res-avatar guides">🧑‍🏫</div>
              <div>
                <div class="res-name">{{ row.name }}</div>
                <div class="res-sub" v-if="row.contact_phone">📞 {{ row.contact_phone }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id_card" label="证件号" width="180">
          <template #default="{ row }">
            <span class="text-muted">{{ row.id_card || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="语言" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="lang in (row.languages || [])" :key="lang" size="small" effect="plain" round class="lang-tag">{{ lang }}</el-tag>
            <span v-if="!(row.languages || []).length" class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="" width="60" align="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除？" @confirm="handleDelete('guide', row.id)">
              <template #reference><el-button text size="small" type="danger"><el-icon><Delete /></el-icon></el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 车辆列表 -->
    <div v-if="activeTab === 'vehicles'" class="table-wrap">
      <el-table v-loading="loading" :data="filteredVehicles" stripe>
        <el-table-column label="车辆" min-width="180">
          <template #default="{ row }">
            <div class="res-cell">
              <div class="res-avatar vehicles">🚐</div>
              <div>
                <div class="res-name">{{ row.name }}</div>
                <div class="res-sub" v-if="row.plate_number">🔖 {{ row.plate_number }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="vehicle_type" label="车型" width="120">
          <template #default="{ row }"><span class="text-muted">{{ row.vehicle_type || '-' }}</span></template>
        </el-table-column>
        <el-table-column label="座位" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.seats" class="seat-badge">{{ row.seats }}座</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="司机" width="140">
          <template #default="{ row }"><span class="text-muted">{{ row.driver_name || '-' }}</span></template>
        </el-table-column>
        <el-table-column label="" width="60" align="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除？" @confirm="handleDelete('vehicle', row.id)">
              <template #reference><el-button text size="small" type="danger"><el-icon><Delete /></el-icon></el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 酒店列表 -->
    <div v-if="activeTab === 'hotels'" class="table-wrap">
      <el-table v-loading="loading" :data="filteredHotels" stripe>
        <el-table-column label="酒店" min-width="200">
          <template #default="{ row }">
            <div class="res-cell">
              <div class="res-avatar hotels">🏨</div>
              <div>
                <div class="res-name">{{ row.name }}</div>
                <div class="res-sub" v-if="row.address">📍 {{ row.address }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="星级" width="140" align="center">
          <template #default="{ row }">
            <span v-if="row.star_rating" class="star-display">{{ '★'.repeat(row.star_rating) }}<span class="star-empty">{{ '★'.repeat(5 - row.star_rating) }}</span></span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="电话" width="140">
          <template #default="{ row }"><span class="text-muted">{{ row.contact_phone || '-' }}</span></template>
        </el-table-column>
        <el-table-column label="" width="60" align="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除？" @confirm="handleDelete('hotel', row.id)">
              <template #reference><el-button text size="small" type="danger"><el-icon><Delete /></el-icon></el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 餐厅列表 -->
    <div v-if="activeTab === 'restaurants'" class="table-wrap">
      <el-table v-loading="loading" :data="filteredRestaurants" stripe>
        <el-table-column label="餐厅" min-width="200">
          <template #default="{ row }">
            <div class="res-cell">
              <div class="res-avatar restaurants">🍽️</div>
              <div>
                <div class="res-name">{{ row.name }}</div>
                <div class="res-sub" v-if="row.address">📍 {{ row.address }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="菜系" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.cuisine" size="small" effect="plain" round>{{ row.cuisine }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="餐标" width="140" align="center">
          <template #default="{ row }">
            <span v-if="row.price_min && row.price_max" class="price-range">¥{{ row.price_min }}-{{ row.price_max }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="" width="60" align="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除？" @confirm="handleDelete('restaurant', row.id)">
              <template #reference><el-button text size="small" type="danger"><el-icon><Delete /></el-icon></el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && currentFilteredList.length === 0" class="empty-state">
      <div class="empty-icon">{{ emptyEmoji }}</div>
      <p class="empty-title">{{ searchText ? '未找到匹配的资源' : '暂无数据' }}</p>
      <p class="empty-desc">{{ searchText ? '试试其他关键词' : `点击上方按钮添加${sectionTitle}` }}</p>
    </div>

    <!-- 添加资源对话框 -->
    <el-dialog v-model="showDialog" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.contact_phone" /></el-form-item>
        <template v-if="dialogType === 'guide'">
          <el-form-item label="证件号"><el-input v-model="form.id_card" /></el-form-item>
        </template>
        <template v-if="dialogType === 'vehicle'">
          <el-form-item label="车牌号"><el-input v-model="form.plate_number" /></el-form-item>
          <el-form-item label="车型"><el-input v-model="form.vehicle_type" /></el-form-item>
          <el-form-item label="座位数"><el-input-number v-model="form.seats" :min="1" /></el-form-item>
          <el-form-item label="司机"><el-input v-model="form.driver_name" /></el-form-item>
        </template>
        <template v-if="dialogType === 'hotel'">
          <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
          <el-form-item label="星级"><el-rate v-model="form.star_rating" /></el-form-item>
        </template>
        <template v-if="dialogType === 'restaurant'">
          <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
          <el-form-item label="菜系"><el-input v-model="form.cuisine" /></el-form-item>
          <el-form-item label="最低餐标"><el-input-number v-model="form.price_min" :min="0" /></el-form-item>
          <el-form-item label="最高餐标"><el-input-number v-model="form.price_max" :min="0" /></el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getGuides, createGuide, deleteGuide,
  getVehicles, createVehicle, deleteVehicle,
  getHotels, createHotel, deleteHotel,
  getRestaurants, createRestaurant, deleteRestaurant
} from '@/api/resources'

const activeTab = ref('guides')
const loading = ref(true)
const searchText = ref('')
const guides = ref([])
const vehicles = ref([])
const hotels = ref([])
const restaurants = ref([])
const showDialog = ref(false)
const dialogType = ref('')
const saving = ref(false)
const formRef = ref(null)
const form = reactive({})

const formRules = { name: [{ required: true, message: '请填写名称', trigger: 'blur' }] }

const sectionTitle = computed(() => ({ guides: '导游', vehicles: '车辆', hotels: '酒店', restaurants: '餐厅' }[activeTab.value]))
const addBtnText = computed(() => ({ guides: '添加导游', vehicles: '添加车辆', hotels: '添加酒店', restaurants: '添加餐厅' }[activeTab.value]))
const emptyEmoji = computed(() => ({ guides: '🧑‍🏫', vehicles: '🚐', hotels: '🏨', restaurants: '🍽️' }[activeTab.value]))
const dialogTitle = computed(() => ({ guide: '添加导游', vehicle: '添加车辆', hotel: '添加酒店', restaurant: '添加餐厅' }[dialogType.value]))

const currentList = computed(() => ({ guides: guides.value, vehicles: vehicles.value, hotels: hotels.value, restaurants: restaurants.value }[activeTab.value] || []))

const createFns = { guide: createGuide, vehicle: createVehicle, hotel: createHotel, restaurant: createRestaurant }
const deleteFns = { guide: deleteGuide, vehicle: deleteVehicle, hotel: deleteHotel, restaurant: deleteRestaurant }

function filterByName(list) {
  if (!searchText.value) return list
  const kw = searchText.value.toLowerCase()
  return list.filter(item => (item.name || '').toLowerCase().includes(kw))
}
const filteredGuides = computed(() => filterByName(guides.value))
const filteredVehicles = computed(() => filterByName(vehicles.value))
const filteredHotels = computed(() => filterByName(hotels.value))
const filteredRestaurants = computed(() => filterByName(restaurants.value))
const currentFilteredList = computed(() => ({ guides: filteredGuides.value, vehicles: filteredVehicles.value, hotels: filteredHotels.value, restaurants: filteredRestaurants.value }[activeTab.value] || []))

watch(activeTab, () => { searchText.value = '' })

async function loadData() {
  loading.value = true
  try {
    guides.value = await getGuides()
    vehicles.value = await getVehicles()
    hotels.value = await getHotels()
    restaurants.value = await getRestaurants()
  } finally { loading.value = false }
}

function openDialog(type) {
  dialogType.value = type
  Object.keys(form).forEach(k => delete form[k])
  showDialog.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await createFns[dialogType.value]({ ...form })
    showDialog.value = false
    ElMessage.success('添加成功')
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(type, id) {
  await deleteFns[type](id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.resources-page { max-width: 1100px; }

/* 统计卡片 */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.stat-card.active {
  border-color: #f59e0b;
  background: #fffbeb;
  box-shadow: 0 4px 16px rgba(245,158,11,0.15);
}
.stat-icon {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-emoji { font-size: 24px; }
.stat-icon.guides { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
.stat-icon.vehicles { background: linear-gradient(135deg, #fef3c7, #fde68a); }
.stat-icon.hotels { background: linear-gradient(135deg, #ede9fe, #ddd6fe); }
.stat-icon.restaurants { background: linear-gradient(135deg, #fce7f3, #fbcfe8); }
.stat-value { font-size: 26px; font-weight: 800; color: #1a1a2e; line-height: 1.2; }
.stat-label { font-size: 13px; color: #909399; font-weight: 500; margin-top: 2px; }

/* 区域标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.section-title-row { display: flex; align-items: baseline; gap: 10px; }
.section-title { font-size: 18px; font-weight: 700; color: #1a1a2e; margin: 0; }
.section-count { font-size: 13px; color: #a8abb2; font-weight: 500; }
.section-actions { display: flex; align-items: center; gap: 10px; }
.search-input { width: 220px; }

/* 表格 */
.table-wrap {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.04);
}
.table-wrap :deep(.el-table__header th) {
  background: #fefce8 !important;
  color: #92400e;
  font-weight: 600;
  font-size: 13px;
}

/* 资源单元格 */
.res-cell { display: flex; align-items: center; gap: 12px; }
.res-avatar {
  width: 40px; height: 40px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.res-avatar.guides { background: #dbeafe; }
.res-avatar.vehicles { background: #fef3c7; }
.res-avatar.hotels { background: #ede9fe; }
.res-avatar.restaurants { background: #fce7f3; }
.res-name { font-weight: 600; font-size: 14px; color: #1a1a2e; }
.res-sub { font-size: 12px; color: #909399; margin-top: 2px; }
.text-muted { color: #c0c4cc; font-size: 13px; }

.lang-tag { margin-right: 4px; }

.seat-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 8px;
  background: #fef3c7;
  color: #92400e;
  font-size: 12px;
  font-weight: 600;
}

.star-display { color: #f59e0b; letter-spacing: 1px; font-size: 14px; }
.star-empty { color: #e5e7eb; }

.price-range { color: #d97706; font-weight: 600; font-size: 13px; }

/* 空状态 */
.empty-state { text-align: center; padding: 60px 0; }
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-title { font-size: 16px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.empty-desc { font-size: 13px; color: #909399; }

@media (max-width: 1024px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .stat-cards { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 14px; }
  .stat-icon { width: 40px; height: 40px; }
  .stat-value { font-size: 20px; }
  .section-header { flex-direction: column; align-items: flex-start; }
  .section-actions { width: 100%; }
  .search-input { flex: 1; width: auto !important; }
  .table-wrap { overflow-x: auto; }
  .table-wrap :deep(.el-table) { min-width: 520px; }
}
@media (max-width: 480px) {
  .stat-cards { grid-template-columns: 1fr 1fr; gap: 8px; }
  .stat-card { padding: 12px; gap: 10px; }
  .stat-icon { width: 36px; height: 36px; }
  .stat-emoji { font-size: 18px; }
  .stat-value { font-size: 18px; }
}
</style>
