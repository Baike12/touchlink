import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    
    // 如果是文件下载，直接返回
    if (response.headers['content-type']?.includes('application/octet-stream')) {
      return response
    }
    
    // 如果返回的是二进制数据，直接返回
    if (response.data instanceof Blob) {
      return response
    }
    
    // 处理业务错误
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      
      // 处理特定错误码
      if (res.code === 401) {
        // 未认证，可以跳转到登录页
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  (error) => {
    console.error('响应错误:', error)
    
    // 详细记录错误信息
    if (error.response) {
      const { status, data, config } = error.response
      console.error(`请求失败 [${status}]:`, {
        url: config.url,
        method: config.method,
        data: config.data,
        response: data
      })
      
      // 显示错误消息
      if (data && data.detail) {
        ElMessage.error(`请求失败: ${data.detail}`)
      } else if (data && typeof data === 'object') {
        ElMessage.error(`请求失败 [${status}]: ${JSON.stringify(data)}`)
      } else {
        ElMessage.error(`请求失败 [${status}]`)
      }
      
      // 处理特定状态码
      if (status === 401) {
        // 未认证，可以跳转到登录页
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('请求超时或网络错误:', error.request)
      ElMessage.error('请求超时或网络错误，请稍后重试')
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message)
      ElMessage.error(`请求错误: ${error.message}`)
    }
    
    return Promise.reject(error)
  }
)

// 封装GET请求
export function get<T>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.get(url, { params, ...config })
}

// 封装POST请求
export function post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.post(url, data, config)
}

// 封装PUT请求
export function put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.put(url, data, config)
}

// 封装DELETE请求
export function del<T>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
  return service.delete(url, { params, ...config })
}

// 导出axios实例
export default service 