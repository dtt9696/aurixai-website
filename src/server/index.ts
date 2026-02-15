import express from 'express';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { appRouter } from './api/root';
import { trackingService } from './services/trackingService';

const app = express();
const PORT = process.env.PORT || 3000;

// 添加 JSON 解析中间件
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// tRPC 中间件
app.use(
  '/trpc',
  createExpressMiddleware({
    router: appRouter,
    createContext: () => ({}),
  })
);

// 首页
app.get('/', (req, res) => {
  res.json({
    name: 'AURIX 跨境哨兵 API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      trpc: '/trpc',
      riskCheck: '/trpc/riskChecker.runCheck',
    },
  });
});

app.listen(PORT, () => {
  console.log(`🚀 AURIX 服务器启动成功`);
  console.log(`📍 监听端口: ${PORT}`);
  console.log(`🔗 API 地址: http://localhost:${PORT}/trpc`);
  console.log(`💚 健康检查: http://localhost:${PORT}/health`);

  // 启动事件追踪服务
  trackingService.start();
  console.log(`📊 事件追踪服务已启动`);
});

export default app;
