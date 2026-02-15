# AURIX 跨境哨兵 — 阿里云 ECS 部署完整指南

**版本**: 1.0  
**日期**: 2026-02-15  
**作者**: Manus AI  
**适用项目**: aurixai-website（后端 API）+ aurixai-dashboard（前端仪表盘）

---

## 一、项目概述与架构

AURIX 跨境哨兵系统由两个独立项目组成，采用前后端分离架构部署在同一台阿里云 ECS 实例上。后端 API 服务基于 Node.js + Express + tRPC 构建，提供风险评估、邮件通知等核心业务接口；前端仪表盘基于 React + Vite 构建，提供用户行为分析可视化界面。Nginx 作为反向代理统一对外提供服务，同时负责静态资源托管和 HTTPS 终结。

| 组件 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 后端 API | Node.js + Express + tRPC + TypeScript | 3000 | 风险检查、订阅管理、邮件通知 |
| 前端仪表盘 | React 19 + Vite + Tailwind 4 + Recharts | 静态文件 | 用户行为分析仪表盘 |
| 反向代理 | Nginx | 80/443 | 静态资源托管 + API 反向代理 + HTTPS |
| 进程管理 | PM2 | — | Node.js 进程守护、自动重启 |

**推荐部署架构**：

```
用户请求 → 阿里云 CDN（可选）→ ECS Nginx（80/443）
                                    ├── /           → 前端静态文件（dist/public/）
                                    ├── /api/       → 后端 API（localhost:3000）
                                    └── /trpc/      → tRPC 接口（localhost:3000）
```

> **为什么选择 ECS 而非 OSS+CDN 或函数计算？** 由于项目包含 Node.js 后端服务（Express API、定时任务、邮件发送），需要持久运行的服务器进程，因此 ECS 是最合适的部署方案。纯前端部分可后续通过阿里云 CDN 加速。

---

## 二、ECS 实例准备

### 2.1 实例配置建议

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 实例规格 | ecs.t6-c1m2.large（2vCPU / 4GB） | 入门级够用，后续可弹性升配 |
| 操作系统 | Ubuntu 22.04 LTS | 长期支持版本，生态完善 |
| 系统盘 | 40GB SSD | 存放系统、代码和日志 |
| 带宽 | 5Mbps 按固定带宽 | 或按流量计费，视访问量而定 |
| 安全组 | 开放 22/80/443 端口 | SSH + HTTP + HTTPS |

### 2.2 安全组配置

登录阿里云控制台，进入 ECS 实例的安全组规则，确保以下端口已开放：

```
入方向规则：
  TCP 22    → 0.0.0.0/0（SSH，建议限制为你的 IP）
  TCP 80    → 0.0.0.0/0（HTTP）
  TCP 443   → 0.0.0.0/0（HTTPS）
```

### 2.3 SSH 连接到服务器

```bash
ssh root@<你的ECS公网IP>
```

如果使用密钥对登录：

```bash
ssh -i ~/.ssh/your-key.pem root@<你的ECS公网IP>
```

---

## 三、服务器环境搭建

### 3.1 系统更新与基础工具

```bash
# 更新系统包
apt update && apt upgrade -y

# 安装基础工具
apt install -y curl wget git build-essential nginx certbot python3-certbot-nginx
```

### 3.2 安装 Node.js 20 LTS

```bash
# 使用 NodeSource 官方源安装
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# 验证安装
node -v    # 应输出 v20.x.x
npm -v     # 应输出 10.x.x
```

### 3.3 安装 pnpm 和 PM2

```bash
# 安装 pnpm
npm install -g pnpm

# 安装 PM2 进程管理器
npm install -g pm2

# 验证
pnpm -v
pm2 -v
```

### 3.4 创建部署用户（推荐）

出于安全考虑，建议创建专用部署用户而非使用 root：

```bash
# 创建用户
adduser deploy
usermod -aG sudo deploy

# 切换到部署用户
su - deploy
```

---

## 四、项目部署

### 4.1 克隆后端项目

```bash
# 创建项目目录
mkdir -p /home/deploy/apps
cd /home/deploy/apps

# 克隆后端仓库
git clone https://github.com/dtt9696/aurixai-website.git
cd aurixai-website

# 安装依赖
pnpm install

# 构建 TypeScript
pnpm run build
```

**注意**：`package.json` 中的 `start` 脚本已修正为 `node dist/server/index.js`，确保生产模式可以正确启动。

### 4.2 配置环境变量

```bash
# 创建环境变量文件
cat > /home/deploy/apps/aurixai-website/.env << 'EOF'
NODE_ENV=production
PORT=3000

# 邮件服务配置（根据实际情况修改）
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
SMTP_PASS=your-password
SMTP_FROM=noreply@aurix.ai

# 其他配置
LOG_LEVEL=info
EOF
```

### 4.3 部署前端仪表盘

前端仪表盘已构建为静态文件，需要将构建产物复制到服务器：

```bash
# 在本地机器上，将前端构建产物打包上传
# 方式一：通过 scp 上传
cd /path/to/aurixai-dashboard
pnpm run build
scp -r dist/public/ deploy@<ECS-IP>:/home/deploy/apps/aurixai-dashboard/

# 方式二：在服务器上直接构建（如果仪表盘也在 Git 仓库中）
cd /home/deploy/apps
mkdir -p aurixai-dashboard
# 将构建好的 dist/public 目录内容放入此目录
```

> **提示**：前端仪表盘是纯静态文件（HTML + CSS + JS），不需要 Node.js 运行时，直接由 Nginx 托管即可。

### 4.4 使用 PM2 管理后端进程

```bash
cd /home/deploy/apps/aurixai-website

# 启动后端服务
pm2 start dist/server/index.js --name "aurix-api" --env production

# 查看运行状态
pm2 status

# 查看日志
pm2 logs aurix-api

# 设置开机自启
pm2 startup
pm2 save
```

PM2 常用管理命令：

| 命令 | 说明 |
|------|------|
| `pm2 start aurix-api` | 启动服务 |
| `pm2 stop aurix-api` | 停止服务 |
| `pm2 restart aurix-api` | 重启服务 |
| `pm2 reload aurix-api` | 零停机重载 |
| `pm2 logs aurix-api` | 查看日志 |
| `pm2 monit` | 实时监控面板 |

### 4.5 配置定时风险检查任务

```bash
# 编辑 crontab
crontab -e

# 添加每日早上 9:00 执行风险检查
0 9 * * * cd /home/deploy/apps/aurixai-website && /usr/bin/node dist/scripts/dailyRiskCheck.js >> logs/cron.log 2>&1
```

---

## 五、Nginx 反向代理配置

### 5.1 创建 Nginx 配置文件

```bash
cat > /etc/nginx/sites-available/aurix << 'NGINX'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 前端静态文件
    root /home/deploy/apps/aurixai-dashboard;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 后端 API 反向代理
    location /trpc/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 60s;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API 根路径
    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 前端路由 — SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
NGINX
```

### 5.2 启用配置并测试

```bash
# 创建软链接启用站点
ln -sf /etc/nginx/sites-available/aurix /etc/nginx/sites-enabled/

# 删除默认站点（可选）
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
nginx -t

# 重载 Nginx
systemctl reload nginx

# 确认 Nginx 正在运行
systemctl status nginx
```

### 5.3 验证部署

```bash
# 测试后端 API
curl http://localhost:3000/health
# 应返回: {"status":"ok","timestamp":"..."}

# 测试 Nginx 代理
curl http://localhost/health
# 应返回同样的结果

# 测试前端页面
curl -I http://localhost/
# 应返回 200 OK
```

---

## 六、域名配置

### 6.1 购买与备案

在阿里云控制台完成以下步骤：

1. **购买域名**：进入「域名注册」页面，搜索并购买你的域名（如 `aurix.ai` 或 `aurix.cn`）。
2. **实名认证**：根据要求完成域名持有者实名认证。
3. **ICP 备案**：进入「ICP 备案」页面，提交网站备案申请。这是在中国大陆使用域名的法律要求，通常需要 5-20 个工作日。

> **重要提示**：未完成 ICP 备案的域名无法在中国大陆正常解析。备案期间可以先使用 ECS 公网 IP 地址访问。

### 6.2 DNS 解析配置

备案通过后，在阿里云「云解析 DNS」中添加解析记录：

| 记录类型 | 主机记录 | 记录值 | TTL |
|----------|----------|--------|-----|
| A | @ | `<你的ECS公网IP>` | 600 |
| A | www | `<你的ECS公网IP>` | 600 |
| A | api | `<你的ECS公网IP>` | 600（可选，用于 API 子域名） |

添加完成后，等待 DNS 生效（通常几分钟到几小时），然后验证：

```bash
# 验证 DNS 解析
dig your-domain.com +short
# 应返回你的 ECS 公网 IP

ping your-domain.com
# 应能 ping 通
```

### 6.3 更新 Nginx 配置中的域名

将 Nginx 配置文件中的 `your-domain.com` 替换为你的实际域名：

```bash
sed -i 's/your-domain.com/实际域名/g' /etc/nginx/sites-available/aurix
nginx -t && systemctl reload nginx
```

---

## 七、HTTPS 证书配置

### 7.1 方案一：Let's Encrypt 免费证书（推荐）

使用 Certbot 自动获取和配置 Let's Encrypt 免费 SSL 证书：

```bash
# 获取证书并自动配置 Nginx
certbot --nginx -d your-domain.com -d www.your-domain.com

# 按提示操作：
# 1. 输入邮箱地址（用于证书到期提醒）
# 2. 同意服务条款
# 3. 选择是否重定向 HTTP → HTTPS（建议选择 2: Redirect）
```

Certbot 会自动修改 Nginx 配置，添加 SSL 证书路径和 HTTPS 重定向。

**自动续期**：Certbot 安装时已自动配置了 systemd timer，证书会在到期前自动续期。验证自动续期：

```bash
# 测试续期流程（不会真正续期）
certbot renew --dry-run

# 查看续期定时器状态
systemctl status certbot.timer
```

### 7.2 方案二：阿里云免费 SSL 证书

如果你更倾向于使用阿里云的证书服务：

1. 登录阿里云控制台，进入「SSL 证书」服务。
2. 点击「免费证书」→「创建证书」→「证书申请」。
3. 填写域名信息，完成 DNS 验证。
4. 下载证书文件（选择 Nginx 格式），得到 `.pem` 和 `.key` 文件。
5. 上传到服务器并配置 Nginx：

```bash
# 创建证书目录
mkdir -p /etc/nginx/ssl

# 上传证书文件后，修改 Nginx 配置
cat > /etc/nginx/sites-available/aurix-ssl << 'NGINX'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/nginx/ssl/your-domain.pem;
    ssl_certificate_key /etc/nginx/ssl/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS（可选，启用后浏览器会强制使用 HTTPS）
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 其余配置与 HTTP 版本相同...
    root /home/deploy/apps/aurixai-dashboard;
    index index.html;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /trpc/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
NGINX

# 启用并重载
ln -sf /etc/nginx/sites-available/aurix-ssl /etc/nginx/sites-enabled/aurix
nginx -t && systemctl reload nginx
```

---

## 八、自动化部署脚本

为了简化后续的代码更新流程，创建一键部署脚本：

```bash
cat > /home/deploy/deploy.sh << 'SCRIPT'
#!/bin/bash
set -e

echo "=========================================="
echo "  AURIX 跨境哨兵 - 自动部署脚本"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 后端部署
echo -e "${YELLOW}[1/5] 更新后端代码...${NC}"
cd /home/deploy/apps/aurixai-website
git pull origin main

echo -e "${YELLOW}[2/5] 安装依赖...${NC}"
pnpm install

echo -e "${YELLOW}[3/5] 构建后端...${NC}"
pnpm run build

echo -e "${YELLOW}[4/5] 重启后端服务...${NC}"
pm2 reload aurix-api

echo -e "${YELLOW}[5/5] 验证服务状态...${NC}"
sleep 2
curl -sf http://localhost:3000/health > /dev/null && echo -e "${GREEN}✅ 后端 API 运行正常${NC}" || echo "❌ 后端 API 启动失败"
curl -sf http://localhost/ > /dev/null && echo -e "${GREEN}✅ 前端页面正常${NC}" || echo "❌ 前端页面异常"

echo ""
echo -e "${GREEN}=========================================="
echo "  部署完成！"
echo "==========================================${NC}"
pm2 status
SCRIPT

chmod +x /home/deploy/deploy.sh
```

使用方式：

```bash
# 每次代码更新后执行
/home/deploy/deploy.sh
```

---

## 九、监控与运维

### 9.1 日志管理

```bash
# 查看后端 API 日志
pm2 logs aurix-api --lines 100

# 查看 Nginx 访问日志
tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log

# 查看风险检查定时任务日志
tail -f /home/deploy/apps/aurixai-website/logs/cron.log
```

### 9.2 PM2 监控

```bash
# 实时监控面板
pm2 monit

# 查看详细信息
pm2 show aurix-api

# 查看 CPU/内存使用
pm2 status
```

### 9.3 系统资源监控

```bash
# 实时资源监控
htop

# 磁盘使用
df -h

# 内存使用
free -h
```

### 9.4 阿里云云监控（推荐）

在阿里云控制台启用「云监控」服务，可以监控 ECS 实例的 CPU、内存、磁盘、网络等指标，并设置告警规则。建议配置以下告警：

| 告警项 | 阈值 | 通知方式 |
|--------|------|----------|
| CPU 使用率 | > 80% 持续 5 分钟 | 短信 + 邮件 |
| 内存使用率 | > 85% 持续 5 分钟 | 短信 + 邮件 |
| 磁盘使用率 | > 90% | 邮件 |
| HTTP 状态码 5xx | > 10 次/分钟 | 短信 + 邮件 |

---

## 十、安全加固

### 10.1 防火墙配置

```bash
# 安装 UFW
apt install -y ufw

# 配置规则
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# 启用防火墙
ufw enable
ufw status
```

### 10.2 SSH 安全加固

```bash
# 编辑 SSH 配置
vim /etc/ssh/sshd_config

# 建议修改：
# PermitRootLogin no          # 禁止 root 登录
# PasswordAuthentication no   # 禁止密码登录（使用密钥）
# MaxAuthTries 3              # 最大尝试次数

# 重启 SSH
systemctl restart sshd
```

### 10.3 自动安全更新

```bash
# 安装自动更新
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## 十一、可选优化：阿里云 CDN 加速

如果你的用户分布在全国各地，建议为前端静态资源配置阿里云 CDN：

1. 登录阿里云控制台，进入「CDN」服务。
2. 添加加速域名（如 `cdn.your-domain.com`）。
3. 源站类型选择「IP」，填写 ECS 公网 IP。
4. 配置 CNAME 解析。
5. 开启 HTTPS（使用之前申请的证书）。
6. 配置缓存规则：

| 文件类型 | 缓存时间 | 说明 |
|----------|----------|------|
| `.html` | 不缓存或 60s | 保证页面实时更新 |
| `.js`, `.css` | 1 年 | 文件名含 hash，内容变化时自动更新 |
| 图片、字体 | 30 天 | 静态资源长期缓存 |

---

## 十二、部署检查清单

在完成部署后，逐项检查以下内容确保一切正常：

| 检查项 | 命令/操作 | 预期结果 |
|--------|-----------|----------|
| Node.js 版本 | `node -v` | v20.x.x |
| PM2 进程状态 | `pm2 status` | aurix-api: online |
| 后端健康检查 | `curl localhost:3000/health` | `{"status":"ok"}` |
| Nginx 状态 | `systemctl status nginx` | active (running) |
| 前端页面 | 浏览器访问域名 | 仪表盘正常显示 |
| HTTPS | 浏览器地址栏 | 显示安全锁标志 |
| API 代理 | `curl https://域名/health` | `{"status":"ok"}` |
| 定时任务 | `crontab -l` | 显示风险检查任务 |
| 防火墙 | `ufw status` | 22/80/443 已开放 |
| 开机自启 | `pm2 startup` | PM2 已配置自启 |

---

## 十三、常见问题排查

**Q: 访问网站显示 502 Bad Gateway**

这通常意味着 Nginx 无法连接到后端服务。检查 PM2 进程是否正常运行：

```bash
pm2 status
pm2 logs aurix-api --lines 50
```

**Q: 前端页面加载后 API 请求失败**

检查浏览器控制台的网络请求，确认 API 请求路径是否正确。如果出现 CORS 错误，需要在后端 Express 中添加 CORS 中间件：

```bash
cd /home/deploy/apps/aurixai-website
pnpm add cors
```

**Q: Let's Encrypt 证书获取失败**

确保域名已正确解析到 ECS IP，且 80 端口可以从外部访问。Certbot 需要通过 HTTP 验证域名所有权。

**Q: 定时任务没有执行**

检查 crontab 配置和日志：

```bash
crontab -l
cat /home/deploy/apps/aurixai-website/logs/cron.log
```

---

## 十四、后续扩展建议

随着业务增长，可以考虑以下扩展方向：

1. **数据库升级**：将 JSON 文件存储迁移到阿里云 RDS（MySQL/PostgreSQL），提升数据可靠性和查询性能。
2. **负载均衡**：当单台 ECS 无法满足需求时，使用阿里云 SLB 实现多实例负载均衡。
3. **容器化部署**：使用 Docker + 阿里云容器服务 ACK，实现更灵活的部署和扩缩容。
4. **日志服务**：接入阿里云 SLS（日志服务），实现集中化日志管理和分析。
5. **微信集成**：前端仪表盘已支持移动端响应式设计，可直接嵌入微信公众号菜单。

---

## 附录：快速命令参考

```bash
# ===== 服务管理 =====
pm2 start aurix-api          # 启动后端
pm2 stop aurix-api           # 停止后端
pm2 restart aurix-api        # 重启后端
pm2 logs aurix-api           # 查看日志
systemctl restart nginx       # 重启 Nginx

# ===== 部署更新 =====
/home/deploy/deploy.sh        # 一键部署

# ===== 证书管理 =====
certbot renew --dry-run       # 测试证书续期
certbot certificates          # 查看证书状态

# ===== 监控 =====
pm2 monit                     # PM2 监控面板
htop                          # 系统资源监控
df -h                         # 磁盘使用
```
