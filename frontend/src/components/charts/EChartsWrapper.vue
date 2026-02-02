<template>
  <div ref="chartRef" :style="{ width: width, height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';

interface Props {
  options: echarts.EChartsOption;
  width?: string;
  height?: string;
  theme?: string;
  initOptions?: echarts.EChartsInitOpts;
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '400px',
  theme: 'default',
  initOptions: () => ({})
});

const chartRef = ref<HTMLElement>();
const chartInstance = ref<echarts.ECharts>();

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;
  
  chartInstance.value = echarts.init(chartRef.value, props.theme, props.initOptions);
  chartInstance.value.setOption(props.options);
};

// 更新图表
const updateChart = () => {
  if (!chartInstance.value) return;
  chartInstance.value.setOption(props.options);
};

// 响应式调整
const resizeChart = () => {
  if (!chartInstance.value) return;
  chartInstance.value.resize();
};

// 监听选项变化
watch(() => props.options, updateChart, { deep: true });

// 监听尺寸变化
watch(() => [props.width, props.height], resizeChart);

// 生命周期
onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  window.removeEventListener('resize', resizeChart);
});

// 暴露方法给父组件
defineExpose({
  getInstance: () => chartInstance.value,
  resize: resizeChart
});
</script>
