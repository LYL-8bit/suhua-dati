<template>
  <div>
    <h2 style="margin-bottom:20px">我的作业</h2>
    <el-row :gutter="16">
      <el-col :span="8" v-for="a in assignments" :key="a.id" style="margin-bottom:16px">
        <el-card shadow="hover">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div style="font-size:15px;font-weight:bold;margin-bottom:8px">{{ a.title }}</div>
              <div style="color:#909399;font-size:13px">共 {{ a.question_count }} 题</div>
              <div v-if="a.deadline" style="color:#909399;font-size:12px;margin-top:4px">
                截止：{{ new Date(a.deadline).toLocaleString() }}
              </div>
            </div>
            <el-tag v-if="a.submitted" type="success">已提交</el-tag>
            <el-tag v-else type="warning">待完成</el-tag>
          </div>
          <div v-if="a.submitted" style="margin-top:12px">
            <el-progress :percentage="a.score / a.total * 100" :format="() => a.score + '/' + a.total" />
          </div>
          <div style="margin-top:12px">
            <el-button
              type="primary" size="small" style="width:100%"
              :disabled="a.submitted"
              @click="$router.push('/student/assignment/' + a.id)"
            >
              {{ a.submitted ? '已完成' : '开始作答' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="assignments.length === 0" description="暂无作业" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const assignments = ref([])

onMounted(async () => {
  assignments.value = await api.get('/api/assignments')
})
</script>
