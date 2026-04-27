# chat_ui_builder streaming ws frames 序列化修复计划

## Stage 1：定向修复
### Task 1.1 app.py 序列化补丁
- 在 `/api/chat/ws/stream` 成功回包前，新增 `frames` 序列化转换。
- 使用 `frame.model_dump(exclude_none=True)` 产出 dict。
- 保持现有协议字段不变。

### Task 1.2 保持范围收敛
- 不改 runtime/service/extractor。
- 不改 ws 其它流程和错误协议。

## Stage 2：校验与记录
### Task 2.1 最小检查
- 运行 `python -m py_compile chat_ui_builder/app.py`。

### Task 2.2 记录与提交
- 追加 `progress.md`。
- 中文 commit。
- 创建 PR 记录。
