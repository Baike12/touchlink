import { get, post } from './index'

// 定义类型
export interface Column {
  name: string;
  type: string;
}

export interface TableForm {
  tableName: string;
  columns: Column[];
}

// 创建表
export const createTable = async (tableForm: TableForm) => {
  return post('/v1/user-tables', tableForm)
}

// 添加数据
export const addTableData = async (tableName: string, data: Record<string, any>) => {
  return post(`/v1/user-tables/${tableName}/data`, data)
}

// 获取表数据
export const getTableData = async (tableName: string) => {
  return get(`/v1/user-tables/${tableName}/data`)
}

// 获取所有用户表
export const getUserTables = async () => {
  return get('/v1/user-tables')
} 