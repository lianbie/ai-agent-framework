# 🤝 贡献指南

感谢你对 AI Agent Framework 项目的关注！我们欢迎任何形式的贡献。

## 📋 目录

- [如何贡献](#如何贡献)
- [开发环境](#开发环境)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [Pull Request流程](#pull-request流程)
- [Issue规范](#issue规范)

## 如何贡献

### 贡献方式

1. **报告Bug** - 提交Issue描述问题
2. **提出建议** - 提交Issue讨论新功能
3. **提交代码** - Fork项目并提交PR
4. **完善文档** - 改进文档或翻译
5. **分享经验** - 在Discussions中分享使用经验

### 贡献流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 开发环境

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-agent-framework.git
cd ai-agent-framework
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\Activate.ps1  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境

```bash
cp config.docker.json config.json
# 编辑config.json填入你的配置
```

### 5. 启动开发服务器

```bash
# 使用Docker启动（推荐）
docker-start.bat start

# 或者直接使用uvicorn
uvicorn server:app --reload --port 7777
```

## 代码规范

### Python代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用 4 空格缩进
- 行长度限制 120 字符
- 使用类型注解

### 命名规范

```python
# 类名：PascalCase
class MyAgent:
    pass

# 函数名：snake_case
def process_message():
    pass

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 私有方法：前缀下划线
def _internal_method():
    pass
```

### 文档字符串

```python
def process_message(message: str, user_id: str) -> dict:
    """
    处理用户消息

    Args:
        message: 用户消息内容
        user_id: 用户ID

    Returns:
        dict: 包含以下字段：
            - success: 是否成功
            - reply: 回复内容
            - agent_used: 使用的Agent

    Raises:
        ValueError: 当参数无效时
    """
    pass
```

### 注释规范

```python
# 单行注释：说明为什么这样做
result = calculate()  # 使用缓存避免重复计算

# 多行注释：解释复杂逻辑
"""
这个算法使用了动态规划来优化性能：
1. 首先将问题分解为子问题
2. 然后自底向上求解
3. 最后合并结果
"""
```

## 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构（不是新功能也不是修复）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```bash
# 新功能
git commit -m "feat(agent): 添加财务数据查询Agent"

# 修复Bug
git commit -m "fix(rag): 修复向量搜索结果为空的问题"

# 文档更新
git commit -m "docs: 更新README部署说明"

# 重构
git commit -m "refactor(router): 重构Agent路由逻辑"
```

## Pull Request流程

### 1. 准备工作

- 确保代码符合规范
- 添加必要的测试
- 更新相关文档

### 2. 创建PR

- 标题清晰描述更改
- 详细说明更改内容
- 关联相关Issue

### 3. PR模板

```markdown
## 描述

简要描述这个PR的目的

## 更改内容

- [ ] 添加了XXX功能
- [ ] 修复了XXX问题
- [ ] 更新了XXX文档

## 测试

说明如何测试这些更改

## 截图（如果适用）

添加相关截图

## 关联Issue

Closes #123
```

### 4. 代码审查

- 至少需要1个审查者批准
- 解决所有审查意见
- 确保CI通过

### 5. 合并

- 使用"Squash and Merge"
- 删除功能分支

## Issue规范

### Bug报告

```markdown
## Bug描述

清晰描述Bug现象

## 复现步骤

1. 执行XXX操作
2. 输入XXX内容
3. 观察XXX现象

## 期望行为

描述期望的正确行为

## 实际行为

描述实际的错误行为

## 环境信息

- OS: [e.g. Windows 11, Ubuntu 22.04]
- Python: [e.g. 3.11.9]
- 项目版本: [e.g. 1.0.0]

## 日志/截图

添加相关日志或截图
```

### 功能建议

```markdown
## 功能描述

清晰描述建议的功能

## 使用场景

描述这个功能的使用场景

## 实现建议

如果有实现建议，请描述

## 替代方案

描述考虑过的替代方案
```

## 开发指南

### 添加新Agent

1. 创建Agent文件 `modules/agent_service/agents/xxx_agent.py`
2. 继承 `BaseDataAgent`
3. 实现抽象方法
4. 注册Agent
5. 添加测试
6. 更新文档

### 添加新API

1. 创建路由文件 `modules/xxx/routes.py`
2. 定义请求/响应模型
3. 实现业务逻辑
4. 在 `server.py` 注册路由
5. 添加测试
6. 更新API文档

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agent.py

# 运行带覆盖率的测试
pytest --cov=modules tests/
```

## 社区准则

### 行为准则

- 尊重所有参与者
- 接受建设性批评
- 关注对社区最有利的事情
- 对他人表示同理心

### 禁止行为

- 骚扰或歧视性语言
- 人身攻击
- 发布他人私人信息
- 其他不当行为

## 获取帮助

- 提交Issue讨论问题
- 在Discussions中提问
- 查看项目文档

## 致谢

感谢所有贡献者的付出！

---

再次感谢你的贡献！🎉
