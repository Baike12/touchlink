import { get, post, put, del } from './index'

// 模板类型
export interface AnalyticsTemplate {
  id: string
  name: string
  description?: string
  datasource_id: string
  tables: string[]
  columns: Record<string, string[]>
  join_relationships?: any[]
  user_id: string
  created_at: string
  updated_at: string
}

// 创建模板请求
export interface CreateTemplateRequest {
  name: string
  description?: string
  datasource_id: string
  tables: string[]
  columns: Record<string, string[]>
  join_relationships?: any[]
}

// 更新模板请求
export interface UpdateTemplateRequest {
  name?: string
  description?: string
  tables?: string[]
  columns?: Record<string, string[]>
  join_relationships?: any[]
}

// 创建模板
export function createTemplate(template: CreateTemplateRequest) {
  return post<AnalyticsTemplate>('/v1/analytics-templates', template)
}

// 获取模板列表
export function getTemplates(datasourceId?: string, limit: number = 1000) {
  const url = datasourceId 
    ? `/v1/analytics-templates?datasource_id=${datasourceId}&limit=${limit}`
    : `/v1/analytics-templates?limit=${limit}`
  return get<AnalyticsTemplate[]>(url)
}

// 获取模板详情
export function getTemplate(id: string) {
  return get<AnalyticsTemplate>(`/v1/analytics-templates/${id}`)
}

// 更新模板
export function updateTemplate(id: string, template: UpdateTemplateRequest) {
  return put<AnalyticsTemplate>(`/v1/analytics-templates/${id}`, template)
}

// 删除模板
export function deleteTemplate(id: string) {
  return del(`/v1/analytics-templates/${id}`)
} 