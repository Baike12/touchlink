import { get, post, put, del } from './index'

// 看板类型定义
export interface Dashboard {
  id: string
  title: string
  description?: string
  layout?: any
  created_at: string
  updated_at: string
}

// 看板项目类型定义
export interface DashboardItem {
  id: string
  chart_id: string
  position_x: number
  position_y: number
  width: number
  height: number
  config?: any
  created_at: string
  updated_at: string
}

// 带图表信息的看板项目
export interface DashboardItemWithChart extends DashboardItem {
  chart: {
    id: string
    title: string
    type: string
    config: any
  }
}

// 带项目的看板
export interface DashboardWithItems extends Dashboard {
  items: DashboardItemWithChart[]
}

// 创建看板请求
export interface DashboardCreateRequest {
  title: string
  description?: string
  layout?: any
}

// 更新看板请求
export interface DashboardUpdateRequest {
  title?: string
  description?: string
  layout?: any
}

// 创建看板项目请求
export interface DashboardItemCreateRequest {
  chart_id: string
  position_x?: number
  position_y?: number
  width?: number
  height?: number
  config?: any
}

// 更新看板项目请求
export interface DashboardItemUpdateRequest {
  position_x?: number
  position_y?: number
  width?: number
  height?: number
  config?: any
}

// 获取看板列表
export function getDashboards() {
  return get<Dashboard[]>('/v1/dashboards')
}

// 获取单个看板
export function getDashboard(id: string) {
  return get<Dashboard>(`/v1/dashboards/${id}`)
}

// 获取带项目的看板
export function getDashboardWithItems(id: string) {
  return get<DashboardWithItems>(`/v1/dashboards/${id}/items`)
}

// 创建看板
export function createDashboard(data: DashboardCreateRequest) {
  return post<Dashboard>('/v1/dashboards', data)
}

// 更新看板
export function updateDashboard(id: string, data: DashboardUpdateRequest) {
  return put<Dashboard>(`/v1/dashboards/${id}`, data)
}

// 删除看板
export function deleteDashboard(id: string) {
  return del<void>(`/v1/dashboards/${id}`)
}

// 添加看板项目
export function addDashboardItem(dashboardId: string, data: DashboardItemCreateRequest) {
  return post<DashboardItem>(`/v1/dashboards/${dashboardId}/items`, data)
}

// 更新看板项目
export function updateDashboardItem(dashboardId: string, itemId: string, data: DashboardItemUpdateRequest) {
  return put<DashboardItem>(`/v1/dashboards/${dashboardId}/items/${itemId}`, data)
}

// 删除看板项目
export function deleteDashboardItem(dashboardId: string, itemId: string) {
  return del<void>(`/v1/dashboards/${dashboardId}/items/${itemId}`)
} 