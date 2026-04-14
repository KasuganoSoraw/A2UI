# chat_ui_builder 远程同步与定点改动计划

## Stage 1：基线同步
### Task 1.1
- 拉取远程 `codex/remove-intentplan-and-legacy-fallback-logic-dxojnz` 并将本地重置到该提交。

## Stage 2：定点修改
### Task 2.1
- 检查 `models.py` 的 `AddRegionTextDelta` 是否已与目标定义一致。
### Task 2.2
- 修改 `app.py` 的 CORS 配置为 `allow_origins=['*']`。
### Task 2.3
- 修改 `prompting.py` 的 `init_plan.layout_hint` 文案，仅保留 `auto | single_column`。
### Task 2.4
- 在 `SYSTEM_PROMPT` 合适位置新增 emoji 风格约束句。

## Stage 3：验证与收尾
### Task 3.1
- 运行最小语法检查。
### Task 3.2
- 追加 `progress.md` 记录并提交。
