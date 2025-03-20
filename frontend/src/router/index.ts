// @ts-ignore
import { createRouter, createWebHistory } from 'vue-router'
// @ts-ignore
import type { RouteRecordRaw } from 'vue-router'

// 预加载关键组件，避免懒加载导致的问题
import HomeView from '../views/HomeView.vue'
// 恢复DataSourceView导入
import DataSourceView from '../views/DataSourceView.vue'
import ImportExcelView from '../views/ImportExcelView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: '首页'
    }
  },
  {
    path: '/datasources',
    name: 'datasources',
    // 恢复使用DataSourceView组件
    component: DataSourceView,
    meta: {
      title: '数据源管理'
    }
  },
  {
    path: '/import-excel',
    name: 'import-excel',
    component: ImportExcelView,
    meta: {
      title: '从Excel导入'
    }
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('../views/AnalyticsView.vue'),
    meta: {
      title: '数据分析'
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: {
      title: '数据看板'
    }
  },
  {
    path: '/exports',
    name: 'exports',
    component: () => import('../views/ExportsView.vue'),
    meta: {
      title: '数据导出'
    }
  },
  {
    path: '/add-data',
    name: 'add-data',
    component: () => import('../views/AddDataView.vue'),
    meta: {
      title: '添加数据'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

const router = createRouter({
  // @ts-ignore
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '首页'} - TouchLink`
  console.log('路由跳转:', from.path, '->', to.path)
  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  console.log('路由跳转完成:', to.path)
})

export default router 