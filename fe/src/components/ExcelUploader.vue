<template>
  <div class="q-pa-md">
    <!-- 업로드 화면 -->
    <q-card v-if="!isProcessing" class="upload-card">
      <q-card-section class="text-center">
        <div class="text-h5 q-mb-md">엑셀 파일 업로드</div>
        <div class="text-subtitle1 text-grey q-mb-lg">
          엑셀 파일을 선택하고 업로드 버튼을 클릭하세요
        </div>
      </q-card-section>

      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12">
            <q-file
              v-model="selectedFile"
              label="엑셀 파일 선택"
              accept=".xlsx,.xls"
              :max-file-size="10485760"
              @rejected="onRejected"
              outlined
              class="upload-area"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
          </div>
          <div class="col-12">
            <div class="text-center q-mb-md">언어 선택</div>
            <div class="row justify-center q-gutter-md">
              <q-radio v-model="selectedLang" val="kor" label="한국어" />
              <q-radio v-model="selectedLang" val="eng" label="English" />
            </div>
          </div>
          <div class="col-12 text-center">
            <q-btn
              color="primary"
              label="업로드"
              :loading="isUploading"
              :disable="!selectedFile || !selectedLang"
              @click="uploadFile"
            />
          </div>
        </div>
      </q-card-section>

      <q-card-section class="text-center q-pa-none">
        <div class="text-caption text-grey q-pa-md">
          지원되는 파일 형식: .xlsx, .xls (최대 10MB)
        </div>
      </q-card-section>
    </q-card>

    <!-- 문서 처리 화면 -->
    <div v-else>
      <q-card class="document-card">
        <q-card-section class="text-center">
          <div class="text-h5 q-mb-md">문서 처리</div>
          <div class="text-subtitle1 text-grey q-mb-lg">
            {{ currentFileIndex + 1 }}/{{ totalFiles }} 번째 문서
          </div>
        </q-card-section>

        <q-card-section>
          <div v-if="documents.length > 0">
            <div v-for="(doc, index) in documents" :key="index" class="q-mb-lg">
              <div class="text-subtitle1 q-mb-sm">세그먼트 {{ index + 1 }}</div>
              <div class="segment-content">
                <template v-for="(token, tokenIndex) in doc.tokens" :key="tokenIndex">
                  <span
                    :class="{
                      'token': true,
                      'noun-token': token[1] === 'noun',
                      'clickable': true
                    }"
                    @click="handleTokenClick(token)"
                  >
                    {{ token[0] }}
                  </span>
                </template>
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
            label="다음 문서"
            :disable="currentFileIndex >= totalFiles - 1"
            @click="processNextFile"
          />
        </q-card-actions>
      </q-card>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'

export default defineComponent({
  name: 'ExcelUploader',
  setup() {
    const $q = useQuasar()
    const selectedFile = ref(null)
    const selectedLang = ref(null)
    const isUploading = ref(false)
    const isProcessing = ref(false)
    const documents = ref([])
    const currentFileIndex = ref(0)
    const totalFiles = ref(0)
    const filePaths = ref([])

    const processNextFile = async () => {
      if (currentFileIndex.value >= filePaths.value.length) {
        isProcessing.value = false
        return
      }

      try {
        const filePath = filePaths.value[currentFileIndex.value]
        const docResponse = await api.get(`/token/document/${filePath}`)
        documents.value = docResponse.data.document
        currentFileIndex.value++
      } catch (error) {
        console.error(`Error processing document ${filePaths.value[currentFileIndex.value]}:`, error)
        $q.notify({
          color: 'negative',
          message: '문서 처리 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top'
        })
      }
    }

    const uploadFile = async () => {
      if (!selectedFile.value || !selectedLang.value) return

      isUploading.value = true
      const formData = new FormData()
      formData.append('metadata', selectedFile.value)
      formData.append('lang', selectedLang.value)

      try {
        const response = await api.post('/token/upload', formData)
        
        if (response.data.success) {
          // 파일 처리 시작
          filePaths.value = response.data.total_file_path_lists
          totalFiles.value = filePaths.value.length
          currentFileIndex.value = 0
          documents.value = []
          
          // 업로드 성공 알림
          $q.notify({
            color: 'positive',
            message: `${response.data.document_counts}개의 문서가 파싱되었습니다. 생성된 단어는 ${response.data.word_counts}개 입니다.`,
            icon: 'check',
            position: 'top',
            timeout: 5000
          })

          // 처리 상태로 전환
          isProcessing.value = true
          isUploading.value = false
          
          // 첫 번째 문서 처리
          await processNextFile()
        }

        selectedFile.value = null
        selectedLang.value = null
      } catch (error) {
        $q.notify({
          color: 'negative',
          message: '파일 업로드에 실패했습니다.',
          icon: 'error',
          position: 'top'
        })
      } finally {
        if (!isProcessing.value) {
          isUploading.value = false
        }
      }
    }

    const handleTokenClick = (token) => {
      $q.notify({
        message: `단어: ${token[0]}, 타입: ${token[1]}`,
        color: 'info',
        position: 'top'
      })
    }

    const onRejected = (rejectedEntries) => {
      $q.notify({
        color: 'negative',
        message: '지원되지 않는 파일 형식입니다.',
        icon: 'error',
        position: 'top'
      })
    }

    return {
      selectedFile,
      selectedLang,
      isUploading,
      isProcessing,
      documents,
      currentFileIndex,
      totalFiles,
      uploadFile,
      handleTokenClick,
      onRejected,
      processNextFile
    }
  }
})
</script>

<style scoped>
.upload-card, .document-card {
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 20px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #1976D2;
  background: #f0f7ff;
}

.segment-content {
  line-height: 1.6;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.token {
  display: inline-block;
  margin: 0 2px;
  padding: 2px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.token:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.noun-token {
  color: #21BA45;
  font-weight: 500;
}

.noun-token:hover {
  background-color: rgba(33, 186, 69, 0.1);
}
</style>