<template>
  <div class="q-pa-md">
    <q-card class="document-card">
      <q-card-section class="text-center">
        <div class="text-h5 q-mb-md">문서 내용</div>
      </q-card-section>

      <q-card-section>
        <div v-if="documents.length > 0">
          <div
            v-for="(doc, index) in documents"
            :key="index"
            class="q-mb-lg"
          >
            <div class="text-subtitle1 q-mb-sm">세그먼트 {{ index + 1 }}</div>
            <div class="segment-content">
              <div class="segment-text">
                <template
                  v-for="(word, wordIndex) in highlightTokensInSegment(doc.segment, doc.tokens)"
                  :key="wordIndex"
                >
                  <template v-if="word.highlight">
                    <span
                      class="token noun-token clickable"
                      @click="handleTokenClick(word.text, index, filePath)"
                    >
                      {{ word.text }}
                    </span>
                  </template>
                  <template v-else>
                    {{ word.text }}
                  </template>
                </template>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center text-grey">
          문서를 불러오는 중...
        </div>
      </q-card-section>
    </q-card>

    <!-- 단어 정보 팝업 -->
    <q-dialog v-model="showDialog">
      <q-card style="min-width: 400px">
        <q-card-section class="text-h6">단어 정보</q-card-section>
        <q-card-section v-if="wordInfo">
          <div><strong>단어:</strong> {{ wordInfo.value }}</div>
          <div><strong>유형:</strong> {{ wordInfo.word_type }}</div>
          <div><strong>전체 등장 횟수:</strong> {{ wordInfo.total_cnt }}</div>
          <div><strong>도메인 수:</strong> {{ wordInfo.domain_cnt }}</div>
          <div><strong>문서 수:</strong> {{ wordInfo.doc_cnt }}</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="닫기" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'

export default defineComponent({
  name: 'DocumentPage',
  setup() {
    const $q = useQuasar()
    const documents = ref([])
    const filePath = ref('C:/Users/dblab/parsing/data/공공행정/IGZO 기반의 Charge Trap Flash 메모리 소자 제작 및 메모리 상태 업데이트.pdf')

    const showDialog = ref(false)
    const wordInfo = ref(null)

    const fetchDocument = async () => {
      try {
        const response = await api.post('/token/document', {
          file_path: filePath.value
        })
        documents.value = response.data.document
      } catch (error) {
        console.error('Error fetching document:', error)
        $q.notify({
          color: 'negative',
          message: '문서를 불러오는 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top',
        })
      }
    }

    const handleTokenClick = async (word, seg_id, path) => {
      try {
        const response = await api.post('/token/document/word', {
          file_path: path,
          word: word,
          seg_id: seg_id + 1,
        })
        if (response.data.success && response.data.document.length > 0) {
          wordInfo.value = response.data.document[0]
          showDialog.value = true
        } else {
          $q.notify({
            message: '단어 정보가 없습니다.',
            color: 'warning',
            position: 'top',
          })
        }
      } catch (err) {
        console.error(err)
        $q.notify({
          message: '단어 정보를 불러오는 중 오류가 발생했습니다.',
          color: 'negative',
          position: 'top',
        })
      }
    }

    // 핵심 하이라이팅 함수: segment 안에 token이 포함되어 있으면 분리해서 강조
    const highlightTokensInSegment = (segment, tokens) => {
  const result = []
  let cursor = 0

  // 하이라이트할 모든 위치 추출
  const matches = []

  for (const [tokenText] of tokens) {
    let startIndex = 0
    while (true) {
      const idx = segment.indexOf(tokenText, startIndex)
      if (idx === -1) break
      matches.push({ index: idx, length: tokenText.length, text: tokenText })
      startIndex = idx + 1 // 한 글자씩 이동하며 중복 탐색 허용
    }
  }

  // 겹치는 구간 제거 + 정렬
  matches.sort((a, b) => a.index - b.index)
  const filtered = []
  let lastEnd = -1
  for (const match of matches) {
    if (match.index >= lastEnd) {
      filtered.push(match)
      lastEnd = match.index + match.length
    }
  }

  // 하이라이팅 단어 조각 만들기
  for (const match of filtered) {
    if (match.index > cursor) {
      result.push({
        text: segment.slice(cursor, match.index),
        highlight: false
      })
    }
    result.push({
      text: segment.slice(match.index, match.index + match.length),
      highlight: true
    })
    cursor = match.index + match.length
  }

  if (cursor < segment.length) {
    result.push({
      text: segment.slice(cursor),
      highlight: false
    })
  }

  return result
}
    onMounted(() => {
      fetchDocument()
    })

    return {
      documents,
      filePath,
      handleTokenClick,
      highlightTokensInSegment,
      showDialog,
      wordInfo,
    }
  },
})
</script>

<style scoped>
.document-card {
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.segment-content {
  line-height: 1.6;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.segment-text {
  padding: 8px;
  background: #fff;
  border-radius: 4px;
  font-size: 1.1em;
  white-space: pre-wrap;
  line-height: 1.8;
}

.token {
  display: inline;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.token:hover {
  background-color: rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.noun-token {
  color: #21ba45;
  font-weight: 500;
}

.noun-token:hover {
  background-color: rgba(33, 186, 69, 0.1);
}
</style>
