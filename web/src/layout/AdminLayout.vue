<template>
  <el-container style="height: 100%">
    <!-- 移动端遮罩 -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="mobileMenuOpen = false"></div>
    <el-aside :width="collapsed ? '72px' : '230px'" class="sidebar" :class="{ collapsed, 'mobile-open': mobileMenuOpen }">
      <div class="logo" @click="router.push('/admin/dashboard')">
        <div class="logo-icon">
          <svg viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg" width="38" height="38">
            <defs><linearGradient id="aGrad" x1="0" y1="0" x2="38" y2="38"><stop stop-color="#d97706"/><stop offset="1" stop-color="#b45309"/></linearGradient></defs>
            <rect width="38" height="38" rx="10" fill="url(#aGrad)"/>
            <path d="M9 10.5 L30 19 L9 27.5 L13 19 Z" fill="#fff" opacity="0.95"/>
            <path d="M13 19 L30 19 L18 25 Z" fill="#fef3c7" opacity="0.6"/>
          </svg>
        </div>
        <transition name="fade">
          <span v-show="!collapsed" class="logo-text">TourOps 管理</span>
        </transition>
      </div>

      <div class="nav-section">
        <transition name="fade">
          <span v-show="!collapsed" class="nav-label">管理</span>
        </transition>
      </div>

      <el-menu
        :default-active="route.path"
        router
        :collapse="collapsed"
        background-color="transparent"
        text-color="#64748b"
        active-text-color="#e6a23c"
        :collapse-transition="false"
        class="sidebar-menu"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>控制台</template>
        </el-menu-item>
        <el-menu-item index="/admin/trips">
          <el-icon><Suitcase /></el-icon>
          <template #title>行程管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/resources">
          <el-icon><OfficeBuilding /></el-icon>
          <template #title>资源管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/templates">
          <el-icon><Files /></el-icon>
          <template #title>模板库</template>
        </el-menu-item>
        <el-menu-item index="/admin/reviews">
          <el-icon><ChatDotSquare /></el-icon>
          <template #title>评价分析</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="collapse-btn" @click="collapsed = !collapsed">
          <el-icon :size="18"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
        </div>
      </div>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <button class="mobile-menu-btn" @click="mobileMenuOpen = !mobileMenuOpen">
            <el-icon size="20"><Fold /></el-icon>
          </button>
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-avatar-wrap">
              <el-avatar :size="34" class="user-avatar" :style="getAvatarStyle(userStore.user?.avatar)">
                <span v-if="getAvatarEmoji(userStore.user?.avatar)">{{ getAvatarEmoji(userStore.user?.avatar) }}</span>
                <span v-else>{{ (userStore.user?.name || '管').charAt(0) }}</span>
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ userStore.user?.name || '未设置昵称' }}</span>
                <span class="user-role">
                  <el-icon size="10"><Star /></el-icon> 管理员
                </span>
              </div>
              <el-icon size="12" color="#c0c4cc"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><UserFilled /></el-icon> 个人资料
                </el-dropdown-item>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- 个人资料弹窗 -->
    <el-dialog v-model="profileVisible" title="个人资料" width="480px" :close-on-click-modal="false">
      <el-form :model="profileForm" label-width="70px">
        <el-form-item label="头像">
          <div class="avatar-picker">
            <div
              v-for="av in avatarOptions"
              :key="av.id"
              class="avatar-option"
              :class="{ active: profileForm.avatar === av.id }"
              :style="{ background: av.bg }"
              @click="profileForm.avatar = av.id"
            >
              <span>{{ av.emoji }}</span>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="profileForm.name" placeholder="请输入昵称" maxlength="20" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileVisible = false">取消</el-button>
        <el-button type="primary" :loading="profileSaving" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { updateProfile } from '@/api/auth'
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)
const mobileMenuOpen = ref(false)
const profileVisible = ref(false)

watch(() => route.path, () => { mobileMenuOpen.value = false })
const profileSaving = ref(false)
const profileForm = reactive({ name: '', avatar: '' })

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

function getAvatarStyle(avatarId) {
  const av = avatarOptions.find(a => a.id === avatarId)
  return av ? { background: av.bg } : {}
}

function getAvatarEmoji(avatarId) {
  const av = avatarOptions.find(a => a.id === avatarId)
  return av ? av.emoji : null
}

const pageTitle = computed(() => {
  const map = {
    '/admin/dashboard': '控制台',
    '/admin/trips': '行程管理',
    '/admin/users': '用户管理',
    '/admin/resources': '资源管理',
    '/admin/templates': '模板库',
    '/admin/reviews': '评价分析'
  }
  return map[route.path] || '管理后台'
})

onMounted(() => { userStore.fetchUser() })

function handleCommand(cmd) {
  if (cmd === 'profile') {
    profileForm.name = userStore.user?.name || ''
    profileForm.avatar = userStore.user?.avatar || ''
    profileVisible.value = true
  } else if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

async function saveProfile() {
  profileSaving.value = true
  try {
    await updateProfile({ name: profileForm.name, avatar: profileForm.avatar })
    await userStore.fetchUser()
    profileVisible.value = false
    ElMessage.success('资料已更新')
  } catch {
    ElMessage.error('更新失败')
  } finally {
    profileSaving.value = false
  }
}
</script>

<style scoped>
.sidebar {
  background: #fff;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e8ecf1;
  position: relative;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 17px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  transition: padding 0.3s ease;
}
.logo-icon {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.25);
  overflow: hidden;
}
.logo-text {
  color: #1e293b;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -0.5px;
}
.collapsed .logo {
  justify-content: center;
  padding: 22px 0;
  gap: 0;
}
.collapsed .logo-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
}

.nav-section {
  padding: 0 20px;
  margin-bottom: 4px;
  height: 20px;
  overflow: hidden;
}
.collapsed .nav-section {
  height: 0;
  margin: 0;
  padding: 0;
}
.nav-label {
  font-size: 11px;
  font-weight: 600;
  color: #c0c4cc;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sidebar-menu :deep(.el-menu-item) {
  margin: 2px 10px;
  border-radius: 12px;
  height: 44px;
  line-height: 44px;
  transition: all 0.25s ease;
  font-size: 14px;
}
.sidebar-menu :deep(.el-menu-item:hover) {
  background: #fffbeb !important;
  color: #d97706 !important;
}
.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #fef3c7, #fde68a) !important;
  color: #b45309 !important;
  font-weight: 600;
}
.sidebar-menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
}
.collapsed .sidebar-menu :deep(.el-menu) {
  width: auto !important;
}
.collapsed .sidebar-menu :deep(.el-menu-item) {
  width: 44px !important;
  min-width: 44px !important;
  max-width: 44px !important;
  height: 44px;
  margin: 2px auto;
  padding: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  justify-content: center;
  display: flex !important;
  align-items: center;
}
.collapsed .sidebar-menu :deep(.el-menu-item .el-icon) {
  margin: 0 !important;
  margin-right: 0 !important;
  font-size: 18px;
}
.collapsed .sidebar-menu :deep(.el-tooltip__trigger) {
  display: flex !important;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 0 !important;
}

.sidebar-footer {
  margin-top: auto;
  border-top: 1px solid #f0f2f5;
}
.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  color: #c0c4cc;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
}
.collapse-btn:hover { color: #d97706; background: #fffbeb; }

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8ecf1;
  padding: 0 28px;
  height: 64px;
}
.page-title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: -0.3px;
}
.header-right { display: flex; align-items: center; gap: 16px; }

.user-avatar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 14px 6px 6px;
  border-radius: 14px;
  transition: all 0.25s ease;
  border: 1px solid transparent;
}
.user-avatar-wrap:hover {
  background: #fffbeb;
  border-color: #fef3c7;
}
.user-avatar {
  background: linear-gradient(135deg, #e6a23c, #f59e0b);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}
.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}
.user-name { font-size: 13px; color: #1e293b; font-weight: 600; }
.user-role {
  font-size: 11px;
  color: #d97706;
  display: flex;
  align-items: center;
  gap: 2px;
  font-weight: 500;
}

.app-main { background: #f5f7fa; padding: 24px; }

.page-enter-active, .page-leave-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.page-enter-from { opacity: 0; transform: translateY(8px); }
.page-leave-to { opacity: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.avatar-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.avatar-option {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  border: 2px solid transparent;
  transition: all 0.2s ease;
}
.avatar-option:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.avatar-option.active {
  border-color: #e6a23c;
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.2);
  transform: scale(1.1);
}

.mobile-menu-btn {
  display: none;
  border: none;
  background: none;
  color: #64748b;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  transition: all 0.2s;
}
.mobile-menu-btn:hover { background: #fffbeb; color: #d97706; }
.mobile-overlay { display: none; }

@media (max-width: 768px) {
  .mobile-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.3);
    z-index: 1999;
  }
  .mobile-menu-btn { display: flex; align-items: center; }
  .sidebar {
    position: fixed !important;
    top: 0; left: 0; bottom: 0;
    z-index: 2000;
    width: 260px !important;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: none;
  }
  .sidebar.mobile-open {
    transform: translateX(0);
    box-shadow: 8px 0 30px rgba(0,0,0,0.12);
  }
  .sidebar.collapsed { width: 260px !important; }
  .collapsed .logo { justify-content: flex-start; padding: 22px 17px; gap: 12px; }
  .collapsed .nav-section { height: 20px; margin-bottom: 4px; padding: 0 20px; }
  .collapsed .sidebar-menu :deep(.el-menu-item) {
    width: auto !important; min-width: auto !important; max-width: none !important;
    padding: 0 20px !important; justify-content: flex-start;
  }
  .collapsed .sidebar-menu :deep(.el-menu-item .el-icon) { margin-right: 8px !important; }
  .sidebar-footer { display: none; }
  .app-header { padding: 0 16px; height: 56px; }
  .header-left { gap: 8px; display: flex; align-items: center; }
  .page-title { font-size: 15px; }
  .user-info { display: none; }
  .user-avatar-wrap { padding: 4px 8px 4px 4px; }
  .app-main { padding: 16px; }
}

@media (max-width: 480px) {
  .app-header { padding: 0 12px; }
  .app-main { padding: 12px; }
}
</style>
