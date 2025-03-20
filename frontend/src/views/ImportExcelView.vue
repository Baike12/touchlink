<template>
  <div class="import-excel-container">
    <div class="page-header">
      <h1 class="page-title">从Excel导入</h1>
      <p class="page-description">
        上传Excel文件并导入到数据库中。支持.xls、.xlsx和.xlsm格式。
      </p>
    </div>

    <div class="card-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>选择Excel文件</span>
          </div>
        </template>

        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="120px"
          class="upload-form"
        >
          <el-form-item label="Excel文件" prop="file">
            <el-upload
              class="excel-uploader"
              :auto-upload="false"
              :show-file-list="true"
              :limit="1"
              :on-change="handleFileChange"
              :on-exceed="handleExceed"
              accept=".xls,.xlsx,.xlsm"
            >
              <el-button type="primary">选择Excel文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  只能上传 xls/xlsx/xlsm 文件
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleUpload" :loading="loading">
              上传并导入
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 导入历史 -->
      <el-card v-if="importHistory.length > 0" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>导入历史</span>
          </div>
        </template>

        <el-table :data="importHistory" style="width: 100%">
          <el-table-column prop="fileName" label="文件名" />
          <el-table-column prop="tableName" label="数据表名" />
          <el-table-column prop="importTime" label="导入时间" />
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance, UploadFile } from 'element-plus'
import { ElMessage, ElNotification } from 'element-plus'
import { uploadExcelFile } from '@/api/datasource'

// 表单引用
const formRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)

// 表单数据
const formData = ref({
  file: null as File | null
})

// 表单验证规则
const formRules = {
  file: [{ required: true, message: '请选择Excel文件', trigger: 'change' }]
}

// 导入历史
const importHistory = ref<Array<{
  fileName: string
  tableName: string
  importTime: string
  status: string
}>>([])

// 处理文件选择
const handleFileChange = (uploadFile: UploadFile) => {
  formData.value.file = uploadFile.raw || null
}

// 处理超出文件数限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 处理文件上传
const handleUpload = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        if (!formData.value.file) {
          ElMessage.error('请选择Excel文件')
          return
        }
        
        const response = await uploadExcelFile(formData.value.file)
        
        // 添加到导入历史
        importHistory.value.unshift({
          fileName: formData.value.file.name,
          tableName: response.table_name,
          importTime: new Date().toLocaleString(),
          status: '成功'
        })
        
        ElNotification({
          title: '上传成功',
          message: response.message,
          type: 'success'
        })
        
        // 重置表单
        formRef.value.resetFields()
        
      } catch (error: any) {
        console.error('上传失败:', error)
        
        // 添加到导入历史
        if (formData.value.file) {
          importHistory.value.unshift({
            fileName: formData.value.file.name,
            tableName: '-',
            importTime: new Date().toLocaleString(),
            status: '失败'
          })
        }
        
        ElNotification({
          title: '上传失败',
          message: error.message || '上传Excel文件失败',
          type: 'error'
        })
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.import-excel-container {
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
  color: #606266;
}

.card-container {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-form {
  max-width: 600px;
  margin: 0 auto;
}

.excel-uploader {
  text-align: center;
  padding: 20px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color .3s;
}

.excel-uploader:hover {
  border-color: #409EFF;
}

.el-upload__tip {
  font-size: 12px;
  color: #606266;
  margin-top: 7px;
}
</style> 