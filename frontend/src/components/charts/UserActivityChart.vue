<template>
  <EChartsWrapper :options="chartOptions" :height="'400px'" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import EChartsWrapper from './EChartsWrapper.vue'
import type { EChartsOption } from 'echarts'

interface Props {
  data?: {
    username: string
    comment_count: number
  }[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  title: '用户活跃度分析'
})

const chartOptions = computed<EChartsOption>(() => {
  const sortedData = [...props.data].sort((a, b) => b.comment_count - a.comment_count).slice(0, 10)
  
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
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>评论数量: ${data.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: sortedData.map(item => item.username),
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
      type: 'bar',
      data: sortedData.map(item => item.comment_count),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: '#36cfc9'
          }, {
            offset: 1,
            color: '#13c2c2'
          }]
        }
      },
      emphasis: {
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0,
              color: '#5cdbd3'
            }, {
              offset: 1,
              color: '#36cfc9'
            }]
          }
        }
      }
    }]
  }
})
</script>
