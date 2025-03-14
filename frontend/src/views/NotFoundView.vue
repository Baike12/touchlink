<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="not-found-code">404</h1>
      <h2 class="not-found-title">页面不存在</h2>
      <p class="not-found-message">
        抱歉，您访问的页面不存在或已被移除。
      </p>
      <el-button type="primary" @click="goHome">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 500px;
}

.not-found-content {
  text-align: center;
}

.not-found-code {
  font-size: 120px;
  color: #409EFF;
  margin: 0;
  line-height: 1.2;
}

.not-found-title {
  font-size: 32px;
  color: #303133;
  margin: 20px 0;
}

.not-found-message {
  font-size: 16px;
  color: #606266;
  margin-bottom: 30px;
}
</style> 