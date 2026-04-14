# chat_ui_builder SkeletonCompiler handler registry 重构计划

## Stage 1：设计与边界固化
### Task 1.1
- 完成设计文档，确认仅改 `skeleton_compiler.py`。

## Stage 2：结构重构实现
### Task 2.1
- 引入 `SkeletonRuntime` 与 `RegionRouter`。
### Task 2.2
- 实现 `PlanHandler`、`RegionHandler`、`ContentHandler`。
### Task 2.3
- 将 `SkeletonCompiler.apply()` 改为 registry 分发。
### Task 2.4
- 保持行为等价（slot、pending、flow region、hero h1 去重）。

## Stage 3：最小验证与进度记录
### Task 3.1
- 执行最小语法检查。
### Task 3.2
- 追加 progress 并提交。
