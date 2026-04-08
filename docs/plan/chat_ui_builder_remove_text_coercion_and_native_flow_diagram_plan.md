# chat_ui_builder 移除文本纠偏与原生 flow_diagram 开发计划

## Stage 1：设计与范围确认
### Task 1.1
- 完成设计文档，确认影响范围：models/skeleton/prompting/tests。

## Stage 2：后端代码清理
### Task 2.1
- 删除 flow_diagram schema 与 union 注册。
### Task 2.2
- 重构 skeleton_compiler：移除 text_coercer、title overlap、native flow handler/override。
### Task 2.3
- 保留 Mermaid flow 类型路由到 `flow` slot。

## Stage 3：合同与测试更新
### Task 3.1
- 更新 prompting 合同，移除原生 flow_diagram 事件说明。
### Task 3.2
- 更新测试：删除原生 flow 测试，保留 Mermaid flow 路由验证。
### Task 3.3
- 运行测试/检查并记录环境限制。

## Stage 4：收尾
### Task 4.1
- 追加 progress 记录并提交。
