# 前端目录结构说明文档
## 目录结构
```text
admin-frontend/
├── public/
├── src/
│   ├── api/                 # API 接口层 (对应 Django Apps的每一个视图路由)
│   ├── assets/              # 静态资源
│   ├── components/          # 全局通用组件
│   ├── layout/              # 后台整体布局
│   │   ├── components/      # Sidebar, Navbar, AppMain
│   │   └── index.vue
│   ├── router/              # 路由配置 (权限路由)
│   ├── storage/             # Pinia 状态管理
│   ├── utils/               # 工具类 (Axios, Coordinate Transform)
│   ├── views/               # 页面视图
│   │   ├── map-editor/
│   │   ├── event-management/
│   │   ├── area-management/
│   │   ├── facility-management/
│   │   └── login&register/
│   ├── App.vue
│   └── main.js
├── .env.development
├── .env.production
├── package.json
├── vite.config.js
└──...
```
## 目录说明
 1. api，每个文件和每个视图集一一对应，存放直接向后端发送请求的函数，相当于对后端的接口进行封装，方便调用
 2. assets，存放诸如图片、图标等静态资源
 3. components，存放可复用的 UI 组件，可供 views 下的页面引用。
 4. layout，控制系统的整体框架。后台管理系统通常是“左侧菜单 + 顶部导航 + 中间内容区”的结构。会作用于每一个页面。
 5. router，定义 URL 地址到 views 文件的映射关系
 6. storage，存放全局共享数据和一些缓存数据，比如前端绘图界面的状态、或是缓存的登录管理员信息。
 7. utils，存放纯JavaScript逻辑，不包含任何 UI 代码（HTML/CSS）。抽象成函数便于前端调用。
 8. views，存放页面代码文件夹。一个子文件夹对应浏览器的一个 URL 路径及其下的子路径，带有页面中具体的逻辑js、页面vue、样式CSS等文件。