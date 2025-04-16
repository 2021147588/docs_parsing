<template>
  <div class="q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 디렉토리 트리 섹션 -->
      <div class="col-2">
        <q-card class="directory-tree-card">
          <q-card-section>
            <!-- 통계 보기 버튼 -->
            <div class="q-mb-md">
              <q-btn 
                color="primary" 
                label="문서 보기" 
                class="full-width"
                :disable="!selectedNode"
                @click="showStatisticsMode = false"
              />
              <q-btn 
                color="primary" 
                label="통계 보기" 
                class="full-width q-mt-sm"
                :disable="!selectedNode"
                :loading="isStatisticsLoading"
                @click="showStatistics"
              />
              <div v-if="!selectedNode" class="text-caption text-grey q-mt-sm">
                통계를 보려면 먼저 문서를 선택해주세요.
              </div>
            </div>
            <div class="text-h6 q-mb-md">문서 디렉토리</div>
            <!-- 상위 경로 표시 -->
            <div class="path-breadcrumb q-mb-md">
              <template v-for="(part, index) in basePathParts" :key="index">
                <span class="path-part">{{ part }}</span>
                <q-icon v-if="index < basePathParts.length - 1" name="chevron_right" size="xs" class="q-mx-xs" />
              </template>
            </div>
            <!-- 하위 디렉토리 트리 -->
            <div v-if="directoryTree.length > 0">
              <div class="text-subtitle2 q-mb-sm">문서 목록</div>
              <q-tree
                :nodes="directoryTree"
                node-key="id"
                :selected.sync="selectedNode"
                @update:selected="handleNodeSelect"
                default-expand-all
                label-key="label"
                class="directory-tree"
              >
                <template v-slot:default-header="prop">
                  <div class="row items-center">
                    <q-icon :name="prop.node.children ? 'folder' : 'description'" class="q-mr-sm" />
                    {{ prop.node.label }}
                  </div>
                </template>
              </q-tree>
            </div>
            <div v-else class="text-center text-grey">
              로드된 문서가 없습니다.
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 문서 내용 섹션 -->
      <div :class="showStatisticsMode ? 'col-10' : 'col-7'">
        <!-- 통계 보기 모드일 때 -->
        <q-card v-if="showStatisticsMode" class="document-card">
          <q-card-section>
            <div class="text-h5 q-mb-md">문서 통계</div>
            
            <!-- 전체 통계 -->
            <div class="text-h6 q-mb-sm">전체 통계</div>
            <div class="row q-col-gutter-md">
              <div class="col-4">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle2">전체 단어 수</div>
                    <div class="text-h6">{{ statistics.statistics.statistics.total_words }}</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-4">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle2">평균 발생 횟수</div>
                    <div class="text-h6">{{ statistics.statistics.statistics.overall_statistics.average.toFixed(4) }}</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-4">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle2">표준 편차</div>
                    <div class="text-h6">{{ statistics.statistics.statistics.overall_statistics.std_dev.toFixed(4) }}</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- 필터 섹션 -->
            <div class="text-h6 q-mt-md q-mb-sm">필터</div>
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle2 q-mb-sm">평균 발생 횟수 범위</div>
                    <div class="row q-col-gutter-sm">
                      <div class="col-5">
                        <q-input
                          v-model="averageRange.min"
                          type="number"
                          label="최소값"
                          dense
                          outlined
                        />
                      </div>
                      <div class="col-2 text-center q-pt-md">~</div>
                      <div class="col-5">
                        <q-input
                          v-model="averageRange.max"
                          type="number"
                          label="최대값"
                          dense
                          outlined
                        />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-6">
                <q-card flat bordered>
                  <q-card-section>
                    <div class="text-subtitle2 q-mb-sm">표준 편차 범위</div>
                    <div class="row q-col-gutter-sm">
                      <div class="col-5">
                        <q-input
                          v-model="stdDevRange.min"
                          type="number"
                          label="최소값"
                          dense
                          outlined
                        />
                      </div>
                      <div class="col-2 text-center q-pt-md">~</div>
                      <div class="col-5">
                        <q-input
                          v-model="stdDevRange.max"
                          type="number"
                          label="최대값"
                          dense
                          outlined
                        />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </div>

            <!-- 파싱 버튼 -->
            <div class="row justify-end q-mt-md">
              <q-btn
                color="primary"
                label="선택한 범위로 문서 파싱"
                :loading="isParsingLoading"
                @click="parseDocumentWithRange"
              />
            </div>

            <!-- 단어별 통계 -->
            <div class="text-h6 q-mt-md q-mb-sm">단어별 통계</div>
            <q-table
              :rows="wordStatisticsRows"
              :columns="wordStatisticsColumns"
              row-key="word"
              :pagination="{ rowsPerPage: 10 }"
              flat
              bordered
            >
              <template v-slot:body-cell="props">
                <q-td :props="props">
                  <template v-if="props.col.name === 'segment_frequencies'">
                    <div class="segment-frequencies">
                      <div v-for="(freq, segment) in props.value" :key="segment" class="segment-item">
                        <span class="segment-label">{{ segment }}:</span>
                        <span class="segment-value">{{ freq }}</span>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    {{ props.value }}
                  </template>
                </q-td>
              </template>
            </q-table>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat color="primary" label="문서 보기" @click="showStatisticsMode = false" />
          </q-card-actions>
        </q-card>

        <!-- 일반 모드일 때 -->
        <q-card v-else class="document-card">
      <q-card-section class="text-center">
            <div class="text-h5 q-mb-sm file-name-container">
              <div class="file-name" ref="fileNameRef">{{ currentFilePath.split('/').pop() }}</div>
            </div>
            <div class="text-subtitle1 text-grey q-mb-sm">
          {{ currentFileIndex + 1 }}/{{ totalFiles }} 번째 문서
        </div>
            <div class="row justify-end q-mb-md">
              <q-btn
                color="primary"
                label="저장"
                :disable="false"
                @click="handleSave()"
              />
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
                          :class="getTextColorClass(word.word_type, word.dictionary)"
                      @click="handleTokenClick(word, index)"
                    >
                      {{ word.word }}
                    </span>
                  </template>
                  <template v-else>
                        <span :class="getTextColorClass(word.word_type, word.dictionary)">
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
    </q-card>
      </div>

      <!-- 단어 정보 사이드 패널 -->
      <div class="col-3" v-if="!showStatisticsMode && wordInfo">
        <q-card class="word-info-card">
        <q-card-section>
          <div class="text-h6">{{ wordInfo?.word || wordInfo?.value }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-if="wordInfo">
              <p><strong>유형:</strong> {{ wordInfo.word_type || '정보 없음' }}</p>
              <p><strong>출현 횟수:</strong> {{ wordInfo.total_cnt || '정보 없음' }}</p>
              <p><strong>도메인 수:</strong> {{ wordInfo.domain_cnt || '정보 없음' }}</p>
              <p><strong>문서 수:</strong> {{ wordInfo.doc_cnt || '정보 없음' }}</p>
          </div>
          
          <div class="q-mt-md">
              <div class="text-subtitle1 dictionary-title">의미사전 정보</div>
              <div class="dictionary-divider"></div>
              <div v-if="dictionaryInfo" class="dictionary-content">
                <p><strong>추가 횟수:</strong> {{ dictionaryInfo.total_add_count || '정보 없음' }}</p>
                <p><strong>삭제 횟수:</strong> {{ dictionaryInfo.total_delete_count || '정보 없음' }}</p>
            </div>
              <div v-else class="dictionary-empty">
              <p>의미사전에 등록되지 않음</p>
            </div>
          </div>
          
          <div class="q-mt-md">
              <div class="text-subtitle1 dictionary-title">불용어사전 정보</div>
              <div class="dictionary-divider"></div>
              <div v-if="stopwordsInfo" class="dictionary-content">
                <p><strong>추가 횟수:</strong> {{ stopwordsInfo.total_add_count || '정보 없음' }}</p>
                <p><strong>삭제 횟수:</strong> {{ stopwordsInfo.total_delete_count || '정보 없음' }}</p>
            </div>
              <div v-else class="dictionary-empty">
              <p>불용어사전에 등록되지 않음</p>
            </div>
            </div>
            
            <div class="q-mt-md">
              <div class="text-subtitle1 dictionary-title">사전 선택</div>
              <div class="dictionary-divider"></div>
              <div class="dictionary-content">
                <q-radio
                  v-model="selectedDictionary"
                  val="meaning"
                  label="의미사전"
                  class="q-mb-sm"
                />
                <q-radio
                  v-model="selectedDictionary"
                  val="stopwords"
                  label="불용어사전"
                  class="q-mb-sm"
              />
            </div>
          </div>
          
            <div class="q-mt-md">
              <div class="dictionary-actions">
              <q-btn 
                  color="primary" 
                  :label="selectedDictionary === 'meaning' ? '의미사전에 추가' : '불용어사전에 추가'" 
                size="sm"
                  @click="handleDictionaryAction('add')"
              />
              <q-btn 
                color="negative" 
                  :label="selectedDictionary === 'meaning' ? '의미사전에서 삭제' : '불용어사전에서 삭제'" 
                size="sm"
                  class="q-ml-sm"
                  @click="handleDictionaryAction('remove')"
              />
            </div>
          </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, watch, nextTick, computed } from 'vue'
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
    const selectedDictionary = ref('meaning')
    
    // 색상 선택 관련 변수
    const selectedMeaningColor = ref('black')
    const selectedStopwordsColor = ref('grey')
    
    // 의미사전 색상 옵션
    const meaningColors = [
      { name: '검정', value: 'black' },
      { name: '파랑', value: 'blue' },
      { name: '초록', value: 'green' },
      { name: '빨강', value: 'red' },
      { name: '보라', value: 'purple' },
      { name: '주황', value: 'orange' }
    ]
    
    // 불용어사전 색상 옵션
    const stopwordsColors = [
      { name: '회색', value: 'grey' },
      { name: '연한 파랑', value: 'light-blue' },
      { name: '연한 초록', value: 'light-green' },
      { name: '연한 빨강', value: 'light-red' },
      { name: '연한 보라', value: 'light-purple' },
      { name: '연한 주황', value: 'light-orange' },
      { name: '연한 노랑', value: 'light-yellow' }
    ]

    const directoryTree = ref([])
    const selectedNode = ref(null)
    const basePathParts = ref([])

    const getTextColorClass = (wordType, dictionary) => {
      if (dictionary === 'stopwords') {
        return 'text-white'
      } else if (dictionary === 'meaning') {
        return 'text-blue'
      } else if (dictionary === 'both') {
        return 'text-red'
      } else if(dictionary === 'other') {
        return 'text-black'
      }
    }

    const fetchDocument = async (filePath) => {
      if (!filePath) {
        console.error('파일 경로가 없습니다.')
        return
      }

      try {
        console.log('Fetching document for path:', filePath)
        const response = await api.post('/token/document', {
          file_path: filePath
        })
        
        console.log('API 응답 데이터:', response.data)
        console.log('문서 데이터:', response.data.document)
        
        if (response.data && response.data.document) {
          // 파일 경로에서 카테고리 정보 추출
          const pathParts = filePath.split('/')
          const cate1 = pathParts[pathParts.length - 2] || null
          const cate2 = null
          
          // 각 문서 세그먼트에 카테고리 정보 추가
          const documentsWithCategories = response.data.document.map(doc => {
            console.log('세그먼트 데이터:', doc)
            return {
            ...doc,
            cate1,
            cate2,
              tokens: doc.tokens ? doc.tokens.map(token => ({
              ...token,
              cate1,
                cate2,
                highlight: true
              })) : []
            }
          })
          
          documents.value = documentsWithCategories
          console.log('처리된 문서 데이터:', documents.value)

          // 문서 로드 후 토큰 클릭 이벤트 재설정
          nextTick(() => {
            const tokens = document.querySelectorAll('.token')
            tokens.forEach(token => {
              token.style.cursor = 'pointer'
              token.addEventListener('click', (e) => {
                const word = e.target.textContent
                const segmentIndex = Array.from(e.target.parentElement.parentElement.parentElement.children)
                  .indexOf(e.target.parentElement.parentElement)
                handleTokenClick({ word }, segmentIndex)
              })
            })
          })
        } else {
          console.error('문서 데이터가 없습니다:', response.data)
          ElMessage({
            type: 'error',
            message: '문서 데이터가 없습니다.',
            duration: 3000
          })
        }
      } catch (error) {
        console.error('문서 가져오기 실패:', error)
        console.error('에러 응답:', error.response?.data)
        ElMessage({
          type: 'error',
          message: '문서를 불러오는 중 오류가 발생했습니다.',
          duration: 3000
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

    const handleSave = async () => {
      try {
        // 현재 문서의 단어들을 사전에 저장
        if (documents.value.length > 0) {
          const { meaningDictionaryCount, stopwordsCount } = await saveWordsToDictionaries(documents.value)
          ElMessage({
            type: 'success',
            message: `의미사전에 ${meaningDictionaryCount}개, 불용어사전에 ${stopwordsCount}개의 단어가 추가되었습니다.`,
            duration: 3000
          })
        }
      } catch (error) {
        console.error('문서 저장 중 오류:', error)
        ElMessage({
          type: 'error',
          message: '문서 저장 중 오류가 발생했습니다.',
          duration: 3000
        })
      }
    }

    // 핵심 하이라이팅 함수: segment 안에 token이 포함되어 있으면 분리해서 강조
    const highlightTokensInSegment = (segment, tokens) => {
      if (!segment || !tokens) {
        console.warn('segment or tokens is undefined:', { segment, tokens })
        return []
      }

      const result = []
      let cursor = 0

      // 하이라이트할 모든 위치 추출
      const matches = []

      for (const token of tokens) {
        if (!token.word) {
          console.warn('token.word is undefined:', token)
          continue
        }

        let startIndex = 0
        while (true) {
          const idx = segment.indexOf(token.word, startIndex)
          if (idx === -1) break
          matches.push({ 
            index: idx, 
            length: token.word.length, 
            word: token.word,
            word_type: token.word_type,
            dictionary: token.dictionary,
            highlight: true
          })
          startIndex = idx + 1
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
          dictionary: match.dictionary,
          highlight: true
        })
        cursor = match.index + match.length
      }

      if (cursor < segment.length) {
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

    // Watch for changes in wordInfo to update selectedDictionary
    watch(wordInfo, (newWordInfo) => {
      if (newWordInfo) {
        // Check if the word exists in either dictionary
        if (dictionaryInfo.value) {
          selectedDictionary.value = 'meaning'
        } else if (stopwordsInfo.value) {
          selectedDictionary.value = 'stopwords'
        } else {
          // Default to meaning dictionary if not in either
          selectedDictionary.value = 'meaning'
        }
      }
    })

    const handleDictionaryAction = async (action) => {
      try {
        const word = wordInfo.value?.word || wordInfo.value?.value
        if (!word) return
        console.log('handleDictionaryAction', word, wordInfo.value)
        let response

        // 삭제 작업 전에 해당 사전에 단어가 존재하는지 확인
        if (action === 'remove') {
          if (selectedDictionary.value === 'meaning' && !dictionaryInfo.value) {
            ElMessage({
              type: 'error',
              message: '의미사전에 존재하지 않는 단어입니다.',
              duration: 3000
            })
            return
          } else if (selectedDictionary.value === 'stopwords' && !stopwordsInfo.value) {
            ElMessage({
              type: 'error',
              message: '불용어사전에 존재하지 않는 단어입니다.',
              duration: 3000
            })
            return
          }
        }

        if (selectedDictionary.value === 'meaning') {
          if (action === 'add') {
            response = await api.post('/token/dictionary/add', {
              word: word,
              cate1: wordInfo.value.cate1,
              cate2: null
            })
          } else {
            response = await api.post('/token/dictionary/remove', {
              word: word,
              cate1: wordInfo.value.cate1,
              cate2: null
            })
          }
        } else {
          if (action === 'add') {
            response = await api.post('/token/stopwords/add', {
              word: word,
              cate1: wordInfo.value.cate1,
              cate2: null
            })
          } else {
            response = await api.post('/token/stopwords/remove', {
              word: word,
              cate1: wordInfo.value.cate1,
              cate2: null
            })
          }
        }

        if (response.data.success) {
          // Update the token's dictionary in the current document
          if (documents.value.length > 0) {
            for (const doc of documents.value) {
              if (doc.tokens) {
                for (const token of doc.tokens) {
                  if (token.word === word) {
                    if (action === 'add') {
                      token.dictionary = selectedDictionary.value
                    } else {
                      token.dictionary = null
                    }
                    console.log('Updated token:', token)
                  }
                }
              }
            }
          }

          ElMessage({
            type: 'success',
            message: `${selectedDictionary.value === 'meaning' ? '의미사전' : '불용어사전'}에서 단어가 ${action === 'add' ? '추가' : '삭제'}되었습니다.`,
            duration: 3000
          })

          // Refresh word info
          await handleTokenClick({ word }, currentFileIndex.value)
        } else {
          ElMessage({
            type: 'error',
            message: response.data.message || `사전 ${action === 'add' ? '추가' : '삭제'}에 실패했습니다.`,
            duration: 3000
          })
        }
      } catch (error) {
        console.error('사전 작업 중 오류:', error)
        ElMessage({
          type: 'error',
          message: '사전 작업 중 오류가 발생했습니다.',
          duration: 3000
        })
      }
    }

    // 디렉토리 트리 데이터 생성
    const createDirectoryTree = (paths) => {
      console.log('Creating directory tree with paths:', paths)
      
      // paths가 배열이 아닌 경우 빈 배열로 처리
      if (!paths || !Array.isArray(paths)) {
        console.error('Invalid paths:', paths)
        return []
      }

      const tree = []
      const pathMap = new Map()

      // 모든 파일 경로를 순회하며 트리 구조 생성
      paths.forEach(filePath => {
        if (!filePath) return  // 빈 경로는 건너뛰기
        
        const parts = filePath.split('/')
        let currentPath = ''
        let parentNode = null
        
        // /data 폴더까지의 경로를 저장
        const dataIndex = parts.findIndex(part => part === 'data')
        if (dataIndex !== -1) {
          basePathParts.value = parts.slice(0, dataIndex + 1)
          
          // /data 이후의 경로로 트리 생성
          const subParts = parts.slice(dataIndex + 1)
          if (subParts.length > 0) {
            subParts.forEach((part, index) => {
              currentPath += (index === 0 ? '' : '/') + part
              
              if (!pathMap.has(currentPath)) {
                const node = {
                  id: currentPath,
                  label: part,
                  path: currentPath,
                  children: []
                }
                
                if (index === 0) {
                  tree.push(node)
                } else if (parentNode) {
                  parentNode.children.push(node)
                }
                
                pathMap.set(currentPath, node)
                parentNode = node
              } else {
                parentNode = pathMap.get(currentPath)
              }
            })
          }
        } else {
          // /data 폴더가 없는 경우 전체 경로를 트리로 표시
          basePathParts.value = []
          parts.forEach((part, index) => {
            currentPath += (index === 0 ? '' : '/') + part
            
            if (!pathMap.has(currentPath)) {
              const node = {
                id: currentPath,
                label: part,
                path: currentPath,
                children: []
              }
              
              if (index === 0) {
                tree.push(node)
              } else if (parentNode) {
                parentNode.children.push(node)
              }
              
              pathMap.set(currentPath, node)
              parentNode = node
            } else {
              parentNode = pathMap.get(currentPath)
            }
          })
        }
      })

      return tree
    }

    // 노드 선택 핸들러
    const handleNodeSelect = (nodeId) => {
      console.log('노드 선택됨:', nodeId)
      
      if (nodeId === 'root') {
        console.log('루트 노드 선택 무시')
        return
      }
      
      const node = findNodeById(directoryTree.value, nodeId)
      console.log('찾은 노드:', node)
      
      if (node && node.path) {
        console.log('현재 파일 경로:', currentFilePath.value)
        console.log('새 파일 경로:', node.path)
        
        // 현재 파일 경로와 다른 경우에만 처리
        if (node.path !== currentFilePath.value) {
          console.log('새 문서 로드 시작')
          currentFilePath.value = node.path
          fetchDocument(node.path)
          
          // 통계 모드가 활성화되어 있다면 비활성화
          if (showStatisticsMode.value) {
            console.log('통계 모드 비활성화')
            showStatisticsMode.value = false
          }
        } else {
          console.log('동일한 문서 선택됨, 무시')
        }
      } else {
        console.log('유효하지 않은 노드:', node)
      }
    }

    // 노드 ID로 노드 찾기
    const findNodeById = (nodes, id) => {
      console.log('노드 찾기 시작:', { nodes, id })
      
      for (const node of nodes) {
        if (node.id === id) {
          console.log('노드 찾음:', node)
          return node
        }
        if (node.children && node.children.length > 0) {
          const found = findNodeById(node.children, id)
          if (found) {
            console.log('하위 노드에서 찾음:', found)
            return found
          }
        }
      }
      console.log('노드를 찾지 못함')
      return null
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
            const parsedPaths = JSON.parse(decodeURIComponent(allFilePaths))
            // parsedPaths가 배열이 아닌 경우 배열로 변환
            filePaths.value = Array.isArray(parsedPaths) ? parsedPaths : [parsedPaths]
            totalFiles.value = filePaths.value.length
            console.log('모든 파일 경로:', filePaths.value)
            
            // 현재 파일 경로 설정
            currentFilePath.value = decodedPath
            currentFileIndex.value = filePaths.value.indexOf(decodedPath)
            if (currentFileIndex.value === -1) {
              currentFileIndex.value = 0
            }
            
            // 디렉토리 트리 생성
            directoryTree.value = createDirectoryTree(filePaths.value)
            // 현재 파일 노드 선택
            selectedNode.value = decodedPath
            
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
          filePaths.value = [decodedPath]  // 배열로 설정
          totalFiles.value = 1
          currentFileIndex.value = 0
          
          // 디렉토리 트리 생성
          directoryTree.value = createDirectoryTree(filePaths.value)
          // 현재 파일 노드 선택
          selectedNode.value = decodedPath
          
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

    const fileNameRef = ref(null)

    // 파일 이름 크기 조정 함수
    const adjustFileNameSize = () => {
      nextTick(() => {
        const container = fileNameRef.value?.parentElement
        const text = fileNameRef.value
        if (!container || !text) return

        const containerWidth = container.offsetWidth
        const textWidth = text.scrollWidth
        const currentFontSize = parseFloat(window.getComputedStyle(text).fontSize)
        
        if (textWidth > containerWidth) {
          const newFontSize = (containerWidth / textWidth) * currentFontSize
          text.style.fontSize = `${newFontSize}px`
        } else {
          text.style.fontSize = ''
        }
      })
    }

    // 파일 이름이 변경될 때마다 크기 조정
    watch(currentFilePath, () => {
      adjustFileNameSize()
    })

    // 창 크기가 변경될 때마다 크기 조정
    onMounted(() => {
      window.addEventListener('resize', adjustFileNameSize)
      adjustFileNameSize()
    })

    const showStatisticsMode = ref(false)
    const isStatisticsLoading = ref(false)
    const statistics = ref({
      statistics: {
        statistics: {
          overall_statistics: {
            average: 0,
            std_dev: 0
          },
          total_words: 0,
          word_types: {},
          word_statistics: {}
        }
      }
    })

    const wordStatisticsColumns = [
      { name: 'word', label: '단어', field: 'word', align: 'left' },
      // { name: 'word_type', label: '품사', field: 'word_type', align: 'left' },
      { name: 'total_cnt', label: '총 발생', field: 'total_cnt', align: 'center' },
      { name: 'doc_cnt', label: '문서 내 발생 횟수', field: 'doc_cnt', align: 'center' },
      { name: 'cate1_cnt', label: '카테고리1 발생 횟수', field: 'cate1_cnt', align: 'center' },
      { name: 'cate2_cnt', label: '카테고리2 발생 횟수', field: 'cate2_cnt', align: 'center' },
      { name: 'average', label: '문서 내 분할별 평균', field: 'average', align: 'center' },
      { name: 'std_dev', label: '문서 내 분할별 표준편차', field: 'std_dev', align: 'center' },
      // { name: 'segment_frequencies', label: '분할별 발생', field: 'segment_frequencies', align: 'left' }
    ]

    const averageRange = ref({
      min: 0,
      max: 100
    })

    const stdDevRange = ref({
      min: 0,
      max: 100
    })

    const wordStatisticsRows = computed(() => {
      if (!statistics.value?.statistics?.statistics?.word_statistics) return []
      
      return Object.entries(statistics.value.statistics.statistics.word_statistics)
        .map(([word, stats]) => ({
          word,
          ...stats,
          average: stats.average?.toFixed(4) || '0.0000',
          std_dev: stats.std_dev?.toFixed(4) || '0.0000'
        }))
        .filter(row => {
          const avg = parseFloat(row.average)
          const std = parseFloat(row.std_dev)
          return avg >= averageRange.value.min && 
                 avg <= averageRange.value.max && 
                 std >= stdDevRange.value.min && 
                 std <= stdDevRange.value.max
        })
    })

    const showStatistics = async () => {
      console.log('통계 보기 버튼 클릭됨')
      console.log('현재 선택된 노드:', selectedNode.value)
      
      if (!selectedNode.value) {
        console.log('선택된 노드가 없음')
        ElMessage({
          type: 'warning',
          message: '통계를 볼 문서를 선택해주세요.',
          duration: 3000
        })
        return
      }

      try {
        isStatisticsLoading.value = true
        if (selectedNode.value) {
          console.log('API 요청 시작:', selectedNode.value)
          const response = await api.post('/token/document/statistics', {
            file_path: selectedNode.value
          })
          console.log('API 응답:', response.data)
          
          if (response.data.success) {
            console.log('통계 데이터 설정 전:', statistics.value)
            statistics.value = response.data
            console.log('통계 데이터 설정 후:', statistics.value)
            
            console.log('통계 모드 활성화 전:', showStatisticsMode.value)
            showStatisticsMode.value = true
            console.log('통계 모드 활성화 후:', showStatisticsMode.value)
          } else {
            console.log('API 응답 실패:', response.data)
            ElMessage({
              type: 'error',
              message: '통계 데이터를 가져오는데 실패했습니다.',
              duration: 3000
            })
          }
        }
      } catch (error) {
        console.error('통계 데이터 가져오기 오류:', error)
        console.error('에러 상세:', error.response?.data)
        ElMessage({
          type: 'error',
          message: '통계 데이터를 가져오는 중 오류가 발생했습니다.',
          duration: 3000
        })
      } finally {
        isStatisticsLoading.value = false
      }
    }

    const isParsingLoading = ref(false)

    const parseDocumentWithRange = async () => {
      try {
        isParsingLoading.value = true
        const response = await api.post('/token/document/parse_with_range', {
          file_path: selectedNode.value,
          average_range: {
            min: averageRange.value.min,
            max: averageRange.value.max
          },
          std_dev_range: {
            min: stdDevRange.value.min,
            max: stdDevRange.value.max
          }
        })

        if (response.data.success) {
          ElMessage({
            type: 'success',
            message: '문서가 성공적으로 파싱되었습니다.',
            duration: 3000
          })
          // 문서 새로고침
          fetchDocument(selectedNode.value)
        } else {
          ElMessage({
            type: 'error',
            message: response.data.message || '문서 파싱에 실패했습니다.',
            duration: 3000
          })
        }
      } catch (error) {
        console.error('문서 파싱 중 오류:', error)
        ElMessage({
          type: 'error',
          message: '문서 파싱 중 오류가 발생했습니다.',
          duration: 3000
        })
      } finally {
        isParsingLoading.value = false
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
      getTextColorClass,
      showWordInfo,
      closeWordInfo,
      addToDictionary,
      removeFromDictionary,
      addToStopwords,
      removeFromStopwords,
      handleSave,
      selectedDictionary,
      handleDictionaryAction,
      selectedMeaningColor,
      selectedStopwordsColor,
      meaningColors,
      stopwordsColors,
      directoryTree,
      selectedNode,
      handleNodeSelect,
      basePathParts,
      fileNameRef,
      showStatisticsMode,
      statistics,
      wordStatisticsColumns,
      wordStatisticsRows,
      showStatistics,
      isStatisticsLoading,
      averageRange,
      stdDevRange,
      isParsingLoading,
      parseDocumentWithRange
    }
  },
})
</script>

<style scoped>
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
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
