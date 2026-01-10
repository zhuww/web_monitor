# Web Monitor AI Agent 安装说明

## 项目概述

Web Monitor AI Agent 是一个用于监控网页内容的智能代理，主要功能包括：
- 自动检测网页类型（简单/复杂）
- 简单网页：直接提取文本内容进行分析
- 复杂网页：使用截图方式获取内容，再进行图像分析
- 支持定时监控和告警关键词检测
- 可生成人类可理解的情况报告

## 依赖库安装

### 1. 安装 Python

本项目需要 Python 3.8 或更高版本。请先安装 Python，并确保将其添加到系统 PATH 中。

### 2. 安装依赖库

项目依赖库已列在 `requirements.txt` 文件中。使用以下命令安装所有依赖：

```bash
pip install -r requirements.txt
```

依赖库包括：
- `requests`：用于获取网页内容
- `beautifulsoup4`：用于解析网页文本
- `selenium`：用于复杂网页的截图
- `webdriver-manager`：用于自动管理 Chrome 驱动
- `Pillow`：用于图像处理
- `openai`：用于调用 AI 模型
- `python-dotenv`：用于环境变量管理
- `configparser`：用于配置文件解析
- `schedule`：用于定时任务调度
- `httpx`：用于 HTTP 请求（由 openai 库内部使用）

### 3. 安装 Chrome 浏览器

由于项目使用 Selenium 进行网页截图，需要安装 Chrome 浏览器。请确保 Chrome 浏览器已安装并更新到最新版本。

## 配置文件设置

### 1. 配置 secret.cfg

项目使用 `secret.cfg` 文件存储 API 密钥和模型配置。该文件已在 `.gitignore` 中配置为忽略，不会被提交到版本控制系统。

`secret.cfg` 的格式如下：

```ini
[silicon-flow]
API_KEY="your_silicon_flow_api_key"
BASE_URL="https://api.siliconflow.cn/v1"
# 模型名称
REASONING_MODEL = "deepseek-ai/DeepSeek-V3"
# 温度参数 (0-1)
temperature = 0.7
VISUAL_MODEL="Qwen/Qwen2.5-VL-72B-Instruct"
```

请确保：
- 所有字符串值使用双引号
- 变量命名统一为大写字母加下划线格式
- 按照实际情况填写 API 密钥

### 2. 配置说明

- `API_KEY`：Silicon Flow 的 API 密钥
- `BASE_URL`：Silicon Flow API 的基础 URL
- `REASONING_MODEL`：用于文本分析的模型名称
- `temperature`：AI 模型的温度参数，控制输出的随机性
- `VISUAL_MODEL`：用于图像分析的模型名称

## 运行方法

### 1. 直接运行

可以直接运行 `ai_agent.py` 文件进行测试：

```bash
python ai_agent.py
```

### 2. 使用示例脚本

项目提供了 `example_usage.py` 作为使用示例：

```bash
python example_usage.py
```

### 3. 运行测试

可以运行 `test_basic.py` 进行基本功能测试：

```bash
python test_basic.py
```

## 常见问题解决

### 1. Chrome 驱动问题

如果遇到 Chrome 驱动相关的错误，可以尝试以下解决方案：

- 确保 Chrome 浏览器已安装并更新到最新版本
- 手动下载与 Chrome 版本匹配的驱动，并将其添加到系统 PATH 中
- 或者修改代码，使用 Firefox 或其他浏览器

### 2. API 密钥问题

如果遇到 API 密钥错误，请检查：

- `secret.cfg` 文件中的 API 密钥格式是否正确
- 是否已将 API 密钥的引号去掉
- API 密钥是否有效

### 3. 截图失败

如果截图功能失败，程序会自动降级到文本分析。常见原因包括：

- Chrome 驱动未正确安装
- 网络问题导致页面加载失败
- 页面内容过于复杂或动态

### 4. 模型调用失败

如果 AI 模型调用失败，请检查：

- API 密钥是否有效
- 网络连接是否正常
- 模型名称是否正确
- 是否有足够的 API 调用额度

## 系统要求

- 操作系统：Windows 10/11、macOS、Linux
- Python 版本：3.8 或更高
- 内存：建议 8GB 或更高
- 磁盘空间：至少 1GB 可用空间

## 注意事项

1. 请保护好您的 API 密钥，不要将 `secret.cfg` 文件分享给他人
2. 定时监控可能会消耗较多的 API 额度，请合理设置监控间隔
3. 对于复杂网页，截图分析可能会比较耗时
4. 如果遇到持续问题，请查看程序输出的详细错误信息

## 升级指南

当需要升级依赖库时，可以使用以下命令：

```bash
pip install -r requirements.txt --upgrade
```

如果需要更新 Chrome 驱动，可以手动删除 `webdriver-manager` 缓存的驱动文件，然后重新运行程序。