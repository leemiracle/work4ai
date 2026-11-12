# batch-028 semantic data (win32-process: koffi lazy loader + tsconfig)
BATCH = {
 'files': {
  'packages/subprocess/win32-process/src/koffi.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '进程域对 koffi CommonJS 入口的惰性访问：requireKoffi 在首次 Win32 原生操作时才加载 koffi（避免未用 FFI 的进程付出加载代价），并导出 Koffi 运行时类型。',
   'tags': ['lazy-loading', 'ffi', 'koffi']},
  'packages/subprocess/win32-process/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-win32-process 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
 },
 'extra_edges': [],
}
