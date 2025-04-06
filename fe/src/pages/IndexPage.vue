<template>
  <div class="q-pa-md">
    <q-card class="upload-card">
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
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useQuasar } from 'quasar'
import { api } from '../boot/axios'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'IndexPage',
  setup() {
    const $q = useQuasar()
    const router = useRouter()
    const selectedFile = ref(null)
    const selectedLang = ref(null)
    const isUploading = ref(false)

    const uploadFile = async () => {
      if (!selectedFile.value || !selectedLang.value) return

      isUploading.value = true
      const formData = new FormData()
      formData.append('metadata', selectedFile.value)
      formData.append('lang', selectedLang.value)

      try {
        const response = await api.post('/token/upload', formData)
        
        if (response.data.success) {
          console.log('업로드 성공:', response.data)
          
          // 파일 경로 처리
          const filePaths = response.data.total_file_path_lists
          if (filePaths && filePaths.length > 0) {
            const firstFilePath = filePaths[0]
            console.log('첫 번째 파일 경로:', firstFilePath)
            
            // 파일 경로 인코딩
            const encodedFilePath = encodeURIComponent(firstFilePath)
            const allFilePathsJson = JSON.stringify(filePaths)
            const encodedAllFilePaths = encodeURIComponent(allFilePathsJson)
            
            // DocumentPage로 이동
            window.location.href = `/document?file_path=${encodedFilePath}&all_file_paths=${encodedAllFilePaths}`
          }

          selectedFile.value = null
          selectedLang.value = null
        }
      } catch (error) {
        console.error('파일 업로드 중 오류가 발생했습니다:', error)
        $q.notify({
          color: 'negative',
          message: '파일 업로드 중 오류가 발생했습니다.',
          icon: 'error',
          position: 'top',
        })
      } finally {
        isUploading.value = false
      }
    }

    const onRejected = (rejectedEntries) => {
      console.log('지원되지 않는 파일 형식입니다.')
    }

    return {
      selectedFile,
      selectedLang,
      isUploading,
      uploadFile,
      onRejected
    }
  }
})
</script>

<style scoped>
.upload-card {
  max-width: 600px;
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
</style> 