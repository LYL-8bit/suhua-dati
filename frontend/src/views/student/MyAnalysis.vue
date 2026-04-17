<template>
  <div>
    <h2 style="margin-bottom:20px">我的学情</h2>
    <template v-if="data">
      <el-row :gutter="16" style="margin-bottom:20px">
        <el-col :span="6" v-for="stat in stats" :key="stat.label">
          <el-card shadow="hover" style="text-align:center">
            <div style="font-size:28px;font-weight:bold" :style="{color: stat.color}">{{ stat.value }}</div>
            <div style="color:#909399;margin-top:4px;font-size:13px">{{ stat.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-card>
            <template #header>知识点掌握雷达图</template>
            <div ref="radarChart" style="height:300px"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>历次作业正确率趋势</template>
            <div ref="trendChartEl" style="height:300px"></div>
          </el-card>
        </el-col>
      </el-row>
    </template>
    <el-skeleton v-else :rows="6" animated />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import api from '../../api'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const data = ref(null)
const radarChart = ref(null)
const trendChartEl = ref(null)

const stats = computed(() => data.value ? [
  { label: '综合正确率', value: data.value.accuracy + '%', color: data.value.accuracy >= 70 ? '#67C23A' : '#F56C6C' },
  { label: '当前档位', value: data.value.tier === 1 ? '一档' : '二档', color: data.value.tier === 1 ? '#67C23A' : '#E6A23C' },
  { label: '总答题数', value: data.value.total_answered, color: '#409EFF' },
  { label: '超过同学', value: data.value.beat_percent + '%', color: '#909399' },
] : [])

onMounted(async () => {
  data.value = await api.get(`/api/analysis/student/${userStore.user.id}`)
  await nextTick()

  // 雷达图
  if (radarChart.value && data.value.tag_analysis.length) {
    const chart = echarts.init(radarChart.value)
    const tags = data.value.tag_analysis
    chart.setOption({
      tooltip: {},
      radar: {
        indicator: tags.map(t => ({ name: t.tag, max: 100 })),
        radius: '65%',
      },
      series: [{
        type: 'radar',
        data: [{ value: tags.map(t => t.accuracy), name: '掌握率', areaStyle: { opacity: 0.3 } }],
        color: '#409EFF',
      }]
    })
  }

  // 趋势图
  if (trendChartEl.value && data.value.trend.length) {
    const chart = echarts.init(trendChartEl.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.value.trend.map(t => t.date) },
      yAxis: { type: 'value', max: 100, name: '正确率(%)' },
      series: [{
        type: 'line', smooth: true, color: '#409EFF',
        data: data.value.trend.map(t => t.accuracy),
        markLine: { data: [{ yAxis: 70, lineStyle: { color: '#F56C6C', type: 'dashed' }, label: { formatter: '档位线70%' } }] },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0)' }] } }
      }]
    })
  }
})
</script>
