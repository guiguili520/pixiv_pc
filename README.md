# Pixiv Illustration Crawler

一个简单而强大的 Python 爬虫脚本，用于从 Pixiv 搜索和下载插画作品。

## 功能特性

- ✨ 按关键词搜索插画
- 📊 支持 Pixiv 排行榜功能（日度、周度、月度）
- 📥 自动下载插画及其元数据
- 🔄 支持多页搜索结果
- ⚙️ 配置文件支持
- 🔁 自动重试机制
- 📊 详细的日志记录
- 🌐 支持代理设置
- ⏱️ 自动延迟控制，尊重服务器限制

## 系统要求

- Python 3.7 或更高版本
- 网络连接

## 安装

### 1. 克隆或下载项目

```bash
cd pixiv_pc
```

### 2. 创建虚拟环境（可选但推荐）

```bash
python -m venv venv

# 激活虚拟环境
# 在 macOS/Linux 上：
source venv/bin/activate

# 在 Windows 上：
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

#### 搜索并下载插画

```bash
python main.py search "anime girl"
```

这将搜索关键词"anime girl"并下载前10页的结果。

#### 自定义搜索页数

```bash
python main.py search "landscape" --max-pages 20
```

#### 自定义输出目录

```bash
python main.py search "architecture" --output ./my_downloads
```

#### 指定排序方式

```bash
python main.py search "anime" --order popular_d
```

排序选项：
- `date_d`: 最新上传（默认）
- `popular_d`: 最受欢迎

### 排行榜功能

#### 获取月度排行榜

```bash
python main.py ranking --mode monthly --date 20251128
```

这将获取2025年11月28日的月度排行榜（查询10月30日-11月28日的内容）。

#### 获取日度排行榜

```bash
python main.py ranking --mode daily
```

这将获取当前日期的日度排行榜。

#### 获取周度排行榜

```bash
python main.py ranking --mode weekly
```

#### 自定义输出目录

```bash
python main.py ranking --mode monthly --date 20251128 --output ./my_downloads
```

排行榜模式说明：
- `daily`: 每日排行榜
- `weekly`: 每周排行榜
- `monthly`: 每月排行榜（推荐）
- 日期格式：`YYYYMMDD`（例如 `20251128` 表示2025年11月28日）

### 配置管理

#### 生成默认配置文件

```bash
python main.py config --generate
```

这将生成 `config.yaml` 文件，您可以根据需要编辑它。

#### 显示当前配置

```bash
python main.py config --show
```

## 配置文件说明

编辑 `config.yaml` 文件来自定义爬虫行为：

```yaml
download:
  output_dir: ./downloads      # 下载目录
  max_pages: 10                # 默认搜索页数
  timeout: 30                  # 请求超时时间（秒）
  retry_times: 3               # 失败重试次数
  delay: 1.0                   # 请求之间的延迟（秒）

proxy:
  enabled: false               # 是否启用代理
  http: null                   # HTTP 代理 URL
  https: null                  # HTTPS 代理 URL

headers:
  user_agent: '...'           # User-Agent
```

## 文件结构

```
pixiv_pc/
├── main.py                    # 主程序入口
├── config.yaml                # 配置文件
├── requirements.txt           # 依赖列表
├── README.md                  # 项目说明
├── logs/                      # 日志目录
├── downloads/                 # 默认下载目录
└── src/
    ├── config/                # 配置模块
    │   └── config.py
    ├── crawler/               # 爬虫模块
    │   ├── pixiv_api.py      # Pixiv API 包装
    │   └── downloader.py      # 下载管理
    └── utils/                 # 工具模块
        └── logger.py          # 日志管理
```

## 下载目录结构

下载的插画将按照以下结构组织：

```
downloads/
├── [艺术家名称]/
│   ├── [插画ID]_[插画标题]/
│   │   ├── p0.jpg
│   │   ├── p1.jpg
│   │   └── ...
│   └── ...
└── ...
```

## 日志

爬虫脚本会在 `logs/` 目录中创建日志文件。日志文件格式为：
- 控制台输出：简化格式，显示关键信息
- 文件输出：详细格式，包含完整的调试信息

日志文件命名格式：`crawler_YYYYMMDD_HHMMSS.log`

## 常见问题

### 1. 下载速度过慢

Pixiv 有速率限制。脚本中设置了默认延迟以尊重这些限制。如果您想加快速度，可以在 `config.yaml` 中减少 `delay` 值：

```yaml
download:
  delay: 0.5  # 减少到 0.5 秒
```

但请注意不要设置过小的值，以避免被限流。

### 2. 某些插画无法下载

这可能是由于：
- 该插画已被删除或限制访问
- 网络连接问题
- 代理问题

检查日志文件以获取更多详细信息。

### 3. 如何在代理后面使用

编辑 `config.yaml` 文件：

```yaml
proxy:
  enabled: true
  http: http://proxy.example.com:8080
  https: https://proxy.example.com:8080
```

### 4. "No module named 'src'" 错误

确保您在项目根目录（包含 `main.py` 的目录）运行脚本。

## 性能建议

1. **增加延迟**：为避免被限流，建议保持 1-2 秒的延迟
2. **分批下载**：不要尝试在一次运行中下载超过 100 页
3. **定期检查**：监控日志文件以识别问题

## 法律声明

此工具仅供学习和研究目的使用。使用此工具时，请遵守 Pixiv 的服务条款和本地法律。不应该：
- 用于商业目的
- 违反 Pixiv 的服务条款
- 用于侵犯他人版权

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.1.0 (2025-12-02)
- ✨ 新增 Pixiv 排行榜功能
- 📊 支持日度、周度、月度排行榜
- 🔍 支持按日期查询排行榜
- 🎯 排行榜功能与搜索功能并行支持

### v1.0.0 (2024-12-02)
- ✨ 初始版本发布
- 💡 支持按关键词搜索
- 📥 自动下载插画
- ⚙️ 配置文件支持
- 🔄 自动重试机制
- 📊 详细日志记录
