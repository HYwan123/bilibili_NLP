<template>
  <EChartsWrapper :options="chartOptions" :width="width" :height="height" />
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import EChartsWrapper from './EChartsWrapper.vue';
import type { EChartsOption } from 'echarts';
import 'echarts-wordcloud';

interface KeywordData {
  word: string;
  count: number;
}

interface Props {
  data?: KeywordData[];
  title?: string;
  width?: string;
  height?: string;
  maxWords?: number;
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '400px',
  maxWords: 50,
  title: '关键词词云'
});

const chartOptions = computed<EChartsOption>(() => {
  const data = props.data || [];
  
  // 格式化数据为词云需要的格式
  const wordCloudData = data
    .slice(0, props.maxWords)
    .map(item => ({
      name: item.word,
      value: item.count
    }));

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
      trigger: 'item',
      formatter: '{b}: {c}'
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '100%',
        height: '100%',
        right: null,
        bottom: null,
        sizeRange: [12, 60],
        rotationRange: [-45, 45],
        rotationStep: 45,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: function () {
            return 'rgb(' + [
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160)
            ].join(',') + ')';
          }
        },
        emphasis: {
          focus: 'self',
          textStyle: {
            shadowBlur: 10,
            shadowColor: '#333'
          }
        },
        data: wordCloudData
      }
    ]
  };
});
</script>
