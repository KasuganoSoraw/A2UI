# chat_ui_builder 日志去重（最小范围）设计

## 需求详情
在已完成“控制台彩色分类 + 文件完整追加落盘”后，当前主链存在两组重复日志：
1. planning delta 重复：`service Parsed planning delta` 与 `skeleton_compiler Compiling skeleton delta`。
2. frame 重复：`service Emitting planning A2UI frame` 与 `app Streaming frame body`。

目标是做最小范围去重，保留主链可追踪但降低阅读噪音。

## 澄清结果
- 不改日志初始化架构，不改彩色/文件双通道机制。
- 不改业务逻辑，仅删除 `service.py` 的两条重复日志。
- 保留链路日志：
  - skeleton_compiler：高层 planning delta
  - compiler：low-level delta
  - app：最终发送 frame

## WHAT（做什么）
1. 删除 `service.py` 中 `Parsed planning delta=...` 日志。
2. 删除 `service.py` 中 `Emitting planning A2UI frame=...` 日志。
3. 清理因上述日志引入且已无用途的辅助函数，保持最小代码整洁。

## WHY（为什么）
- 相邻层重复打印同一 payload 会显著增加控制台噪音。
- 去重后保留“每层一个关键入口/出口日志”即可完整追踪主链。
- 保持文件日志干净且聚焦，提升排查效率。

## HOW（如何做）
- 仅修改 `chat_ui_builder/service.py`：
  - `_compile_planning_records()` 中不再打印 parsed/emitting 两类重复日志。
  - 移除不再使用的 full_message 日志拼装辅助函数。
- 不修改 `logging_utils.py` 配置逻辑，确保 console/file 行为不回退。
