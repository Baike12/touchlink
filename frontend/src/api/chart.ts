import { get, post, put, del } from './index'

// 图表类型定义
export interface Chart {
  id: string
  title: string
  description?: string
  type: string
  config: any
  data_source?: any
  analysis_task_id?: string
  created_at: string
  updated_at: string
}

// 图表类型
export interface ChartType {
  type: string
  name: string
}

// 图表选项
export interface ChartOptions {
  options: any
}

// 创建图表请求
export interface ChartCreateRequest {
  title: string
  description?: string
  type: string
  config: any
  data_source?: any
  analysis_task_id?: string
}

// 更新图表请求
export interface ChartUpdateRequest {
  title?: string
  description?: string
  type?: string
  config?: any
  data_source?: any
}

// 获取图表列表
export function getCharts() {
  return get<Chart[]>('/v1/charts')
}

// 获取单个图表
export function getChart(id: string) {
  return get<Chart>(`/v1/charts/${id}`)
}

// 创建图表
export function createChart(data: ChartCreateRequest) {
  return post<Chart>('/v1/charts', data)
}

// 更新图表
export function updateChart(id: string, data: ChartUpdateRequest) {
  return put<Chart>(`/v1/charts/${id}`, data)
}

// 删除图表
export function deleteChart(id: string) {
  return del<void>(`/v1/charts/${id}`)
}

// 获取图表类型列表
export function getChartTypes() {
  return get<ChartType[]>('/v1/charts/types')
}

// 获取图表选项
export function getChartOptions(type: string) {
  return get<ChartOptions>(`/v1/charts/options/${type}`)
}

// 预览图表
export function previewChart(data: ChartCreateRequest) {
  return post<any>('/v1/charts/preview', data)
}

// 获取图表数据
export function getChartData(id: string) {
  return get<any>(`/v1/charts/${id}/data`)
} 