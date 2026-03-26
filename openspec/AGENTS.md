# OpenSpec 指令

为使用 OpenSpec 进行规范驱动开发的 AI 编程助手提供的指令。

## TL;DR 快速检查清单

- 搜索现有工作：`openspec spec list --long`、`openspec list`（仅在全文搜索时使用 `rg`）
- 确定范围：新增功能还是修改现有功能
- 选择唯一的 `change-id`：短横线连接，动词开头（`add-`、`update-`、`remove-`、`refactor-`）
- 脚手架：创建 `proposal.md`、`tasks.md`、`design.md`（仅必要时），以及每个受影响能力的增量规范
- 编写增量：使用 `## ADDED|MODIFIED|REMOVED|RENAMED Requirements`；每个需求至少包含一个 `#### Scenario:`
- 验证：`openspec validate [change-id] --strict` 并修复问题
- 请求批准：在提案批准前不要开始实施

## 三阶段工作流

### 第一阶段：创建变更

在以下情况下创建提案：
- 添加功能或特性
- 做出破坏性变更（API、Schema）
- 更改架构或模式
- 优化性能（改变行为）
- 更新安全模式

触发词（示例）：
- "帮助我创建变更提案"
- "帮助我规划变更"
- "帮助我创建提案"
- "我想创建规范提案"
- "我想创建规范"

宽松匹配指引：
- 包含以下任一词：`proposal`、`change`、`spec`
- 搭配以下任一词：`create`、`plan`、`make`、`start`、`help`

无需提案的情况：
- 修复 bug（恢复预期行为）
- 拼写错误、格式、注释
- 依赖更新（非破坏性）
- 配置更改
- 测试现有行为

**工作流**
1. 查看 `openspec/project.md`、`openspec list` 和 `openspec list --specs` 了解当前上下文。
2. 选择唯一的动词开头 `change-id`，在 `openspec/changes/<id>/` 下创建 `proposal.md`、`tasks.md`、可选的 `design.md` 和规范增量。
3. 使用 `## ADDED|MODIFIED|REMOVED Requirements` 编写规范增量，每个需求至少包含一个 `#### Scenario:`。
4. 运行 `openspec validate <id> --strict`，在分享提案前解决所有问题。

### 第二阶段：实施变更

将这些步骤跟踪为待办事项，逐个完成。
1. **阅读 proposal.md** - 了解要构建什么
2. **阅读 design.md**（如果存在）- 审查技术决策
3. **阅读 tasks.md** - 获取实施检查清单
4. **按顺序实施任务** - 按顺序完成
5. **确认完成** - 确保 `tasks.md` 中的每个项目都完成后才更新状态
6. **更新检查清单** - 所有工作完成后，将每个任务设置为 `- [x]`，使列表反映实际情况
7. **批准门槛** - 在提案经过审查和批准之前不要开始实施

### 第三阶段：归档变更

部署后，创建独立的 PR 来：
- 将 `changes/[name]/` 移动到 `changes/archive/YYYY-MM-DD-[name]/`
- 如果能力发生变化，更新 `specs/`
- 对于仅工具变更，使用 `openspec archive <change-id> --skip-specs --yes`（始终显式传递变更 ID）
- 运行 `openspec validate --strict` 确认归档的变更通过检查

## 任何任务之前

**上下文检查清单：**
- [ ] 阅读 `specs/[capability]/spec.md` 中的相关规范
- [ ] 检查 `changes/` 中的待处理变更是否有冲突
- [ ] 阅读 `openspec/project.md` 了解约定
- [ ] 运行 `openspec list` 查看活动变更
- [ ] 运行 `openspec list --specs` 查看现有能力

**创建规范之前：**
- 始终检查能力是否已存在
- 优先修改现有规范而非创建重复规范
- 使用 `openspec show [spec]` 审查当前状态
- 如果请求不明确，在创建脚手架前询问 1-2 个澄清问题

### 搜索指引

- 枚举规范：`openspec spec list --long`（或 `--json` 用于脚本）
- 枚举变更：`openspec list`（或 `openspec change list --json` - 已废弃但可用）
- 显示详情：
  - 规范：`openspec show <spec-id> --type spec`（使用 `--json` 进行过滤）
  - 变更：`openspec show <change-id> --json --deltas-only`
- 全文搜索（使用 ripgrep）：`rg -n "Requirement:|Scenario:" openspec/specs`

## 快速开始

### CLI 命令

```bash
# 基础命令
openspec list                  # 列出活动变更
openspec list --specs          # 列出规范
openspec show [item]           # 显示变更或规范
openspec validate [item]       # 验证变更或规范
openspec archive <change-id> [--yes|-y]   # 部署后归档（为非交互式运行添加 --yes）

# 项目管理
openspec init [path]           # 初始化 OpenSpec
openspec update [path]         # 更新指令文件

# 交互模式
openspec show                  # 提示选择
openspec validate              # 批量验证模式

# 调试
openspec show [change] --json --deltas-only
openspec validate [change] --strict
```

### 命令标志

- `--json` - 机器可读输出
- `--type change|spec` - 消除项目歧义
- `--strict` - 全面验证
- `--no-interactive` - 禁用提示
- `--skip-specs` - 无需规范更新即可归档
- `--yes`/`-y` - 跳过确认提示（非交互式归档）

## 目录结构

```
openspec/
├── project.md              # 项目约定
├── specs/                  # 当前真相 - 实际构建了什么
│   └── [capability]/       # 单一聚焦能力
│       ├── spec.md         # 需求和场景
│       └── design.md       # 技术模式
├── changes/                # 提案 - 应当改变什么
│   ├── [change-name]/
│   │   ├── proposal.md     # 为什么、做什么、影响
│   │   ├── tasks.md        # 实施检查清单
│   │   ├── design.md       # 技术决策（可选；见标准）
│   │   └── specs/          # 增量变更
│   │       └── [capability]/
│   │           └── spec.md # ADDED/MODIFIED/REMOVED
│   └── archive/            # 已完成的变更
```

## 创建变更提案

### 决策树

```
新请求？
├─ 修复恢复规范行为的 bug？ → 直接修复
├─ 拼写错误/格式/注释？ → 直接修复
├─ 新功能/能力？ → 创建提案
├─ 破坏性变更？ → 创建提案
├─ 架构变更？ → 创建提案
└─ 不清楚？ → 创建提案（更安全）
```

### 提案结构

1. **创建目录：** `changes/[change-id]/`（短横线连接，动词开头，唯一）

2. **编写 proposal.md：**
```markdown
# 变更：[变更的简要描述]

## 原因
[1-2 句关于问题/机会]

## 变更内容
- [变更列表]
- [用 **BREAKING** 标记破坏性变更]

## 影响
- 受影响的规范：[能力列表]
- 受影响的代码：[关键文件/系统]
```

3. **创建规范增量：** `specs/[capability]/spec.md`
```markdown
## ADDED Requirements
### Requirement: 新功能
系统应提供...

#### Scenario: 成功案例
- **WHEN** 用户执行操作
- **THEN** 预期结果

## MODIFIED Requirements
### Requirement: 现有功能
[完整的修改后需求]

## REMOVED Requirements
### Requirement: 旧功能
**原因**：[为什么移除]
**迁移**：[如何处理]
```

如果多个能力受影响，在 `changes/[change-id]/specs/<capability>/spec.md` 下创建多个增量文件——每个能力一个。

4. **创建 tasks.md：**
```markdown
## 1. 实施
- [ ] 1.1 创建数据库 Schema
- [ ] 1.2 实现 API 端点
- [ ] 1.3 添加前端组件
- [ ] 1.4 编写测试
```

5. **在需要时创建 design.md：**
如果满足以下任一条件则创建 `design.md`；否则省略：
- 跨领域变更（多个服务/模块）或新的架构模式
- 新增外部依赖或重大数据模型变更
- 安全、性能或迁移复杂性
- 在编码前受益于技术决策的模糊性

最小 `design.md` 框架：
```markdown
## 背景
[背景、约束、利益相关者]

## 目标 / 非目标
- 目标：[...]
- 非目标：[...]

## 决策
- 决策：[内容和原因]
- 考虑的替代方案：[选项 + 理由]

## 风险 / 权衡
- [风险] → 缓解措施

## 迁移计划
[步骤、回滚]

## 开放问题
- [...]
```

## 规范文件格式

### 关键：场景格式

**正确**（使用 #### 标题）：
```markdown
#### Scenario: 用户登录成功
- **WHEN** 提供有效凭据
- **THEN** 返回 JWT 令牌
```

**错误**（不要使用项目符号或粗体）：
```markdown
- **Scenario: 用户登录**  ❌
**Scenario**: 用户登录     ❌
### Scenario: 用户登录      ❌
```

每个需求必须至少有一个场景。

### 需求措辞

- 对规范性需求使用 SHALL/MUST（除非有意非规范性，否则避免 should/may）

### 增量操作

- `## ADDED Requirements` - 新能力
- `## MODIFIED Requirements` - 变更行为
- `## REMOVED Requirements` - 废弃功能
- `## RENAMED Requirements` - 名称变更

标题使用 `trim(header)` 匹配——忽略空白。

#### 何时使用 ADDED vs MODIFIED

- ADDED：引入可以独立存在的新能力或子能力。当变更是正交的（例如添加"斜杠命令配置"）而非改变现有需求的语义时，优先使用 ADDED。
- MODIFIED：更改现有需求的行为、范围或验收标准。始终粘贴完整的更新需求内容（标题 + 所有场景）。归档器将用你提供的内容替换整个需求；部分增量将丢失先前细节。
- RENAMED：仅在名称更改时使用。如果同时更改行为，使用 RENAMED（名称）加上引用新名称的 MODIFIED（内容）。

常见陷阱：在不完全包含先前文本的情况下使用 MODIFIED 添加新关注点。这会导致归档时丢失细节。如果你没有明确更改现有需求，应在 ADDED 下添加新需求。

正确编写 MODIFIED 需求的方法：
1. 在 `openspec/specs/<capability>/spec.md` 中找到现有需求。
2. 复制整个需求块（从 `### Requirement: ...` 到其场景）。
3. 粘贴到 `## MODIFIED Requirements` 下并编辑以反映新行为。
4. 确保标题文本完全匹配（忽略空白），并保留至少一个 `#### Scenario:`。

RENAMED 示例：
```markdown
## RENAMED Requirements
- FROM: `### Requirement: 登录`
- TO: `### Requirement: 用户认证`
```

## 故障排除

### 常见错误

**"变更必须至少有一个增量"**
- 检查 `changes/[name]/specs/` 存在且包含 .md 文件
- 验证文件具有操作前缀（## ADDED Requirements）

**"需求必须至少有一个场景"**
- 检查场景使用 `#### Scenario:` 格式（4 个井号）
- 不要使用项目符号或粗体作为场景标题

**静默场景解析失败**
- 确切的格式要求：`#### Scenario: 名称`
- 使用 `openspec show [change] --json --deltas-only` 进行调试

### 验证技巧

```bash
# 始终使用严格模式进行综合检查
openspec validate [change] --strict

# 调试增量解析
openspec show [change] --json | jq '.deltas'

# 检查特定需求
openspec show [spec] --json -r 1
```

## 快乐路径脚本

```bash
# 1) 探索当前状态
openspec spec list --long
openspec list
# 可选全文搜索：
# rg -n "Requirement:|Scenario:" openspec/specs
# rg -n "^#|Requirement:" openspec/changes

# 2) 选择变更 ID 并创建脚手架
CHANGE=add-two-factor-auth
mkdir -p openspec/changes/$CHANGE/{specs/auth}
printf "## Why\n...\n\n## What Changes\n- ...\n\n## Impact\n- ...\n" > openspec/changes/$CHANGE/proposal.md
printf "## 1. Implementation\n- [ ] 1.1 ...\n" > openspec/changes/$CHANGE/tasks.md

# 3) 添加增量（示例）
cat > openspec/changes/$CHANGE/specs/auth/spec.md << 'EOF'
## ADDED Requirements
### Requirement: 双因素认证
用户必须在登录期间提供第二个因素。

#### Scenario: 需要 OTP
- **WHEN** 提供有效凭据
- **THEN** 需要 OTP 挑战
EOF

# 4) 验证
openspec validate $CHANGE --strict
```

## 多能力示例

```
openspec/changes/add-2fa-notify/
├── proposal.md
├── tasks.md
└── specs/
    ├── auth/
    │   └── spec.md   # ADDED: 双因素认证
    └── notifications/
        └── spec.md   # ADDED: OTP 邮件通知
```

auth/spec.md
```markdown
## ADDED Requirements
### Requirement: 双因素认证
...
```

notifications/spec.md
```markdown
## ADDED Requirements
### Requirement: OTP 邮件通知
...
```

## 最佳实践

### 简单优先
- 默认小于 100 行新代码
- 单文件实现直到证明不足
- 没有明确理由避免使用框架
- 选择无聊但经过验证的模式

### 复杂性触发器

仅在以下情况下添加复杂性：
- 性能数据显示当前解决方案太慢
- 明确规模要求（>1000 用户，>100MB 数据）
- 多个经过验证的用例需要抽象

### 清晰引用
- 使用 `file.ts:42` 格式表示代码位置
- 将规范引用为 `specs/auth/spec.md`
- 链接相关变更和 PR

### 能力命名
- 使用动词-名词：`user-auth`、`payment-capture`
- 每个能力单一目的
- 10 分钟可理解规则
- 如果描述需要"和"则拆分

### 变更 ID 命名
- 使用短横线连接，简短描述：`add-two-factor-auth`
- 优先使用动词前缀：`add-`、`update-`、`remove-`、`refactor-`
- 确保唯一性；如果已被占用，附加 `-2`、`-3` 等

## 工具选择指南

| 任务 | 工具 | 原因 |
|------|------|-----|
| 按模式查找文件 | Glob | 快速模式匹配 |
| 搜索代码内容 | Grep | 优化正则搜索 |
| 读取特定文件 | Read | 直接文件访问 |
| 探索未知范围 | Task | 多步骤调查 |

## 错误恢复

### 变更冲突
1. 运行 `openspec list` 查看活动变更
2. 检查重叠的规范
3. 与变更负责人协调
4. 考虑合并提案

### 验证失败
1. 使用 `--strict` 标志运行
2. 检查 JSON 输出获取详情
3. 验证规范文件格式
4. 确保场景正确格式化

### 缺少上下文
1. 首先阅读 project.md
2. 检查相关规范
3. 查看最近的归档
4. 请求澄清

## 快速参考

### 阶段指示器
- `changes/` - 已提案，尚未构建
- `specs/` - 已构建并部署
- `archive/` - 已完成的变更

### 文件用途
- `proposal.md` - 为什么和做什么
- `tasks.md` - 实施步骤
- `design.md` - 技术决策
- `spec.md` - 需求和行为

### CLI  Essentials
```bash
openspec list              # 什么正在进行中？
openspec show [item]       # 查看详情
openspec validate --strict # 正确吗？
openspec archive <change-id> [--yes|-y]  # 标记完成（为自动化添加 --yes）
```

记住：规范是真相。变更是提案。保持同步。

---

## 提案规范（中文）

本节详细说明变更提案的编写规范和要求。

### 提案文件结构

每个提案必须包含以下文件：

```
openspec/changes/[change-id]/
├── proposal.md      # 变更提案说明
├── tasks.md         # 实施任务清单
├── design.md        # 技术设计（可选）
└── specs/
    └── [capability]/
        └── spec.md  # 增量规范
```

### proposal.md 格式

**必须包含以下四个部分：**

```markdown
# 变更：[简短描述]

## 变更原因
- 说明为什么需要此变更
- 描述问题或机会

## 变更内容
- 列出具体变更点
- 用 **BREAKING** 标记破坏性变更

## 影响范围
- 受影响的规范列表
- 受影响的代码模块
```

**命名规则：**
- `change-id` 使用短横线连接
- 以动词开头：`add-`、`update-`、`remove-`、`refactor-`
- 保持简短且唯一

### tasks.md 格式

**任务清单结构：**

```markdown
## 1. 实施阶段
- [ ] 1.1 具体任务
- [ ] 1.2 具体任务

## 2. 测试阶段
- [ ] 2.1 具体任务

## 3. 部署阶段
- [ ] 3.1 具体任务
```

**注意事项：**
- 任务按顺序编号
- 未完成任务使用 `- [ ]`
- 已完成任务使用 `- [x]`

### 增量规范格式

**规范增量类型：**

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `## ADDED Requirements` | 新增需求 | 添加新功能 |
| `## MODIFIED Requirements` | 修改需求 | 变更现有行为 |
| `## REMOVED Requirements` | 移除需求 | 删除功能 |
| `## RENAMED Requirements` | 重命名需求 | 名称变更 |

**需求格式：**

```markdown
## ADDED Requirements
### Requirement: 功能名称
系统必须提供...

#### Scenario: 场景名称
- **WHEN** 条件描述
- **THEN** 预期结果
```

**场景格式要求：**
- 使用 `#### Scenario:` 标题（4个井号）
- 必须包含 `**WHEN**` 和 `**THEN**` 关键字
- 每个需求至少包含一个场景

### 质量检查清单

提交提案前检查：

- [ ] `proposal.md` 包含原因、变更内容、影响范围
- [ ] `change-id` 唯一且以动词开头
- [ ] 增量规范使用正确的操作类型前缀
- [ ] 每个需求至少有一个场景
- [ ] 场景使用 `#### Scenario:` 格式
- [ ] 运行 `openspec validate [change-id] --strict` 通过验证
- [ ] 提案经过审查和批准后再开始实施

### 常见错误

| 错误信息 | 解决方法 |
|----------|----------|
| "变更必须至少有一个增量" | 检查 `specs/` 目录存在且包含 `.md` 文件 |
| "需求必须至少有一个场景" | 确保场景使用 `#### Scenario:` 格式 |
| "增量操作无效" | 检查操作类型为 ADDED/MODIFIED/REMOVED/RENAMED |
| "场景格式错误" | 使用 `#### Scenario: 名称` 格式，不要使用粗体或项目符号 |
