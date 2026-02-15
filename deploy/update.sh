#!/bin/bash
#================================================================
# AURIX 跨境哨兵 — 一键更新脚本
# 
# 使用方法：在本地电脑执行
#   ./update.sh
#
# 功能：拉取最新代码 → 重新构建 → 重启服务
#================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}AURIX 跨境哨兵 — 一键更新${NC}"
echo ""

read -p "🖥️  ECS 服务器公网 IP: " ECS_IP
read -p "🔑 ECS root 密码: " -s ECS_PASSWORD
echo ""

SSH_CMD="sshpass -p '${ECS_PASSWORD}' ssh -o StrictHostKeyChecking=no root@${ECS_IP}"

echo -e "${CYAN}🔄 正在更新...${NC}"

eval ${SSH_CMD} << 'REMOTE_UPDATE'
cd /opt/aurix
echo "📥 拉取最新代码..."
git pull origin main

echo "📦 安装依赖..."
pnpm install --frozen-lockfile 2>/dev/null || pnpm install

echo "🔨 重新构建..."
pnpm run build

echo "🔄 重启服务..."
pm2 restart all

echo ""
echo "✅ 更新完成！"
pm2 list
REMOTE_UPDATE

echo ""
echo -e "${GREEN}✅ 更新部署完成！${NC}"
echo -e "  💚 健康检查: ${GREEN}http://${ECS_IP}/health${NC}"
