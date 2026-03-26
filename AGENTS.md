<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## 全局规则
请全程使用中文与我交流
每次修改完代码都先详细告诉我你做了哪些修改，最后在用5-20字做一个修改概括

# 仓库指南（Repository Guidelines）

## 项目结构与模块组织（Project Structure & Module Organization）

* **`api/`** – 包含 Tornado 入口文件（`api.py`）、接口处理器位于 `api/handlers/`、共享配置在 `api/config/`、模型在 `api/models/`、通用工具与日志在 `api/utils/`。
* **`api/api_admin.py`** 及其 `handlers_admin*/` 为运营后台提供支持；路由风格与公共 API 保持一致。
* **`admin/`** 存放授权码/激活码的维护脚本；其生成的 CSV/TXT 文件为一次性产物，不需要持久保存。
* **`buds/`、`summary/`、`budsImage/`** 分别存储蓝牙设备元数据、本地化摘要模板以及配套资源文件；三者需保持同步。
* **`test/`** 包含集成测试工具与媒体样例；调试网关接口时应复用这些资源。
* **`logs/`** 存储由 `utils.myLog.setup_logger` 输出的运行日志；自动生成的日志文件不要加入版本控制。

## 构建、测试与开发命令（Build, Test, and Development Commands）

* `python -m venv .venv && source .venv/bin/activate` – 创建隔离的 Python 运行环境。
* `pip install -r requirements.txt` – 安装 Tornado、Tortoise ORM、AI SDK 以及相关工具（如 `black`）。
* `python api/api.py --port 8888` – 启动公共 API（读取 `.env` 与 `api/config/config.json`）。
* `python api/api_admin.py` – 启动后台管理 API（默认端口 6667）。
* `python test/test.py gpt3 <MAC_ADDR>` – 调用真实网关；将 `gpt3` 替换为 `join`、`text2Img` 等其他网关名称即可。

## 代码风格与命名规范（Coding Style & Naming Conventions）

* 使用 **4 空格缩进**、**UTF-8 文件编码**。
* 变量与函数统一使用 **snake_case（下划线命名）**，处理器类使用 **PascalCase（帕斯卡命名）**。
* 格式化修改过的代码：`black .`
* 统一使用 `utils.myLog` 输出日志。
* 常量放入 `api/config/constant.py` 或模块级 `ALL_CAPS` 常量。
* 所有新增的 handler 或工具函数需添加**精简 docstring** 与 **类型注解**。
* JSON 字段名保持 **lowercase_with_underscores**，与数据库列命名一致。

## 测试规范（Testing Guidelines）

* 扩展 `test/` 下的脚本，而不是编写临时测试工具。
* 测试脚本应接受命令行参数（网关名称、设备 ID 等）。
* 测试所需的媒体文件应与脚本放在一起。
* 每个接口至少覆盖 **一个正常流程（happy path）** 与 **一个被保护场景**。
* 在提交 PR 前，需要运行你改动相关的测试项，并附上测试命令的终端输出，方便审阅者验证。

## 提交与 Pull Request 规范（Commit & Pull Request Guidelines）

* 提交信息使用简洁、动词开头的摘要（常用中文，例如 `天气信息`）。
* 每个 commit 只做一件事（单一关注点）。
* PR 需列出涉及的 API 路由 / 数据集 / 配置文件修改，关联相关 issue。
* 必须贴上使用过的测试命令及其输出。
* 若改动到后台工具或数据导出，应附上截图或日志。
* 如修改 `.env` 或 `api/config/*.json`，务必在 PR 中明确说明，以便团队协调密钥或配置的同步与轮换。

## 安全与配置提示（Security & Configuration Tips）

* **禁止提交** `.env`、激活码导出文件以及生成的日志。
* 所有密钥应存放在环境变量或 `api/config/` 中的结构化 JSON 模板里，并通过后台管理服务进行轮换。
* 分享由 `admin/` 生成文件前，应**先做脱敏**。

---