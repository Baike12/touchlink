<template>
  <div class="add-data-container">
    <h1 class="page-title">添加数据</h1>
    
    <!-- 表格列表页面 -->
    <div class="tables-list-section" v-if="!currentTable && !showCreateTable">
      <div class="section-header">
        <h2>我的数据表</h2>
        <el-button type="primary" @click="showCreateTable = true">
          <el-icon><plus /></el-icon> 新建表
        </el-button>
      </div>
      
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="tables.length === 0" class="empty-state">
        <el-empty description="暂无数据表">
          <el-button type="primary" @click="showCreateTable = true">新建表</el-button>
        </el-empty>
      </div>
      
      <div v-else class="tables-grid">
        <el-card 
          v-for="table in tables" 
          :key="table.tableName" 
          class="table-card"
          @click="selectTable(table)"
        >
          <template #header>
            <div class="table-card-header">
              <span class="table-name">{{ table.tableName }}</span>
              <el-tag size="small">{{ table.columns.length }} 个字段</el-tag>
            </div>
          </template>
          <div class="table-card-content">
            <div class="table-columns">
              <el-tag 
                v-for="column in table.columns.slice(0, 3)" 
                :key="column.name"
                size="small"
                class="column-tag"
              >
                {{ column.name }}
                <small>({{ getTypeLabel(column.type) }})</small>
              </el-tag>
              <span v-if="table.columns.length > 3" class="more-columns">
                +{{ table.columns.length - 3 }} 个字段
              </span>
            </div>
            <div class="table-meta">
              <span class="create-time">创建于: {{ formatDate(table.createdAt) }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 创建表单 -->
    <div class="create-table-section" v-if="showCreateTable">
      <div class="section-header">
        <h2>创建新表</h2>
        <el-button @click="showCreateTable = false">返回表格列表</el-button>
      </div>
      
      <el-form :model="tableForm" label-width="120px">
        <el-form-item label="表名">
          <el-input v-model="tableForm.tableName" placeholder="请输入表名"></el-input>
        </el-form-item>
        
        <h3>表字段</h3>
        <div class="columns-container">
          <div v-for="(column, index) in tableForm.columns" :key="index" class="column-item">
            <el-row :gutter="10">
              <el-col :span="10">
                <el-input v-model="column.name" placeholder="字段名"></el-input>
              </el-col>
              <el-col :span="10">
                <el-select v-model="column.type" placeholder="数据类型">
                  <el-option label="数值" value="int"></el-option>
                  <el-option label="文字" value="varchar"></el-option>
                  <el-option label="时间戳" value="timestamp"></el-option>
                </el-select>
              </el-col>
              <el-col :span="4">
                <el-button type="danger" @click="removeColumn(index)" :disabled="tableForm.columns.length <= 1">
                  删除
                </el-button>
              </el-col>
            </el-row>
          </div>
        </div>
        
        <div class="column-actions">
          <el-button type="primary" @click="addColumn">添加字段</el-button>
        </div>
        
        <div class="form-actions">
          <el-button @click="showCreateTable = false">取消</el-button>
          <el-button type="primary" @click="createTable" :loading="loading">创建表</el-button>
        </div>
      </el-form>
    </div>
    
    <!-- 添加数据表单 -->
    <div class="add-data-section" v-if="currentTable">
      <div class="section-header">
        <h2>向表 "{{ currentTable.tableName }}" 添加数据</h2>
        <el-button @click="backToTablesList">返回表格列表</el-button>
      </div>
      
      <!-- 编辑表格 -->
      <div class="edit-table-section">
        <el-table :data="editingData" border style="width: 100%; margin-bottom: 20px;">
          <el-table-column 
            v-for="column in currentTable.columns" 
            :key="column.name"
            :prop="column.name"
            :label="column.name"
          >
            <template #default="scope">
              <el-input 
                v-if="column.type !== 'timestamp'"
                v-model="scope.row[column.name]" 
                :placeholder="`请输入${column.name}`"
                :type="getInputType(column.type)"
              ></el-input>
              <el-date-picker
                v-else
                v-model="scope.row[column.name]"
                type="datetime"
                placeholder="选择日期时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
                style="width: 100%"
              ></el-date-picker>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="danger" 
                size="small" 
                @click="removeEditingRow(scope.$index)"
              >删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="table-actions">
          <el-button type="primary" @click="addNewRow">添加行</el-button>
          <el-button type="success" @click="submitData" :loading="loading">提交数据</el-button>
        </div>
      </div>
      
      <!-- 显示已添加的数据 -->
      <div class="data-display" v-if="tableData.length > 0">
        <h3>已添加的数据</h3>
        <el-table :data="tableData" border style="width: 100%">
          <el-table-column 
            v-for="column in currentTable.columns" 
            :key="column.name"
            :prop="column.name"
            :label="column.name"
          ></el-table-column>
          <el-table-column label="ID" prop="id"></el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createTable as apiCreateTable, addTableData, getUserTables, getTableData } from '../api/user-table'
import type { TableForm, Column } from '../api/user-table'
import { Plus } from '@element-plus/icons-vue'

interface Table {
  tableName: string;
  columns: Column[];
  createdAt?: string;
  updatedAt?: string;
}

// 表单数据
const tableForm = reactive<TableForm>({
  tableName: '',
  columns: [{ name: '', type: 'varchar' }]
})

// 当前表
const currentTable = ref<Table | null>(null)

// 是否显示创建表单
const showCreateTable = ref(false)

// 编辑中的数据
const editingData = ref<Record<string, any>[]>([])

// 表格数据
const tableData = ref<any[]>([])

// 所有表格
const tables = ref<Table[]>([])

// 加载状态
const loading = ref(false)

// 在组件挂载时加载表格列表
onMounted(async () => {
  await loadTables()
})

// 加载表格列表
const loadTables = async () => {
  try {
    loading.value = true
    const response = await getUserTables()
    tables.value = response
  } catch (error: any) {
    console.error('获取表格列表失败:', error)
    ElMessage.error('获取表格列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 选择表格
const selectTable = async (table: Table) => {
  currentTable.value = table
  
  // 清空编辑数据
  editingData.value = []
  
  // 添加一行空数据
  addNewRow()
  
  // 加载表格数据
  try {
    loading.value = true
    const response = await getTableData(table.tableName)
    tableData.value = response
  } catch (error: any) {
    console.error('获取表格数据失败:', error)
    ElMessage.error('获取表格数据失败: ' + (error.response?.data?.detail || error.message))
    tableData.value = []
  } finally {
    loading.value = false
  }
}

// 添加字段
const addColumn = () => {
  tableForm.columns.push({ name: '', type: 'varchar' })
}

// 删除字段
const removeColumn = (index: number) => {
  if (tableForm.columns.length > 1) {
    tableForm.columns.splice(index, 1)
  }
}

// 创建表
const createTable = async () => {
  // 验证表单
  if (!tableForm.tableName) {
    ElMessage.error('请输入表名')
    return
  }
  
  for (const column of tableForm.columns) {
    if (!column.name) {
      ElMessage.error('请填写所有字段名')
      return
    }
  }
  
  try {
    loading.value = true
    await apiCreateTable(tableForm)
    ElMessage.success('表创建成功')
    
    // 重新加载表格列表
    await loadTables()
    
    // 重置表单
    tableForm.tableName = ''
    tableForm.columns = [{ name: '', type: 'varchar' }]
    
    // 返回表格列表
    showCreateTable.value = false
  } catch (error: any) {
    console.error('创建表失败:', error)
    ElMessage.error('创建表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 添加新行
const addNewRow = () => {
  const newRow: Record<string, any> = {}
  if (currentTable.value) {
    currentTable.value.columns.forEach(column => {
      newRow[column.name] = ''
    })
  }
  editingData.value.push(newRow)
}

// 删除编辑中的行
const removeEditingRow = (index: number) => {
  editingData.value.splice(index, 1)
}

// 提交数据
const submitData = async () => {
  if (!currentTable.value || editingData.value.length === 0) return
  
  try {
    loading.value = true
    
    // 逐个提交数据
    for (const rowData of editingData.value) {
      const response = await addTableData(currentTable.value.tableName, rowData)
      tableData.value.push(response)
    }
    
    // 清空编辑数据
    editingData.value = []
    ElMessage.success('数据添加成功')
  } catch (error: any) {
    console.error('添加数据失败:', error)
    ElMessage.error('添加数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 返回表格列表
const backToTablesList = () => {
  currentTable.value = null
  tableData.value = []
}

// 根据数据类型获取输入类型
const getInputType = (type: string) => {
  switch (type) {
    case 'int':
      return 'number'
    case 'timestamp':
      return 'datetime-local'
    default:
      return 'text'
  }
}

// 获取数据类型标签
const getTypeLabel = (type: string) => {
  switch (type) {
    case 'int':
      return '数值'
    case 'varchar':
      return '文字'
    case 'timestamp':
      return '时间戳'
    default:
      return type
  }
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.add-data-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
}

.tables-list-section,
.create-table-section, 
.add-data-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px 0;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.table-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.table-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.table-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-name {
  font-weight: bold;
  font-size: 16px;
}

.table-columns {
  margin-bottom: 10px;
}

.column-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.more-columns {
  font-size: 12px;
  color: #909399;
}

.table-meta {
  font-size: 12px;
  color: #909399;
}

.columns-container {
  margin-bottom: 20px;
}

.column-item {
  margin-bottom: 10px;
}

.column-actions {
  margin-bottom: 20px;
}

.form-actions {
  margin-top: 20px;
}

.data-display {
  margin-top: 30px;
}

.edit-table-section {
  margin-bottom: 30px;
}

.table-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}
</style>