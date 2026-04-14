# Chat UI Builder：标题规则前移与骨架清理开发计划

关联设计：`docs/chat_ui_builder_prompt_first_heading_and_skeleton_cleanup_design.md`

## Stage 1：规则收敛
### Task 1.1
- 明确 prompt 侧标题层级与 role 责任表达。

### Task 1.2
- 明确后端 hero 兜底边界：仅明显重复时介入。

## Stage 2：编码实现
### Task 2.1
- 修改 `prompting.py` 的 SYSTEM_PROMPT：补充页面唯一 h1、hero 职责、role 语义。

### Task 2.2
- 修改 `skeleton_compiler.py`：
  - 删除 `_build_role_buckets()`；
  - 简化 `_ensure_bucket_for_role()` parent 逻辑；
  - 收紧 hero h1 兜底，不再默认降级。

### Task 2.3
- 更新相关测试断言，确保与新行为一致。

## Stage 3：验证与收尾
### Task 3.1
- 执行测试或语法检查并记录环境限制。

### Task 3.2
- 追加 `progress.md` 记录。

### Task 3.3
- 分阶段提交中文 commit。
