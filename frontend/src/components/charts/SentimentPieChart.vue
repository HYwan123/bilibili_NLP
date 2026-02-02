<template>
  <EChartsWrapper :options="chartOptions" :width="width" :height="height" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import EChartsWrapper from './EChartsWrapper.vue';
import type { EChartsOption } from 'echarts';

interface Props {
  data?: {
    positive: number;
    neutral: number;
    negative: number;
  };
  width?: string;
  height?: string;
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '400px'
});

const chartOptions = computed<EChartsOption>(() => {
  const data = props.data || { positive: 0, neutral: 0, negative: 0 };
  const total = data.positive + data.neutral + data.negative;
  
  return {
    title: {
      text: '情感分析分布',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 10,
      data: ['正面', '中性', '负面']
    },
    series: [
      {
        name: '情感分析',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c} ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: [
          {
            value: data.positive,
            name: '正面',
            itemStyle: { color: '#4ade80' }
          },
          {
            value: data.neutral,
            name: '中性',
            itemStyle: { color: '#fbbf24' }
          },
          {
            value: data.negative,
            name: '负面',
            itemStyle: { color: '#ef4444' }
          }
        ]
      }
    ]
  };
});
</script>
