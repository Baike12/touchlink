<template>
  <div class="analytics-container">
    <div class="page-header">
      <h1 class="page-title">数据分析</h1>
      <p class="page-description">
        选择数据源，分析您的数据，并生成可视化图表。
      </p>
    </div>
    
    <div class="card-container">
      <!-- 数据源选择卡片 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>选择数据源</span>
            <div v-if="selectedDataSource">
              <el-button type="primary" @click="showTemplateDialog" size="small">
                加载模板
              </el-button>
            </div>
          </div>
        </template>
        
        <el-form label-position="top">
          <el-form-item label="数据源">
            <el-select 
              v-model="selectedDataSource" 
              placeholder="请选择数据源"
              @change="handleDataSourceChange"
              style="width: 100%"
            >
              <el-option
                v-for="source in dataSources"
                :key="source.id"
                :label="source.name"
                :value="source.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="数据表" v-if="selectedDataSource">
            <el-select 
              v-model="selectedTables" 
              multiple 
              placeholder="请选择数据表"
              @change="handleTablesChange"
              style="width: 100%"
            >
              <el-option
                v-for="table in tables"
                :key="table.name"
                :label="table.label || table.name"
                :value="table.name"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 列选择卡片 -->
      <el-card v-if="selectedTables.length > 0">
        <template #header>
          <div class="card-header">
            <span>选择列</span>
            <div>
              <el-button 
                type="success" 
                :disabled="!hasSelectedColumns"
                @click="showSaveTemplateDialog"
                size="small"
              >
                保存为模板
              </el-button>
              <el-button 
                type="primary" 
                :disabled="!hasSelectedColumns"
                @click="generateCombinedTable"
              >
                生成结果
              </el-button>
            </div>
          </div>
        </template>
        
        <div v-for="table in selectedTables" :key="table" class="table-columns">
          <h3>{{ table }}</h3>
          <el-checkbox-group v-model="selectedColumnsByTable[table]">
            <el-checkbox 
              v-for="column in tableSchemas[table]?.columns || []"
              :key="column.name"
              :label="column.name"
            >
              {{ column.label || column.name }} ({{ column.type }})
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </el-card>
      
      <!-- JOIN关系设置卡片 -->
      <el-card v-if="selectedTables.length > 1">
        <template #header>
          <div class="card-header">
            <span>设置JOIN关系</span>
          </div>
        </template>
        
        <div v-for="(join, index) in joinRelationships" :key="index" class="join-relationship">
          <el-divider v-if="index > 0" />
          
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="左表">
                <el-select v-model="join.leftTable" placeholder="选择左表" @change="updateJoinColumns(index, 'left')">
                  <el-option
                    v-for="table in selectedTables"
                    :key="table"
                    :label="table"
                    :value="table"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="8">
              <el-form-item label="JOIN类型">
                <el-select v-model="join.type" placeholder="选择JOIN类型">
                  <el-option label="INNER JOIN" value="inner" />
                  <el-option label="LEFT JOIN" value="left" />
                  <el-option label="RIGHT JOIN" value="right" />
                  <el-option label="FULL JOIN" value="full" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="8">
              <el-form-item label="右表">
                <el-select v-model="join.rightTable" placeholder="选择右表" @change="updateJoinColumns(index, 'right')">
                  <el-option
                    v-for="table in selectedTables"
                    :key="table"
                    :label="table"
                    :value="table"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="11">
              <el-form-item label="左表列">
                <el-select v-model="join.leftColumn" placeholder="选择左表列">
                  <el-option
                    v-for="column in getTableColumns(join.leftTable)"
                    :key="column.name"
                    :label="column.label || column.name"
                    :value="column.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="2" class="join-equals">
              <span>=</span>
            </el-col>
            
            <el-col :span="11">
              <el-form-item label="右表列">
                <el-select v-model="join.rightColumn" placeholder="选择右表列">
                  <el-option
                    v-for="column in getTableColumns(join.rightTable)"
                    :key="column.name"
                    :label="column.label || column.name"
                    :value="column.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-button type="danger" @click="removeJoinRelationship(index)" v-if="joinRelationships.length > 1">
            删除JOIN关系
          </el-button>
        </div>
        
        <el-button type="primary" @click="addJoinRelationship" class="add-join-btn">
          添加JOIN关系
        </el-button>
      </el-card>
      
      <!-- 生成结果卡片 -->
      <el-card v-if="showResults" class="result-card">
        <template #header>
          <div class="card-header">
            <span>分析结果</span>
            <div>
              <el-button type="primary" @click="exportToExcel">
                <el-icon><Download /></el-icon> 导出Excel
              </el-button>
              <el-button type="success" @click="showCreateChartDialog">
                <el-icon><PieChart /></el-icon> 生成图表
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table
          :data="combinedData"
          style="width: 100%"
          height="400"
          border
          stripe
          :header-cell-style="{ background: '#f5f7fa' }"
        >
          <el-table-column
            v-for="column in selectedColumns"
            :key="column.name"
            :prop="column.name"
            :label="column.label || column.name"
            sortable
          />
        </el-table>
      </el-card>
      
      <!-- 创建图表对话框 -->
      <el-dialog
        v-model="createChartDialogVisible"
        title="创建图表"
        width="800px"
      >
        <el-form :model="chartForm" label-width="120px" :rules="chartRules" ref="chartFormRef">
          <el-form-item label="图表标题" prop="title">
            <el-input v-model="chartForm.title" placeholder="请输入图表标题" />
          </el-form-item>
          
          <el-form-item label="图表类型" prop="type">
            <el-select v-model="chartForm.type" placeholder="请选择图表类型" @change="handleChartTypeChange">
              <el-option
                v-for="type in chartTypes"
                :key="type.type"
                :label="type.name"
                :value="type.type"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="图表描述">
            <el-input
              v-model="chartForm.description"
              type="textarea"
              placeholder="请输入图表描述"
              :rows="3"
            />
          </el-form-item>
          
          <template v-if="chartForm.type === 'bar' || chartForm.type === 'line' || chartForm.type === 'area'">
            <el-form-item label="X轴字段" prop="xAxis.field">
              <el-select v-model="chartForm.config.xAxis.field" placeholder="请选择X轴字段">
                <el-option
                  v-for="column in selectedColumns"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Y轴字段" prop="seriesFields">
              <el-select
                v-model="chartForm.config.seriesFields"
                multiple
                placeholder="请选择Y轴字段"
                @change="handleSeriesChange"
              >
                <el-option
                  v-for="column in selectedColumns"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
          </template>
          
          <template v-else-if="chartForm.type === 'pie'">
            <el-form-item label="名称字段" prop="nameField">
              <el-select v-model="chartForm.config.nameField" placeholder="请选择名称字段">
                <el-option
                  v-for="column in selectedColumns"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="数值字段" prop="valueField">
              <el-select v-model="chartForm.config.valueField" placeholder="请选择数值字段">
                <el-option
                  v-for="column in selectedColumns.filter(col => isNumeric(col.name))"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
          </template>
          
          <template v-else-if="chartForm.type === 'scatter'">
            <el-form-item label="X轴字段" prop="xField">
              <el-select v-model="chartForm.config.xField" placeholder="请选择X轴字段">
                <el-option
                  v-for="column in selectedColumns.filter(col => isNumeric(col.name))"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Y轴字段" prop="yField">
              <el-select v-model="chartForm.config.yField" placeholder="请选择Y轴字段">
                <el-option
                  v-for="column in selectedColumns.filter(col => isNumeric(col.name))"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
          </template>
          
          <template v-else-if="chartForm.type === 'table'">
            <el-form-item label="表格列" prop="columns">
              <el-select
                v-model="chartForm.config.columnFields"
                multiple
                placeholder="请选择表格列"
                @change="handleColumnsChange"
              >
                <el-option
                  v-for="column in selectedColumns"
                  :key="column.name"
                  :label="column.label || column.name"
                  :value="column.name"
                />
              </el-select>
            </el-form-item>
          </template>
        </el-form>
        
        <template #footer>
          <el-button @click="createChartDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createChart" :loading="loading">创建</el-button>
        </template>
      </el-dialog>
      
      <!-- 保存模板对话框 -->
      <el-dialog
        v-model="saveTemplateDialogVisible"
        title="保存为模板"
        width="500px"
      >
        <el-form :model="templateForm" label-position="top">
          <el-form-item label="模板名称" required>
            <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
          </el-form-item>
          
          <el-form-item label="模板描述">
            <el-input 
              v-model="templateForm.description" 
              type="textarea" 
              placeholder="请输入模板描述" 
              :rows="3" 
            />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="saveTemplateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate" :loading="loading">保存</el-button>
        </template>
      </el-dialog>
      
      <!-- 加载模板对话框 -->
      <el-dialog
        v-model="loadTemplateDialogVisible"
        title="加载模板"
        width="600px"
      >
        <div v-if="templates.length === 0" class="empty-templates">
          <el-empty description="暂无可用模板" />
        </div>
        
        <el-table
          v-else
          :data="templates"
          style="width: 100%"
          @row-click="handleTemplateRowClick"
          highlight-current-row
        >
          <el-table-column prop="name" label="模板名称" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ new Date(scope.row.created_at).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="loadTemplate(scope.row)"
              >
                加载
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click.stop="deleteTemplateConfirm(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <template #footer>
          <el-button @click="loadTemplateDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import { ElMessage, ElLoading, ElMessageBox } from 'element-plus';
import { Download, PieChart } from '@element-plus/icons-vue';
import { getDataSources, getTables, getTableSchema, getTableData } from '@/api/datasource';
import { createChart as apiCreateChart } from '@/api/chart';
import { getChartTypes } from '@/api/chart';
import { 
  createTemplate, 
  getTemplates, 
  deleteTemplate, 
  getTemplate
} from '@/api/analytics_template';
import type { AnalyticsTemplate } from '@/api/analytics_template';

// 数据源
const dataSources = ref<any[]>([]);
const selectedDataSource = ref('');

// 数据表
const tables = ref<any[]>([]);
const selectedTables = ref<string[]>([]);
const tableSchemas = ref<Record<string, any>>({});
const selectedColumnsByTable = ref<Record<string, string[]>>({});

// JOIN关系
const joinRelationships = ref<any[]>([
  {
    leftTable: '',
    rightTable: '',
    leftColumn: '',
    rightColumn: '',
    type: 'inner'
  }
]);

// 组合表格数据
const combinedTableData = ref<any[]>([]);
const combinedTableColumns = ref<string[]>([]);

// 分析结果
const combinedData = ref<any[]>([]);
const showResults = ref(false);

// 图表表单
const chartForm = ref<any>({
  title: '',
  type: '',
  description: '',
  config: {
    xAxis: { field: '' },
    yAxis: { name: '' },
    seriesFields: [],
    series: [],
    nameField: '',
    valueField: '',
    xField: '',
    yField: '',
    columnFields: [],
    columns: []
  },
  data_source: null
});

const createChartDialogVisible = ref(false);
const loading = ref(false);
const chartRules = ref({
  title: [{ required: true, message: '请输入图表标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择图表类型', trigger: 'change' }]
});

// 模板相关
const templates = ref<AnalyticsTemplate[]>([]);
const saveTemplateDialogVisible = ref(false);
const loadTemplateDialogVisible = ref(false);
const templateForm = ref({
  name: '',
  description: ''
});

// 计算属性：是否有选择的列
const hasSelectedColumns = computed(() => {
  return Object.values(selectedColumnsByTable.value).some(columns => columns.length > 0);
});

// 计算属性：所有选择的列
const selectedColumns = computed(() => {
  const columns: any[] = [];
  
  Object.entries(selectedColumnsByTable.value).forEach(([tableName, columnNames]) => {
    const tableSchema = tableSchemas.value[tableName];
    if (tableSchema && tableSchema.columns) {
      columnNames.forEach(columnName => {
        const column = tableSchema.columns.find((col: any) => col.name === columnName);
        if (column) {
          columns.push({
            ...column,
            tableName
          });
        }
      });
    }
  });
  
  return columns;
});

// 初始化
const init = async () => {
  try {
    // 获取数据源列表
    const response = await getDataSources();
    dataSources.value = response; // 直接使用响应，不需要.data
  } catch (error) {
    console.error('获取数据源失败:', error);
    ElMessage.error('获取数据源失败');
  }
};

// 处理数据源变更
const handleDataSourceChange = async () => {
  if (!selectedDataSource.value) return;
  
  try {
    const loading = ElLoading.service({
      lock: true,
      text: '加载数据表...',
      background: 'rgba(0, 0, 0, 0.7)'
    });
    
    // 重置选择的表和列
    selectedTables.value = [];
    selectedColumnsByTable.value = {};
    tableSchemas.value = {};
    
    // 获取数据表列表
    const response = await getTables(selectedDataSource.value);
    tables.value = response.tables.map(table => ({
      name: table,
      label: table
    }));
    
    loading.close();
  } catch (error) {
    console.error('获取数据表失败:', error);
    ElMessage.error('获取数据表失败');
  }
};

// 处理表格变更
const handleTablesChange = async () => {
  // 重置选择的列
  selectedColumnsByTable.value = {};
  
  // 为每个选择的表初始化列选择
  for (const table of selectedTables.value) {
    selectedColumnsByTable.value[table] = [];
    
    // 如果还没有获取表结构，则获取
    if (!tableSchemas.value[table]) {
      try {
        const response = await getTableSchema(table, selectedDataSource.value);
        tableSchemas.value[table] = {
          table_name: response.table_name,
          columns: response.columns
        };
      } catch (error) {
        console.error(`获取表 ${table} 结构失败:`, error);
        ElMessage.error(`获取表 ${table} 结构失败`);
      }
    }
  }
  
  // 重置JOIN关系
  if (selectedTables.value.length > 1) {
    joinRelationships.value = [
      {
        leftTable: selectedTables.value[0],
        rightTable: selectedTables.value[1],
        leftColumn: '',
        rightColumn: '',
        type: 'inner'
      }
    ];
  } else {
    joinRelationships.value = [];
  }
};

// 获取表的列
const getTableColumns = (tableName: string) => {
  if (!tableName || !tableSchemas.value[tableName]) return [];
  return tableSchemas.value[tableName].columns || [];
};

// 添加JOIN关系
const addJoinRelationship = () => {
  joinRelationships.value.push({
    leftTable: '',
    rightTable: '',
    leftColumn: '',
    rightColumn: '',
    type: 'inner'
  });
};

// 移除JOIN关系
const removeJoinRelationship = (index: number) => {
  joinRelationships.value.splice(index, 1);
};

// 更新JOIN列选项
const updateJoinColumns = (index: number, side: 'left' | 'right') => {
  const join = joinRelationships.value[index];
  if (side === 'left') {
    join.leftColumn = '';
  } else {
    join.rightColumn = '';
  }
};

// 生成组合表格
const generateCombinedTable = async () => {
  if (!hasSelectedColumns.value) {
    ElMessage.warning('请至少选择一列');
    return;
  }
  
  try {
    const loading = ElLoading.service({
      lock: true,
      text: '生成结果...',
      background: 'rgba(0, 0, 0, 0.7)'
    });
    
    // 这里应该调用后端API来获取组合数据
    // 临时模拟数据
    combinedData.value = Array(10).fill(0).map((_, index) => {
      const row: Record<string, any> = {};
      selectedColumns.value.forEach(column => {
        row[column.name] = `${column.name}_${index}`;
      });
      return row;
    });
    
    showResults.value = true;
    loading.close();
    
    ElMessage.success('结果生成成功');
  } catch (error) {
    console.error('生成结果失败:', error);
    ElMessage.error('生成结果失败');
  }
};

// 导出Excel
const exportToExcel = () => {
  // 导出Excel的逻辑
  ElMessage.success('导出成功');
};

// 图表相关
const chartTypes = ref([
  { type: 'bar', name: '柱状图' },
  { type: 'line', name: '折线图' },
  { type: 'area', name: '面积图' },
  { type: 'pie', name: '饼图' },
  { type: 'scatter', name: '散点图' },
  { type: 'table', name: '表格' }
]);

const handleChartTypeChange = () => {
  // 根据图表类型初始化配置
  const type = chartForm.value.type;
  
  // 重置配置
  if (type === 'bar' || type === 'line' || type === 'area') {
    chartForm.value.config = {
      xAxis: { field: '' },
      yAxis: { name: '值' },
      seriesFields: [],
      series: []
    };
  } else if (type === 'pie') {
    chartForm.value.config = {
      nameField: '',
      valueField: '',
      series: []
    };
  } else if (type === 'scatter') {
    chartForm.value.config = {
      xField: '',
      yField: '',
      series: []
    };
  } else if (type === 'table') {
    chartForm.value.config = {
      columnFields: [],
      columns: []
    };
  } else {
    // 默认空配置
    chartForm.value.config = {};
  }
};

const handleSeriesChange = (values: string[]) => {
  // 处理Y轴字段变更的逻辑
  chartForm.value.config.seriesFields = values;
  chartForm.value.config.series = values.map((series: any) => ({
    name: series,
    field: series,
    // 添加表名信息
    tableName: getColumnTableName(series)
  }));
};

const handleColumnsChange = (values: string[]) => {
  // 处理表格列变更的逻辑
  chartForm.value.config.columns = values.map((column: any) => ({
    field: column,
    title: column,
    // 添加表名信息
    tableName: getColumnTableName(column)
  }));
};

const isNumeric = (fieldName: string) => {
  // 判断字段是否为数值类型
  const column = selectedColumns.value.find(col => col.name === fieldName);
  
  // 更宽松的数值类型判断，包括可能的数值类型名称
  const numericTypes = [
    'int', 'integer', 'tinyint', 'smallint', 'mediumint', 'bigint',
    'float', 'double', 'decimal', 'number', 'numeric', 'real',
    'money', 'smallmoney', 'currency'
  ];
  
  // 如果找不到列类型信息，默认允许选择
  if (!column || !column.type) return true;
  
  // 检查类型是否为数值类型
  const lowerType = column.type.toLowerCase();
  return numericTypes.some(type => lowerType.includes(type));
};

const showCreateChartDialog = () => {
  // 初始化图表表单
  chartForm.value = {
    title: '分析结果图表',
    type: '',
    description: '',
    config: {
      xAxis: { field: '' },
      yAxis: { name: '值' },
      seriesFields: [],
      series: [],
      nameField: '',
      valueField: '',
      xField: '',
      yField: '',
      columnFields: [],
      columns: []
    },
    data_source: {
      id: selectedDataSource.value,
      type: 'datasource'
    }
  };
  createChartDialogVisible.value = true;
};

const createChart = async () => {
  if (!chartForm.value.type) {
    ElMessage.warning('请选择图表类型');
    return;
  }
  
  loading.value = true;
  try {
    // 根据图表类型准备配置
    let finalConfig: any = { title: chartForm.value.title };
    
    if (chartForm.value.type === 'bar' || chartForm.value.type === 'line' || chartForm.value.type === 'area') {
      if (!chartForm.value.config.xAxis.field) {
        ElMessage.warning('请选择X轴字段');
        loading.value = false;
        return;
      }
      
      if (!chartForm.value.config.seriesFields || chartForm.value.config.seriesFields.length === 0) {
        ElMessage.warning('请选择Y轴字段');
        loading.value = false;
        return;
      }
      
      // 只保存元数据信息
      finalConfig = {
        title: chartForm.value.title,
        xAxis: { 
          field: chartForm.value.config.xAxis.field,
          // 添加表名信息
          tableName: getColumnTableName(chartForm.value.config.xAxis.field)
        },
        yAxis: { name: '值' },
        series: chartForm.value.config.series.map((series: any) => ({
          name: series.name,
          field: series.field,
          // 添加表名信息
          tableName: getColumnTableName(series.field)
        }))
      };
    } else if (chartForm.value.type === 'pie') {
      if (!chartForm.value.config.nameField) {
        ElMessage.warning('请选择名称字段');
        loading.value = false;
        return;
      }
      
      if (!chartForm.value.config.valueField) {
        ElMessage.warning('请选择数值字段');
        loading.value = false;
        return;
      }
      
      // 只保存元数据信息
      finalConfig = {
        title: chartForm.value.title,
        series: [{
          name: '数据系列',
          nameField: chartForm.value.config.nameField,
          valueField: chartForm.value.config.valueField,
          // 添加表名信息
          nameTableName: getColumnTableName(chartForm.value.config.nameField),
          valueTableName: getColumnTableName(chartForm.value.config.valueField)
        }]
      };
    } else if (chartForm.value.type === 'scatter') {
      if (!chartForm.value.config.xField) {
        ElMessage.warning('请选择X轴字段');
        loading.value = false;
        return;
      }
      
      if (!chartForm.value.config.yField) {
        ElMessage.warning('请选择Y轴字段');
        loading.value = false;
        return;
      }
      
      // 只保存元数据信息
      finalConfig = {
        title: chartForm.value.title,
        series: [{
          name: '数据系列',
          xField: chartForm.value.config.xField,
          yField: chartForm.value.config.yField,
          // 添加表名信息
          xTableName: getColumnTableName(chartForm.value.config.xField),
          yTableName: getColumnTableName(chartForm.value.config.yField)
        }]
      };
    } else if (chartForm.value.type === 'table') {
      if (!chartForm.value.config.columnFields || chartForm.value.config.columnFields.length === 0) {
        ElMessage.warning('请选择表格列');
        loading.value = false;
        return;
      }
      
      // 只保存元数据信息
      finalConfig = {
        title: chartForm.value.title,
        columns: chartForm.value.config.columns.map((column: any) => ({
          field: column.field,
          title: column.title,
          // 添加表名信息
          tableName: getColumnTableName(column.field)
        }))
      };
    }
    
    // 添加JOIN关系信息
    if (joinRelationships.value.length > 0) {
      finalConfig.joinRelationships = joinRelationships.value;
    }
    
    // 打印详细的请求数据
    console.log('创建图表配置:', JSON.stringify(finalConfig, null, 2));
    
    // 准备图表数据（只包含元数据，不包含实际数据）
    const chartData = {
      title: chartForm.value.title,
      description: chartForm.value.description,
      type: chartForm.value.type,
      config: finalConfig,
      data_source: chartForm.value.data_source,
      // 添加选择的表信息
      tables: selectedTables.value
    };
    
    console.log('发送图表数据:', JSON.stringify(chartData, null, 2));
    
    // 创建图表
    try {
      const response = await apiCreateChart(chartData);
      console.log('创建图表成功:', response);
      ElMessage.success('图表创建成功');
      createChartDialogVisible.value = false;
    } catch (apiError: any) {
      console.error('API调用失败:', apiError);
      
      // 尝试直接使用fetch发送请求
      if (apiError.message && apiError.message.includes('Network Error')) {
        try {
          console.log('尝试使用fetch重新发送请求');
          const fetchResponse = await fetch('/api/v1/charts', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(chartData)
          });
          
          if (fetchResponse.ok) {
            const data = await fetchResponse.json();
            console.log('fetch请求成功:', data);
            ElMessage.success('图表创建成功');
            createChartDialogVisible.value = false;
            return;
          } else {
            const errorText = await fetchResponse.text();
            console.error('fetch请求失败:', fetchResponse.status, errorText);
            throw new Error(`请求失败 [${fetchResponse.status}]: ${errorText}`);
          }
        } catch (fetchError) {
          console.error('fetch请求异常:', fetchError);
          throw fetchError;
        }
      } else {
        throw apiError;
      }
    }
  } catch (error: any) {
    console.error('创建图表失败:', error);
    
    // 显示详细错误信息
    if (error.response && error.response.data) {
      const errorDetail = error.response.data.detail || JSON.stringify(error.response.data);
      ElMessage.error(`创建图表失败: ${errorDetail}`);
    } else {
      ElMessage.error(`创建图表失败: ${error.message || '未知错误'}`);
    }
  } finally {
    loading.value = false;
  }
};

// 获取列所属的表名
const getColumnTableName = (columnName: string) => {
  for (const column of selectedColumns.value) {
    if (column.name === columnName) {
      return column.tableName;
    }
  }
  return '';
};

// 显示保存模板对话框
const showSaveTemplateDialog = () => {
  templateForm.value = {
    name: '',
    description: ''
  };
  saveTemplateDialogVisible.value = true;
};

// 保存模板
const saveTemplate = async () => {
  if (!templateForm.value.name) {
    ElMessage.warning('请输入模板名称');
    return;
  }
  
  try {
    loading.value = true;
    
    // 准备模板数据
    const templateData = {
      name: templateForm.value.name,
      description: templateForm.value.description,
      datasource_id: selectedDataSource.value,
      tables: selectedTables.value,
      columns: selectedColumnsByTable.value,
      join_relationships: joinRelationships.value
    };
    
    // 打印详细的请求数据
    console.log('发送模板数据:', JSON.stringify(templateData, null, 2));
    
    // 检查数据格式
    if (!Array.isArray(templateData.tables)) {
      console.error('表格数据不是数组:', templateData.tables);
      ElMessage.error('表格数据格式错误');
      return;
    }
    
    if (typeof templateData.columns !== 'object') {
      console.error('列数据不是对象:', templateData.columns);
      ElMessage.error('列数据格式错误');
      return;
    }
    
    // 保存模板到数据库
    try {
      const response = await createTemplate(templateData);
      console.log('保存模板成功:', response);
      ElMessage.success('模板保存成功');
      saveTemplateDialogVisible.value = false;
    } catch (apiError: any) {
      console.error('API调用失败:', apiError);
      
      // 尝试直接使用fetch发送请求
      if (apiError.message && apiError.message.includes('Network Error')) {
        try {
          console.log('尝试使用fetch重新发送请求');
          const fetchResponse = await fetch('/api/v1/analytics-templates', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(templateData)
          });
          
          if (fetchResponse.ok) {
            const data = await fetchResponse.json();
            console.log('fetch请求成功:', data);
            ElMessage.success('模板保存成功');
            saveTemplateDialogVisible.value = false;
            return;
          } else {
            const errorText = await fetchResponse.text();
            console.error('fetch请求失败:', fetchResponse.status, errorText);
            throw new Error(`请求失败 [${fetchResponse.status}]: ${errorText}`);
          }
        } catch (fetchError) {
          console.error('fetch请求异常:', fetchError);
          throw fetchError;
        }
      } else {
        throw apiError;
      }
    }
  } catch (error: any) {
    console.error('保存模板失败:', error);
    
    // 显示详细错误信息
    if (error.response && error.response.data) {
      const errorDetail = error.response.data.detail || JSON.stringify(error.response.data);
      ElMessage.error(`保存模板失败: ${errorDetail}`);
    } else {
      ElMessage.error(`保存模板失败: ${error.message || '未知错误'}`);
    }
  } finally {
    loading.value = false;
  }
};

// 显示加载模板对话框
const showTemplateDialog = async () => {
  try {
    loading.value = true;
    
    // 获取模板列表，设置较大的限制以获取所有模板
    const response = await getTemplates(selectedDataSource.value, 1000);
    templates.value = response;
    
    loadTemplateDialogVisible.value = true;
  } catch (error) {
    console.error('获取模板列表失败:', error);
    ElMessage.error('获取模板列表失败');
  } finally {
    loading.value = false;
  }
};

// 处理模板行点击
const handleTemplateRowClick = (row: AnalyticsTemplate) => {
  // 可以在这里预览模板
  console.log('选择模板:', row);
};

// 加载模板
const loadTemplate = async (template: AnalyticsTemplate) => {
  try {
    loading.value = true;
    
    // 设置选择的表
    selectedTables.value = template.tables;
    
    // 加载表结构
    for (const table of template.tables) {
      if (!tableSchemas.value[table]) {
        try {
          const response = await getTableSchema(table, selectedDataSource.value);
          tableSchemas.value[table] = {
            table_name: response.table_name,
            columns: response.columns
          };
        } catch (error) {
          console.error(`获取表 ${table} 结构失败:`, error);
          ElMessage.error(`获取表 ${table} 结构失败`);
        }
      }
    }
    
    // 设置选择的列
    selectedColumnsByTable.value = template.columns;
    
    // 设置JOIN关系
    if (template.join_relationships && template.join_relationships.length > 0) {
      joinRelationships.value = template.join_relationships;
    }
    
    loadTemplateDialogVisible.value = false;
    ElMessage.success('模板加载成功');
  } catch (error) {
    console.error('加载模板失败:', error);
    ElMessage.error('加载模板失败');
  } finally {
    loading.value = false;
  }
};

// 删除模板确认
const deleteTemplateConfirm = (template: AnalyticsTemplate) => {
  ElMessageBox.confirm(
    `确定要删除模板 "${template.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      deleteTemplateAction(template.id);
    })
    .catch(() => {
      // 取消删除
    });
};

// 删除模板
const deleteTemplateAction = async (id: string) => {
  try {
    loading.value = true;
    
    // 删除模板
    await deleteTemplate(id);
    
    // 更新模板列表
    templates.value = templates.value.filter(item => item.id !== id);
    
    ElMessage.success('模板删除成功');
  } catch (error) {
    console.error('删除模板失败:', error);
    ElMessage.error('删除模板失败');
  } finally {
    loading.value = false;
  }
};

// 初始化
init();
</script>

<style scoped>
.analytics-container {
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
  color: #666;
  font-size: 14px;
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

.table-columns {
  margin-bottom: 20px;
}

.table-columns h3 {
  margin-bottom: 10px;
  font-size: 16px;
}

.join-relationship {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.join-equals {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.add-join-btn {
  margin-top: 10px;
}

.result-card {
  margin-top: 20px;
}

.empty-templates {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}
</style> 