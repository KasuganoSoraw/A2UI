# Chat UI Builder add_region_table 全链路接入计划

关联设计：`docs/chat_ui_builder_add_region_table_chain_design.md`

## Stage 1：协议与模型扩展
### Task 1.1
- 在 `models.py` 增加 table 列定义、planning 事件、low-level 事件。

### Task 1.2
- 将新增事件接入 `SkeletonDelta` 与 `Delta` 联合类型。

## Stage 2：编译链路实现
### Task 2.1
- 在 `skeleton_compiler.py` 新增 `add_region_table` 路由逻辑，复用 `text` 通用落点。

### Task 2.2
- 在 `compiler.py` 新增 `AddTableDelta` 到 `Table` 组件的编译实现与 dataModelUpdate 写入。

### Task 2.3
- 在 `prompting.py` 增加 `add_region_table` 的 contract 与使用约束说明。

## Stage 3：测试与收尾
### Task 3.1
- 增加测试覆盖 schema 解析、skeleton 编译、frame 输出、与现有内容共存。

### Task 3.2
- 运行测试/语法检查并记录环境限制。

### Task 3.3
- 追加 `progress.md` 并按阶段提交中文 commit。
