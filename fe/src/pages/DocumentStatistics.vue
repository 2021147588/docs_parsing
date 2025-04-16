<template>
  <div class="q-pa-md">
    <q-card class="statistics-card">
      <q-card-section>
        <div class="text-h5 q-mb-md">문서 통계</div>
        
        <!-- 전체 통계 -->
        <div class="text-h6 q-mb-sm">전체 통계</div>
        <div class="row q-col-gutter-md">
          <div class="col-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">전체 토큰 수</div>
                <div class="text-h6">{{ statistics.total_tokens }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 분할별 통계 -->
        <div class="text-h6 q-mt-md q-mb-sm">분할별 통계</div>
        <div class="row q-col-gutter-md">
          <div v-for="(segment, id) in statistics.segments" :key="id" class="col-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">분할 {{ id }}</div>
                <div class="text-h6">{{ segment.token_count }} 토큰</div>
                <div class="text-caption">고유 토큰: {{ segment.unique_tokens.length }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 카테고리별 통계 -->
        <div class="text-h6 q-mt-md q-mb-sm">카테고리별 통계</div>
        <div class="row q-col-gutter-md">
          <div v-for="(category, name) in statistics.categories" :key="name" class="col-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">{{ name }}</div>
                <div class="text-h6">{{ category.token_count }} 토큰</div>
                <div class="text-caption">고유 토큰: {{ category.unique_tokens.length }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 도메인별 통계 -->
        <div class="text-h6 q-mt-md q-mb-sm">도메인별 통계</div>
        <div class="row q-col-gutter-md">
          <div v-for="(domain, name) in statistics.domains" :key="name" class="col-4">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle2">{{ name }}</div>
                <div class="text-h6">{{ domain.token_count }} 토큰</div>
                <div class="text-caption">고유 토큰: {{ domain.unique_tokens.length }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat color="primary" label="돌아가기" @click="goBack" />
      </q-card-actions>
    </q-card>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'DocumentStatistics',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const statistics = ref({})
    const statisticsData = ref({})
    const currentFilePath = ref('')

    onMounted(() => {
      // localStorage에서 데이터 읽기
      const statistics = localStorage.getItem('documentStatistics')
      const filePath = localStorage.getItem('documentPath')
      
      if (statistics && filePath) {
        try {
          statisticsData.value = JSON.parse(statistics)
          currentFilePath.value = filePath
          
          // 데이터 사용 후 localStorage에서 삭제
          localStorage.removeItem('documentStatistics')
          localStorage.removeItem('documentPath')
        } catch (error) {
          console.error('통계 데이터 파싱 오류:', error)
          ElMessage({
            type: 'error',
            message: '통계 데이터를 불러오는 중 오류가 발생했습니다.',
            duration: 3000
          })
        }
      } else {
        ElMessage({
          type: 'warning',
          message: '통계 데이터를 찾을 수 없습니다.',
          duration: 3000
        })
      }
    })

    const goBack = () => {
      router.back()
    }

    return {
      statistics,
      goBack
    }
  }
})
</script>

<style scoped>
.statistics-card {
  max-width: 1200px;
  margin: 0 auto;
}

.text-h6 {
  font-size: 1.1rem;
  font-weight: 500;
}

.text-subtitle2 {
  font-size: 0.9rem;
  color: #666;
}

.text-caption {
  font-size: 0.8rem;
  color: #999;
}
</style> 