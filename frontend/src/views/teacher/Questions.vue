<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>题库管理</h2>
      <el-button type="primary" @click="openAdd">添加题目</el-button>
    </div>

    <el-card style="margin-bottom:16px">
      <el-row :gutter="12">
        <el-col :span="6">
          <el-select v-model="filter.subject_id" placeholder="按科目筛选" clearable @change="loadQuestions">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filter.difficulty" placeholder="按难度筛选" clearable @change="loadQuestions">
            <el-option label="基础（一档）" :value="1" />
            <el-option label="进阶（二档）" :value="2" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <el-table :data="questions" stripe>
      <el-table-column type="index" width="50" />
      <el-table-column prop="content" label="题目" show-overflow-tooltip />
      <el-table-column label="科目" width="80">
        <template #default="{ row }">{{ subjectName(row.subject_id) }}</template>
      </el-table-column>
      <el-table-column label="难度" width="100">
        <template #default="{ row }">
          <el-tag :type="row.difficulty === 1 ? 'info' : 'warning'">
            {{ row.difficulty === 1 ? '基础' : '进阶' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="答案" width="60">
        <template #default="{ row }">
          <el-tag type="success">{{ row.answer }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="知识点" width="180">
        <template #default="{ row }">
          <el-tag v-for="t in (row.tags || [])" :key="t" size="small" style="margin:2px">{{ t }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="danger" size="small" link @click="deleteQuestion(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDialog" title="添加题目" width="600px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="科目">
          <el-select v-model="form.subject_id" placeholder="选择科目">
            <el-option v-for="s in subjects" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度">
          <el-radio-group v-model="form.difficulty">
            <el-radio :value="1">基础（适合二档学生）</el-radio>
            <el-radio :value="2">进阶（适合一档学生）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="题目">
          <el-input v-model="form.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item v-for="(opt, i) in form.options" :key="i" :label="'选项' + labels[i]">
          <el-input v-model="form.options[i]" :placeholder="labels[i] + '.'" />
        </el-form-item>
        <el-form-item label="正确答案">
          <el-radio-group v-model="form.answer">
            <el-radio v-for="l in labels" :key="l" :value="l">{{ l }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="form.explanation" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="知识点">
          <el-input v-model="tagsInput" placeholder="用逗号分隔，如：半径,直径" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const labels = ['A', 'B', 'C', 'D']
const questions = ref([])
const subjects = ref([])
const filter = ref({ subject_id: null, difficulty: null })
const showDialog = ref(false)
const tagsInput = ref('')
const form = ref({
  content: '', options: ['', '', '', ''], answer: 'A',
  explanation: '', difficulty: 1, subject_id: null, tags: []
})

const subjectName = (id) => subjects.value.find(s => s.id === id)?.name || ''

async function loadQuestions() {
  const params = {}
  if (filter.value.subject_id) params.subject_id = filter.value.subject_id
  if (filter.value.difficulty) params.difficulty = filter.value.difficulty
  questions.value = await api.get('/api/questions', { params })
}

function openAdd() {
  form.value = { content: '', options: ['', '', '', ''], answer: 'A', explanation: '', difficulty: 1, subject_id: subjects.value[0]?.id || null, tags: [] }
  tagsInput.value = ''
  showDialog.value = true
}

async function submit() {
  const payload = {
    ...form.value,
    tags: tagsInput.value ? tagsInput.value.split(',').map(t => t.trim()) : [],
  }
  await api.post('/api/questions', payload)
  ElMessage.success('题目添加成功')
  showDialog.value = false
  loadQuestions()
}

async function deleteQuestion(id) {
  await ElMessageBox.confirm('确定删除该题目？', '提示', { type: 'warning' })
  await api.delete(`/api/questions/${id}`)
  ElMessage.success('已删除')
  loadQuestions()
}

onMounted(async () => {
  subjects.value = await api.get('/api/subjects')
  loadQuestions()
})
</script>
