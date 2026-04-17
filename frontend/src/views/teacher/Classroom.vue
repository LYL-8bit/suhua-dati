<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>课堂实时答题</h2>
      <el-button type="primary" @click="showDialog = true">发起课堂答题</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-table :data="sessions" stripe>
          <el-table-column prop="title" label="课堂标题" />
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                {{ row.status === 'active' ? '进行中' : '已结束' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="提交情况" width="120">
            <template #default="{ row }">{{ row.submission_count }}/{{ row.student_count }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button size="small" @click="viewStats(row)">查看统计</el-button>
              <el-button size="small" type="warning" v-if="row.status === 'active'" @click="closeSession(row.id)">结束</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-col>

      <el-col :span="10">
        <!-- 二维码显示区 -->
        <el-card v-if="activeSession">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span>{{ activeSession.title }}</span>
              <el-tag type="success">学生扫码进入</el-tag>
            </div>
          </template>
          <div style="text-align:center;padding:16px">
            <img :src="'data:image/png;base64,' + activeSession.qr_base64" style="width:200px;height:200px" />
            <div style="margin-top:12px;color:#606266;font-size:13px">学生用手机扫描二维码进入答题</div>
            <div style="margin-top:8px;color:#909399;font-size:12px;word-break:break-all">{{ activeSession.join_url }}</div>
          </div>
        </el-card>

        <!-- 实时统计 -->
        <el-card v-if="sessionStats" style="margin-top:16px">
          <template #header>实时统计</template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="已提交">{{ sessionStats.submitted_count }}/{{ sessionStats.student_count }}</el-descriptions-item>
            <el-descriptions-item label="平均正确率">{{ sessionStats.avg_accuracy }}%</el-descriptions-item>
          </el-descriptions>
          <div style="margin-top:12px" v-for="q in sessionStats.question_stats" :key="q.question_id">
            <div style="font-size:12px;color:#606266;margin-bottom:4px">{{ q.content }}</div>
            <el-progress :percentage="q.accuracy" :format="p => q.correct + '/' + q.total + ' (' + p + '%)'">
              <template #default="{ percentage }">
                <span style="font-size:12px">{{ q.correct }}/{{ q.total }} ({{ percentage }}%)</span>
              </template>
            </el-progress>
          </div>
          <el-button style="margin-top:12px" size="small" @click="refreshStats">刷新数据</el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showDialog" title="发起课堂答题" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="班级">
          <el-select v-model="form.class_id">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="科目">
          <el-select v-model="form.subject_id" @change="loadQs">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选题">
          <el-select v-model="form.question_ids" multiple style="width:100%">
            <el-option v-for="q in allQs" :key="q.id" :label="'[' + (q.difficulty===1?'基础':'进阶') + '] ' + q.content.substring(0,40)" :value="q.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="createSession">发起</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const sessions = ref([])
const classes = ref([])
const subjects = ref([])
const allQs = ref([])
const showDialog = ref(false)
const activeSession = ref(null)
const sessionStats = ref(null)
const form = ref({ title: '', class_id: null, subject_id: null, question_ids: [] })

async function loadSessions() {
  sessions.value = await api.get('/api/classroom/sessions')
}

async function loadQs() {
  if (!form.value.subject_id) return
  allQs.value = await api.get('/api/questions', { params: { subject_id: form.value.subject_id } })
}

async function createSession() {
  const res = await api.post('/api/classroom/sessions', form.value)
  activeSession.value = res
  showDialog.value = false
  ElMessage.success('课堂已发起，学生可扫码进入')
  loadSessions()
}

async function viewStats(session) {
  activeSession.value = null
  sessionStats.value = await api.get(`/api/classroom/sessions/${session.id}/stats`)
}

async function refreshStats() {
  if (sessionStats.value) {
    sessionStats.value = await api.get(`/api/classroom/sessions/${sessionStats.value.session_id}/stats`)
  }
}

async function closeSession(id) {
  await api.post(`/api/classroom/sessions/${id}/close`)
  ElMessage.success('课堂已结束')
  loadSessions()
}

onMounted(async () => {
  classes.value = await api.get('/api/classes')
  subjects.value = await api.get('/api/subjects')
  loadSessions()
})
</script>
