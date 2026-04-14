# Chat UI Builder Prompt 展示编排定位重构计划

关联设计：`docs/chat_ui_builder_prompt_display_orchestrator_design.md`

## Stage 1：需求固化
### Task 1.1
- 阅读 `prompting.py` 现有 SYSTEM_PROMPT 并定位与本次目标冲突的文案（特别是默认保留 raw/evidence 倾向）。

### Task 1.2
- 固化新的提示结构：职责定位、关键规则、交互编排重点、保留能力清单。

## Stage 2：代码修改（仅 prompting.py）
### Task 2.1
- 重写 SYSTEM_PROMPT 的“角色定义/输出目标/禁止项”。

### Task 2.2
- 重写 raw/evidence 相关规则为“仅按需展示”。

### Task 2.3
- 保留并对齐以下既有能力文案：
  - usage_hint
  - role×presentation
  - list.timeline 变体
  - FlowDiagram 通用规则与 one-shot

## Stage 3：验证与收尾
### Task 3.1
- 做最小语法检查，确认 `prompting.py` 可被 Python 正常编译。

### Task 3.2
- 在 `progress.md` 追加本次任务记录（只追加）。

### Task 3.3
- 分阶段提交，提交信息中文且简要。
