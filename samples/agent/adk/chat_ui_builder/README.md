# Chat UI Builder Demo

这个 demo 会把自然语言需求转换成增量 A2UI 数据帧。
它通过 LiteLLM 调用本地 OpenAI-compatible 模型，要求模型流式输出 **planning delta**（一行一个 JSON 事件），
后端解析后直接编译成 A2UI v0.8 数据帧并流式返回前端。

当前定位：A2UI 是**上游 Agent 结果展示层**，负责组织和呈现输入数据，不负责补充新的业务结论或解决方案。

## 为什么需要这个 demo

和固定领域模板示例不同，这个 demo 不把模型锁死在单一业务域里。
模型会流式输出页面规划事件，后端负责把事件增量编译成可渲染帧。

## 本地模型配置

服务默认指向一个本地 OpenAI-compatible 端点：

```bash
export OPENAI_API_BASE="http://10.50.95.196:8000/v1"
export OPENAI_API_KEY="sk-1234"
export LITELLM_MODEL="openai/qwen3.5"
```

可选日志参数：

```bash
export LOG_LEVEL="INFO"
export MAX_LOG_CHARS="1200"
```

后端会记录：
- LLM 调用端点、模型名、温度
- 发送给 LLM 的消息
- LLM 的流式 chunk / planning delta
- planning delta 与编译后的 A2UI 骨架帧摘要
- 编译后的 A2UI 数据帧

## 启动后端

```bash
cd samples/agent/adk/chat_ui_builder
uv run .
```

默认启动在 `http://localhost:8010`。

## API

### `POST /api/chat/stream`

请求体：

```json
{
  "source_data": {
    "summary": "模型推理耗时上升",
    "metrics": {"latency_p95_ms": 920, "error_rate": "2.1%"},
    "logs": ["10:32 timeout request_id=abc123", "10:34 upstream reset"]
  },
  "user_query": "帮我看一下线上推理服务发生了什么"
}
```

兼容旧格式（`message`）仍可使用，但推荐以 `source_data` 作为主输入。

### 日志搜索模板（log_search_result_template）

当 `source_data` 命中日志结果特征（如 `exceptionInfos/logs/records/events`）时，后端会走内置展示模板，稳定产出：
- 概览区（标题、事实性摘要、关键统计）
- 事件主视图（按时间顺序列表）
- 对象与上下文区（ciName/ciType/abnormalityId/query/source）
- 原始数据区（JSON 证据）

该模板默认不生成 actions 区，除非输入中显式包含动作项。

返回：
- `application/x-ndjson`
- 每一行都是一个合法的 A2UI envelope（`beginRendering`、`surfaceUpdate`、`dataModelUpdate` 或 `deleteSurface`）

## 中间层说明

当前版本主路径：

- `init_plan / add_region* / finalize_plan` 等 planning delta 事件（逐行 JSON）

后端链路：

- `PlanningDeltaStreamParser`：解析 LLM 流中的 planning delta 行
- `SkeletonCompiler`：将 planning delta 编译成低层布局增量
- `FrameCompiler`：输出 `beginRendering` / `surfaceUpdate` / `dataModelUpdate`
- 前端按帧渐进式渲染

当前 demo 不再包含 IntentPlan fallback 或 legacy line-by-line fallback。
并且默认启用“展示层约束”：若输入未明确提供 actions/recommendations/next_steps，不会渲染 actions 区域。

## 前端 demo

对应的 React 前端位于：

```bash
samples/client/react/chat_ui_builder
```
