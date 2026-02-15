#!/bin/bash
#================================================================
# AURIX 跨境哨兵 — 阿里云 ECS 一键部署脚本
# 
# 使用方法（在你的 Mac/Windows 本地电脑执行）：
#   chmod +x setup-ecs.sh
#   ./setup-ecs.sh
#
# 脚本会自动完成：
#   1. 连接到你的 ECS 服务器
#   2. 安装 Node.js 20、Nginx、PM2、Certbot
#   3. 克隆 GitHub 仓库并安装依赖
#   4. 配置 Nginx 反向代理
#   5. 启动后端 API 和仪表盘服务
#   6. 配置 HTTPS 证书（如有域名）
#
# 你只需要提供：
#   - ECS 服务器公网 IP
#   - ECS 登录密码（root 用户）
#   - GitHub 仓库地址（已预填）
#   - 域名（可选，用于 HTTPS）
#================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║   AURIX 跨境哨兵 — 阿里云 ECS 一键部署工具     ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ===== 收集信息 =====
echo -e "${YELLOW}请输入以下信息：${NC}"
echo ""

read -p "🖥️  ECS 服务器公网 IP 地址: " ECS_IP
if [ -z "$ECS_IP" ]; then
  echo -e "${RED}错误：IP 地址不能为空${NC}"
  exit 1
fi

read -p "🔑 ECS root 密码（输入时不显示）: " -s ECS_PASSWORD
echo ""
if [ -z "$ECS_PASSWORD" ]; then
  echo -e "${RED}错误：密码不能为空${NC}"
  exit 1
fi

GITHUB_REPO="https://github.com/dtt9696/aurixai-website.git"
echo -e "📦 GitHub 仓库: ${GREEN}${GITHUB_REPO}${NC}"

read -p "🌐 域名（没有请直接回车跳过，后续可配置）: " DOMAIN
read -p "📧 邮箱（用于 HTTPS 证书，没有域名可跳过）: " EMAIL

DASHBOARD_PORT=3001
API_PORT=3000

echo ""
echo -e "${CYAN}========== 配置确认 ==========${NC}"
echo -e "  ECS IP:    ${GREEN}${ECS_IP}${NC}"
echo -e "  仓库:      ${GREEN}${GITHUB_REPO}${NC}"
echo -e "  域名:      ${GREEN}${DOMAIN:-（暂不配置）}${NC}"
echo -e "  API 端口:  ${GREEN}${API_PORT}${NC}"
echo -e "  仪表盘端口: ${GREEN}${DASHBOARD_PORT}${NC}"
echo -e "${CYAN}==============================${NC}"
echo ""
read -p "确认以上信息正确？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
  echo "已取消部署"
  exit 0
fi

# ===== 检查 sshpass =====
if ! command -v sshpass &> /dev/null; then
  echo -e "${YELLOW}正在安装 sshpass（用于自动 SSH 登录）...${NC}"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install sshpass 2>/dev/null || brew install hudochenkov/sshpass/sshpass
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get install -y sshpass 2>/dev/null || sudo yum install -y sshpass
  fi
fi

# SSH 命令封装
SSH_CMD="sshpass -p '${ECS_PASSWORD}' ssh -o StrictHostKeyChecking=no root@${ECS_IP}"
SCP_CMD="sshpass -p '${ECS_PASSWORD}' scp -o StrictHostKeyChecking=no"

echo ""
echo -e "${GREEN}🚀 开始部署...${NC}"
echo ""

# ===== 生成远程安装脚本 =====
cat > /tmp/aurix-remote-setup.sh << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

echo "📦 [1/8] 更新系统包..."
apt-get update -qq
apt-get upgrade -y -qq

echo "📦 [2/8] 安装 Node.js 20..."
if ! command -v node &> /dev/null || [[ $(node -v | cut -d. -f1 | tr -d 'v') -lt 20 ]]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi
echo "   Node.js 版本: $(node -v)"
echo "   npm 版本: $(npm -v)"

echo "📦 [3/8] 安装 pnpm 和 PM2..."
npm install -g pnpm pm2 2>/dev/null
echo "   pnpm 版本: $(pnpm -v)"
echo "   PM2 版本: $(pm2 -v)"

echo "📦 [4/8] 安装 Nginx..."
apt-get install -y nginx
systemctl enable nginx
systemctl start nginx

echo "📦 [5/8] 安装 Git 和 Certbot..."
apt-get install -y git certbot python3-certbot-nginx

echo "📦 [6/8] 克隆项目代码..."
PROJECT_DIR="/opt/aurix"
if [ -d "$PROJECT_DIR" ]; then
  echo "   项目目录已存在，拉取最新代码..."
  cd "$PROJECT_DIR"
  git pull origin main
else
  git clone GITHUB_REPO_PLACEHOLDER "$PROJECT_DIR"
  cd "$PROJECT_DIR"
fi

echo "📦 [7/8] 安装依赖并构建..."
cd "$PROJECT_DIR"
pnpm install --frozen-lockfile 2>/dev/null || pnpm install
pnpm run build

echo "📦 [8/8] 配置 PM2 进程..."

# 创建 PM2 生态系统配置
cat > "$PROJECT_DIR/ecosystem.config.cjs" << 'PM2_CONFIG'
module.exports = {
  apps: [
    {
      name: "aurix-api",
      script: "dist/server/index.js",
      cwd: "/opt/aurix",
      env: {
        NODE_ENV: "production",
        PORT: "API_PORT_PLACEHOLDER",
        DASHBOARD_URL: "http://localhost:DASHBOARD_PORT_PLACEHOLDER"
      },
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      max_memory_restart: "500M",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      error_file: "/var/log/aurix/api-error.log",
      out_file: "/var/log/aurix/api-out.log",
      merge_logs: true
    }
  ]
};
PM2_CONFIG

# 创建日志目录
mkdir -p /var/log/aurix

# 替换端口占位符
sed -i "s/API_PORT_PLACEHOLDER/${API_PORT}/g" "$PROJECT_DIR/ecosystem.config.cjs"
sed -i "s/DASHBOARD_PORT_PLACEHOLDER/${DASHBOARD_PORT}/g" "$PROJECT_DIR/ecosystem.config.cjs"

# 停止旧进程并启动新进程
pm2 delete all 2>/dev/null || true
pm2 start "$PROJECT_DIR/ecosystem.config.cjs"
pm2 save
pm2 startup systemd -u root --hp /root 2>/dev/null || true

echo ""
echo "✅ 服务已启动！"
pm2 list

REMOTE_SCRIPT

# 替换占位符
sed -i "s|GITHUB_REPO_PLACEHOLDER|${GITHUB_REPO}|g" /tmp/aurix-remote-setup.sh
sed -i "s|API_PORT_PLACEHOLDER|${API_PORT}|g" /tmp/aurix-remote-setup.sh
sed -i "s|DASHBOARD_PORT_PLACEHOLDER|${DASHBOARD_PORT}|g" /tmp/aurix-remote-setup.sh

# ===== 生成 Nginx 配置 =====
if [ -n "$DOMAIN" ]; then
  # 有域名的配置
  cat > /tmp/aurix-nginx.conf << NGINX_CONF
# AURIX 跨境哨兵 Nginx 配置
server {
    listen 80;
    server_name ${DOMAIN};

    # API 服务
    location /api/ {
        proxy_pass http://127.0.0.1:${API_PORT}/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # tRPC 接口
    location /trpc/ {
        proxy_pass http://127.0.0.1:${API_PORT}/trpc/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:${API_PORT}/health;
    }

    # 默认首页
    location / {
        proxy_pass http://127.0.0.1:${API_PORT}/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
}
NGINX_CONF
else
  # 无域名的配置（直接用 IP 访问）
  cat > /tmp/aurix-nginx.conf << NGINX_CONF
# AURIX 跨境哨兵 Nginx 配置（IP 访问模式）
server {
    listen 80 default_server;
    server_name _;

    # API 服务
    location /api/ {
        proxy_pass http://127.0.0.1:${API_PORT}/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # tRPC 接口
    location /trpc/ {
        proxy_pass http://127.0.0.1:${API_PORT}/trpc/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:${API_PORT}/health;
    }

    # 默认首页
    location / {
        proxy_pass http://127.0.0.1:${API_PORT}/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
}
NGINX_CONF
fi

# ===== 生成 HTTPS 配置脚本 =====
cat > /tmp/aurix-setup-https.sh << HTTPS_SCRIPT
#!/bin/bash
# HTTPS 证书配置脚本
if [ -z "${DOMAIN}" ]; then
  echo "未配置域名，跳过 HTTPS 配置"
  echo "后续配置域名后，运行: certbot --nginx -d 你的域名"
  exit 0
fi

echo "🔒 配置 HTTPS 证书..."
certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos -m ${EMAIL:-admin@${DOMAIN}} --redirect
echo "✅ HTTPS 证书配置完成！"

# 设置自动续期
echo "⏰ 配置证书自动续期..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
echo "✅ 自动续期已配置（每天凌晨 3 点检查）"
HTTPS_SCRIPT

# ===== 上传文件到 ECS =====
echo -e "${CYAN}📤 上传部署脚本到 ECS...${NC}"
eval ${SCP_CMD} /tmp/aurix-remote-setup.sh root@${ECS_IP}:/tmp/aurix-remote-setup.sh
eval ${SCP_CMD} /tmp/aurix-nginx.conf root@${ECS_IP}:/tmp/aurix-nginx.conf
eval ${SCP_CMD} /tmp/aurix-setup-https.sh root@${ECS_IP}:/tmp/aurix-setup-https.sh

# ===== 执行远程安装 =====
echo -e "${CYAN}🔧 在 ECS 上执行安装（预计 3-5 分钟）...${NC}"
echo ""

eval ${SSH_CMD} << 'REMOTE_EXEC'
# 设置环境变量
export API_PORT=API_PORT_PLACEHOLDER
export DASHBOARD_PORT=DASHBOARD_PORT_PLACEHOLDER

# 执行安装脚本
chmod +x /tmp/aurix-remote-setup.sh
bash /tmp/aurix-remote-setup.sh

# 配置 Nginx
echo ""
echo "🌐 配置 Nginx..."
cp /tmp/aurix-nginx.conf /etc/nginx/sites-available/aurix
ln -sf /etc/nginx/sites-available/aurix /etc/nginx/sites-enabled/aurix
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "✅ Nginx 配置完成"

# 配置 HTTPS
chmod +x /tmp/aurix-setup-https.sh
bash /tmp/aurix-setup-https.sh

# 配置防火墙
echo ""
echo "🛡️  配置防火墙..."
ufw allow 80/tcp 2>/dev/null || true
ufw allow 443/tcp 2>/dev/null || true
ufw allow 22/tcp 2>/dev/null || true

# 最终验证
echo ""
echo "🔍 验证服务状态..."
sleep 3
curl -s http://localhost:${API_PORT}/health || echo "⚠️  API 服务启动中..."
echo ""
pm2 list
echo ""
echo "================================================"
echo "✅ 部署完成！"
echo "================================================"
REMOTE_EXEC

# 替换远程脚本中的占位符
eval ${SSH_CMD} "sed -i 's/API_PORT_PLACEHOLDER/${API_PORT}/g' /tmp/aurix-remote-setup.sh"
eval ${SSH_CMD} "sed -i 's/DASHBOARD_PORT_PLACEHOLDER/${DASHBOARD_PORT}/g' /tmp/aurix-remote-setup.sh"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🎉 AURIX 部署完成！                    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
if [ -n "$DOMAIN" ]; then
  echo -e "  🌐 API 地址:    ${GREEN}https://${DOMAIN}/trpc${NC}"
  echo -e "  💚 健康检查:    ${GREEN}https://${DOMAIN}/health${NC}"
else
  echo -e "  🌐 API 地址:    ${GREEN}http://${ECS_IP}/trpc${NC}"
  echo -e "  💚 健康检查:    ${GREEN}http://${ECS_IP}/health${NC}"
fi
echo ""
echo -e "${YELLOW}后续操作：${NC}"
echo -e "  1. 访问上面的健康检查地址，确认返回 {\"status\":\"ok\"}"
echo -e "  2. 如需配置域名，请在阿里云 DNS 添加 A 记录指向 ${ECS_IP}"
echo -e "  3. 配置域名后运行: ssh root@${ECS_IP} 'certbot --nginx -d 你的域名'"
echo -e "  4. 查看日志: ssh root@${ECS_IP} 'pm2 logs'"
echo -e "  5. 重启服务: ssh root@${ECS_IP} 'cd /opt/aurix && git pull && pnpm run build && pm2 restart all'"
echo ""
