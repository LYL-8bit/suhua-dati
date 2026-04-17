<template>
  <div style="max-width:800px;margin:0 auto">
    <div v-if="!result">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
        <h2>{{ title }}</h2>
        <el-tag>{{ currentIndex + 1 }} / {{ questions.length }}</el-tag>
      </div>

      <el-card v-if="questions.length">
        <div style="font-size:16px;margin-bottom:20px;line-height:1.6">
          {{ currentIndex + 1 }}. {{ currentQ.content }}
        </div>
        <el-radio-group v-model="answers[currentQ.id]" style="display:flex;flex-direction:column;gap:12px">
          <el-radio v-for="opt in currentQ.options" :key="opt" :value="opt[0]" style="height:auto;white-space:normal">
            {{ opt }}
          </el-radio>
        </el-radio-group>
        <div style="display:flex;justify-content:space-between;margin-top:24px">
          <el-button @click="currentIndex--" :disabled="currentIndex === 0">上一题</el-button>
          <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="currentIndex++" :disabled="!answers[currentQ.id]">
            下一题
          </el-button>
          <el-button v-else type="success" @click="submit" :loading="submitting" :disabled="!allAnswered">
            提交作业
          </el-button>
        </div>
      </el-card>

      <!-- 答题进度 -->
      <el-card style="margin-top:16px">
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <el-button
            v-for="(q, i) in questions" :key="q.id"
            :type="answers[q.id] ? 'primary' : 'default'"
            size="small" circle
            @click="currentIndex = i"
          >{{ i + 1 }}</el-button>
        </div>
      </el-card>
    </div>

    <!-- 结果页 -->
    <div v-else>
      <el-result
        :icon="result.accuracy >= 70 ? 'success' : 'warning'"
        :title="result.accuracy >= 70 ? '太棒了！' : '继续加油！'"
        :sub-title="'本次得分：' + result.score + '/' + result.total + '，正确率 ' + result.accuracy + '%'"
      >
        <template #extra>
          <el-button @click="$router.push('/student/home')">返回作业列表</el-button>
          <el-button type="primary" @click="$router.push('/student/wrong-book')">查看错题本</el-button>
        </template>
      </el-result>

      <el-card style="margin-top:20px">
        <template #header>详细解析</template>
        <div v-for="d in result.details" :key="d.question_id" style="margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid #eee">
          <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px">
            <el-icon v-if="d.is_correct" color="#67C23A" size="18"><CircleCheck /></el-icon>
            <el-icon v-else color="#F56C6C" size="18"><CircleClose /></el-icon>
            <span style="font-size:15px">{{ d.content }}</span>
          </div>
          <div style="margin-left:26px">
            <div v-for="opt in d.options" :key="opt" style="padding:4px 0;font-size:14px"
              :style="{color: opt[0] === d.correct_answer ? '#67C23A' : (opt[0] === d.student_answer && !d.is_correct ? '#F56C6C' : '#606266')}">
              {{ opt }}
              <span v-if="opt[0] === d.correct_answer"> ✓</span>
              <span v-if="opt[0] === d.student_answer && !d.is_correct"> ✗（你的答案）</span>
            </div>
            <div v-if="d.explanation" style="margin-top:8px;padding:8px;background:#f0f9eb;border-radius:4px;font-size:13px;color:#67C23A">
              解析：{{ d.explanation }}
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import api from '../../api'

const route = useRoute()
const assignmentId = route.params.id
const title = ref('')
const questions = ref([])
const answers = ref({})
const currentIndex = ref(0)
const result = ref(null)
const submitting = ref(false)

const currentQ = computed(() => questions.value[currentIndex.value] || {})
const allAnswered = computed(() => questions.value.every(q => answers.value[q.id]))

async function submit() {
  submitting.value = true
  try {
    result.value = await api.post('/api/submissions', {
      answers: answers.value,
      assignment_id: parseInt(assignmentId),
    })
  } catch (e) {
    ElMessage.error(typeof e === 'string' ? e : '提交失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const qs = await api.get(`/api/assignments/${assignmentId}/questions`)
  questions.value = qs
  title.value = '作业答题'
})
</script>
