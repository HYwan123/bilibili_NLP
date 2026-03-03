import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export const useLayoutStore = defineStore('layout', () => {
  const isCollapse = ref(false);
  const theme = ref(localStorage.getItem('theme') || 'light');

  function toggleCollapse() {
    isCollapse.value = !isCollapse.value;
  }

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  }

  // 监听主题变化并应用到 html 标签
  watch(theme, (newTheme) => {
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  }, { immediate: true });

  function applyTheme(t: string) {
    const html = document.documentElement;
    if (t === 'dark') {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  }

  return { isCollapse, theme, toggleCollapse, toggleTheme };
});
