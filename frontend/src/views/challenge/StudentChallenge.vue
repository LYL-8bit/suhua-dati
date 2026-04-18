<template>
  <div style="min-height:100vh;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:16px">

    <!-- 未登录 -->
    <div v-if="!user" style="max-width:400px;margin:60px auto">
      <el-card style="background:rgba(255,255,255,0.95)">
        <h3 style="text-align:center;margin-bottom:4px">圆趣无限 · 闯关任务</h3>
        <p style="text-align:center;color:#909399;font-size:13px;margin-bottom:20px">探月初级工程师训练营</p>
        <el-form @submit.prevent="doLogin">
          <el-form-item>
            <el-input v-model="loginForm.username" placeholder="学号" size="large" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" show-password />
          </el-form-item>
          <el-button type="primary" size="large" style="width:100%" native-type="submit" :loading="logging">进入任务</el-button>
        </el-form>
        <p v-if="loginError" style="color:red;text-align:center;margin-top:8px;font-size:13px">{{ loginError }}</p>
      </el-card>
    </div>

    <!-- 已登录：闯关主界面 -->
    <div v-else style="max-width:600px;margin:0 auto">
      <!-- 顶部信息 -->
      <div style="text-align:center;padding:20px 0;color:#fff">
        <div style="font-size:22px;font-weight:bold;margin-bottom:4px">圆趣无限 · 探月闯关</div>
        <div style="font-size:14px;opacity:0.8">欢迎，{{ user.name }}</div>
      </div>

      <!-- 三关入口 -->
      <div style="display:flex;flex-direction:column;gap:12px">
        <!-- 第一关 -->
        <el-card
          style="cursor:pointer;border:2px solid transparent"
          :style="{borderColor: currentRound === 1 ? '#409EFF' : 'transparent'}"
          @click="enterRound(1)"
        >
          <div style="display:flex;align-items:center;gap:16px">
            <div style="width:48px;height:48px;border-radius:50%;background:#409EFF;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">🚀</div>
            <div style="flex:1">
              <div style="font-weight:bold;font-size:15px">第一关 · 基础巩固</div>
              <div style="color:#909399;font-size:13px;margin-top:2px">轨道参数计算 · 全员必答</div>
            </div>
            <el-tag v-if="r1Done" type="success">已完成 {{ r1Score }}/3</el-tag>
            <el-tag v-else type="primary">进行中</el-tag>
          </div>
        </el-card>

        <!-- 第二关 -->
        <el-card
          style="cursor:pointer;border:2px solid transparent"
          :style="{borderColor: currentRound === 2 ? '#67C23A' : 'transparent'}"
          @click="enterRound(2)"
        >
          <div style="display:flex;align-items:center;gap:16px">
            <div style="width:48px;height:48px;border-radius:50%;background:#67C23A;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">✏️</div>
            <div style="flex:1">
              <div style="font-weight:bold;font-size:15px">第二关 · 实操提升</div>
              <div style="color:#909399;font-size:13px;margin-top:2px">轨道与徽章设计 · 拍照提交</div>
            </div>
            <el-tag v-if="r2Done" type="success">已提交</el-tag>
            <el-tag v-else type="warning">待完成</el-tag>
          </div>
        </el-card>

        <!-- 第三关 -->
        <el-card
          style="cursor:pointer;border:2px solid transparent"
          :style="{borderColor: currentRound === 3 ? '#E6A23C' : 'transparent'}"
          @click="enterRound(3)"
        >
          <div style="display:flex;align-items:center;gap:16px">
            <div style="width:48px;height:48px;border-radius:50%;background:#E6A23C;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">⚡</div>
            <div style="flex:1">
              <div style="font-weight:bold;font-size:15px">第三关 · 拓展应用</div>
              <div style="color:#909399;font-size:13px;margin-top:2px">跨学科解读 · 全员抢答</div>
            </div>
            <el-tag type="info">抢答模式</el-tag>
          </div>
        </el-card>
      </div>

      <!-- 各关内容 -->
      <div style="margin-top:20px">

        <!-- 第一关内容 -->
        <el-card v-if="currentRound === 1 && !r1Done">
          <template #header><b>第一关 · 轨道参数计算</b></template>
          <div v-for="(q, i) in r1Questions" :key="q.id" style="margin-bottom:24px">
            <div style="font-weight:500;margin-bottom:10px;line-height:1.6">{{ i+1 }}. {{ q.content }}</div>
            <div v-if="q.type === 'fill'" style="display:flex;align-items:center;gap:8px">
              <el-input v-model="r1Answers[q.id]" :placeholder="'请输入数字'" style="width:160px" size="large" />
              <span style="color:#909399">{{ q.unit }}</span>
            </div>
            <div v-if="q.type === 'judge'">
              <el-radio-group v-model="r1Answers[q.id]">
                <el-radio value="true">✓ 正确</el-radio>
                <el-radio value="false">✗ 错误</el-radio>
              </el-radio-group>
            </div>
          </div>
          <el-button type="primary" size="large" style="width:100%" @click="submitR1" :loading="submitting" :disabled="!r1AllAnswered">
            提交答案
          </el-button>
        </el-card>

        <!-- 第一关结果 -->
        <el-card v-if="currentRound === 1 && r1Done">
          <template #header><b>第一关 · 答题结果</b></template>
          <el-result
            :icon="r1Score === 3 ? 'success' : 'warning'"
            :title="'得分：' + r1Score + ' / 3'"
          />
          <div v-for="d in r1Details" :key="d.id" style="margin-bottom:16px;padding:12px;background:#f5f7fa;border-radius:8px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
              <span style="font-size:18px">{{ d.is_correct ? '✅' : '❌' }}</span>
              <span>你的答案：{{ d.student_answer }}</span>
              <span v-if="!d.is_correct" style="color:#67C23A">正确答案：{{ d.correct_answer }}</span>
            </div>
            <div style="color:#909399;font-size:13px">💡 {{ d.hint }}</div>
          </div>
        </el-card>

        <!-- 第二关内容 -->
        <el-card v-if="currentRound === 2">
          <template #header><b>第二关 · 轨道与徽章设计</b></template>
          <div style="background:#f0f9eb;padding:16px;border-radius:8px;margin-bottom:20px;line-height:1.8;font-size:14px">
            <div style="font-weight:bold;margin-bottom:8px">📋 任务说明</div>
            <div>用圆规画出一个<b>半径 3 厘米</b>的环月轨道，标出<b>圆心、半径、直径</b>，写出直径的长度；</div>
            <div style="margin-top:4px">再用圆设计 1 个<b>航天主题徽章</b>的基础轮廓，融入圆的轴对称性。</div>
          </div>

          <div v-if="!r2Done">
            <div style="text-align:center;margin-bottom:16px;color:#606266;font-size:14px">完成后拍照上传</div>
            <div
              style="border:2px dashed #ddd;border-radius:8px;padding:40px;text-align:center;cursor:pointer"
              @click="$refs.photoInput.click()"
            >
              <div style="font-size:32px;margin-bottom:8px">📷</div>
              <div style="color:#909399">点击拍照或选择图片</div>
            </div>
            <input ref="photoInput" type="file" accept="image/*" capture="environment" style="display:none" @change="handlePhoto" />
            <div v-if="photoPreview" style="margin-top:12px">
              <img :src="photoPreview" style="width:100%;border-radius:8px;max-height:300px;object-fit:contain" />
              <el-button type="primary" style="width:100%;margin-top:12px" @click="uploadPhoto" :loading="uploading">提交作品</el-button>
            </div>
          </div>
          <el-result v-else icon="success" title="作品已提交！" sub-title="等待教师点评" />
        </el-card>

        <!-- 第三关内容 -->
        <el-card v-if="currentRound === 3">
          <template #header><b>第三关 · 跨学科拓展抢答</b></template>

          <div v-if="calledQuestion" style="background:#fff7e6;padding:16px;border-radius:8px;margin-bottom:16px;border-left:4px solid #E6A23C">
            <div style="font-size:12px;color:#E6A23C;margin-bottom:6px">📢 教师点名题目</div>
            <div style="font-size:14px;line-height:1.7">{{ calledQuestion.content }}</div>
          </div>

          <div v-if="myBuzzRank" style="text-align:center;margin:20px 0">
            <div style="font-size:48px">{{ myBuzzRank === 1 ? '🥇' : myBuzzRank === 2 ? '🥈' : '🥉' }}</div>
            <div style="font-size:18px;font-weight:bold;margin-top:8px">你是第 {{ myBuzzRank }} 个抢到！</div>
            <div v-if="myResult === 'correct'" style="color:#67C23A;font-size:16px;margin-top:8px">✅ 回答正确！</div>
            <div v-if="myResult === 'incorrect'" style="color:#F56C6C;font-size:16px;margin-top:8px">❌ 继续加油！</div>
          </div>

          <div style="text-align:center;margin-top:20px">
            <el-button
              type="warning"
              size="large"
              style="width:200px;height:80px;font-size:22px;border-radius:50%"
              :disabled="!!myBuzzRank"
              @click="buzz"
            >
              {{ myBuzzRank ? '已抢答' : '⚡ 抢答' }}
            </el-button>
          </div>

          <!-- 抢答排行 -->
          <div v-if="buzzList.length" style="margin-top:20px">
            <div style="font-weight:bold;margin-bottom:8px;color:#606266">抢答排行</div>
            <div v-for="(b, i) in buzzList" :key="b.student_id"
              style="display:flex;align-items:center;gap:12px;padding:8px;border-radius:6px;margin-bottom:4px"
              :style="{background: b.student_id === user.id ? '#e8f4ff' : '#f5f7fa'}"
            >
              <span style="font-size:18px">{{ i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i+1) + '.' }}</span>
              <span style="flex:1">{{ b.name }}</span>
              <el-tag v-if="b.result === 'correct'" type="success" size="small">✓ 正确</el-tag>
              <el-tag v-if="b.result === 'incorrect'" type="danger" size="small">✗</el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api'

const route = useRoute()
const sessionId = route.params.session_id

const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
const loginForm = ref({ username: '', password: '' })
const loginError = ref('')
const logging = ref(false)
const currentRound = ref(1)

// 第一关
const r1Questions = ref([])
const r1Answers = ref({})
const r1Done = ref(false)
const r1Score = ref(0)
const r1Details = ref([])
const submitting = ref(false)
const r1AllAnswered = computed(() => r1Questions.value.every(q => r1Answers.value[q.id] !== undefined && r1Answers.value[q.id] !== ''))

// 第二关
const photoPreview = ref(null)
const photoFile = ref(null)
const r2Done = ref(false)
const uploading = ref(false)
const photoInput = ref(null)

// 第三关
const buzzList = ref([])
const myBuzzRank = ref(null)
const myResult = ref(null)
const calledQuestion = ref(null)

// WebSocket
let ws = null

async function doLogin() {
  logging.value = true
  loginError.value = ''
  try {
    const res = await api.post('/api/auth/login', loginForm.value)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    user.value = res.user
    init()
  } catch (e) {
    loginError.value = '账号或密码错误'
  } finally {
    logging.value = false
  }
}

function enterRound(n) {
  currentRound.value = n
}

async function init() {
  r1Questions.value = await api.get('/api/challenge/round1/questions')
  connectWS()
}

function connectWS() {
  if (!user.value) return
  const clientId = `student_${user.value.id}`
  ws = new WebSocket(`ws://localhost:8001/api/challenge/ws/${sessionId}/${clientId}`)
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data)
    if (msg.type === 'r3_buzz') {
      buzzList.value = msg.buzz_list
      const mine = msg.buzz_list.find(b => b.student_id === user.value.id)
      if (mine) myBuzzRank.value = msg.buzz_list.indexOf(mine) + 1
    }
    if (msg.type === 'r3_call') {
      calledQuestion.value = msg.question
    }
    if (msg.type === 'r3_result') {
      buzzList.value = msg.buzz_list
      if (msg.student_id === user.value.id) myResult.value = msg.result
    }
    if (msg.type === 'r3_reset') {
      buzzList.value = []
      myBuzzRank.value = null
      myResult.value = null
      calledQuestion.value = null
    }
  }
}

async function submitR1() {
  submitting.value = true
  try {
    const res = await api.post('/api/challenge/round1/submit', {
      session_id: sessionId,
      answers: r1Answers.value,
    })
    r1Score.value = res.score
    r1Details.value = res.details
    r1Done.value = true
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

function handlePhoto(e) {
  const file = e.target.files[0]
  if (!file) return
  photoFile.value = file
  photoPreview.value = URL.createObjectURL(file)
}

async function uploadPhoto() {
  if (!photoFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('session_id', sessionId)
    fd.append('file', photoFile.value)
    await api.post('/api/challenge/round2/upload', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    r2Done.value = true
    ElMessage.success('作品提交成功！')
  } catch (e) {
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

async function buzz() {
  try {
    const res = await api.post('/api/challenge/round3/buzz', { session_id: sessionId })
    myBuzzRank.value = res.rank
  } catch (e) {
    ElMessage.error('抢答失败')
  }
}

onMounted(() => {
  if (user.value) init()
})

onUnmounted(() => {
  if (ws) ws.close()
})
</script>
