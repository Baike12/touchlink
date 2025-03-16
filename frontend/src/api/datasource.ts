import { get, post, del } from './index'

// 数据源类型
export interface DataSourceConfig {
  type: string
  host: string
  port: number
  user: string
  password: string
  database: string
}

export interface DataSourceCreateRequest {
  name: string
  type: string
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
  return get<string[]>('/v1/datasources/types')
}

// 测试数据源连接
export function testDataSourceConnection(config: DataSourceConfig) {
  return post<DataSourceResponse>('/v1/datasources/test', config)
}

// 连接数据源
export function connectDataSource(config: DataSourceConfig) {
  return post<DataSourceResponse>('/v1/datasources/connect', config)
}

// 保存数据源
export function saveDataSource(request: DataSourceCreateRequest) {
  return post<DataSourceDetail>('/v1/datasources', request)
}

// 获取表列表
export function getTables(datasourceId?: string) {
  // 如果没有数据源ID，则使用当前会话中的临时连接
  const url = datasourceId 
    ? `/v1/datasources/${datasourceId}/tables` 
    : `/v1/datasources/session/tables`;
  console.log('请求表列表URL:', url);
  return get<TableListResponse>(url);
}

// 获取表结构
export function getTableSchema(tableName: string, datasourceId?: string) {
  // 如果没有数据源ID，则使用当前会话中的临时连接
  const url = datasourceId
    ? `/v1/datasources/${datasourceId}/tables/${tableName}/schema`
    : `/v1/datasources/tables/${tableName}/schema`;
  return get<TableSchemaResponse>(url);
}

// 获取表数据
export function getTableData(tableName: string, limit: number = 100, datasourceId?: string) {
  // 如果没有数据源ID，则使用当前会话中的临时连接
  const url = datasourceId
    ? `/v1/datasources/${datasourceId}/tables/${tableName}/data`
    : `/v1/datasources/tables/${tableName}/data`;
  return get<TableDataResponse>(`${url}?limit=${limit}`);
}

// 获取所有数据源
export function getDataSources() {
  return get<DataSourceDetail[]>('/v1/datasources')
}

// 获取数据源详情
export function getDataSourceDetail(id: string) {
  return get<DataSourceDetail>(`/v1/datasources/${id}`)
}

// 删除数据源
export function deleteDataSource(id: string) {
  return del(`/v1/datasources/${id}`)
} 