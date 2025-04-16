<template>
  <div>
    <div v-if="isLoading">로딩 중...</div>
    <ExcelUploader v-else />
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import ExcelUploader from '../components/ExcelUploader.vue'

export default defineComponent({
  name: 'ExcelUploadPage',
  components: {
    ExcelUploader
  },
  setup() {
    const isLoading = ref(true)

    onMounted(() => {
      console.log('ExcelUploadPage mounted')
      console.log('ExcelUploader component:', ExcelUploader)
      isLoading.value = false
    })

    return {
      isLoading
    }
  }
})
</script> 