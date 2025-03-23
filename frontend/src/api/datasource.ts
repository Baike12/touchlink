import { get, post, del } from './index'

// 数据源类型
export interface BaseDataSourceConfig {
  type: 'mysql' | 'mongodb' | 'excel'
}

export interface DatabaseConfig extends BaseDataSourceConfig {
  type: 'mysql' | 'mongodb'
  host: string
  port: number
  user: string
  password: string
  database: string
}

export interface ExcelConfig extends BaseDataSourceConfig {
  type: 'excel'
  file_path: string
  table_name: string
}

export type DataSourceConfig = DatabaseConfig | ExcelConfig

export interface DataSourceCreateRequest {
  name: string
  type: 'mysql' | 'mongodb' | 'excel'
  config: DataSourceConfig
}

export interface DataSourceResponse {
  id?: string
  type: string
  name: string
  status: string
  message?: string
}

export interface DataSourceDetail {
  id: string
  name: string
  type: string
  config?: DataSourceConfig
  created_at: string
  updated_at: string
}

export interface TableListResponse {
  tables: string[]
}

export interface TableColumn {
  name: string
  type: string
  nullable: boolean
  default?: any
  primary_key: boolean
}

export interface TableSchemaResponse {
  table_name: string
  columns: TableColumn[]
}

export interface TableDataResponse {
  columns: string[]
  data: Record<string, any>[]
}

// 获取支持的数据源类型
export function getDataSourceTypes() {
  return get<string[]>('/datasources/types')
}

// 测试数据源连接
export function testDataSourceConnection(config: DataSourceConfig) {
  return post<DataSourceResponse>('/datasources/test', config)
}

// 连接数据源
export function connectDataSource(config: DataSourceConfig) {
  return post<DataSourceResponse>('/datasources/connect', config)
}

// 保存数据源
export function saveDataSource(request: DataSourceCreateRequest) {
  return post<DataSourceDetail>('/datasources', request)
}

// 获取表列表
export function getTables(datasourceId?: string) {
  // 如果没有数据源ID，则使用当前会话中的临时连接
  const url = datasourceId 
    ? `/datasources/${datasourceId}/tables` 
    : `/datasources/session/tables`;
  console.log('请求表列表URL:', url);
  return get<TableListResponse>(url);
}

// 获取表结构
export function getTableSchema(tableName: string, datasourceId?: string) {
  // 如果没有数据源ID，则使用当前会话中的临时连接
  const url = datasourceId
    ? `/datasources/${datasourceId}/tables/${tableName}/schema`
    : `/datasources/tables/${tableName}/schema`;
  return get<TableSchemaResponse>(url);
}

// 获取表数据
export function getTableData(tableName: string, limit: number = 100, datasourceId?: string) {
  // 如果没有数据源ID，则使用当前会话中的临时连接
  const url = datasourceId
    ? `/datasources/${datasourceId}/tables/${tableName}/data`
    : `/datasources/tables/${tableName}/data`;
  return get<TableDataResponse>(`${url}?limit=${limit}`);
}

// 获取所有数据源
export function getDataSources() {
  return get<DataSourceDetail[]>('/datasources')
}

// 获取数据源详情
export function getDataSourceDetail(id: string) {
  return get<DataSourceDetail>(`/datasources/${id}`)
}

// 删除数据源
export function deleteDataSource(id: string) {
  return del(`/datasources/${id}`)
}

// 上传Excel文件
export function uploadExcelFile(formData: FormData) {
  return post<{
    file_path: string
    table_name: string
    original_filename: string
    message: string
  }>('/upload/excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 