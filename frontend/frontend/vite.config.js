import { defineConfig } from 'vite';
import plugin from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [plugin()],
    server: {
        port: 49691,
        // 只有在本地 npm run dev 时生效，Docker 里的 Nginx 不用这个。
        proxy: {
            '/api': {
                // 指向docker-compose映射到宿主机的端口8081。
                target: 'http://localhost:8081',
                changeOrigin: true,
                // 如果你的后端 Django 路由需要 /api 前缀，就不要重写(rewrite)路径
                // 如果后端不需要 /api 前缀，则取消注释下面这行：
                // rewrite: (path) => path.replace(/^\/api/, '') 
            }
        }
    }
})