<template>
  <EChartsWrapper :options="chartOption" :height="'400px'" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import EChartsWrapper from './EChartsWrapper.vue'
import type { EChartsOption } from 'echarts'

interface Props {
  data?: {
    time: string
    count: number
  }[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  title: '评论趋势分析'
})

const chartOption = computed<EChartsOption>(() => {
  return {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal' as const
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>评论数量: ${data.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.data.map(item => item.time),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '评论数量'
    },
    series: [{
      name: '评论数量',
      type: 'line',
      data: props.data.map(item => item.count),
      smooth: true,
      lineStyle: {
        color: '#5470c6',
        width: 3
      },
      itemStyle: {
        color: '#5470c6'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(84, 112, 198, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(84, 112, 198, 0.1)'
          }]
        }
      }
    }]
  }
})
</script>
