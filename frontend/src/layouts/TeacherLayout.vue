<template>
  <el-container style="min-height:100vh">
    <el-aside width="200px" style="background:#304156">
      <div style="padding:20px;color:#fff;font-size:16px;font-weight:bold;border-bottom:1px solid #435166">
        数智学情平台
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/teacher/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>首页总览</span>
        </el-menu-item>
        <el-menu-item index="/teacher/classes">
          <el-icon><School /></el-icon>
          <span>班级管理</span>
        </el-menu-item>
        <el-menu-item index="/teacher/questions">
          <el-icon><Document /></el-icon>
          <span>题库管理</span>
        </el-menu-item>
        <el-menu-item index="/teacher/assignments">
          <el-icon><Finished /></el-icon>
          <span>作业管理</span>
        </el-menu-item>
        <el-menu-item index="/teacher/classroom">
          <el-icon><Monitor /></el-icon>
          <span>课堂答题</span>
        </el-menu-item>
        <el-menu-item index="/teacher/analysis">
          <el-icon><TrendCharts /></el-icon>
          <span>学情分析</span>
        </el-menu-item>
        <el-menu-item index="/teacher/challenge">
          <el-icon><Trophy /></el-icon>
          <span>闯关任务</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background:#fff;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #eee">
        <span style="font-size:15px;color:#606266">欢迎，{{ userStore.user?.name }}</span>
        <el-button type="danger" link @click="handleLogout">退出登录</el-button>
      </el-header>
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
import { DataAnalysis, School, Document, Finished, Monitor, TrendCharts, Trophy } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const activeMenu = computed(() => route.path)

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>
