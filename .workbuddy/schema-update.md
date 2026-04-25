# Schema 更新流程

> 本文档描述如何安全地更新 `workbuddy-wiki-schema.md`，避免污染现有知识库。

## 更新触发

**手动触发**：用户说"检查 Schema 更新"或"更新知识库构建Schema"

**不自动执行**：避免在用户不知情的情况下修改核心文件。

---

## 更新流程

### 1. 获取远程最新

```bash
git fetch origin main
```

### 2. 读取版本号

**本地版本**（当前工作区）：
```powershell
Select-String -Path "workbuddy-wiki-schema.md" -Pattern "^\*\*版本\*\*：(.+)$" | % { $_.Matches.Groups[1].Value.Trim() }
```

**远程版本**（待合并）：
```powershell
git show origin/main:workbuddy-wiki-schema.md | Select-String -Pattern "^\*\*版本\*\*：(.+)$" | % { $_.Matches.Groups[1].Value.Trim() }
```

### 3. 版本对比

如果远程版本 = 本地版本 → **无需更新**，结束流程。

如果远程版本 ≠ 本地版本 → 继续下一步。

### 4. 显示变更日志

**读取远程变更说明**：
```powershell
git log HEAD..origin/main --oneline -- workbuddy-wiki-schema.md
```

**显示变更内容**（给用户审查）：
```powershell
git diff HEAD origin/main -- workbuddy-wiki-schema.md
```

用自然语言总结变更：
- 新增了哪些章节？
- 修改了哪些核心概念？
- 是否有破坏性变更（Breaking Change）？

### 5. 用户确认

**询问用户**：
```
发现新版本 Schema：
  本地：v0.3.0 (v2026-04-26-04611bb)
  远程：v0.4.0 (v2026-04-27-xxxxx)

主要变更：
- 新增：XXX 章节
- 修改：XXX 概念
- 修复：XXX 问题

是否应用此更新？
1. 是（执行 git pull）
2. 否（跳过，下次再提醒）
3. 查看详细差异（显示完整 diff）
```

### 6. 应用更新

如果用户确认"是"：

```bash
git pull origin main
```

**验证更新成功**：
```powershell
Select-String -Path "workbuddy-wiki-schema.md" -Pattern "^\*\*版本\*\*：(.+)$"
```

**通知用户**：
```
✅ Schema 已更新至 v0.4.0 (v2026-04-27-xxxxx)

建议下一步：
1. 阅读新版本 Schema（workbuddy-wiki-schema.md）
2. 检查现有 wiki/ 是否需要调整
3. 如有问题，可回滚：git checkout v2026-04-26-04611bb
```

### 7. 如果用户选择"否"

**记录跳过原因**（可选）：
```markdown
<!-- 用户在 2026-04-26 跳过更新 v0.4.0，原因：XXX -->
```

**下次提醒**：在 `wiki/log.md` 中记录，下次会话时再次提醒（最多提醒 3 次）。

---

## 回滚方案

如果用户应用更新后发现问题，可以回滚：

```bash
# 回滚到上一个稳定版本
git checkout v2026-04-26-04611bb

# 或者回滚到指定版本
git checkout <tag-name>
```

**通知用户**：
```
⚠️ 已回滚至 v2026-04-26-04611bb

如需重新尝试更新，请再次说"检查 Schema 更新"。
```

---

## 跨贡献者协作

### 贡献者提交更新

1. Fork 仓库或创建分支
2. 修改 `workbuddy-wiki-schema.md`
3. 更新版本号（遵循本文档的"版本号规范"）
4. 提交 PR（Pull Request）
5. 等待 Maintainer（元一）Review

### Maintainer Review 标准

- **兼容性**：是否有破坏性变更？
- **必要性**：是否真的需要修改核心 Schema？
- **清晰性**：变更说明是否清晰？
- **测试**：是否在某工作区测试过？

### 合并后通知

PR 合并后，打新标签，通知所有工作区：

```bash
git tag v2026-04-27-xxxxx
git push origin --tags
```

---

## 版本号规范

### 格式

**人类可读版本**：`v<major>.<minor>.<patch>`
- major：破坏性变更（不兼容旧版本）
- minor：新增功能（兼容旧版本）
- patch：Bug 修复（兼容旧版本）

**Git 精确版本**：`v<YYYY>-<MM>-<DD>-<short-hash>`
- 用于精确回滚
- 由 post-commit hook 自动生成

### 示例

| 变更类型 | 人类版本 | Git 版本 |
|----------|----------|-----------|
| 初始版本 | v0.1.0 | v2026-04-25-xxxxxxx |
| 新增"接口决策规则"章节 | v0.2.0 | v2026-04-25-yyyyyyy |
| 合并中文版独有章节 | v0.3.0 | v2026-04-26-04611bb |
| 修复某处错误 | v0.3.1 | v2026-04-26-zzzzzzz |
| 重构核心概念（破坏性） | v1.0.0 | v2026-05-01-xxxxxxx |

---

## 检查清单

更新前，确保：

- [ ] 已备份当前工作区（Git commit）
- [ ] 已读取远程版本号
- [ ] 已显示变更日志给用户
- [ ] 用户已确认"是"
- [ ] 更新后已验证版本号
- [ ] 已通知用户更新完成

回滚前，确保：

- [ ] 用户明确说"回滚"
- [ ] 已告知用户回滚版本号
- [ ] 已执行 `git checkout <tag>`

---

## 故障排查

### 问题1：`git fetch` 失败

**原因**：网络问题或远程仓库不存在。

**解决**：
```bash
# 检查远程仓库
git remote -v

# 如果不存在，添加远程仓库
git remote add origin <repo-url>
```

### 问题2：版本号解析失败

**原因**：`workbuddy-wiki-schema.md` 开头格式错误。

**解决**：
1. 手动检查文件开头是否符合规范：
   ```
   > **版本**：v0.3.0 (v2026-04-26-04611bb)
   ```
2. 如果格式错误，手动修复或回滚到上一个版本。

### 问题3：合并冲突

**原因**：本地和远程都修改了同一处。

**解决**：
```bash
# 查看冲突
git status

# 手动解决冲突（编辑 workbuddy-wiki-schema.md）
# 然后提交
git add workbuddy-wiki-schema.md
git commit -m "resolve: 解决 Schema 更新冲突"
```

---

*本文档是 Schema 版本化管理的核心规范，所有更新操作必须遵循此流程。*
