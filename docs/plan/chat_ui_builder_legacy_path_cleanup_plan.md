# chat_ui_builder 旧目录残留清理开发计划

关联设计：`docs/chat_ui_builder_legacy_path_cleanup_design.md`

## Stage 1：基线核验
### Task 1.1 旧目录存在性核验
- 检查历史 agent 目录是否存在。
- 若存在则纳入删除清单；若不存在则记录核验结果。

### Task 1.2 旧路径引用盘点
- 使用全文检索定位旧目录路径的全部残留引用。

## Stage 2：定向清理
### Task 2.1 清理旧目录残留
- 删除旧目录（仅在存在时执行）。

### Task 2.2 清理旧路径字符串
- 仅对命中的旧目录路径字符串做替换，统一为 `chat_ui_builder/...` 形式。

## Stage 3：验收与记录
### Task 3.1 回归检索
- 再次检索确认仓库中不再出现旧目录路径字符串。

### Task 3.2 进度与提交
- 追加 `progress.md` 条目记录本次任务。
- 完成 git 提交（中文简要说明）。
