#!/bin/bash

# AI智能客服框架 - Docker启动脚本

set -e

echo "=========================================="
echo "  AI智能客服框架 - Docker启动脚本"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker未安装，请先安装Docker"
    echo "   安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose未安装，请先安装"
    echo "   安装指南: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "⚠️  警告: config.json不存在，将使用Docker默认配置"
    if [ -f "config.docker.json" ]; then
        cp config.docker.json config.json
        echo "✅ 已复制Docker默认配置到config.json"
        echo "   请编辑config.json填入你的API密钥"
    fi
fi

# 解析命令行参数
ACTION=${1:-"start"}

case $ACTION in
    start)
        echo ""
        echo "🚀 启动服务（自动构建镜像）..."
        docker-compose up -d --build
        echo ""
        echo "✅ 服务启动成功！"
        echo ""
        echo "📍 访问地址:"
        echo "   - 管理后台: http://localhost"
        echo "   - 聊天演示: http://localhost/demo"
        echo "   - API文档: http://localhost/docs"
        echo "   - 后端API: http://localhost:7777"
        echo ""
        echo "📊 查看日志: docker-compose logs -f"
        echo "🛑 停止服务: ./docker-start.sh stop"
        ;;

    stop)
        echo ""
        echo "🛑 停止服务..."
        docker-compose down
        echo "✅ 服务已停止"
        ;;

    restart)
        echo ""
        echo "🔄 重启服务..."
        docker-compose restart
        echo "✅ 服务已重启"
        ;;

    build)
        echo ""
        echo "🔨 重新构建镜像..."
        docker-compose build --no-cache
        echo "✅ 镜像构建完成"
        ;;

    logs)
        echo ""
        echo "📊 查看日志..."
        docker-compose logs -f
        ;;

    status)
        echo ""
        echo "📊 服务状态:"
        docker-compose ps
        ;;

    clean)
        echo ""
        echo "🧹 清理所有数据..."
        read -p "⚠️  这将删除所有数据，确定继续吗？(y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            docker-compose down -v
            echo "✅ 数据已清理"
        else
            echo "❌ 已取消"
        fi
        ;;

    *)
        echo ""
        echo "用法: ./docker-start.sh [命令]"
        echo ""
        echo "命令:"
        echo "  start   - 启动服务（默认）"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  build   - 重新构建镜像"
        echo "  logs    - 查看日志"
        echo "  status  - 查看状态"
        echo "  clean   - 清理所有数据"
        ;;
esac
