# samples/agent/adk 无关示例清理开发计划

关联设计：`docs/adk_samples_irrelevant_cleanup_design.md`

## Stage 1：设计与基线确认
### Task 1.1 建立清理范围
- 盘点 `samples/agent/adk/` 下现存目录。
- 明确候选删除目录集合（除 chat_ui_builder 外）。

### Task 1.2 依赖安全核验
- 检索 `chat_ui_builder/` 对候选目录的直接依赖。
- 若存在直接依赖，标记并排除删除。

## Stage 2：整块删除无关示例
### Task 2.1 执行目录删除
- 对确认无依赖的示例目录执行整目录删除。
- 不改动 `chat_ui_builder/` 目录。

### Task 2.2 回归检查
- 复核 `samples/agent/adk/` 清理结果。
- 确认删除范围与目标一致。

## Stage 3：记录与交付
### Task 3.1 进度追加
- 仅追加写入 `progress.md` 本次任务记录。

### Task 3.2 提交与PR
- 使用中文简要 commit 信息。
- 生成 PR 信息。
