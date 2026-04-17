<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>班级管理</h2>
      <el-button type="primary" @click="showClassDialog = true">新建班级</el-button>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="8" v-for="cls in classes" :key="cls.id">
        <el-card shadow="hover" style="cursor:pointer" @click="selectClass(cls)">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-size:16px;font-weight:bold">{{ cls.name }}</div>
              <div style="color:#909399;margin-top:4px">{{ cls.student_count }} 名学生</div>
            </div>
            <el-icon size="32" color="#409EFF"><School /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="selectedClass">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>{{ selectedClass.name }} - 学生列表</span>
          <el-button type="primary" size="small" @click="showStudentDialog = true">添加学生</el-button>
        </div>
      </template>
      <el-table :data="students" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column label="档位" width="120">
          <template #default="{ row }">
            <el-tag :type="row.tier === 1 ? 'success' : 'danger'">
              {{ row.tier === 1 ? '一档（优秀）' : '二档（加强）' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.accuracy" :color="row.accuracy >= 70 ? '#67C23A' : '#F56C6C'" />
          </template>
        </el-table-column>
        <el-table-column prop="total_answered" label="答题数" width="80" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click="deleteStudent(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建班级对话框 -->
    <el-dialog v-model="showClassDialog" title="新建班级" width="400px">
      <el-form :model="classForm">
        <el-form-item label="班级名称">
          <el-input v-model="classForm.name" placeholder="例：六年级（1）班" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showClassDialog = false">取消</el-button>
        <el-button type="primary" @click="createClass">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加学生对话框 -->
    <el-dialog v-model="showStudentDialog" title="添加学生" width="400px">
      <el-form :model="studentForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="studentForm.name" /></el-form-item>
        <el-form-item label="用户名"><el-input v-model="studentForm.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="studentForm.password" type="password" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showStudentDialog = false">取消</el-button>
        <el-button type="primary" @click="createStudent">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { School } from '@element-plus/icons-vue'
import api from '../../api'

const classes = ref([])
const students = ref([])
const selectedClass = ref(null)
const showClassDialog = ref(false)
const showStudentDialog = ref(false)
const classForm = ref({ name: '' })
const studentForm = ref({ name: '', username: '', password: '123456' })

async function loadClasses() {
  classes.value = await api.get('/api/classes')
}

async function selectClass(cls) {
  selectedClass.value = cls
  students.value = await api.get(`/api/classes/${cls.id}/students`)
}

async function createClass() {
  await api.post('/api/classes', classForm.value)
  ElMessage.success('班级创建成功')
  showClassDialog.value = false
  classForm.value.name = ''
  loadClasses()
}

async function createStudent() {
  await api.post('/api/classes/students', { ...studentForm.value, class_id: selectedClass.value.id })
  ElMessage.success('学生添加成功')
  showStudentDialog.value = false
  selectClass(selectedClass.value)
  loadClasses()
}

async function deleteStudent(id) {
  await ElMessageBox.confirm('确定删除该学生？', '提示', { type: 'warning' })
  await api.delete(`/api/classes/students/${id}`)
  ElMessage.success('已删除')
  selectClass(selectedClass.value)
}

onMounted(loadClasses)
</script>
