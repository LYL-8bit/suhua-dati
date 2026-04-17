<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 style="text-align:center;margin-bottom:24px;color:#303133">数智学情平台</h2>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width:100%" :loading="loading" native-type="submit">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <p v-if="error" style="color:red;text-align:center;margin-top:8px">{{ error }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const user = await userStore.login(form.value.username, form.value.password)
    router.push(user.role === 'teacher' ? '/teacher' : '/student')
  } catch (e) {
    error.value = typeof e === 'string' ? e : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 380px;
  padding: 20px;
}
</style>
