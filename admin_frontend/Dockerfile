# 前端构建阶段
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:18-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm install --registry=https://registry.npmmirror.com

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 生产阶段 - 使用nginx
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
