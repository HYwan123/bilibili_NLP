<template>
  <EChartsWrapper :options="chartOptions" :width="width" :height="height" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import EChartsWrapper from './EChartsWrapper.vue';
import type { EChartsOption } from 'echarts';

interface KeywordData {
  word: string;
  count: number;
}

interface Props {
  data?: KeywordData[];
  width?: string;
  height?: string;
  title?: string;
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '400px',
  title: '关键词分析'
});

const chartOptions = computed<EChartsOption>(() => {
  const data = props.data || [];
  const sortedData = [...data].sort((a, b) => b.count - a.count).slice(0, 15);
  
  return {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}: {c}次'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '出现次数',
      axisLabel: {
        rotate: 0
      }
    },
    yAxis: {
      type: 'category',
      data: sortedData.map(item => item.word),
      axisLabel: {
        interval: 0,
        rotate: 0,
        formatter: (value: string) => {
          return value.length > 10 ? value.substring(0, 10) + '...' : value;
        }
      }
    },
    series: [
      {
        name: '出现次数',
        type: 'bar',
        data: sortedData.map(item => item.count),
        itemStyle: {
          color: (params) => {
            const colors = [
              '#667eea', '#764ba2', '#f093fb', '#4ade80', '#fbbf24',
              '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
            ];
            return colors[params.dataIndex % colors.length];
          },
          borderRadius: [0, 5, 5, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };
});
</script>
