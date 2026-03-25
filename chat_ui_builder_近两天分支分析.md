# 当前分支分析（聚焦 `chat_ui_builder`，近两天）

## 时间窗口
- 分析窗口：近两天（截至 2026-03-25，UTC）
- 相关提交：
  - `7d4ce74`（2026-03-25 09:27:29 +0800）`回归后端结构语义并引入前端样式合并层`
  - `9fbc5e9`（2026-03-25 10:54:15 +0800）`引入宽度语义与窄栏动作回退策略`
  - `082fcc8`（2026-03-24 14:42:25 +0800）`Update service.py`

## 总体结论
近两天的变化把 `chat_ui_builder` 从“仅靠低层 delta 直接拼 UI”推进到“意图规划 + 结构编排 + 编译输出”的双路径架构：

1. **主路径升级为 Intent Plan 流程**：
   - 模型先给出页面意图（`Intent Plan`），
   - 后端经过 `Design Lint -> Layout Policy -> Layout IR -> IntentFrameCompiler`，
   - 最终输出严格 A2UI 帧。
2. **兼容旧路径与流式规划路径**：
   - 仍兼容 skeleton/planning delta 与 legacy delta。
3. **布局能力增强**：
   - 新增宽度语义（`full/readable/compact/card_grid_item`）与窄侧栏动作降级策略（`primary_plus_overflow`）。
4. **前端 demo 完整落地**：
   - React + `@a2ui/react`，以 NDJSON 增量驱动渲染。

## 提交逐条解读

### 1) `7d4ce74`：架构落地 + 前后端 demo 初版成型
该提交一次性引入大量文件（后端 agent demo + 前端 react demo）。核心价值：

- **后端服务骨架**：
  - FastAPI 暴露 `/api/chat/stream`，按行输出 NDJSON A2UI 帧。
- **语义编排链路**：
  - README 明确“Intent Plan 为主路径，旧 skeleton/delta 为 fallback”。
- **Skeleton 编译器与 region archetype**：
  - 区域模板化，减少模型直接关心低层组件树。
- **前端接流渲染**：
  - `fetch + ReadableStream + processMessages` 实时刷新 A2UI 视图。
- **样式合并层**：
  - 通过 `cn + tailwind-merge` 做 class 合并，降低样式冲突。

### 2) `9fbc5e9`：宽度语义与窄栏动作策略增强
这是对布局策略最关键的一次迭代：

- `RegionBuildContext` 新增 `width_behavior`、`actions_mode`。
- `SkeletonCompiler` 引入 `role_width` 与 `side_behavior`，按 `page_kind / emphasis / layout_hint` 推导布局 recipe。
- 在窄侧栏场景下，`actions` 区域动作布局退化为 “主动作 + overflow” 双槽位，避免挤压。
- 补充了测试：dashboard 卡片网格宽度、窄栏动作槽位、form action-first 的 footer 路由、pending delta flush 行为。

### 3) `082fcc8`：`service.py` 小幅补丁
在服务层追加了少量逻辑（5 行），属于在主流程上做增量修正，方向与上面两次提交一致：增强流式处理/容错链路。

## 当前实现（按运行链路）

### 后端链路
1. `POST /api/chat/stream` 收到消息。
2. `ChatUIService.stream_frames` 先发 loading 帧。
3. 调用 LiteLLM 流式读取模型输出：
   - 若识别到 planning delta：走 `SkeletonCompiler` 增量编译。
   - 若未识别到 planning delta：尝试解析 Intent Plan JSON，走新主路径编译。
   - 若 Intent-like 但校验失败：返回错误 surface。
   - 否则走 legacy fallback（旧 delta 解析）。

### 布局/区域编排亮点
- `LayoutRecipe` 将页面拆为 `main/side/footer` + role bucket。
- `ROLE_DEFAULT_WIDTH` + 条件覆盖，统一控制各 role 宽度语义。
- `RegionArchetypeBuilder` 将 hero/summary/details/actions/form/workflow/list 等角色模板化。
- 支持 region 先后乱序：region item 可先入队，待 region 创建后 flush。

### 前端链路
- 左侧控制台输入需求并发请求。
- 逐行解析 NDJSON，每帧调用 `processMessages([frame])`，实现增量渲染。
- 记录历史请求、动作回调、帧日志，便于联调。

## 风险与建议

### 1) 架构并行期复杂度偏高
当前同时维护 Intent 主路径 + planning delta + legacy fallback，短期利于兼容，长期建议：
- 设定退役计划：明确什么时候下线 legacy delta。
- 增加“路径命中率”指标日志（主路径/兼容路径占比）。

### 2) 布局策略规则继续增多
`page_kind/emphasis/layout_hint/side_behavior/role_width` 组合会快速膨胀，建议：
- 把策略表进一步数据化（配置驱动），减少硬编码分支。
- 增加 snapshot 测试覆盖关键组合。

### 3) 前端样式目前偏“重覆盖”
`App.css` 对 `.a2ui-*` 选择器覆盖较多，建议：
- 后续抽一层主题 token，逐步减少结构性选择器耦合。
- 对卡片嵌套、窄屏响应式补视觉回归基线。

## 结论（给当前分支）
这两天的提交使 `chat_ui_builder` 从“可演示”走向“可扩展的编排型 demo”：
- 技术上已经具备语义规划、布局决策、模板化落地和流式渲染的完整闭环；
- 下一阶段重点应从“功能补齐”转向“策略可维护性 + 回归测试 + 路径收敛”。
