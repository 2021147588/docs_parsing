<template>
  <div class="q-pa-md">
    <q-card class="document-card">
      <q-card-section class="text-center">
        <div class="text-h5 q-mb-md">문서 내용</div>
        <div class="text-subtitle1 text-grey q-mb-lg">
          {{ currentFileIndex + 1 }}/{{ totalFiles }} 번째 문서
        </div>
      </q-card-section>

      <q-card-section>
        <div v-if="documents.length > 0">
          <div
            v-for="(doc, index) in documents"
            :key="index"
            class="q-mb-lg"
          >
            <div class="text-subtitle1 q-mb-sm">분할 {{ index + 1 }}</div>
            <div class="segment-content">
              <div class="segment-text">
                <template
                  v-for="(word, wordIndex) in highlightTokensInSegment(doc.segment, doc.tokens)"
                  :key="wordIndex"
                >
                  <template v-if="word.highlight">
                    <span
                      class="token"
                      :class="getTextColorClass(word.word_type)"
                      @click="handleTokenClick(word, index)"
                    >
                      {{ word.word }}
                    </span>
                  </template>
                  <template v-else>
                    <span :class="getTextColorClass(word.word_type)">
                      {{ word.word }}
                    </span>
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

      <q-card-actions align="right" class="q-pa-md">
        <q-btn
          color="primary"
          :label="currentFileIndex >= totalFiles - 1 ? '저장' : '다음 문서'"
          :disable="false"
          @click="currentFileIndex >= totalFiles - 1 ? handleSave() : processNextFile()"
        />
      </q-card-actions>
    </q-card>

    <!-- 단어 정보 팝업 -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">{{ wordInfo?.word || wordInfo?.value }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-if="wordInfo">
            <p><strong>유형:</strong> {{ wordInfo.word_type || 'null' }}</p>
            <p><strong>출현 횟수:</strong> {{ wordInfo.total_cnt || 'null' }}</p>
            <p><strong>도메인 수:</strong> {{ wordInfo.domain_cnt || 'null' }}</p>
            <p><strong>문서 수:</strong> {{ wordInfo.doc_cnt || 'null' }}</p>
          </div>
          
          <div class="q-mt-md">
            <div class="text-subtitle1">의미사전 정보</div>
            <div v-if="dictionaryInfo">
              <p><strong>추가 횟수:</strong> {{ dictionaryInfo.total_add_count || 'null' }}</p>
              <p><strong>삭제 횟수:</strong> {{ dictionaryInfo.total_delete_count || 'null' }}</p>
            </div>
            <div v-else>
              <p>의미사전에 등록되지 않음</p>
            </div>
            <div class="q-mt-sm">
              <q-btn 
                color="positive" 
                label="의미사전에 추가" 
                size="sm"
                @click="addToDictionary(wordInfo.word)"
              />
              <q-btn 
                color="negative" 
                label="의미사전에서 삭제" 
                size="sm"
                class="q-ml-sm"
                @click="removeFromDictionary(wordInfo.word)"
              />
            </div>
          </div>
          
          <div class="q-mt-md">
            <div class="text-subtitle1">불용어사전 정보</div>
            <div v-if="stopwordsInfo">
              <p><strong>추가 횟수:</strong> {{ stopwordsInfo.total_add_count || 'null' }}</p>
              <p><strong>삭제 횟수:</strong> {{ stopwordsInfo.total_delete_count || 'null' }}</p>
            </div>
            <div v-else>
              <p>불용어사전에 등록되지 않음</p>
            </div>
            <div class="q-mt-sm">
              <q-btn 
                color="positive" 
                label="불용어사전에 추가" 
                size="sm"
                @click="addToStopwords(wordInfo.word)"
              />
              <q-btn 
                color="negative" 
                label="불용어사전에서 삭제" 
                size="sm"
                class="q-ml-sm"
                @click="removeFromStopwords(wordInfo.word)"
              />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="닫기" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Word Info Modal -->
    <div v-if="showWordInfo" class="word-info-modal">
      <div class="word-info-content">
        <div class="word-info-header">
          <h3>{{ wordInfo.word || wordInfo.value }}</h3>
          <button @click="closeWordInfo" class="close-button">&times;</button>
        </div>
        <div class="word-info-body">
          <div class="word-info-section">
            <h4>단어 정보</h4>
            <p><strong>단어:</strong> {{ wordInfo.word || wordInfo.value }}</p>
            <p><strong>유형:</strong> {{ wordInfo.word_type }}</p>
            <p><strong>출현 횟수:</strong> {{ wordInfo.total_cnt }}</p>
            <p><strong>도메인 수:</strong> {{ wordInfo.domain_cnt }}</p>
            <p><strong>문서 수:</strong> {{ wordInfo.doc_cnt }}</p>
          </div>
          
          <div class="word-info-section">
            <h4>의미사전 정보</h4>
            <p v-if="dictionaryInfo">
              <strong>추가 횟수:</strong> {{ dictionaryInfo.add_count || 0 }}
              <strong>삭제 횟수:</strong> {{ dictionaryInfo.delete_count || 0 }}
            </p>
            <p v-else>의미사전에 등록되지 않음</p>
            <div class="q-mt-sm">
              <q-btn 
                v-if="!dictionaryInfo"
                color="positive" 
                label="의미사전에 추가" 
                size="sm"
                @click="addToDictionary(wordInfo.word)"
              />
              <q-btn 
                v-else
                color="negative" 
                label="의미사전에서 삭제" 
                size="sm"
                @click="removeFromDictionary(wordInfo.word)"
              />
            </div>
          </div>
          
          <div class="word-info-section">
            <h4>불용어사전 정보</h4>
            <p v-if="stopwordsInfo">
              <strong>추가 횟수:</strong> {{ stopwordsInfo.add_count || 0 }}
              <strong>삭제 횟수:</strong> {{ stopwordsInfo.delete_count || 0 }}
            </p>
            <p v-else>불용어사전에 등록되지 않음</p>
            <div class="q-mt-sm">
              <q-btn 
                v-if="!stopwordsInfo"
                color="positive" 
                label="불용어사전에 추가" 
                size="sm"
                @click="addToStopwords(wordInfo.word)"
              />
              <q-btn 
                v-else
                color="negative" 
                label="불용어사전에서 삭제" 
                size="sm"
                @click="removeFromStopwords(wordInfo.word)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default defineComponent({
  name: 'DocumentPage',
  setup() {
    const $q = useQuasar()
    const documents = ref([])
    const filePaths = ref([])
    const currentFileIndex = ref(0)
    const totalFiles = ref(0)
    const currentFilePath = ref('')
    const showDialog = ref(false)
    const wordInfo = ref(null)
    const dictionaryInfo = ref(null)
    const stopwordsInfo = ref(null)
    const route = useRoute()
    const showWordInfo = ref(false)
    const showAddWordModal = ref(false)
    const newWord = ref({
      word: '',
      cate1: '',
      cate2: ''
    })
    const router = useRouter()

    const getTextColorClass = (wordType) => {
      return wordType === '기타' ? 'text-grey' : 'text-black'
    }

    const fetchDocument = async (filePath) => {
      if (!filePath) {
        console.error('파일 경로가 없습니다.')
        return
      }

      try {
        console.log('문서 요청 경로:', filePath)
        const response = await api.post('/token/document', {
          file_path: filePath
        })
        
        if (response.data && response.data.document) {
          // 파일 경로에서 카테고리 정보 추출
          const pathParts = filePath.split('/')
          const cate1 = pathParts[pathParts.length - 2] || null
          const cate2 = null
          
          // 각 문서 세그먼트에 카테고리 정보 추가
          const documentsWithCategories = response.data.document.map(doc => ({
            ...doc,
            cate1,
            cate2,
            tokens: doc.tokens.map(token => ({
              ...token,
              cate1,
              cate2
            }))
          }))
          
          documents.value = documentsWithCategories
          console.log('문서 데이터:', documents.value)
        } else {
          console.error('문서 데이터가 없습니다:', response.data)
          $q.notify({
            color: 'negative',
            message: '문서 데이터가 없습니다.',
            icon: 'error',
            position: 'top',
          })
        }
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

    const saveWordsToDictionaries = async (documents) => {
      try {
        // 모든 토큰을 하나의 배열로 수집
        const allTokens = []
        for (const doc of documents) {
          if (doc.tokens) {
            // 각 토큰에 카테고리 정보 추가
            const tokensWithCategories = doc.tokens.map(token => ({
              ...token,
              cate1: doc.cate1 || null,
              cate2: doc.cate2 || null
            }))
            allTokens.push(...tokensWithCategories)
          }
        }

        // 중복 제거를 위해 Set 사용 (카테고리 정보를 포함하여 비교)
        const uniqueTokens = Array.from(new Set(allTokens.map(token => JSON.stringify({
          word: token.word,
          word_type: token.word_type,
          cate1: token.cate1,
          cate2: token.cate2
        }))))
          .map(str => JSON.parse(str))

        // 일괄 업데이트 요청
        const response = await api.post('/token/document/batch_update', {
          file_path: currentFilePath.value,
          tokens: uniqueTokens
        })

        if (response.data.success) {
          return {
            meaningDictionaryCount: response.data.meaning_count,
            stopwordsCount: response.data.stopwords_count
          }
        } else {
          throw new Error(response.data.message)
        }
      } catch (error) {
        console.error('사전 업데이트 중 오류:', error)
        throw error
      }
    }

    const processNextFile = async () => {
      if (currentFileIndex.value >= filePaths.value.length - 1) {
        return
      }

      // 현재 문서의 단어들을 사전에 저장
      if (documents.value.length > 0) {
        const { meaningDictionaryCount, stopwordsCount } = await saveWordsToDictionaries(documents.value)
        $q.notify({
          color: 'positive',
          message: `의미사전에 ${meaningDictionaryCount}개, 불용어사전에 ${stopwordsCount}개의 단어가 추가되었습니다.`,
          icon: 'check',
          position: 'top',
          timeout: 3000
        })
      }

      currentFileIndex.value++
      const nextFilePath = filePaths.value[currentFileIndex.value]
      currentFilePath.value = nextFilePath
      
      // URL 업데이트
      const encodedPath = encodeURIComponent(nextFilePath)
      window.history.replaceState(
        {}, 
        '', 
        `/document?file_path=${encodedPath}`
      )
      
      await fetchDocument(nextFilePath)
    }

    const fetchDictionaryInfo = async (word) => {
      try {
        const response = await api.get(`/dictionary/search?word=${encodeURIComponent(word)}`)
        if (response.data && response.data.success && response.data.dictionary.length > 0) {
          dictionaryInfo.value = response.data.dictionary[0]
        } else {
          dictionaryInfo.value = null
        }
      } catch (error) {
        console.error('의미사전 정보 조회 중 오류:', error)
        dictionaryInfo.value = null
      }
    }

    const fetchStopwordsInfo = async (word) => {
      try {
        const response = await api.get(`/stopwords/search?word=${encodeURIComponent(word)}`)
        if (response.data && response.data.success && response.data.stopwords.length > 0) {
          stopwordsInfo.value = response.data.stopwords[0]
        } else {
          stopwordsInfo.value = null
        }
      } catch (error) {
        console.error('불용어사전 정보 조회 중 오류:', error)
        stopwordsInfo.value = null
      }
    }

    const handleTokenClick = async (token, segmentIndex) => {
      try {
        console.log('Clicked word:', token, 'in segment:', segmentIndex)
        const response = await api.post('/token/document/word', {
          file_path: currentFilePath.value,
          word: token.word,
          seg_id: segmentIndex+1
        })
        console.log('API response:', response.data)
        wordInfo.value = response.data.document
        dictionaryInfo.value = response.data.meaning_dictionary
        stopwordsInfo.value = response.data.stopwords
        showDialog.value = true
      } catch (error) {
        console.error('Failed to get word info:', error)
      }
    }

    const addToDictionary = async (word) => {
      try {
        console.log('addToDictionary', wordInfo.value.value)
        const response = await api.post('/token/dictionary/add', {
          word: wordInfo.value.value,
          cate1: wordInfo.value.cate1,
          cate2: null
        })
        if (response.data.success) {
          $q.notify({
            color: 'positive',
            message: '의미사전에 단어가 추가되었습니다.',
            icon: 'check',
            position: 'top',
          })
          // Refresh word info
          await handleTokenClick({ word }, currentFileIndex.value)
        } else {
          $q.notify({
            color: 'negative',
            message: response.data.message || '의미사전에 단어를 추가하는 데 실패했습니다.',
            icon: 'error',
            position: 'top',
          })
        }
      } catch (error) {
        console.error('의미사전에 단어 추가 중 오류:', error)
        $q.notify({
          color: 'negative',
          message: '의미사전에 단어를 추가하는 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top',
        })
      }
    }

    const removeFromDictionary = async (word) => {
      try {
        console.log('removeFromDictionary', word)
        const response = await api.post('/token/dictionary/remove', {
          word: wordInfo.value.value,
          cate1: wordInfo.value.cate1,
          cate2: null
        })
        if (response.data.success) {
          $q.notify({
            color: 'positive',
            message: '의미사전에서 단어가 삭제되었습니다.',
            icon: 'check',
            position: 'top',
          })
          // Refresh word info
          await handleTokenClick({ word }, currentFileIndex.value)
        } else {
          $q.notify({
            color: 'negative',
            message: response.data.message || '의미사전에서 단어를 삭제하는 데 실패했습니다.',
            icon: 'error',
            position: 'top',
          })
        }
      } catch (error) {
        console.error('의미사전에서 단어 삭제 중 오류:', error)
        $q.notify({
          color: 'negative',
          message: '의미사전에서 단어를 삭제하는 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top',
        })
      }
    }

    const addToStopwords = async (word) => {
      try {
        console.log('addToStopwords', wordInfo.value.value)
        const response = await api.post('/token/stopwords/add', {
          word: wordInfo.value.value,
          cate1: wordInfo.value.cate1,
          cate2: null
        })
        if (response.data.success) {
          $q.notify({
            color: 'positive',
            message: '불용어사전에 단어가 추가되었습니다.',
            icon: 'check',
            position: 'top',
          })
          // Refresh word info
          await handleTokenClick({ word }, currentFileIndex.value)
        } else {
          $q.notify({
            color: 'negative',
            message: response.data.message || '불용어사전에 단어를 추가하는 데 실패했습니다.',
            icon: 'error',
            position: 'top',
          })
        }
      } catch (error) {
        console.error('불용어사전에 단어 추가 중 오류:', error)
        $q.notify({
          color: 'negative',
          message: '불용어사전에 단어를 추가하는 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top',
        })
      }
    }

    const removeFromStopwords = async (word) => {
      try {
        const response = await api.post('/token/stopwords/remove', {
          word: wordInfo.value.value,
          cate1: wordInfo.value.cate1,
          cate2: null
        })
        if (response.data.success) {
          $q.notify({
            color: 'positive',
            message: '불용어사전에서 단어가 삭제되었습니다.',
            icon: 'check',
            position: 'top',
          })
          // Refresh word info
          await handleTokenClick({ word }, currentFileIndex.value)
        } else {
          $q.notify({
            color: 'negative',
            message: response.data.message || '불용어사전에서 단어를 삭제하는 데 실패했습니다.',
            icon: 'error',
            position: 'top',
          })
        }
      } catch (error) {
        console.error('불용어사전에서 단어 삭제 중 오류:', error)
        $q.notify({
          color: 'negative',
          message: '불용어사전에서 단어를 삭제하는 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top',
        })
      }
    }

    const saveDocument = async () => {
      try {
        // 현재 문서의 단어들을 사전에 저장
        if (documents.value.length > 0) {
          const { meaningDictionaryCount, stopwordsCount } = await saveWordsToDictionaries(documents.value)
          $q.notify({
            color: 'positive',
            message: `의미사전에 ${meaningDictionaryCount}개, 불용어사전에 ${stopwordsCount}개의 단어가 추가되었습니다.`,
            icon: 'check',
            position: 'top',
            timeout: 3000
          })
        }
        
        // 저장 후 메인 페이지로 이동
        window.location.href = '/'
      } catch (error) {
        console.error('문서 저장 중 오류:', error)
        $q.notify({
          color: 'negative',
          message: '문서 저장 중 오류가 발생했습니다.',
          icon: 'error',
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

      for (const token of tokens) {
        let startIndex = 0
        while (true) {
          const idx = segment.indexOf(token.word, startIndex)
          if (idx === -1) break
          matches.push({ 
            index: idx, 
            length: token.word.length, 
            word: token.word,
            word_type: token.word_type 
          })
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
          // 원문의 공백을 유지하면서 텍스트 추가
          const text = segment.slice(cursor, match.index)
          if (text) {
            result.push({
              word: text,
              highlight: false
            })
          }
        }
        result.push({
          word: segment.slice(match.index, match.index + match.length),
          word_type: match.word_type,
          highlight: true
        })
        cursor = match.index + match.length
      }

      if (cursor < segment.length) {
        // 원문의 공백을 유지하면서 텍스트 추가
        const text = segment.slice(cursor)
        if (text) {
          result.push({
            word: text,
            highlight: false
          })
        }
      }

      return result
    }

    const closeWordInfo = () => {
      showDialog.value = false
      wordInfo.value = null
      dictionaryInfo.value = null
      stopwordsInfo.value = null
    }

    // URL 쿼리 파라미터에서 file_path 가져오기
    onMounted(() => {
      const urlParams = new URLSearchParams(window.location.search)
      const encodedPath = urlParams.get('file_path')
      console.log('URL에서 가져온 인코딩된 파일 경로:', encodedPath)
      
      if (encodedPath) {
        // URL 디코딩
        const decodedPath = decodeURIComponent(encodedPath)
        console.log('디코딩된 파일 경로:', decodedPath)
        
        // 모든 파일 경로 가져오기
        const allFilePaths = urlParams.get('all_file_paths')
        if (allFilePaths) {
          try {
            filePaths.value = JSON.parse(decodeURIComponent(allFilePaths))
            totalFiles.value = filePaths.value.length
            console.log('모든 파일 경로:', filePaths.value)
            
            // 현재 파일 경로 설정
            currentFilePath.value = decodedPath
            currentFileIndex.value = filePaths.value.indexOf(decodedPath)
            if (currentFileIndex.value === -1) {
              currentFileIndex.value = 0
            }
            
            fetchDocument(decodedPath)
          } catch (error) {
            console.error('파일 경로 파싱 오류:', error)
            $q.notify({
              color: 'negative',
              message: '파일 경로 처리 중 오류가 발생했습니다.',
              icon: 'error',
              position: 'top',
            })
          }
        } else {
          // 단일 파일 경로만 있는 경우
          currentFilePath.value = decodedPath
          filePaths.value = [decodedPath]
          totalFiles.value = 1
          currentFileIndex.value = 0
          fetchDocument(decodedPath)
        }
      } else {
        console.error('URL에 파일 경로가 없습니다.')
        $q.notify({
          color: 'warning',
          message: '파일 경로가 지정되지 않았습니다.',
          icon: 'warning',
          position: 'top',
        })
      }
    })

    const handleSave = async () => {
      try {
        // 저장 로직 실행
        await saveDocument()
        
        // 성공 메시지 표시
        ElMessage.success('문서가 성공적으로 저장되었습니다.')
        
        // 토큰 페이지로 이동
        router.push('/document/tokens')
      } catch (error) {
        console.error('문서 저장 중 오류:', error)
        ElMessage.error('문서 저장에 실패했습니다.')
      }
    }

    return {
      documents,
      currentFilePath,
      currentFileIndex,
      totalFiles,
      handleTokenClick,
      highlightTokensInSegment,
      showDialog,
      wordInfo,
      dictionaryInfo,
      stopwordsInfo,
      processNextFile,
      getTextColorClass,
      showWordInfo,
      closeWordInfo,
      addToDictionary,
      removeFromDictionary,
      addToStopwords,
      removeFromStopwords,
      saveDocument,
      handleSave
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
  padding: 0;
  border-radius: 4px;
  transition: background-color 0.2s;
  cursor: pointer;
  margin: 0;
}

.token:hover {
  text-decoration: underline;
}

.text-black {
  color: #000000;
}

.text-grey {
  color: #9e9e9e;
}

.text-grey-7 {
  color: #757575;
  font-style: italic;
}

.word-info-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.word-info-content {
  background-color: white;
  border-radius: 8px;
  width: 80%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.word-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.word-info-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.word-info-body {
  padding: 16px;
}

.word-info-section {
  margin-bottom: 20px;
}

.word-info-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.word-info-section p {
  margin: 8px 0;
}

.word-info-section strong {
  margin-right: 8px;
  color: #555;
}
</style>

