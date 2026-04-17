<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>作业管理</h2>
      <el-button type="primary" @click="showDialog = true">发布作业</el-button>
    </div>

    <el-table :data="assignments" stripe>
      <el-table-column prop="title" label="作业标题" />
      <el-table-column label="科目" width="80">
        <template #default="{ row }">{{ subjectName(row.subject_id) }}</template>
      </el-table-column>
      <el-table-column label="一档题数" width="100">
        <template #default="{ row }"><el-tag type="success">{{ row.tier1_count }} 题</el-tag></template>
      </el-table-column>
      <el-table-column label="二档题数" width="100">
        <template #default="{ row }"><el-tag type="warning">{{ row.tier2_count }} 题</el-tag></template>
      </el-table-column>
      <el-table-column label="提交人数" width="100">
        <template #default="{ row }">{{ row.submission_count }} 人</template>
      </el-table-column>
      <el-table-column label="截止时间" width="160">
        <template #default="{ row }">{{ row.deadline ? new Date(row.deadline).toLocaleString() : '不限' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-button type="danger" link size="small" @click="deleteAssignment(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="发布作业" width="700px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="作业标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="班级">
          <el-select v-model="form.class_id">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="科目">
          <el-select v-model="form.subject_id" @change="loadQuestionsBySubject">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间">
          <el-date-picker v-model="form.deadline" type="datetime" placeholder="不设置则不限" />
        </el-form-item>
        <el-form-item label="一档题目（优秀学生做）">
          <div style="color:#909399;font-size:12px;margin-bottom:8px">正确率≥70%的学生将看到这些题</div>
          <el-select v-model="form.tier1_question_ids" multiple placeholder="选择进阶题" style="width:100%">
            <el-option v-for="q in advancedQs" :key="q.id" :label="q.content.substring(0,40)" :value="q.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="二档题目（加强学生做）">
          <div style="color:#909399;font-size:12px;margin-bottom:8px">正确率&lt;70%的学生将看到这些题</div>
          <el-select v-model="form.tier2_question_ids" multiple placeholder="选择基础题" style="width:100%">
            <el-option v-for="q in basicQs" :key="q.id" :label="q.content.substring(0,40)" :value="q.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submit">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const assignments = ref([])
const classes = ref([])
const subjects = ref([])
const basicQs = ref([])
const advancedQs = ref([])
const showDialog = ref(false)
const form = ref({
  title: '', class_id: null, subject_id: null, deadline: null,
  tier1_question_ids: [], tier2_question_ids: []
})

const subjectName = (id) => subjects.value.find(s => s.id === id)?.name || ''

async function loadQuestionsBySubject() {
  if (!form.value.subject_id) return
  const all = await api.get('/api/questions', { params: { subject_id: form.value.subject_id } })
  basicQs.value = all.filter(q => q.difficulty === 1)
  advancedQs.value = all.filter(q => q.difficulty === 2)
}

async function submit() {
  await api.post('/api/assignments', form.value)
  ElMessage.success('作业发布成功')
  showDialog.value = false
  loadAssignments()
}

async function deleteAssignment(id) {
  await ElMessageBox.confirm('确定删除该作业？', '提示', { type: 'warning' })
  await api.delete(`/api/assignments/${id}`)
  ElMessage.success('已删除')
  loadAssignments()
}

async function loadAssignments() {
  assignments.value = await api.get('/api/assignments')
}

onMounted(async () => {
  classes.value = await api.get('/api/classes')
  subjects.value = await api.get('/api/subjects')
  loadAssignments()
})
</script>
