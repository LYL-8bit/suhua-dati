<template>
  <div>
    <h2 style="margin-bottom:20px">错题本</h2>
    <el-empty v-if="wrongs.length === 0" description="暂无错题，继续保持！" />
    <div v-for="w in wrongs" :key="w.wrong_id" style="margin-bottom:16px">
      <el-card>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
          <span style="font-size:15px;line-height:1.6">{{ w.content }}</span>
          <el-tag type="danger" size="small">错了 {{ w.wrong_count }} 次</el-tag>
        </div>
        <el-radio-group :model-value="w.answer" style="display:flex;flex-direction:column;gap:8px">
          <el-radio v-for="opt in w.options" :key="opt" :value="opt[0]" disabled
            :style="{color: opt[0] === w.answer ? '#67C23A' : '#606266'}">
            {{ opt }}{{ opt[0] === w.answer ? ' ✓（正确答案）' : '' }}
          </el-radio>
        </el-radio-group>
        <div v-if="w.explanation" style="margin-top:12px;padding:10px;background:#f0f9eb;border-radius:4px;font-size:13px;color:#67C23A">
          解析：{{ w.explanation }}
        </div>
        <div style="margin-top:8px">
          <el-tag v-for="t in (w.tags||[])" :key="t" size="small" style="margin-right:4px">{{ t }}</el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const wrongs = ref([])
onMounted(async () => {
  wrongs.value = await api.get('/api/submissions/wrong-answers')
})
</script>
