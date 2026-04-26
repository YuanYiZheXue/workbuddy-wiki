# MEMORY.md - 跨会话长期记忆

> 本文档记录在多个会话中稳定的事实、用户偏好、项目约定。
> 由 WorkBuddy 在每次完成实质性工作时更新。

---

## 用户信息

- **称呼**：元一
- **职业**：金融科技 + 嵌入式 AI 工程师
- **项目**：WorkBuddy（AI 助手/知识库 Wiki）+ CodeBuddy
- **工作风格**：简洁直接、指令化强、偏好短命令快速确认
- **沟通语言**：中文

---

## 项目核心

### WorkBuddy Wiki

- **仓库**：`d:\Obsidian_KN\知识库构建`（本地路径）
- **远程**：GitHub `YuanYiZheXue/workbuddy-wiki` + Gitee `yuanyizhexue/workbuddy-wiki`
- **Git 命令**：不在 PATH，需用完整路径 `& "C:\Program Files\Git\bin\git.exe"`
- **版本管理**：post-commit hook 自动打标签 `vYYYY-MM-DD-hash`
- **版本号规则**：委托 AI 判断，原则：新功能（minor）、Bug 修复（patch）、不兼容变更（major）

### 元一思想（四原则）

1. **存续为体，形式为用** — 有用性为根本，具体做法都是形式
2. **流动趋效，均衡为度** — 信息高效流动，但以不过载为限度
3. **意义生于博弈，固于认同** — 意义在互动中碰撞产生
4. **结构求稳，接口预变** — 底层稳定，新需求通过接口适应

> 四原则是**网络互锁**关系，非顺序流转。

---

## 的经验（踩坑记录）

### B 站动态发布

- `bilibili-api-python` 的 `send_dynamic()` 返回 `-400` 时，**先验证 cookies 是否过期**，再调 API
- Cookies 验证方法：`user.User(uid, credential).get_user_info()`
- `SESSDATA` 中的 `%2C` 需 `unquote` 解码为逗号，`%2A` 解码为星号
- PowerShell 默认编码 GBK，`print()` 中的 emoji/中文会报 `UnicodeEncodeError`

### 小红书 MCP

- PyPI 包名：`xiaohongshu-mcp-server`
- Python 模块名：`xhs_mcp`（不是 `xiaohongshu_mcp_server`）
- CLI 入口：`D:\ProgramFiles\anaconda3\Scripts\xhs-mcp.exe`
- mcp.json 路径：`C:\Users\11010\.workbuddy\mcp.json`（用户级配置）
- **配置后需重启 WorkBuddy 客户端**才能加载新 MCP 服务

### Git 操作

- Git 不在 PATH，必须用完整路径：`& "C:\Program Files\Git\bin\git.exe" -C "<path>" <subcommand>`
- 提交纪律：功能 + 版本号更新合并为一次提交，不单独 `chore: 更新版本号`

### Web 请求性能

- `web_fetch` 访问 GitHub 很慢（>10s），因为它用 AI 模型解析完整 HTML
- **访问 GitHub 内容必须用 GitHub API**（`Invoke-RestMethod`），实测 ~1272ms
- `web_fetch` 只用于普通网页（CSDN、知乎、官方文档等）

### 通用

- 阻塞阈值：同一问题尝试 2 次不成功 → 换思路；3 次还不行 → 记录并绕开
- 响应结构：结论/结果在前，分析在后
- 不要为了「把问题搞清楚」而陷入分析循环

---

## 当前系统状态（2026-04-26）

| 项目 | 状态 |
|------|------|
| B 站动态发布 | ✅ 已通（cookies 有效，两条动态已发） |
| 小红书 MCP | 🟡 已安装 `xiaohongshu-mcp-server`，`mcp.json` 已配置，需重启客户端生效 |
| wiki schema 版本 | v0.6.0 |
| 最近产出质量 | ⚠️ 偏低，分析过多、执行密度不足 |

---

*最后更新：2026-04-26*
