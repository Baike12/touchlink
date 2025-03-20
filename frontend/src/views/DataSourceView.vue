<template>
  <div class="datasource-container">
    <div class="page-header">
      <h1 class="page-title">数据源管理</h1>
      <p class="page-description">
        连接和管理多种数据源，包括MySQL、MongoDB和Excel等。
      </p>
    </div>
    
    <el-tabs v-model="activeTab" class="datasource-tabs">
      <!-- 新建数据源标签页 -->
      <el-tab-pane label="新建数据源" name="connect">
        <div class="card-container">
          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-width="100px"
            class="datasource-form"
          >
            <el-form-item label="数据源类型" prop="type">
              <el-select v-model="formData.type" placeholder="请选择数据源类型" style="width: 100%" @change="handleTypeChange">
                <el-option
                  v-for="type in supportedTypes"
                  :key="type"
                  :label="type"
                  :value="type"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="数据源名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入数据源名称" />
            </el-form-item>
            
            <!-- Excel文件上传 -->
            <template v-if="formData.type === 'Excel'">
              <el-form-item label="Excel文件" prop="file">
                <el-upload
                  class="excel-uploader"
                  :auto-upload="false"
                  :show-file-list="true"
                  :limit="1"
                  :on-change="handleFileChange"
                  :on-exceed="handleExceed"
                  accept=".xls,.xlsx,.xlsm"
                >
                  <el-button type="primary">选择Excel文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      只能上传 xls/xlsx/xlsm 文件
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
            </template>
            
            <!-- MySQL配置 -->
            <template v-if="formData.type === 'MySQL'">
              <el-form-item label="主机地址" prop="host">
                <el-input v-model="formData.host" placeholder="请输入主机地址" />
              </el-form-item>
              
              <el-form-item label="端口" prop="port">
                <el-input-number v-model="formData.port" :min="1" :max="65535" style="width: 100%" />
              </el-form-item>
              
              <el-form-item label="用户名" prop="user">
                <el-input v-model="formData.user" placeholder="请输入用户名" />
              </el-form-item>
              
              <el-form-item label="密码" prop="password">
                <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password />
              </el-form-item>
              
              <el-form-item label="数据库" prop="database">
                <el-input v-model="formData.database" placeholder="请输入数据库名称" />
              </el-form-item>
            </template>
            
            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="loading">
                {{ formData.type === 'Excel' ? '上传并导入' : '测试连接' }}
              </el-button>
              <el-button type="success" @click="previewData" :loading="loading" v-if="formData.type !== 'Excel'">
                预览数据
              </el-button>
              <el-button type="info" @click="saveDataSource" :loading="loading" v-if="formData.type !== 'Excel'">
                保存数据源
              </el-button>
            </el-form-item>
          </el-form>
          
          <!-- 预览数据部分 -->
          <div v-if="showPreview" class="preview-container">
            <el-divider>
              <span class="divider-title">数据预览</span>
            </el-divider>
            
            <div v-if="loadingTables" class="loading-container">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="tables.length === 0" class="empty-container">
              <el-empty description="未找到任何表" />
            </div>
            <div v-else>
              <div class="table-selection">
                <el-select 
                  v-model="selectedTable" 
                  placeholder="请选择要浏览的表" 
                  @change="handleTableChange"
                  style="width: 100%"
                >
                  <el-option 
                    v-for="table in tables" 
                    :key="table" 
                    :label="table" 
                    :value="table" 
                  />
                </el-select>
              </div>
              
              <div v-if="selectedTable" class="table-info">
                <div class="table-header">
                  <h4>表: {{ selectedTable }}</h4>
                  <div class="table-actions">
                    <el-button type="primary" size="small" @click="refreshTableData">
                      刷新数据
                    </el-button>
                  </div>
                </div>
                
                <el-tabs v-model="dataTab" class="data-tabs">
                  <el-tab-pane label="数据" name="data">
                    <div v-if="loadingData" class="loading-container">
                      <el-skeleton :rows="5" animated />
                    </div>
                    <div v-else-if="!tableData.data || tableData.data.length === 0" class="empty-container">
                      <el-empty description="表中没有数据" />
                    </div>
                    <div v-else class="table-container">
                      <el-table 
                        :data="tableData.data" 
                        border 
                        stripe 
                        style="width: 100%"
                        max-height="500px"
                      >
                        <el-table-column 
                          v-for="column in tableData.columns" 
                          :key="column" 
                          :prop="column" 
                          :label="column" 
                          min-width="150"
                        />
                      </el-table>
                      <div class="table-pagination">
                        <el-pagination
                          layout="total, sizes, prev, pager, next"
                          :total="100"
                          :page-sizes="[20, 50, 100, 200]"
                          :page-size="pageSize"
                          @size-change="handleSizeChange"
                        />
                      </div>
                    </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="结构" name="schema">
                    <div v-if="loadingSchema" class="loading-container">
                      <el-skeleton :rows="5" animated />
                    </div>
                    <div v-else-if="!tableSchema.columns || tableSchema.columns.length === 0" class="empty-container">
                      <el-empty description="无法获取表结构" />
                    </div>
                    <div v-else class="schema-container">
                      <el-table 
                        :data="tableSchema.columns" 
                        border 
                        stripe 
                        style="width: 100%"
                      >
                        <el-table-column prop="name" label="列名" min-width="150" />
                        <el-table-column prop="type" label="类型" min-width="120" />
                        <el-table-column prop="nullable" label="可为空">
                          <template #default="scope">
                            <el-tag :type="scope.row.nullable ? 'info' : 'danger'" size="small">
                              {{ scope.row.nullable ? '是' : '否' }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="default" label="默认值" min-width="120">
                          <template #default="scope">
                            <span>{{ scope.row.default === null ? '-' : scope.row.default }}</span>
                          </template>
                        </el-table-column>
                        <el-table-column prop="primary_key" label="主键">
                          <template #default="scope">
                            <el-tag v-if="scope.row.primary_key" type="success" size="small">是</el-tag>
                            <span v-else>-</span>
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 数据源管理标签页 -->
      <el-tab-pane label="数据源管理" name="manage">
        <div class="card-container">
          <div class="datasource-header">
            <h3>已保存的数据源</h3>
            <el-button type="primary" @click="activeTab = 'connect'" size="small">
              添加数据源
            </el-button>
          </div>
          
          <div v-if="loadingSavedDataSources" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="savedDataSources.length === 0" class="empty-container">
            <el-empty description="未找到任何保存的数据源">
              <el-button type="primary" @click="activeTab = 'connect'">
                添加数据源
              </el-button>
            </el-empty>
          </div>
          <div v-else>
            <el-table :data="savedDataSources" style="width: 100%" border>
              <el-table-column prop="name" label="名称" min-width="150" />
              <el-table-column prop="type" label="类型" width="120">
                <template #default="scope">
                  <el-tag>{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" />
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="connectToSavedDataSource(scope.row)">
                    连接
                  </el-button>
                  <el-button type="danger" size="small" @click="confirmDeleteDataSource(scope.row)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { FormInstance, UploadFile } from 'element-plus'
import { ElMessage, ElNotification, ElMessageBox, ElLoading } from 'element-plus'
import { 
  getTables, 
  getTableSchema,
  getTableData,
  testDataSourceConnection,
  connectDataSource as apiConnectDataSource,
  saveDataSource as apiSaveDataSource,
  getDataSources,
  deleteDataSource as apiDeleteDataSource,
  uploadExcelFile,
  type TableSchemaResponse,
  type TableDataResponse,
  type DataSourceConfig,
  type DataSourceCreateRequest,
  type DataSourceDetail,
  getDataSourceDetail
} from '@/api/datasource'

// 表单引用
const formRef = ref<FormInstance>()

// 当前激活的标签页
const activeTab = ref('connect')

// 支持的数据源类型
const supportedTypes = ref(['MySQL', 'MongoDB', 'Excel'])

// 连接状态
const connected = ref(false)
const loading = ref(false)
const showPreview = ref(false)

// 表单数据
const formData = ref({
  type: 'MySQL',
  name: '',
  host: '127.0.0.1',
  port: 3306,
  user: 'root',
  password: 'your_password_here',
  database: 'shop',
  file: null as File | null
})

// 表单验证规则
const formRules = {
  type: [{ required: true, message: '请选择数据源类型', trigger: 'change' }],
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  user: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  database: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  file: [{ required: true, message: '请选择Excel文件', trigger: 'change' }]
}

// 表格相关数据
const tables = ref<string[]>([])
const selectedTable = ref('')
const loadingTables = ref(false)
const loadingData = ref(false)
const loadingSchema = ref(false)
const dataTab = ref('data')
const tableData = ref<TableDataResponse>({ columns: [], data: [] })
const tableSchema = ref<TableSchemaResponse>({ table_name: '', columns: [] })
const pageSize = ref(100)

// 已保存的数据源
const savedDataSources = ref<DataSourceDetail[]>([])
const loadingSavedDataSources = ref(false)

// 处理数据源类型变更
const handleTypeChange = (type: string) => {
  // 重置表单数据
  formData.value = {
    type,
    name: '',
    host: '127.0.0.1',
    port: 3306,
    user: 'root',
    password: 'your_password_here',
    database: 'shop',
    file: null
  }
}

// 处理文件选择
const handleFileChange = (uploadFile: UploadFile) => {
  formData.value.file = uploadFile.raw || null
  formData.value.name = uploadFile.name.split('.')[0] // 使用文件名作为数据源名称
}

// 处理超出文件数限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        if (formData.value.type === 'Excel') {
          // 上传Excel文件
          if (!formData.value.file) {
            ElMessage.error('请选择Excel文件')
            return
          }
          
          const response = await uploadExcelFile(formData.value.file)
          
          ElNotification({
            title: '上传成功',
            message: response.message,
            type: 'success'
          })
          
          // 重置表单
          formRef.value.resetFields()
          
        } else {
          // 测试数据源连接
          await testConnection()
        }
      } catch (error: any) {
        console.error('操作失败:', error)
        ElNotification({
          title: '操作失败',
          message: error.message || '操作失败',
          type: 'error'
        })
      } finally {
        loading.value = false
      }
    }
  })
}

// 测试数据源连接
const testConnection = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 调用API测试连接
        const config: DataSourceConfig = {
          type: formData.value.type.toLowerCase(),
          host: formData.value.host,
          port: formData.value.port,
          user: formData.value.user,
          password: formData.value.password,
          database: formData.value.database
        }
        
        const response = await testDataSourceConnection(config)
        
        if (response && response.status === 'success') {
          ElNotification({
            title: '连接成功',
            message: '数据源连接测试成功',
            type: 'success'
          })
        } else {
          ElNotification({
            title: '连接失败',
            message: response?.message || '数据源连接测试失败',
            type: 'error'
          })
        }
      } catch (error: any) {
        console.error('测试连接失败:', error)
        
        ElNotification({
          title: '连接失败',
          message: '数据源连接测试失败',
          type: 'error'
        })
      } finally {
        loading.value = false
      }
    }
  })
}

// 预览数据
const previewData = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 使用API连接数据库
        const config: DataSourceConfig = {
          type: formData.value.type.toLowerCase(),
          host: formData.value.host,
          port: formData.value.port,
          user: formData.value.user,
          password: formData.value.password,
          database: formData.value.database
        }
        
        const response = await apiConnectDataSource(config)
        
        if (response && response.status === 'success') {
          connected.value = true
          showPreview.value = true
          
          ElNotification({
            title: '连接成功',
            message: '数据源连接成功，正在加载数据预览',
            type: 'success'
          })
          
          // 加载表列表
          loadTables()
        } else {
          ElNotification({
            title: '连接失败',
            message: response?.message || '数据源连接失败',
            type: 'error'
          })
        }
      } catch (error: any) {
        console.error('连接数据源失败:', error)
        
        ElNotification({
          title: '连接失败',
          message: '数据源连接失败',
          type: 'error'
        })
      } finally {
        loading.value = false
      }
    }
  })
}

// 断开数据源连接
const disconnectDataSource = () => {
  connected.value = false
  showPreview.value = false
  tables.value = []
  selectedTable.value = ''
  tableData.value = { columns: [], data: [] }
  tableSchema.value = { table_name: '', columns: [] }
  ElMessage.success('已断开数据源连接')
}

// 保存数据源
const saveDataSource = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 构建数据源配置
        const config: DataSourceConfig = {
          type: formData.value.type.toLowerCase(),
          host: formData.value.host,
          port: formData.value.port,
          user: formData.value.user,
          password: formData.value.password,
          database: formData.value.database
        }
        
        // 构建保存请求
        const request: DataSourceCreateRequest = {
          name: formData.value.name,
          type: formData.value.type.toLowerCase(),
          config: config
        }
        
        // 调用API保存数据源
        const response = await apiSaveDataSource(request)
        
        if (response && response.id) {
          ElNotification({
            title: '保存成功',
            message: `数据源 ${response.name} 已保存`,
            type: 'success'
          })
        } else {
          ElNotification({
            title: '保存失败',
            message: '保存数据源失败',
            type: 'error'
          })
        }
      } catch (error: any) {
        console.error('保存数据源失败:', error)
        
        ElNotification({
          title: '保存失败',
          message: '保存数据源失败',
          type: 'error'
        })
      } finally {
        loading.value = false
      }
    }
  })
}

// 加载表列表
const loadTables = async () => {
  loadingTables.value = true
  
  try {
    console.log('开始加载表列表...');
    // 调用API获取表列表
    const response = await getTables()
    console.log('获取到表列表响应:', response);
    
    if (response && response.tables) {
      tables.value = response.tables
      
      if (tables.value.length > 0) {
        selectedTable.value = tables.value[0]
        handleTableChange(selectedTable.value)
      } else {
        console.log('表列表为空');
      }
    } else {
      console.error('表列表响应格式不正确:', response);
    }
  } catch (error: any) {
    console.error('获取表列表失败:', error)
    
    // 显示更详细的错误信息
    if (error.response) {
      console.error('错误状态码:', error.response.status)
      console.error('错误详情:', error.response.data)
      ElMessage.error(`获取表列表失败: ${error.response.status} - ${error.response.data?.detail || '未知错误'}`)
    } else if (error.request) {
      console.error('未收到响应:', error.request)
      ElMessage.error('获取表列表失败: 服务器未响应')
    } else {
      console.error('请求配置错误:', error.message)
      ElMessage.error(`获取表列表失败: ${error.message}`)
    }
  } finally {
    loadingTables.value = false
  }
}

// 处理表格选择变化
const handleTableChange = (tableName: string) => {
  if (!tableName) return
  
  loadTableData(tableName)
  loadTableSchema(tableName)
}

// 加载表数据
const loadTableData = async (tableName: string) => {
  loadingData.value = true
  
  try {
    // 调用API获取表数据
    const response = await getTableData(tableName, pageSize.value)
    tableData.value = response
  } catch (error: any) {
    console.error('获取表数据失败:', error)
    ElMessage.error('获取表数据失败')
  } finally {
    loadingData.value = false
  }
}

// 加载表结构
const loadTableSchema = async (tableName: string) => {
  loadingSchema.value = true
  
  try {
    // 调用API获取表结构
    const response = await getTableSchema(tableName)
    tableSchema.value = response
  } catch (error: any) {
    console.error('获取表结构失败:', error)
    ElMessage.error('获取表结构失败')
  } finally {
    loadingSchema.value = false
  }
}

// 刷新表数据
const refreshTableData = () => {
  if (selectedTable.value) {
    loadTableData(selectedTable.value)
  }
}

// 处理每页显示数量变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  if (selectedTable.value) {
    loadTableData(selectedTable.value)
  }
}

// 加载已保存的数据源
const loadSavedDataSources = async () => {
  loadingSavedDataSources.value = true
  
  try {
    const response = await getDataSources()
    savedDataSources.value = response
  } catch (error: any) {
    console.error('获取已保存的数据源失败:', error)
    ElMessage.error('获取已保存的数据源失败')
  } finally {
    loadingSavedDataSources.value = false
  }
}

// 连接到已保存的数据源
const connectToSavedDataSource = async (dataSource: DataSourceDetail) => {
  try {
    // 获取数据源详情
    const detail = await getDataSourceDetail(dataSource.id)
    
    // 设置表单数据
    formData.value.name = detail.name
    formData.value.type = detail.type
    
    // 使用后端返回的配置信息
    if (detail.config) {
      formData.value.host = detail.config.host
      formData.value.port = detail.config.port
      formData.value.user = detail.config.user
      formData.value.password = detail.config.password
      formData.value.database = detail.config.database
    }
    
    // 调用API连接数据源
    const config: DataSourceConfig = {
      type: detail.type.toLowerCase(),
      host: formData.value.host,
      port: formData.value.port,
      user: formData.value.user,
      password: formData.value.password,
      database: formData.value.database
    }
    
    // 调用API连接数据源
    const response = await apiConnectDataSource(config)
    
    if (response && response.status === 'success') {
      connected.value = true
      
      ElNotification({
        title: '连接成功',
        message: '数据源连接成功',
        type: 'success'
      })
      
      // 切换到浏览标签页并加载表列表
      activeTab.value = 'connect'
      loadTables()
    } else {
      ElNotification({
        title: '连接失败',
        message: response?.message || '数据源连接失败',
        type: 'error'
      })
    }
  } catch (error: any) {
    console.error('连接到已保存的数据源失败:', error)
    ElMessage.error('连接到已保存的数据源失败')
  }
}

// 确认删除数据源
const confirmDeleteDataSource = (dataSource: DataSourceDetail) => {
  ElMessageBox.confirm(
    `确定要删除数据源 "${dataSource.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteDataSource(dataSource.id)
  }).catch(() => {
    // 用户取消删除
  })
}

// 删除数据源
const deleteDataSource = async (id: string) => {
  try {
    await apiDeleteDataSource(id)
    ElMessage.success('数据源删除成功')
    loadSavedDataSources()
  } catch (error: any) {
    console.error('删除数据源失败:', error)
    ElMessage.error('删除数据源失败')
  }
}

// 组件挂载时执行
onMounted(() => {
  console.log('DataSourceView.vue组件已挂载')
  loadSavedDataSources()
})
</script>

<style scoped>
.datasource-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  margin-bottom: 8px;
}

.page-description {
  color: #606266;
}

.datasource-tabs {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-container {
  padding: 20px;
}

.datasource-form {
  max-width: 800px;
}

.empty-container {
  padding: 40px 0;
  text-align: center;
}

.loading-container {
  padding: 20px 0;
}

.datasource-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-selection {
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-container {
  margin-top: 20px;
}

.table-pagination {
  margin-top: 20px;
  text-align: right;
}

.datasource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.preview-container {
  margin-top: 30px;
}

.divider-title {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.excel-uploader {
  text-align: center;
  padding: 20px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color .3s;
}

.excel-uploader:hover {
  border-color: #409EFF;
}

.el-upload__tip {
  font-size: 12px;
  color: #606266;
  margin-top: 7px;
}
</style> 