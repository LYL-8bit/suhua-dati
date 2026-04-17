<template>
  <div style="min-height:100vh;background:#f5f7fa;padding:20px">
    <!-- 未登录：先登录 -->
    <div v-if="!user" style="max-width:400px;margin:40px auto">
      <el-card>
        <h3 style="text-align:center;margin-bottom:20px">课堂答题 - 请先登录</h3>
        <el-form @submit.prevent="doLogin">
          <el-form-item>
            <el-input v-model="loginForm.username" placeholder="学号" size="large" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" />
          </el-form-item>
          <el-button type="primary" size="large" style="width:100%" native-type="submit" :loading="logging">进入课堂</el-button>
        </el-form>
      </el-card>
    </div>

    <!-- 已登录：答题 -->
    <div v-else-if="!result" style="max-width:700px;margin:0 auto">
      <el-card style="margin-bottom:16px">
        <h3>{{ sessionInfo?.title }}</h3>
        <el-tag>{{ currentIndex + 1 }} / {{ questions.length }}</el-tag>
      </el-card>

      <el-card v-if="questions.length">
        <div style="font-size:16px;margin-bottom:20px;line-height:1.6">
          {{ currentIndex + 1 }}. {{ currentQ.content }}
        </div>
        <el-radio-group v-model="answers[currentQ.id]" style="display:flex;flex-direction:column;gap:12px">
          <el-radio v-for="opt in currentQ.options" :key="opt" :value="opt[0]" style="height:auto;white-space:normal">
            {{ opt }}
          </el-radio>
        </el-radio-group>
        <div style="display:flex;justify-content:space-between;margin-top:24px">
          <el-button @click="currentIndex--" :disabled="currentIndex === 0">上一题</el-button>
          <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="currentIndex++" :disabled="!answers[currentQ.id]">下一题</el-button>
          <el-button v-else type="success" @click="submit" :loading="submitting">提交</el-button>
        </div>
      </el-card>
    </div>

    <!-- 结果 -->
    <div v-else style="max-width:500px;margin:40px auto">
      <el-result
        :icon="result.accuracy >= 70 ? 'success' : 'warning'"
        :title="'得分：' + result.score + '/' + result.total"
        :sub-title="'正确率 ' + result.accuracy + '%'"
      />
    </div>

    <el-alert v-if="error" :title="error" type="error" style="margin-top:20px" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api'

const route = useRoute()
const token = route.params.token
const sessionInfo = ref(null)
const questions = ref([])
const answers = ref({})
const currentIndex = ref(0)
const result = ref(null)
const submitting = ref(false)
const error = ref('')
const logging = ref(false)
const loginForm = ref({ username: '', password: '' })
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

const currentQ = computed(() => questions.value[currentIndex.value] || {})

async function loadSession() {
  try {
    const data = await api.get(`/api/classroom/join/${token}`)
    sessionInfo.value = data
    questions.value = data.questions
  } catch (e) {
    error.value = typeof e === 'string' ? e : '无效的课堂码或课堂已结束'
  }
}

async function doLogin() {
  logging.value = true
  try {
    const res = await api.post('/api/auth/login', loginForm.value)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    user.value = res.user
  } catch (e) {
    ElMessage.error('登录失败')
  } finally {
    logging.value = false
  }
}

async function submit() {
  submitting.value = true
  try {
    result.value = await api.post('/api/submissions', {
      answers: answers.value,
      classroom_session_id: sessionInfo.value.session_id,
    })
  } catch (e) {
    ElMessage.error(typeof e === 'string' ? e : '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadSession)
</script>
