# chat_ui_builder 日志系统改造设计（控制台彩色分类 + 文件完整追加）

## 需求详情
当前 `samples/agent/adk/chat_ui_builder` 通过 `app.py` 的 `logging.basicConfig` 进行统一初始化，控制台日志单一格式输出，且关键链路日志在人眼辨识和问题追溯方面均不足。

本次需求要求将日志系统拆分为两条并行通道：
- 控制台：实时、彩色分类、便于快速观察阶段流转。
- 文件：完整、追加、无 ANSI 污染、可稳定 grep 追溯。

## 澄清结果
- 仅整理日志系统，不改 A2UI/planning/skeleton 编译业务语义。
- 文件日志目录固定为 `samples/agent/adk/chat_ui_builder/logs`，文件名固定 `chat_ui_builder.log`。
- 颜色分类按“消息内容特征”实现，不仅按 level。
- 需要避免重复挂载 handler（重载、多次 import 场景）。
- 在不大规模改造业务日志调用前提下，尽量改善长 payload 日志在文件中被截断的问题。

## WHAT（做什么）
1. 新增 `logging_utils.py`：
   - `ensure_log_dir()`
   - `ColoredCategoryFormatter`（按关键子串分类着色）
   - `PlainFileFormatter`（优先写 `record.full_message`，保证文件不带 ANSI）
   - `build_console_handler()` / `build_file_handler()`
   - `configure_logging()`（root 级初始化 + 幂等防重）
2. 修改 `app.py`：去掉 `basicConfig`，启动时改为调用 `configure_logging()`。
3. 轻量调整关键日志调用（不重构业务逻辑）：
   - 为 `Streaming frame body=` / `Parsed planning delta=` / `Emitting planning A2UI frame=` 增加 `extra.full_message`，让文件优先写完整内容。
4. 保持其余模块 `logging.getLogger(__name__)` 自动继承 root handlers，实现全模块覆盖落盘。

## WHY（为什么）
- 控制台彩色分类可快速识别阶段事件（planning 解析、compiler 编译、frame 发射、stream 输出）。
- 文件完整无色日志利于追溯和排查复杂链路，避免终端可读性优化影响离线分析。
- 通过 formatter + `extra.full_message` 的方式，在小改动下提升“文件尽量完整”目标达成度。

## HOW（如何做）
- 使用标准库 `logging` + ANSI 码实现控制台着色，不引入第三方框架。
- 控制台 formatter：
  - `Streaming frame body=` -> 一种颜色
  - `Parsed planning delta=` -> 一种颜色
  - `Emitting planning A2UI frame=` -> 一种颜色
  - `Compiling delta type=` -> 一种颜色
  - Warning/Error 使用更强告警色
- 文件 formatter：
  - 统一固定格式：时间/级别/logger/message
  - 若有 `record.full_message` 则优先写完整内容
  - 永不写 ANSI 控制字符
- `configure_logging()` 以 root logger 安装 console + file handler，并打标记避免重复安装。
