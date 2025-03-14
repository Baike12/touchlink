<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎使用 TouchLink 数据分析平台</h1>
      <p class="welcome-description">
        TouchLink 是一个强大的数据分析平台，帮助您从多种数据源加载数据，进行分析并导出结果。
      </p>
    </div>
    
    <div class="features-section">
      <div class="feature-card" @click="navigateTo('/add-data')">
        <div class="feature-icon">📝</div>
        <h3>添加数据</h3>
        <p>创建自定义表格并添加数据</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>数据连接</h3>
        <p>连接多种数据源，包括MySQL、MongoDB、Excel等</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📈</div>
        <h3>数据分析</h3>
        <p>强大的分析工具，帮助您理解数据并获取洞察</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📋</div>
        <h3>可视化看板</h3>
        <p>创建交互式看板，实时监控关键指标</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📤</div>
        <h3>数据导出</h3>
        <p>将分析结果导出为多种格式，方便分享和使用</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 导航到指定路径
const navigateTo = (path: string) => {
  router.push(path)
}

// 在组件挂载后执行
onMounted(() => {
  console.log('HomeView.vue组件已挂载')
})
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin: 20px 0 40px;
  padding: 40px 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.welcome-title {
  font-size: 28px;
  color: #303133;
  margin-bottom: 16px;
}

.welcome-description {
  font-size: 16px;
  color: #606266;
  max-width: 800px;
  margin: 0 auto;
}

.features-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.feature-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 30px 20px;
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px 0 rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 18px;
  color: #303133;
  margin-bottom: 12px;
}

.feature-card p {
  font-size: 14px;
  color: #606266;
}
</style> 