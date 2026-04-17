<template>
  <el-container style="min-height:100vh">
    <el-header style="background:#409EFF;display:flex;align-items:center;justify-content:space-between;padding:0 24px">
      <span style="color:#fff;font-size:18px;font-weight:bold">数智学情平台</span>
      <div style="display:flex;align-items:center;gap:16px">
        <span style="color:#fff">{{ userStore.user?.name }}</span>
        <el-button type="info" size="small" @click="handleLogout">退出</el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="180px" style="background:#fff;border-right:1px solid #eee">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/student/home">
            <el-icon><House /></el-icon>
            <span>我的作业</span>
          </el-menu-item>
          <el-menu-item index="/student/wrong-book">
            <el-icon><EditPen /></el-icon>
            <span>错题本</span>
          </el-menu-item>
          <el-menu-item index="/student/analysis">
            <el-icon><TrendCharts /></el-icon>
            <span>我的学情</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main style="padding:20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { House, EditPen, TrendCharts } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const activeMenu = computed(() => route.path)

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>
