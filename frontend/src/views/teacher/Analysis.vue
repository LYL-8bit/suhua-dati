<template>
  <div>
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
      <h2>学情分析</h2>
      <el-select v-model="selectedClassId" placeholder="选择班级" @change="loadAnalysis">
        <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
    </div>

    <template v-if="analysis">
      <!-- 班级概览 -->
      <el-row :gutter="16" style="margin-bottom:20px">
        <el-col :span="6" v-for="stat in overviewStats" :key="stat.label">
          <el-card shadow="hover" style="text-align:center">
            <div style="font-size:32px;font-weight:bold;color:#409EFF">{{ stat.value }}</div>
            <div style="color:#909399;margin-top:4px">{{ stat.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-bottom:20px">
        <el-col :span="12">
          <el-card>
            <template #header>知识点掌握率</template>
            <div ref="tagChart" style="height:300px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>成绩分布</template>
            <div ref="distChart" style="height:300px"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 学生列表 -->
      <el-card>
        <template #header>学生学情详情</template>
        <el-table :data="analysis.students" stripe @row-click="row => { selectedStudent = row; drawerVisible = true }">
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column label="档位" width="130">
            <template #default="{ row }">
              <el-tag :type="row.tier === 1 ? 'success' : 'danger'">
                {{ row.tier === 1 ? '一档（优秀）' : '二档（加强）' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="正确率" width="200">
            <template #default="{ row }">
              <el-progress :percentage="row.accuracy" :color="row.accuracy >= 70 ? '#67C23A' : '#F56C6C'" />
            </template>
          </el-table-column>
          <el-table-column prop="total_answered" label="答题数" width="80" />
          <el-table-column label="趋势">
            <template #default="{ row }">
              <span v-if="row.trend.length >= 2">
                <el-icon v-if="row.trend[row.trend.length-1].accuracy > row.trend[0].accuracy" color="#67C23A"><ArrowUp /></el-icon>
                <el-icon v-else color="#F56C6C"><ArrowDown /></el-icon>
              </span>
              <span v-else style="color:#909399">--</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 单生详情 -->
      <el-drawer v-model="drawerVisible" title="学生详情" size="500px">
        <template v-if="selectedStudent">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">{{ selectedStudent.name }}</el-descriptions-item>
            <el-descriptions-item label="档位">
              <el-tag :type="selectedStudent.tier === 1 ? 'success' : 'danger'">
                {{ selectedStudent.tier === 1 ? '一档' : '二档' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="正确率">{{ selectedStudent.accuracy }}%</el-descriptions-item>
            <el-descriptions-item label="答题数">{{ selectedStudent.total_answered }}</el-descriptions-item>
          </el-descriptions>
          <div style="margin-top:16px">
            <div style="font-weight:bold;margin-bottom:8px">历次作业趋势</div>
            <div ref="trendChart" style="height:200px"></div>
          </div>
        </template>
      </el-drawer>
    </template>
    <el-empty v-else description="请选择班级查看学情" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import api from '../../api'

const classes = ref([])
const selectedClassId = ref(null)
const analysis = ref(null)
const selectedStudent = ref(null)
const drawerVisible = ref(false)
const tagChart = ref(null)
const distChart = ref(null)
const trendChart = ref(null)
const overviewStats = ref([])

async function loadAnalysis() {
  if (!selectedClassId.value) return
  analysis.value = await api.get(`/api/analysis/class/${selectedClassId.value}`)

  overviewStats.value = [
    { label: '学生总数', value: analysis.value.student_count },
    { label: '班级平均正确率', value: analysis.value.avg_accuracy + '%' },
    { label: '一档人数（≥70%）', value: analysis.value.tier1_count },
    { label: '二档人数（<70%）', value: analysis.value.tier2_count },
  ]

  await nextTick()
  renderCharts()
}

function renderCharts() {
  if (tagChart.value && analysis.value.tag_analysis.length) {
    const chart = echarts.init(tagChart.value)
    const tags = analysis.value.tag_analysis
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: tags.map(t => t.tag), axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', max: 100, name: '掌握率(%)' },
      series: [{
        type: 'bar', data: tags.map(t => t.accuracy),
        itemStyle: { color: (params) => params.value >= 70 ? '#67C23A' : '#F56C6C' },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
  }

  if (distChart.value) {
    const dist = analysis.value.score_distribution
    const chart = echarts.init(distChart.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: '60%',
        data: [
          { value: dist['90-100'], name: '优秀 (90-100%)', itemStyle: { color: '#67C23A' } },
          { value: dist['70-89'], name: '良好 (70-89%)', itemStyle: { color: '#409EFF' } },
          { value: dist['60-69'], name: '一般 (60-69%)', itemStyle: { color: '#E6A23C' } },
          { value: dist['0-59'], name: '待提高 (<60%)', itemStyle: { color: '#F56C6C' } },
        ],
        label: { formatter: '{b}\n{c}人' }
      }]
    })
  }
}

watch(drawerVisible, async (val) => {
  if (!val || !selectedStudent.value) return
  const student = selectedStudent.value
  await nextTick()
  if (trendChart.value && student.trend.length) {
    const chart = echarts.init(trendChart.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: student.trend.map(t => t.date) },
      yAxis: { type: 'value', max: 100, name: '正确率(%)' },
      series: [{ type: 'line', data: student.trend.map(t => t.accuracy), smooth: true, color: '#409EFF', markLine: { data: [{ yAxis: 70, name: '档位线', lineStyle: { color: '#F56C6C', type: 'dashed' } }] } }]
    })
  }
})

onMounted(async () => {
  classes.value = await api.get('/api/classes')
  if (classes.value.length) {
    selectedClassId.value = classes.value[0].id
    loadAnalysis()
  }
})
</script>
