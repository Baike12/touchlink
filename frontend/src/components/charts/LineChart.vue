<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  chartData: {
    type: Array as () => Record<string, any>[],
    required: true
  },
  chartOptions: {
    type: Object,
    default: () => ({})
  }
});

const chartContainer = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return;
  
  // 创建图表实例
  chartInstance = echarts.init(chartContainer.value);
  
  // 更新图表
  updateChart();
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', handleResize);
};

// 更新图表
const updateChart = () => {
  if (!chartInstance) return;
  
  const { chartData, chartOptions } = props;
  
  // 添加调试信息
  console.log('折线图数据:', chartData);
  console.log('折线图配置:', chartOptions);
  
  // 如果没有数据，显示空图表
  if (!chartData || chartData.length === 0) {
    chartInstance.setOption({
      title: {
        text: typeof chartOptions.title === 'string' ? chartOptions.title : (chartOptions.title?.text || '折线图'),
        left: 'center'
      },
      tooltip: {
        formatter: '暂无数据'
      }
    });
    return;
  }
  
  // 默认配置
  const defaultOptions = {
    title: {
      text: typeof chartOptions.title === 'string' ? chartOptions.title : (chartOptions.title?.text || '折线图'),
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [] as any[],
      boundaryGap: false
    },
    yAxis: {
      type: 'value'
    },
    series: [] as any[]
  };
  
  try {
    // 合并配置
    const options = {
      ...defaultOptions
    };
    
    // 处理标题
    if (typeof chartOptions.title === 'string') {
      options.title.text = chartOptions.title;
    } else if (chartOptions.title && chartOptions.title.text) {
      options.title.text = chartOptions.title.text;
    }
    
    // 获取X轴字段名
    const firstItem = chartData[0];
    const xField = (chartOptions.xAxis?.field as string) || Object.keys(firstItem)[0];
    
    // 处理X轴数据
    options.xAxis.data = chartData.map(item => item[xField]);
    
    // 获取系列字段名
    let seriesFields: string[] = [];
    if (chartOptions.series && Array.isArray(chartOptions.series) && chartOptions.series.length > 0) {
      seriesFields = chartOptions.series.map((serie: any) => serie.field || serie.name);
    } else {
      // 如果没有指定系列，使用除X轴字段外的第一个字段
      const fields = Object.keys(firstItem);
      seriesFields = fields.filter(field => field !== xField).slice(0, 1);
    }
    
    // 处理系列数据
    options.series = seriesFields.map((field: string) => {
      const seriesItem = {
        name: field,
        type: 'line',
        data: chartData.map(item => item[field]),
        smooth: true
      };
      return seriesItem;
    });
    
    console.log('X轴数据:', options.xAxis.data);
    console.log('系列数据:', options.series);
    console.log('最终折线图配置:', options);
    
    // 设置图表选项
    chartInstance.setOption(options);
  } catch (error) {
    console.error('更新图表时发生错误:', error);
  }
};

// 处理窗口大小变化
const handleResize = () => {
  chartInstance?.resize();
};

// 监听数据变化
watch(() => props.chartData, updateChart, { deep: true });
watch(() => props.chartOptions, updateChart, { deep: true });

// 组件挂载时初始化图表
onMounted(() => {
  initChart();
});

// 组件卸载时销毁图表
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style> 