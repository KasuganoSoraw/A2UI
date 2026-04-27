# chat_ui_builder 远程分支同步与三处定点对齐设计

## 需求详情
- 先将本地工程同步到远程分支 `KasuganoSoraw/A2UI` 的 `codex/remove-intentplan-and-legacy-fallback-logic-dxojnz` 当前状态。
- 在此基准上，仅对用户点名的 3 个文件做定点变更：
  1. `chat_ui_builder/models.py`
  2. `chat_ui_builder/app.py`
  3. `chat_ui_builder/prompting.py`

## 澄清结果
- `models.py` 只检查 `AddRegionTextDelta` 是否与目标定义一致；若一致则不改。
- `app.py` 仅替换 CORS 的 `allow_origin_regex` 为 `allow_origins=['*']`，其余逻辑不动。
- `prompting.py` 仅修改 `PLANNING_DELTA_CONTRACT` 里 `init_plan.layout_hint` 的枚举文案，并在 `SYSTEM_PROMPT` 合适位置新增一句“文字与条目部分可以附加合适的emoji来展示”。
- 不进行额外重构、格式化大改、命名调整或无关清理。

## WHAT
- 基于远程目标分支硬同步本地工作树。
- 对 3 个目标文件做最小改动。
- 追加进度记录，保留历史。

## WHY
- 需要确保本地代码与指定远程分支一致，避免在旧基线上叠加改动。
- 通过最小变更降低回归风险，并满足“只改明确内容”的要求。

## HOW
1. `git fetch` 指定远程分支并 `git reset --hard FETCH_HEAD` 完成同步。
2. 逐文件检查并定点改动：
   - `models.py`：只核对 `AddRegionTextDelta`。
   - `app.py`：替换 CORS 白名单配置。
   - `prompting.py`：收窄 `layout_hint` 枚举文案并新增 emoji 风格约束句。
3. 运行最小检查，追加 `progress.md`，提交代码。
