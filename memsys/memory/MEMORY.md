# MEMORY.md - 长期记忆

## GitHub 上游 PR 提交标准流程（已提炼）

当需要把 pip 包内的修复推送到上游开源仓库时：

1. **克隆上游**：`git clone <upstream_url> <local_path>` + 设置代理 `$env:HTTPS_PROXY="http://127.0.0.1:10809"`
2. **Fork 创建**：用户手动去 GitHub 网页创建，或用 GitHub API + Token 创建
3. **设置认证**：远程 URL 嵌入 Token：`https://<TOKEN>@github.com/user/repo.git`
4. **覆盖修复**：把 site-packages 里已修改的文件复制过来
5. **提交推送**：`git add . && git commit && git push origin <branch>`
6. **创建 PR**：用 GitHub API POST 到 `/repos/<owner>/<repo>/pulls`，或让用户手动提

关键约束：
- Token 永远不写入日志/笔记
- pip 安装的包没有 .git，需要另起仓库工作
- 先克隆再改，避免污染原始安装目录

### 记忆方案设计讨论与最终落地

**设计背景**：Agent 需要跨会话记忆，但面临两个矛盾——记忆太多会过载，记忆太少会失忆。Obsidian 作为知识库很自然，但 Agent 工作记忆（推理过程、临时结论）和永久知识需要分层。

**讨论核心**：
1. 第一层直觉：Agent 所有记忆都存 Obsidian——但这样 Obsidian 会变成 Agent 的"草稿纸"，污染知识库
2. 引入 MemPalace：Agent 的工作记忆放在 MemPalace（向量检索 + KG），只在"做笔记"/"提取"时输出到 Obsidian wiki/
3. 关键闭环：沉淀后 Agent 根据 wiki/ 的内容**压缩 MemPalace 的冗余记忆**——这才是三层架构的灵魂

**最终落地方案——三层记忆架构**：

```
外层：raw/（原始资料，不可变）← 信息入口，系统级只读约束（NTFS 只读）
中层：MemPalace（Agent 工作记忆，向量+KG）← 动态吞吐，可增删改
内层：Obsidian wiki/（知识沉淀，Git 版本化）← 只增不减，人类可读
```

**关键设计决策**：
- raw/ 设为 NTFS 只读，作为系统级不可变约束，防止 Agent 误改原始资料
- MemPalace 不追求"完整记忆"，而是"有效记忆"——能支持当前推理即可
- wiki/ 是沉淀层而非存档层——内容要经过 Agent 整理，不是原始记忆的转储
- 闭环方向：wiki/ → 压缩 MemPalace（不是反过来），避免 MemPalace 无限膨胀

### 三层记忆架构（核心设计）

```
MemPalace（Agent工作记忆）←→ Obsidian wiki/（知识沉淀）
```

- **MemPalace**：Agent 的工作记忆，处理推理、构建 KG、事务处理
- **Obsidian wiki/**：知识沉淀层，用户触发"做笔记"/"提取"时输出
- **闭环**：沉淀后 Agent 根据 wiki/ 内容压缩 MemPalace 的冗余记忆

### Obsidian vs MemPalace 分工

| | Obsidian wiki/ | MemPalace |
|---|---|---|
| **角色** | 知识图书馆 | Agent 工作台 |
| **特点** | 只增不减，有 Git 版本历史 | 动态吞吐，有进有出 |
| **谁来写** | Agent 按需输出 | Agent 自由构建 |
| **谁来读** | 用户直接阅读 | Agent 语义检索 |

### MemPalace 规则落地记录

规则已系统写入 MemPalace（2026-04-27）。落地清单：

| 房间 | 内容 | 来源 |
|------|------|------|
| memory-arch | 三层记忆架构 + 分工 + 冗余管理 | MEMORY.md |
| wiki-rules | Ingest/Query/Lint + 会话管理 + Ralph Wiggum循环 | workbuddy-wiki-schema.md |
| yuan-yi-principles | 元一思想四原则 + 四极飞轮 + 接口决策规则 | workbuddy-wiki-schema.md |
| github-workflow | GitHub PR提交标准流程 | MEMORY.md |
| user-info | 用户基本信息 + 偏好 | MEMORY.md |
| mempalace-rules | MemPalace安装排查手册 | MEMORY.md |
| protocol | MemPalace记忆协议（ON WAKE-UP等） | MemPalace官方规范 |

### AAAK 压缩规格

- **压缩比**：官方标注 **30x**（lossless，无信息损失）
- **原理**：3位实体代码 + 结构化字段分隔符 + 情绪标记 + 星级重要性，替代自然语言描述
- **适用场景**：日记写入、跨会话总结、中间推理压缩
- **效果**：英文最佳情况 30x（高重复内容+充分AAAK规范），一般英文叙述约 3-10x；中文约 1.5-5x（信息密度高，缩写收益小）。实测：英文 562→185字符=3x，中文 112→71字符=1.6x。均 lossless，人类和 LLM 可直接读

### MemPalace 冗余管理

- 重要结论已沉淀到 wiki/ 后，Agent 应清理 MemPalace 中对应的冗余中间过程
- 保留：KG 核心关联、开放问题、用户偏好/约定
- 清理：已沉淀的推理链中间步骤、被替代的旧关联、已确认的错误假设

## 元一思想四原则

1. **存续为体，形式为用**：Wiki 价值在于被使用，不是为了完美
2. **流动趋效，均衡为度**：信息高效流动，以不过载为限度
3. **意义生于博弈，固于认同**：内容优先级由实际使用需求驱动
4. **结构求稳，接口预变**：Schema 既稳定又可扩展

## WorkBuddy Wiki 构建规范

### 三层架构

```
raw/（原始资料，不可变，WorkBuddy只读）
wiki/（WorkBuddy完全拥有的Markdown文件集合）
Schema（workbuddy-wiki-schema.md，定义Wiki结构和工作流）
```

### 核心操作

- **Ingest**：一次只处理一篇资料，自下而上构建（来源→实体→概念→index）
- **Query**：搜索相关页面，综合答案，优秀答案归档回 Wiki
- **Lint**：健康检查（悬空链接、双向链接完整性、命名一致性、孤儿页面）

### 会话管理

- 历史对话最多保存 100 个
- 每会话不超过 30 轮
- 会话结束前确保 index、log、memory 都已更新
- **Ralph Wiggum 循环**：自我验证工作是否完成

### 关键原则

- **自下而上**：先有素材，再建概念页
- **先验验证**：网络获取信息使用前必须抽样验证
- **存续为体**：Wiki 的价值在于被使用

## 用户信息

- 腾讯产品经理，名 元一（YuanYi）
- 当前核心项目：WorkBuddy 多智能体系统
- WorkBuddy 成员：元一、哲哲、数数、算算、金金
- V2Ray 代理：端口 10809
- 偏好中文，习惯先看结论再决定行动

## MemPalace MCP 安装与排查手册

### 正确安装流程

1. **先杀进程**（防止文件被占用）：`taskkill /F /IM mempalace-mcp.exe`
2. **pip 安装**：`pip install mempalace`（Python ≥3.9）
3. **修正 config.json**：检查 `C:\Users\SJC\.mempalace\config.json` 中 `palace_path` 是否指向正确目录
4. **init --yes**：`python -m mempalace init --yes <项目路径>`（必须加 `--yes` 否则交互式卡住）
5. **mine**：设置 UTF-8 编码后执行 `python -m mempalace mine <项目路径>`
6. **配置 mcp.json**：指向 `mempalace-mcp.exe --palace <palace路径>`

### 关键配置文件

| 文件 | 路径 | 作用 |
|---|---|---|
| config.json | `C:\Users\SJC\.mempalace\config.json` | 全局配置，`palace_path` 决定数据存储位置 |
| mempalace.yaml | `<项目目录>\mempalace.yaml` | 项目级配置，定义 Wing/Room 结构 |
| mcp.json | `C:\Users\SJC\.workbuddy\mcp.json` | WorkBuddy MCP 服务配置 |

### 踩坑速查

| # | 现象 | 原因 | 解决 |
|---|---|---|---|
| 1 | pip uninstall 报 WinError 32 | mempalace-mcp.exe 被 WorkBuddy 占用 | 先 taskkill 杀进程再卸载 |
| 2 | pip install 一直报 WARNING invalid distribution | site-packages 残留 `~empalace` 目录 | 手动删除 `site-packages\~empalace*` |
| 3 | `mempalace init` 卡住无输出 | 默认交互式，等待用户输入 | 加 `--yes` 参数 |
| 4 | `mempalace mine` 报 UnicodeEncodeError | Windows 控制台 GBK 编码无法处理中文文件名 | 设置 `[Console]::OutputEncoding = UTF8` + `PYTHONIOENCODING=utf-8` |
| 5 | 数据写到错误位置 | `config.json` 的 `palace_path` 配置错误/不存在 | 每次安装后检查 `palace_path` |
| 6 | mcp.json 删除条目后 JSON 解析失败 | 尾部逗号非法 | 删除条目时同步移除尾部逗号 |
| 7 | MCP 写入工具报 -32000 Internal error | **根本原因**：WorkBuddy 传输字符串时注入 lone surrogate（`\udc95` 等），SHA256 hash 计算和 ChromaDB upsert 都会因此抛 UnicodeEncodeError | 修复 `mcp_server.py` 三处：① `tool_add_drawer` drawer_id hash 改用 `encode('utf-8', 'surrogatepass')`；② `tool_add_drawer` ChromaDB upsert 前用同样方法清理 content；③ `diary_write` 同理清理 entry/topic/agent_name。所有 metadata 字符串字段均需清理 |
| 8 | `TextInputSequence must be str in upsert` | ChromaDB 的 upsert/add 在序列化 metadata 时遇到 lone surrogate 报错 | 同上，在写入 ChromaDB 前对所有字符串字段调用 surrogatepass 清理 |
| 9 | 修改 mcp_server.py 后写入仍报错（旧代码） | Python 优先加载 `.pyc` 字节码缓存，`.py` 修改不生效 | 每次修改后清理 `site-packages/mempalace/__pycache__` 和 `*.pyc`，或重启 WorkBuddy 让 MCP 服务重新加载 |

| 10 | Git 未安装，git 命令不可用 | 系统没有 Git 环境 | 下载 Git for Windows 安装包，静默安装：`Start-Process -FilePath "安装包路径" -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=cmd,assoc,assoc_sh" -Wait` |
| 11 | 修复代码提交到上游 | 需要 fork → PR 流程 | 上游仓库：`https://github.com/MemPalace/mempalace`，克隆到 `D:\mempalace-upstream`，用户 fork：`https://github.com/YuanYiZheXue/mempalace`，GitHub Token 已记录（`ghp_`开头）。完整流程：① 克隆上游仓库；② 添加 upstream remote；③ 覆盖文件；④ push 到用户 fork；⑤ GitHub API 创建 PR。git 代理：`http://127.0.0.1:10809`（V2Ray）。参考：`D:\gitfork\docs\fix-lone-surrogate.md` |

### 验证清单

安装/重装后，重启 WorkBuddy 并执行：
1. `mempalace_status` → 确认 `palace_path` 正确、`total_drawers > 0`
2. `mempalace_search` → 测试读取正常
3. `mempalace_add_drawer`（带中文 content）→ 测试写入不再报 -32000
4. `mempalace_diary_write`（带中文 entry）→ 测试日记写入正常
