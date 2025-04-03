<template>
  <div>
    <ExcelUploader />
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import ExcelUploader from 'components/ExcelUploader.vue'

export default defineComponent({
  name: 'ExcelUploadPage',
  components: {
    ExcelUploader
  }
})
</script> 