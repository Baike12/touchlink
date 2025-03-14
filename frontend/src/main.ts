import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './assets/main.css'

console.log('开始初始化Vue应用')

try {
  // 创建Vue应用实例
  const app = createApp(App)
  console.log('Vue应用创建成功')

  // 注册Pinia状态管理
  app.use(createPinia())
  console.log('Pinia状态管理已加载')

  // 注册Vue Router
  app.use(router)
  console.log('Vue Router已加载')

  // 注册Element Plus
  app.use(ElementPlus)
  console.log('Element Plus已加载')

  // 挂载应用到DOM
  app.mount('#app')
  console.log('Vue应用已挂载到#app元素')
} catch (error) {
  console.error('Vue应用初始化失败:', error)
  document.body.innerHTML += `<div style="color: red; margin: 20px; border: 1px solid red; padding: 10px;">
    <h2>Vue应用初始化失败</h2>
    <pre>${error}</pre>
  </div>`
} 