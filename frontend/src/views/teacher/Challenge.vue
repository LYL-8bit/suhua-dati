<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h2>闯关任务控制台</h2>
      <div style="display:flex;gap:12px;align-items:center">
        <el-select v-model="sessionId" placeholder="选择或创建课堂会话" style="width:220px">
          <el-option v-for="s in sessions" :key="s.id" :label="s.title" :value="String(s.id)" />
        </el-select>
        <el-button type="primary" @click="showCreateDialog = true">新建闯关会话</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" v-if="sessionId">
      <!-- 第一关 -->
      <el-tab-pane label="🚀 第一关 · 在线作答" name="r1">
        <el-row :gutter="16" style="margin-bottom:16px">
          <el-col :span="8" v-for="stat in r1Stats" :key="stat.id">
            <el-card shadow="hover" style="text-align:center">
              <div style="font-size:13px;color:#606266;margin-bottom:8px;line-height:1.4">{{ stat.content }}</div>
              <el-progress type="circle" :percentage="stat.accuracy" :color="stat.accuracy >= 70 ? '#67C23A' : '#F56C6C'" :width="80" />
              <div style="font-size:12px;color:#909399;margin-top:6px">{{ stat.correct }}/{{ stat.total }} 人答对</div>
            </el-card>
          </el-col>
        </el-row>
        <el-card>
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>提交情况（{{ r1Submissions.length }} 人）</span>
              <el-button size="small" @click="loadR1">刷新</el-button>
            </div>
          </template>
          <el-table :data="r1Submissions" stripe size="small">
            <el-table-column prop="student_name" label="姓名" width="100" />
            <el-table-column label="得分" width="80">
              <template #default="{ row }">
                <el-tag :type="row.score === row.total ? 'success' : row.score >= 2 ? 'warning' : 'danger'">
                  {{ row.score }}/{{ row.total }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="各题情况">
              <template #default="{ row }">
                <span v-for="d in row.details" :key="d.id" style="margin-right:6px;font-size:16px">
                  {{ d.is_correct ? '✅' : '❌' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 第二关 -->
      <el-tab-pane label="✏️ 第二关 · 拍照批注" name="r2">
        <div style="display:flex;gap:12px;flex-wrap:wrap">
          <div
            v-for="photo in r2Photos" :key="photo.student_id"
            style="width:200px;cursor:pointer"
            @click="openAnnotate(photo)"
          >
            <el-card shadow="hover" :body-style="{padding:'8px'}">
              <img
                :src="'http://localhost:8001/uploads/' + photo.filename"
                style="width:100%;height:150px;object-fit:cover;border-radius:4px"
              />
              <div style="padding:6px 0;display:flex;justify-content:space-between;align-items:center">
                <span style="font-size:13px;font-weight:500">{{ photo.student_name }}</span>
                <el-tag v-if="photo.tag === 'excellent'" type="success" size="small">⭐ 优秀</el-tag>
                <el-tag v-else-if="photo.tag === 'improve'" type="warning" size="small">📝 待改</el-tag>
              </div>
            </el-card>
          </div>
          <el-empty v-if="r2Photos.length === 0" description="等待学生提交作品" style="width:100%" />
        </div>
        <el-button style="margin-top:12px" size="small" @click="loadR2">刷新</el-button>

        <!-- 批注对话框 -->
        <el-dialog v-model="showAnnotate" title="图片批注" width="90vw" :close-on-click-modal="false">
          <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
            <span style="font-weight:bold">{{ annotatingPhoto?.student_name }} 的作品</span>
            <div style="display:flex;gap:8px;align-items:center">
              <span style="font-size:13px;color:#606266">画笔颜色：</span>
              <div v-for="c in brushColors" :key="c"
                :style="{width:'24px',height:'24px',borderRadius:'50%',background:c,cursor:'pointer',border: brushColor===c ? '3px solid #303133' : '2px solid #ddd'}"
                @click="brushColor = c"
              />
            </div>
            <el-slider v-model="brushSize" :min="2" :max="20" style="width:100px" />
            <el-button size="small" @click="clearCanvas">清除</el-button>
            <el-button size="small" type="primary" @click="addText">+ 文字</el-button>
            <el-select v-model="tagValue" size="small" placeholder="打标签" style="width:110px">
              <el-option label="⭐ 优秀" value="excellent" />
              <el-option label="📝 待改进" value="improve" />
            </el-select>
            <el-button size="small" type="success" @click="saveAnnotation" :loading="saving">保存批注</el-button>
          </div>

          <div style="position:relative;display:inline-block;max-width:100%">
            <img
              ref="annotateImg"
              :src="annotatingPhoto ? 'http://localhost:8001/uploads/' + annotatingPhoto.filename : ''"
              style="max-width:100%;max-height:65vh;display:block"
              @load="initCanvas"
            />
            <canvas
              ref="annotateCanvas"
              style="position:absolute;top:0;left:0;cursor:crosshair"
              @mousedown="startDraw"
              @mousemove="drawing"
              @mouseup="stopDraw"
              @touchstart.prevent="startDrawTouch"
              @touchmove.prevent="drawingTouch"
              @touchend="stopDraw"
            />
          </div>
        </el-dialog>
      </el-tab-pane>

      <!-- 第三关 -->
      <el-tab-pane label="⚡ 第三关 · 抢答控制" name="r3">
        <el-row :gutter="16">
          <el-col :span="14">
            <!-- 题目选择 -->
            <el-card style="margin-bottom:16px">
              <template #header>选择展示题目</template>
              <div v-for="q in r3Questions" :key="q.id" style="margin-bottom:8px">
                <el-button
                  :type="activeQuestion === q.id ? 'primary' : 'default'"
                  style="width:100%;text-align:left;height:auto;padding:10px 16px;white-space:normal"
                  @click="callQuestion(q)"
                >
                  <div>
                    <el-tag size="small" style="margin-right:6px">{{ q.subject }}</el-tag>
                    {{ q.content.substring(0, 40) }}...
                  </div>
                </el-button>
              </div>
            </el-card>

            <!-- 当前题目 -->
            <el-card v-if="activeQuestion">
              <template #header>当前展示题目</template>
              <div v-if="currentQ" style="line-height:1.8;font-size:15px">
                <el-tag>{{ currentQ.subject }}</el-tag>
                <div style="margin-top:8px">{{ currentQ.content }}</div>
              </div>
            </el-card>
          </el-col>

          <el-col :span="10">
            <el-card>
              <template #header>
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <span>抢答排行（{{ buzzList.length }} 人）</span>
                  <el-button size="small" type="warning" @click="resetBuzz">重置抢答</el-button>
                </div>
              </template>
              <div v-if="buzzList.length === 0" style="text-align:center;color:#909399;padding:20px">等待学生抢答...</div>
              <div v-for="(b, i) in buzzList" :key="b.student_id"
                style="display:flex;align-items:center;gap:12px;padding:10px;border-radius:8px;margin-bottom:6px"
                :style="{background: i === 0 ? '#fff7e6' : '#f5f7fa'}"
              >
                <span style="font-size:20px;width:28px">{{ i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i+1) }}</span>
                <span style="flex:1;font-weight: i===0 ? 'bold' : 'normal'">{{ b.name }}</span>
                <div style="display:flex;gap:6px">
                  <el-button size="small" type="success" @click="mark(b.student_id, 'correct')" :disabled="!!b.result">✓</el-button>
                  <el-button size="small" type="danger" @click="mark(b.student_id, 'incorrect')" :disabled="!!b.result">✗</el-button>
                </div>
                <el-tag v-if="b.result === 'correct'" type="success" size="small">正确</el-tag>
                <el-tag v-if="b.result === 'incorrect'" type="danger" size="small">错误</el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <el-empty v-else description="请先选择或新建一个闯关会话" />

    <!-- 新建会话对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建闯关会话" width="400px">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="会话名称">
          <el-input v-model="createForm.title" placeholder="例：圆的认识-第1课时" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="createForm.class_id" style="width:100%">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createSession">创建并获取二维码</el-button>
      </template>
    </el-dialog>

    <!-- 二维码弹窗 -->
    <el-dialog v-model="showQR" title="学生扫码进入闯关" width="360px">
      <div style="text-align:center;padding:16px">
        <img v-if="qrBase64" :src="'data:image/png;base64,' + qrBase64" style="width:220px;height:220px" />
        <div style="margin-top:12px;color:#606266;font-size:13px">{{ qrUrl }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const activeTab = ref('r1')
const sessionId = ref('')
const sessions = ref([])
const classes = ref([])
const showCreateDialog = ref(false)
const showQR = ref(false)
const qrBase64 = ref('')
const qrUrl = ref('')
const createForm = ref({ title: '', class_id: null })

// 第一关
const r1Stats = ref([])
const r1Submissions = ref([])

// 第二关
const r2Photos = ref([])
const showAnnotate = ref(false)
const annotatingPhoto = ref(null)
const annotateImg = ref(null)
const annotateCanvas = ref(null)
const brushColor = ref('#FF0000')
const brushSize = ref(4)
const brushColors = ['#FF0000', '#FF6600', '#67C23A', '#409EFF', '#303133']
const tagValue = ref(null)
const saving = ref(false)
let isDrawing = false
let ctx = null

// 第三关
const r3Questions = ref([])
const buzzList = ref([])
const activeQuestion = ref(null)
const currentQ = computed(() => r3Questions.value.find(q => q.id === activeQuestion.value))
let ws = null

// ===== 生命周期 =====
onMounted(async () => {
  classes.value = await api.get('/api/classes')
  await loadSessions()
  r3Questions.value = await api.get('/api/challenge/round3/questions')
})

onUnmounted(() => { if (ws) ws.close() })

watch(sessionId, (val) => {
  if (val) {
    loadR1()
    loadR2()
    connectWS()
  }
})

// ===== 会话 =====
async function loadSessions() {
  sessions.value = await api.get('/api/classroom/sessions')
}

async function createSession() {
  const res = await api.post('/api/classroom/sessions', {
    ...createForm.value,
    subject_id: 1,
    question_ids: [],
    is_challenge: true,
  })
  qrBase64.value = res.qr_base64
  qrUrl.value = res.join_url.replace('/classroom/join/', '/challenge/')
  sessionId.value = String(res.id)
  showCreateDialog.value = false
  showQR.value = true
  loadSessions()
}

// ===== 第一关 =====
async function loadR1() {
  if (!sessionId.value) return
  const data = await api.get(`/api/challenge/round1/stats/${sessionId.value}`)
  r1Submissions.value = data.submissions
  r1Stats.value = data.stats
}

// ===== 第二关 =====
async function loadR2() {
  if (!sessionId.value) return
  r2Photos.value = await api.get(`/api/challenge/round2/photos/${sessionId.value}`)
}

function openAnnotate(photo) {
  annotatingPhoto.value = photo
  tagValue.value = photo.tag || null
  showAnnotate.value = true
  ctx = null
}

function initCanvas() {
  const img = annotateImg.value
  const canvas = annotateCanvas.value
  if (!img || !canvas) return
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  canvas.style.width = img.offsetWidth + 'px'
  canvas.style.height = img.offsetHeight + 'px'
  ctx = canvas.getContext('2d')
}

function getPos(e, canvas) {
  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top) * scaleY,
  }
}

function startDraw(e) {
  isDrawing = true
  if (!ctx) return
  ctx.beginPath()
  const pos = getPos(e, annotateCanvas.value)
  ctx.moveTo(pos.x, pos.y)
}

function drawing(e) {
  if (!isDrawing || !ctx) return
  ctx.strokeStyle = brushColor.value
  ctx.lineWidth = brushSize.value
  ctx.lineCap = 'round'
  const pos = getPos(e, annotateCanvas.value)
  ctx.lineTo(pos.x, pos.y)
  ctx.stroke()
}

function stopDraw() { isDrawing = false }

function startDrawTouch(e) {
  isDrawing = true
  if (!ctx) return
  ctx.beginPath()
  const touch = e.touches[0]
  const rect = annotateCanvas.value.getBoundingClientRect()
  const scaleX = annotateCanvas.value.width / rect.width
  const scaleY = annotateCanvas.value.height / rect.height
  ctx.moveTo((touch.clientX - rect.left) * scaleX, (touch.clientY - rect.top) * scaleY)
}

function drawingTouch(e) {
  if (!isDrawing || !ctx) return
  ctx.strokeStyle = brushColor.value
  ctx.lineWidth = brushSize.value
  ctx.lineCap = 'round'
  const touch = e.touches[0]
  const rect = annotateCanvas.value.getBoundingClientRect()
  const scaleX = annotateCanvas.value.width / rect.width
  const scaleY = annotateCanvas.value.height / rect.height
  ctx.lineTo((touch.clientX - rect.left) * scaleX, (touch.clientY - rect.top) * scaleY)
  ctx.stroke()
}

function clearCanvas() {
  if (ctx && annotateCanvas.value) {
    ctx.clearRect(0, 0, annotateCanvas.value.width, annotateCanvas.value.height)
  }
}

function addText() {
  const text = prompt('请输入批注文字：')
  if (!text || !ctx) return
  ctx.font = `${brushSize.value * 5}px Microsoft YaHei`
  ctx.fillStyle = brushColor.value
  ctx.fillText(text, 20, 40)
}

async function saveAnnotation() {
  if (!annotateCanvas.value || !annotatingPhoto.value) return
  saving.value = true
  try {
    const dataURL = annotateCanvas.value.toDataURL('image/png')
    await api.post('/api/challenge/round2/annotate', {
      session_id: sessionId.value,
      student_id: annotatingPhoto.value.student_id,
      annotation_data: dataURL,
      tag: tagValue.value,
    })
    ElMessage.success('批注已保存')
    annotatingPhoto.value.tag = tagValue.value
    showAnnotate.value = false
    loadR2()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// ===== 第三关 =====
function connectWS() {
  if (ws) ws.close()
  ws = new WebSocket(`ws://localhost:8001/api/challenge/ws/${sessionId.value}/teacher`)
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data)
    if (msg.type === 'r3_buzz' || msg.type === 'r3_result' || msg.type === 'r3_reset') {
      buzzList.value = msg.buzz_list || []
    }
    if (msg.type === 'r1_update') loadR1()
    if (msg.type === 'r2_new_photo') loadR2()
  }
}

async function callQuestion(q) {
  activeQuestion.value = q.id
  await api.post('/api/challenge/round3/call', {
    session_id: sessionId.value,
    student_id: 0,
    question_id: q.id,
  })
}

async function mark(studentId, result) {
  await api.post('/api/challenge/round3/mark', {
    session_id: sessionId.value,
    student_id: studentId,
    result,
  })
}

async function resetBuzz() {
  await api.post(`/api/challenge/round3/reset-buzz?session_id=${sessionId.value}`)
  buzzList.value = []
}
</script>
