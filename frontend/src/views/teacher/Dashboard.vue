<template>
  <div>
    <h2 style="margin-bottom:20px">首页总览</h2>
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover">
          <div style="display:flex;align-items:center;gap:12px">
            <div :style="{background: stat.color, borderRadius:'50%', width:'48px', height:'48px', display:'flex', alignItems:'center', justifyContent:'center'}">
              <el-icon size="24" color="#fff"><component :is="stat.icon" /></el-icon>
            </div>
            <div>
              <div style="font-size:28px;font-weight:bold;color:#303133">{{ stat.value }}</div>
              <div style="color:#909399;font-size:13px">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card>
          <template #header>班级档位分布</template>
          <div ref="tierChart" style="height:260px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>近期作业提交率</template>
          <div ref="submitChart" style="height:260px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import api from '../../api'
import { School, Document, Finished, TrendCharts } from '@element-plus/icons-vue'

const tierChart = ref(null)
const submitChart = ref(null)
const stats = ref([
  { label: '班级总数', value: 0, color: '#409EFF', icon: 'School' },
  { label: '学生总数', value: 0, color: '#67C23A', icon: 'Document' },
  { label: '题库题目', value: 0, color: '#E6A23C', icon: 'Finished' },
  { label: '已发作业', value: 0, color: '#F56C6C', icon: 'TrendCharts' },
])

onMounted(async () => {
  try {
    const [classes, questions, assignments] = await Promise.all([
      api.get('/api/classes'),
      api.get('/api/questions'),
      api.get('/api/assignments'),
    ])

    let studentCount = 0
    let tier1 = 0, tier2 = 0
    for (const cls of classes) {
      const students = await api.get(`/api/classes/${cls.id}/students`)
      studentCount += students.length
      tier1 += students.filter(s => s.tier === 1).length
      tier2 += students.filter(s => s.tier === 2).length
    }

    stats.value[0].value = classes.length
    stats.value[1].value = studentCount
    stats.value[2].value = questions.length
    stats.value[3].value = assignments.length

    // 档位饼图
    const pie = echarts.init(tierChart.value)
    pie.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: [
          { value: tier1, name: '一档（优秀≥70%）', itemStyle: { color: '#67C23A' } },
          { value: tier2, name: '二档（需加强<70%）', itemStyle: { color: '#F56C6C' } },
        ],
        label: { formatter: '{b}: {c}人' }
      }]
    })

    // 提交率柱状图
    const bar = echarts.init(submitChart.value)
    const recentAssignments = assignments.slice(0, 5).reverse()
    bar.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: recentAssignments.map(a => a.title.substring(0, 8)) },
      yAxis: { type: 'value', name: '提交人数' },
      series: [{
        type: 'bar', name: '提交人数', color: '#409EFF',
        data: recentAssignments.map(a => a.submission_count),
        label: { show: true, position: 'top' }
      }]
    })
  } catch (e) {
    console.error(e)
  }
})
</script>
