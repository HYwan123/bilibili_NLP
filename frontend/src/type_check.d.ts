declare module '*.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// markdown-it 类型定义
declare module 'markdown-it' {
  const MarkdownIt: any
  export default MarkdownIt
}
