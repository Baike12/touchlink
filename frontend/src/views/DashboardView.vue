<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1 class="page-title">数据看板</h1>
      <p class="page-description">
        创建交互式看板，以可视化方式展示您的数据和分析结果。
      </p>
    </div>
    
    <div class="card-container">
      <!-- 图表列表 -->
      <el-card v-if="!currentDashboard && !fullscreenChart">
        <template #header>
          <div class="card-header">
            <span>我的图表</span>
            <div>
              <el-button type="primary" @click="goToAnalytics">
                <el-icon><Plus /></el-icon> 创建图表
              </el-button>
              <el-button type="success" @click="refreshRecentCharts">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
          </div>
        </template>
        
        <div v-if="recentCharts.length === 0" class="empty-state">
          <el-empty description="暂无图表" />
          <el-button type="primary" @click="goToAnalytics">创建第一个图表</el-button>
        </div>
        
        <el-row :gutter="20" v-else>
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="chart in recentCharts" :key="chart.id">
            <el-card class="chart-card" shadow="hover" @click="viewFullscreenChart(chart)">
              <div class="chart-preview">
                <component
                  :is="getChartComponent(chart.type)"
                  :chart-data="chartDataMap[chart.id] || []"
                  :chart-options="getChartOptions(chart)"
                />
              </div>
              <p class="chart-meta">类型: {{ getChartTypeName(chart.type) }} | 创建于: {{ formatDate(chart.created_at) }}</p>
            </el-card>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 全屏图表显示 -->
      <div v-if="fullscreenChart" class="fullscreen-chart">
        <div class="fullscreen-header">
          <div class="fullscreen-title">
            <h2>{{ fullscreenChart.title }}</h2>
            <p>{{ fullscreenChart.description || '无描述' }}</p>
          </div>
          <div class="fullscreen-actions">
            <el-button @click="exitFullscreen">
              <el-icon><Back /></el-icon> 返回列表
            </el-button>
          </div>
        </div>
        
        <div class="fullscreen-content">
          <component
            :is="getChartComponent(fullscreenChart.type)"
            :chart-data="chartDataMap[fullscreenChart.id] || []"
            :chart-options="getChartOptions(fullscreenChart)"
          />
        </div>
      </div>
      
      <!-- 看板详情 -->
      <div v-if="currentDashboard" class="dashboard-detail">
        <div class="dashboard-header">
          <div class="dashboard-title">
            <h2>{{ currentDashboard.title }}</h2>
            <p>{{ currentDashboard.description }}</p>
          </div>
          <div class="dashboard-actions">
            <el-button @click="backToDashboardList">
              <el-icon><Back /></el-icon> 返回列表
            </el-button>
            <el-button type="primary" @click="showAddChartDialog">
              <el-icon><Plus /></el-icon> 添加图表
            </el-button>
            <el-button type="success" @click="saveDashboardLayout">
              <el-icon><Check /></el-icon> 保存布局
            </el-button>
          </div>
        </div>
        
        <div class="dashboard-grid">
          <el-empty v-if="currentDashboard.items.length === 0" description="看板中暂无图表" />
          
          <grid-layout
            v-else
            :layout="gridLayout"
            :col-num="12"
            :row-height="30"
            :is-draggable="true"
            :is-resizable="true"
            :vertical-compact="true"
            :use-css-transforms="true"
            @layout-updated="onLayoutUpdated"
          >
            <grid-item
              v-for="item in currentDashboard.items"
              :key="item.id"
              :x="item.position_x"
              :y="item.position_y"
              :w="item.width"
              :h="item.height"
              :i="item.id"
              drag-allow-from=".chart-drag-handle"
              drag-ignore-from=".chart-actions"
            >
              <div class="chart-container">
                <div class="chart-header">
                  <div class="chart-drag-handle">
                    <el-icon><Rank /></el-icon>
                    <span>{{ item.chart.title }}</span>
                  </div>
                  <div class="chart-actions">
                    <el-button type="text" @click="viewFullscreenChart({
                      ...item.chart,
                      created_at: item.chart.created_at || new Date().toISOString(),
                      updated_at: item.chart.updated_at || new Date().toISOString()
                    } as Chart)">
                      <el-icon><FullScreen /></el-icon>
                    </el-button>
                    <el-button type="text" @click="editChartItem(item)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button type="text" @click="confirmRemoveChartItem(item)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div class="chart-content">
                  <component
                    :is="getChartComponent(item.chart.type)"
                    :chart-data="chartDataMap[item.chart.id] || []"
                    :chart-options="getChartOptions(item.chart)"
                  />
                </div>
              </div>
            </grid-item>
          </grid-layout>
        </div>
      </div>
      
      <!-- 创建看板对话框 -->
      <el-dialog
        v-model="createDashboardDialogVisible"
        title="创建看板"
        width="500px"
      >
        <el-form :model="dashboardForm" label-width="100px" :rules="dashboardRules" ref="dashboardFormRef">
          <el-form-item label="标题" prop="title">
            <el-input v-model="dashboardForm.title" placeholder="请输入看板标题" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="dashboardForm.description"
              type="textarea"
              placeholder="请输入看板描述"
              :rows="3"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createDashboardDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createDashboard" :loading="loading">创建</el-button>
        </template>
      </el-dialog>
      
      <!-- 编辑看板对话框 -->
      <el-dialog
        v-model="editDashboardDialogVisible"
        title="编辑看板"
        width="500px"
      >
        <el-form :model="dashboardForm" label-width="100px" :rules="dashboardRules" ref="dashboardFormRef">
          <el-form-item label="标题" prop="title">
            <el-input v-model="dashboardForm.title" placeholder="请输入看板标题" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="dashboardForm.description"
              type="textarea"
              placeholder="请输入看板描述"
              :rows="3"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDashboardDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateDashboard" :loading="loading">保存</el-button>
        </template>
      </el-dialog>
      
      <!-- 添加图表对话框 -->
      <el-dialog
        v-model="addChartDialogVisible"
        title="添加图表"
        width="800px"
      >
        <el-tabs v-model="chartTabsActive">
          <el-tab-pane label="选择已有图表" name="existing">
            <el-table
              v-if="charts.length > 0"
              :data="charts"
              style="width: 100%"
              @row-click="selectChart"
              highlight-current-row
            >
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="type" label="类型" />
              <el-table-column prop="created_at" label="创建时间">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button type="primary" size="small" @click.stop="addChartToDashboard(scope.row)">
                    添加
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无图表" />
          </el-tab-pane>
          <el-tab-pane label="创建新图表" name="new">
            <el-form :model="chartForm" label-width="100px" :rules="chartRules" ref="chartFormRef">
              <el-form-item label="标题" prop="title">
                <el-input v-model="chartForm.title" placeholder="请输入图表标题" />
              </el-form-item>
              <el-form-item label="描述">
                <el-input
                  v-model="chartForm.description"
                  type="textarea"
                  placeholder="请输入图表描述"
                  :rows="2"
                />
              </el-form-item>
              <el-form-item label="图表类型" prop="type">
                <el-select v-model="chartForm.type" placeholder="请选择图表类型" style="width: 100%">
                  <el-option
                    v-for="type in chartTypes"
                    :key="type.type"
                    :label="type.name"
                    :value="type.type"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="数据源" prop="data_source">
                <el-select v-model="chartForm.data_source.id" placeholder="请选择数据源" style="width: 100%">
                  <el-option
                    v-for="source in dataSources"
                    :key="source.id"
                    :label="source.name"
                    :value="source.id"
                  />
                </el-select>
              </el-form-item>
              <!-- 这里可以根据图表类型添加更多配置选项 -->
            </el-form>
            <div class="chart-preview" v-if="chartForm.type">
              <h3>预览</h3>
              <div class="chart-preview-container">
                <!-- 图表预览组件 -->
              </div>
            </div>
            <div class="dialog-footer">
              <el-button @click="addChartDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="createAndAddChart" :loading="loading">创建并添加</el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-dialog>
      
      <!-- 图表详情对话框 -->
      <el-dialog
        v-model="chartDetailDialogVisible"
        :title="currentChart ? currentChart.title : '图表详情'"
        width="800px"
      >
        <div v-if="currentChart" class="chart-detail">
          <div class="chart-info">
            <p><strong>描述:</strong> {{ currentChart.description || '无描述' }}</p>
            <p><strong>类型:</strong> {{ getChartTypeName(currentChart.type) }}</p>
            <p><strong>创建时间:</strong> {{ formatDate(currentChart.created_at) }}</p>
          </div>
          
          <div class="chart-preview-large">
            <component
              :is="getChartComponent(currentChart.type)"
              :chart-data="chartDataMap[currentChart.id] || []"
              :chart-options="getChartOptions(currentChart)"
            />
          </div>
          
          <div class="chart-actions-footer">
            <el-button type="primary" @click="addChartToDashboard(currentChart)" v-if="currentDashboard">
              添加到当前看板
            </el-button>
            <el-button type="success" @click="createDashboardWithChart" v-else>
              创建包含此图表的看板
            </el-button>
            <el-button @click="chartDetailDialogVisible = false">关闭</el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, MoreFilled, Back, Check, Rank, Refresh, FullScreen } from '@element-plus/icons-vue'
import { GridLayout, GridItem } from 'vue-grid-layout'
import { 
  getDashboards, 
  getDashboardWithItems, 
  createDashboard as apiCreateDashboard,
  updateDashboard as apiUpdateDashboard,
  deleteDashboard as apiDeleteDashboard,
  addDashboardItem,
  updateDashboardItem,
  deleteDashboardItem
} from '@/api/dashboard'
import { 
  getCharts, 
  getChartTypes, 
  createChart as apiCreateChart,
  getChart,
  getChartData as apiGetChartData
} from '@/api/chart'
import { getDataSources } from '@/api/datasource'
import type { 
  Dashboard, 
  DashboardWithItems, 
  DashboardItemWithChart 
} from '@/api/dashboard'
import type { Chart, ChartType } from '@/api/chart'
import BarChart from '@/components/charts/BarChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import { useRouter } from 'vue-router'

// 看板列表
const dashboards = ref<Dashboard[]>([])
const currentDashboard = ref<DashboardWithItems | null>(null)
const loading = ref(false)

// 图表列表
const charts = ref<Chart[]>([])
const chartTypes = ref<ChartType[]>([])
const dataSources = ref<any[]>([])

// 对话框控制
const createDashboardDialogVisible = ref(false)
const editDashboardDialogVisible = ref(false)
const addChartDialogVisible = ref(false)
const chartTabsActive = ref('existing')

// 表单引用
const dashboardFormRef = ref()
const chartFormRef = ref()

// 看板表单
const dashboardForm = reactive({
  id: '',
  title: '',
  description: ''
})

// 图表表单
const chartForm = reactive({
  title: '',
  description: '',
  type: '',
  config: {
    data: {},
    options: {}
  },
  data_source: {
    id: '',
    type: ''
  }
})

// 表单验证规则
const dashboardRules = {
  title: [{ required: true, message: '请输入看板标题', trigger: 'blur' }]
}

const chartRules = {
  title: [{ required: true, message: '请输入图表标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择图表类型', trigger: 'change' }],
  'data_source.id': [{ required: true, message: '请选择数据源', trigger: 'change' }]
}

// 网格布局
const gridLayout = computed(() => {
  if (!currentDashboard.value) return []
  
  return currentDashboard.value.items.map(item => ({
    x: item.position_x,
    y: item.position_y,
    w: item.width,
    h: item.height,
    i: item.id
  }))
})

// 路由
const router = useRouter()

// 最近创建的图表
const recentCharts = ref<Chart[]>([])

// 当前查看的图表
const currentChart = ref<Chart | null>(null)
const chartDetailDialogVisible = ref(false)

// 图表数据缓存
const chartDataMap = ref<Record<string, any[]>>({})

// 添加全屏图表状态
const fullscreenChart = ref<Chart | null>(null)

// 加载图表数据
const loadChartData = async (chartId: string) => {
  try {
    console.log(`开始加载图表 ${chartId} 数据`);
    const chartData = await apiGetChartData(chartId);
    console.log(`图表 ${chartId} 数据加载成功:`, chartData);
    
    if (chartData && chartData.data && Array.isArray(chartData.data)) {
      chartDataMap.value[chartId] = chartData.data;
    } else {
      console.warn(`图表 ${chartId} 返回的数据格式不正确:`, chartData);
      chartDataMap.value[chartId] = [];
    }
  } catch (error) {
    console.error(`加载图表 ${chartId} 数据失败:`, error);
    chartDataMap.value[chartId] = [];
  }
}

// 初始化
onMounted(async () => {
  await fetchDashboards()
  await fetchChartTypes()
  await fetchDataSources()
  await fetchRecentCharts()
})

// 获取看板列表
const fetchDashboards = async () => {
  loading.value = true
  try {
    dashboards.value = await getDashboards()
  } catch (error) {
    console.error('获取看板列表失败:', error)
    ElMessage.error('获取看板列表失败')
  } finally {
    loading.value = false
  }
}

// 获取图表类型
const fetchChartTypes = async () => {
  try {
    chartTypes.value = await getChartTypes()
  } catch (error) {
    console.error('获取图表类型失败:', error)
    ElMessage.error('获取图表类型失败')
  }
}

// 获取数据源
const fetchDataSources = async () => {
  try {
    dataSources.value = await getDataSources()
  } catch (error) {
    console.error('获取数据源失败:', error)
    ElMessage.error('获取数据源失败')
  }
}

// 获取最近创建的图表
const fetchRecentCharts = async () => {
  loading.value = true
  try {
    const charts = await getCharts()
    // 按创建时间排序，最新的排在前面
    recentCharts.value = charts.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    ).slice(0, 8) // 只显示最近的8个图表
    
    // 加载所有图表数据
    if (recentCharts.value.length > 0) {
      const promises = recentCharts.value.map(chart => 
        loadChartData(chart.id)
      )
      await Promise.all(promises)
    }
  } catch (error) {
    console.error('获取最近图表失败:', error)
    ElMessage.error('获取最近图表失败')
  } finally {
    loading.value = false
  }
}

// 刷新最近创建的图表
const refreshRecentCharts = () => {
  fetchRecentCharts()
}

// 跳转到分析页面创建图表
const goToAnalytics = () => {
  router.push('/analytics')
}

// 查看图表详情
const viewChartDetail = async (chart: Chart) => {
  currentChart.value = chart
  chartDetailDialogVisible.value = true
  
  // 加载图表数据
  await loadChartData(chart.id)
}

// 创建包含此图表的看板
const createDashboardWithChart = async () => {
  if (!currentChart.value) return
  
  // 先创建看板
  dashboardForm.id = ''
  dashboardForm.title = `包含 ${currentChart.value.title} 的看板`
  dashboardForm.description = `自动创建的包含图表 ${currentChart.value.title} 的看板`
  
  loading.value = true
  try {
    const response = await apiCreateDashboard({
      title: dashboardForm.title,
      description: dashboardForm.description,
      layout: undefined
    })
    
    // 获取新创建的看板ID
    const dashboardId = response.id
    
    // 添加图表到看板
    await addDashboardItem(dashboardId, {
      chart_id: currentChart.value.id,
      position_x: 0,
      position_y: 0,
      width: 6,
      height: 8
    })
    
    ElMessage.success('创建看板并添加图表成功')
    chartDetailDialogVisible.value = false
    
    // 打开新创建的看板
    await openDashboard(dashboardId)
  } catch (error) {
    console.error('创建看板失败:', error)
    ElMessage.error('创建看板失败')
  } finally {
    loading.value = false
  }
}

// 获取图表类型名称
const getChartTypeName = (type: string) => {
  const chartTypes: Record<string, string> = {
    'bar': '柱状图',
    'line': '折线图',
    'pie': '饼图',
    'scatter': '散点图',
    'area': '面积图',
    'radar': '雷达图',
    'heatmap': '热力图',
    'table': '表格'
  }
  
  return chartTypes[type] || type
}

// 显示创建看板对话框
const showCreateDashboardDialog = () => {
  dashboardForm.id = ''
  dashboardForm.title = ''
  dashboardForm.description = ''
  createDashboardDialogVisible.value = true
}

// 显示编辑看板对话框
const showEditDashboardDialog = (dashboard: Dashboard) => {
  dashboardForm.id = dashboard.id
  dashboardForm.title = dashboard.title
  dashboardForm.description = dashboard.description || ''
  editDashboardDialogVisible.value = true
}

// 创建看板
const createDashboard = async () => {
  if (!dashboardFormRef.value) return
  
  await dashboardFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    loading.value = true
    try {
      const response = await apiCreateDashboard({
        title: dashboardForm.title,
        description: dashboardForm.description || undefined,
        layout: undefined
      })
      
      ElMessage.success('创建看板成功')
      createDashboardDialogVisible.value = false
      await fetchDashboards()
    } catch (error) {
      console.error('创建看板失败:', error)
      ElMessage.error('创建看板失败')
    } finally {
      loading.value = false
    }
  })
}

// 更新看板
const updateDashboard = async () => {
  if (!dashboardFormRef.value) return
  
  await dashboardFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    loading.value = true
    try {
      await apiUpdateDashboard(dashboardForm.id, {
        title: dashboardForm.title,
        description: dashboardForm.description || undefined,
        layout: undefined
      })
      
      ElMessage.success('更新看板成功')
      editDashboardDialogVisible.value = false
      await fetchDashboards()
      
      // 如果当前正在查看该看板，更新当前看板信息
      if (currentDashboard.value && currentDashboard.value.id === dashboardForm.id) {
        currentDashboard.value.title = dashboardForm.title
        currentDashboard.value.description = dashboardForm.description || undefined
      }
    } catch (error) {
      console.error('更新看板失败:', error)
      ElMessage.error('更新看板失败')
    } finally {
      loading.value = false
    }
  })
}

// 确认删除看板
const confirmDeleteDashboard = (dashboard: Dashboard) => {
  ElMessageBox.confirm(
    `确定要删除看板"${dashboard.title}"吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    loading.value = true
    try {
      await apiDeleteDashboard(dashboard.id)
      ElMessage.success('删除看板成功')
      await fetchDashboards()
    } catch (error) {
      console.error('删除看板失败:', error)
      ElMessage.error('删除看板失败')
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 打开看板
const openDashboard = async (dashboardId: string) => {
  loading.value = true
  try {
    currentDashboard.value = await getDashboardWithItems(dashboardId)
    
    // 加载所有图表数据
    if (currentDashboard.value && currentDashboard.value.items.length > 0) {
      const promises = currentDashboard.value.items.map(item => 
        loadChartData(item.chart.id)
      )
      await Promise.all(promises)
    }
  } catch (error) {
    console.error('获取看板详情失败:', error)
    ElMessage.error('获取看板详情失败')
  } finally {
    loading.value = false
  }
}

// 返回看板列表
const backToDashboardList = () => {
  currentDashboard.value = null
}

// 显示添加图表对话框
const showAddChartDialog = async () => {
  chartTabsActive.value = 'existing'
  
  // 重置图表表单
  chartForm.title = ''
  chartForm.description = ''
  chartForm.type = ''
  chartForm.data_source.id = ''
  
  // 获取图表列表
  loading.value = true
  try {
    charts.value = await getCharts()
  } catch (error) {
    console.error('获取图表列表失败:', error)
    ElMessage.error('获取图表列表失败')
  } finally {
    loading.value = false
  }
  
  addChartDialogVisible.value = true
}

// 选择图表
const selectChart = (row: Chart) => {
  // 高亮选中的图表
}

// 添加图表到看板
const addChartToDashboard = async (chart: Chart) => {
  if (!currentDashboard.value) return
  
  loading.value = true
  try {
    // 计算新图表的位置
    const position = calculateNewItemPosition()
    
    const dashboardId = currentDashboard.value.id
    await addDashboardItem(dashboardId, {
      chart_id: chart.id,
      position_x: position.x,
      position_y: position.y,
      width: 6,
      height: 8
    })
    
    ElMessage.success('添加图表成功')
    addChartDialogVisible.value = false
    
    // 重新获取看板详情
    await openDashboard(dashboardId)
  } catch (error) {
    console.error('添加图表失败:', error)
    ElMessage.error('添加图表失败')
  } finally {
    loading.value = false
  }
}

// 创建并添加图表
const createAndAddChart = async () => {
  if (!chartFormRef.value || !currentDashboard.value) return
  
  await chartFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    loading.value = true
    try {
      // 创建图表
      const chart = await apiCreateChart({
        title: chartForm.title,
        description: chartForm.description,
        type: chartForm.type,
        config: chartForm.config,
        data_source: {
          id: chartForm.data_source.id,
          type: 'datasource'
        }
      })
      
      // 计算新图表的位置
      const position = calculateNewItemPosition()
      
      // 添加到看板
      const dashboardId = currentDashboard.value!.id
      await addDashboardItem(dashboardId, {
        chart_id: chart.id,
        position_x: position.x,
        position_y: position.y,
        width: 6,
        height: 8
      })
      
      ElMessage.success('创建并添加图表成功')
      addChartDialogVisible.value = false
      
      // 重新获取看板详情
      await openDashboard(dashboardId)
    } catch (error) {
      console.error('创建并添加图表失败:', error)
      ElMessage.error('创建并添加图表失败')
    } finally {
      loading.value = false
    }
  })
}

// 编辑图表项
const editChartItem = (item: DashboardItemWithChart) => {
  // 实现编辑图表项的逻辑
  ElMessage.info('编辑图表功能开发中')
}

// 确认移除图表项
const confirmRemoveChartItem = (item: DashboardItemWithChart) => {
  if (!currentDashboard.value) return
  
  ElMessageBox.confirm(
    `确定要从看板中移除图表"${item.chart.title}"吗？`,
    '移除确认',
    {
      confirmButtonText: '移除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    loading.value = true
    try {
      const dashboardId = currentDashboard.value!.id
      await deleteDashboardItem(dashboardId, item.id)
      ElMessage.success('移除图表成功')
      
      // 重新获取看板详情
      await openDashboard(dashboardId)
    } catch (error) {
      console.error('移除图表失败:', error)
      ElMessage.error('移除图表失败')
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户取消移除
  })
}

// 保存看板布局
const saveDashboardLayout = async () => {
  if (!currentDashboard.value) return
  
  loading.value = true
  try {
    // 保存每个图表项的位置和大小
    const promises = currentDashboard.value.items.map(item => {
      const layoutItem = gridLayout.value.find(layout => layout.i === item.id)
      if (!layoutItem) return Promise.resolve()
      
      return updateDashboardItem(currentDashboard.value!.id, item.id, {
        position_x: layoutItem.x,
        position_y: layoutItem.y,
        width: layoutItem.w,
        height: layoutItem.h
      })
    })
    
    await Promise.all(promises)
    ElMessage.success('保存布局成功')
  } catch (error) {
    console.error('保存布局失败:', error)
    ElMessage.error('保存布局失败')
  } finally {
    loading.value = false
  }
}

// 布局更新事件
const onLayoutUpdated = (newLayout: any[]) => {
  // 更新布局
}

// 计算新图表项的位置
const calculateNewItemPosition = () => {
  if (!currentDashboard.value || currentDashboard.value.items.length === 0) {
    return { x: 0, y: 0 }
  }
  
  // 找到当前最大的y坐标
  let maxY = 0
  currentDashboard.value.items.forEach(item => {
    const bottomY = item.position_y + item.height
    if (bottomY > maxY) {
      maxY = bottomY
    }
  })
  
  return { x: 0, y: maxY }
}

// 获取图表组件
const getChartComponent = (type: string) => {
  // 添加调试信息
  console.log('图表类型:', type);
  
  // 根据图表类型返回对应的组件
  switch (type) {
    case 'bar':
      return BarChart;
    case 'line':
      return LineChart;
    default:
      console.log('未知图表类型:', type);
      return 'div'; // 临时返回div
  }
}

// 获取图表数据
const getChartData = async (chart: any) => {
  console.log('处理图表数据:', chart);
  
  // 如果配置中已有数据，直接使用
  if (chart.config && chart.config.data) {
    return chart.config.data;
  }
  
  // 否则从API获取数据
  try {
    const chartData = await apiGetChartData(chart.id);
    console.log('从API获取的图表数据:', chartData);
    return chartData.data || [];
  } catch (error) {
    console.error('获取图表数据失败:', error);
    ElMessage.error('获取图表数据失败');
    return [];
  }
}

// 获取图表选项
const getChartOptions = (chart: any) => {
  console.log('处理图表选项:', chart);
  const options = { ...chart.config };
  delete options.data; // 移除数据，避免重复
  
  // 直接将图表标题设置为字符串，而不是对象
  options.title = chart.title || '未命名图表';
  
  return options;
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 查看全屏图表
const viewFullscreenChart = async (chart: Chart) => {
  // 确保chart是完整的Chart类型
  if (!chart.created_at || !chart.updated_at) {
    // 如果缺少必要属性，尝试获取完整的图表信息
    try {
      const fullChart = await getChart(chart.id);
      fullscreenChart.value = fullChart;
    } catch (error) {
      console.error('获取完整图表信息失败:', error);
      // 回退方案：使用现有的chart并添加缺失的属性
      fullscreenChart.value = {
        ...chart,
        created_at: chart.created_at || new Date().toISOString(),
        updated_at: chart.updated_at || new Date().toISOString()
      } as Chart;
    }
  } else {
    fullscreenChart.value = chart;
  }
  
  // 加载图表数据
  await loadChartData(chart.id);
}

// 退出全屏
const exitFullscreen = () => {
  fullscreenChart.value = null
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.card-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 40px 0;
}

.chart-card {
  height: 280px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-preview {
  height: 150px;
  overflow: hidden;
  margin-bottom: 10px;
}

.chart-description {
  color: #666;
  font-size: 14px;
  margin: 5px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.chart-meta {
  color: #999;
  font-size: 12px;
  margin-top: auto;
}

.dashboard-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-title h2 {
  margin: 0;
}

.dashboard-title p {
  margin: 5px 0 0;
  color: #666;
}

.dashboard-grid {
  margin-top: 20px;
  min-height: 500px;
}

.chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
  background-color: #f5f7fa;
}

.chart-drag-handle {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: move;
}

.chart-content {
  flex-grow: 1;
  padding: 10px;
  overflow: auto;
}

.chart-preview-container {
  height: 300px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
}

.dialog-footer {
  margin-top: 20px;
  text-align: right;
}

.chart-preview-large {
  height: 400px;
  width: 100%;
}

.chart-actions-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 添加全屏图表样式 */
.fullscreen-chart {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: white;
  z-index: 1000;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.fullscreen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.fullscreen-title h2 {
  margin: 0;
}

.fullscreen-title p {
  margin: 5px 0 0;
  color: #666;
}

.fullscreen-content {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-content > * {
  width: 100%;
  height: 100%;
}
</style> 