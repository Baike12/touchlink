import axios from 'axios'

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
  const response = await axios.post('/api/v1/user-tables', tableForm)
  return response.data
}

// 添加数据
export const addTableData = async (tableName: string, data: Record<string, any>) => {
  const response = await axios.post(`/api/v1/user-tables/${tableName}/data`, data)
  return response.data
}

// 获取表数据
export const getTableData = async (tableName: string) => {
  const response = await axios.get(`/api/v1/user-tables/${tableName}/data`)
  return response.data
}

// 获取所有用户表
export const getUserTables = async () => {
  const response = await axios.get('/api/v1/user-tables')
  return response.data
} 