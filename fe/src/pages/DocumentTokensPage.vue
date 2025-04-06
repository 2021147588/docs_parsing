<template>
  <div class="document-tokens-page">
    <h1>문서 토큰 목록</h1>
    
    <!-- 필터 섹션 -->
    <div class="filters">
      <el-input
        v-model="filters.word"
        placeholder="단어 검색"
        clearable
        @clear="handleFilter"
        @keyup.enter="handleFilter"
      />
      <el-select v-model="filters.word_type" placeholder="품사" clearable @change="handleFilter">
        <el-option label="명사" value="명사" />
        <el-option label="동사" value="동사" />
        <el-option label="형용사" value="형용사" />
        <el-option label="부사" value="부사" />
      </el-select>
      <el-input
        v-model="filters.cate1"
        placeholder="1차 카테고리"
        clearable
        @clear="handleFilter"
        @keyup.enter="handleFilter"
      />
      <el-input
        v-model="filters.cate2"
        placeholder="2차 카테고리"
        clearable
        @clear="handleFilter"
        @keyup.enter="handleFilter"
      />
      <el-button type="primary" @click="handleFilter">검색</el-button>
    </div>
    
    <!-- 토큰 테이블 -->
    <el-table
      v-loading="loading"
      :data="tokens"
      style="width: 100%"
      border
    >
      <el-table-column prop="word" label="단어" width="150" />
      <el-table-column prop="word_type" label="품사" width="100" />
      <el-table-column prop="cate1" label="1차 카테고리" width="150" />
      <el-table-column prop="cate2" label="2차 카테고리" width="150" />
      <el-table-column prop="total_cnt" label="총 개수" width="100" sortable />
      <el-table-column prop="meaning_cnt" label="의미사전 개수" width="120" sortable />
      <el-table-column prop="stopwords_cnt" label="불용어사전 개수" width="120" sortable />
    </el-table>
    
    <!-- 페이지네이션 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const tokens = ref([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = ref({
  word: '',
  word_type: '',
  cate1: '',
  cate2: ''
})

const fetchTokens = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/document/tokens', {
      params: {
        page: currentPage.value,
        per_page: pageSize.value,
        ...filters.value
      }
    })
    
    if (response.data.success) {
      tokens.value = response.data.tokens
      totalCount.value = response.data.total_count
    } else {
      ElMessage.error(response.data.message || '토큰 목록을 불러오는데 실패했습니다.')
    }
  } catch (error) {
    console.error('토큰 목록 조회 중 오류:', error)
    ElMessage.error('토큰 목록을 불러오는데 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  fetchTokens()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchTokens()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchTokens()
}

onMounted(() => {
  fetchTokens()
})
</script>

<style scoped>
.document-tokens-page {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 