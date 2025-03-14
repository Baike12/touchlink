<template>
  <div class="app-container">
    <el-container>
      <el-aside width="220px" class="app-sidebar">
        <div class="logo">
          <h1>TouchLink</h1>
        </div>
        <el-menu
          router
          :default-active="activePath"
          class="app-menu"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <span class="menu-icon">🏠</span>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/add-data">
            <span class="menu-icon">📝</span>
            <span>添加数据</span>
          </el-menu-item>
          <el-menu-item index="/datasources">
            <span class="menu-icon">💾</span>
            <span>数据源</span>
          </el-menu-item>
          <el-menu-item index="/analytics">
            <span class="menu-icon">📊</span>
            <span>分析</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <span class="menu-icon">📈</span>
            <span>看板</span>
          </el-menu-item>
          <el-menu-item index="/exports">
            <span class="menu-icon">📥</span>
            <span>导出</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="app-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-dropdown">
                用户 <span class="dropdown-icon">▼</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人设置</el-dropdown-item>
                  <el-dropdown-item divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activePath = computed(() => route.path)
const pageTitle = computed(() => {
  if (route.meta && route.meta.title) {
    return route.meta.title
  }
  return '页面'
})

// 在组件挂载后执行
onMounted(() => {
  console.log('App.vue组件已挂载')
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
}

.app-sidebar {
  background-color: #001529;
  color: white;
  height: 100vh;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-menu {
  border-right: none;
}

.menu-icon {
  margin-right: 8px;
  font-size: 16px;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.dropdown-icon {
  margin-left: 5px;
  font-size: 12px;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
</style>