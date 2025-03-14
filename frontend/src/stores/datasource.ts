import { defineStore } from 'pinia'
import { 
  getDataSourceTypes, 
  testDataSourceConnection, 
  connectDataSource,
  getTables,
  getTableSchema,
  type DataSourceConfig,
  type DataSourceResponse,
  type TableListResponse,
  type TableSchemaResponse
} from '../api/datasource'

export const useDataSourceStore = defineStore('datasource', {
  state: () => ({
    // 支持的数据源类型
    supportedTypes: [] as string[],
    
    // 当前连接的数据源
    currentDataSource: null as DataSourceResponse | null,
    
    // 表列表
    tables: [] as string[],
    
    // 表结构信息
    tableSchemas: {} as Record<string, TableSchemaResponse>,
    
    // 加载状态
    loading: {
      types: false,
      connection: false,
      tables: false,
      schema: false
    }
  }),
  
  actions: {
    // 获取支持的数据源类型
    async fetchDataSourceTypes() {
      this.loading.types = true
      try {
        console.log('开始获取数据源类型')
        const types = await getDataSourceTypes()
        console.log('获取到数据源类型:', types)
        this.supportedTypes = types
      } catch (error) {
        console.error('获取数据源类型失败:', error)
        // 不抛出错误，让组件继续使用默认值
      } finally {
        this.loading.types = false
      }
    },
    
    // 测试数据源连接
    async testConnection(config: DataSourceConfig) {
      this.loading.connection = true
      try {
        console.log('开始测试数据源连接:', config)
        const response = await testDataSourceConnection(config)
        console.log('测试数据源连接结果:', response)
        return response
      } catch (error) {
        console.error('测试数据源连接失败:', error)
        // 返回一个错误响应，而不是抛出错误
        return {
          type: config.type,
          name: `${config.host}:${config.port}/${config.database}`,
          status: 'error',
          message: error instanceof Error ? error.message : '未知错误'
        } as DataSourceResponse
      } finally {
        this.loading.connection = false
      }
    },
    
    // 连接数据源
    async connect(config: DataSourceConfig) {
      this.loading.connection = true
      try {
        const response = await connectDataSource(config)
        this.currentDataSource = response
        
        // 连接成功后获取表列表
        if (response.status === 'success') {
          await this.fetchTables()
        }
        
        return response
      } catch (error) {
        console.error('连接数据源失败:', error)
        throw error
      } finally {
        this.loading.connection = false
      }
    },
    
    // 获取表列表
    async fetchTables() {
      if (!this.currentDataSource) {
        return
      }
      
      this.loading.tables = true
      try {
        const response = await getTables()
        this.tables = response.tables
      } catch (error) {
        console.error('获取表列表失败:', error)
      } finally {
        this.loading.tables = false
      }
    },
    
    // 获取表结构
    async fetchTableSchema(tableName: string) {
      if (!this.currentDataSource) {
        return
      }
      
      this.loading.schema = true
      try {
        const schema = await getTableSchema(tableName)
        this.tableSchemas[tableName] = schema
        return schema
      } catch (error) {
        console.error(`获取表${tableName}结构失败:`, error)
      } finally {
        this.loading.schema = false
      }
    },
    
    // 断开连接
    disconnect() {
      this.currentDataSource = null
      this.tables = []
      this.tableSchemas = {}
    }
  }
}) 