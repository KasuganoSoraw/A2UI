# chat_ui_builder streaming session 级 StreamCompiler 隔离修复设计

## 需求详情
定向修复 streaming 链路中 `StreamCompiler` 全局复用导致的 session/轮次状态污染问题。

## 澄清结果
- 仅修复 compiler 生命周期归属问题。
- 不做 runtime/service 其它无关重构。
- `StreamCompiler` 应由 runtime 以 session 维度管理并跨轮复用。
- service 不再持有全局 `_stream_compiler`。

## WHAT
1. `streaming/runtime.py`
   - 新增 `self._session_compilers: dict[str, StreamCompiler]`。
   - 每个 session 首次创建 compiler 并复用。
   - 调用 service 时显式传入该 session compiler。
   - 增加两条关键日志：compiler 创建、每轮调用绑定 session compiler。

2. `streaming/service.py`
   - 移除 `__init__` 中全局 `_stream_compiler` 持有。
   - `stream_project_segment(...)` 增加参数 `stream_compiler: StreamCompiler`。
   - event 编译改为 `stream_compiler.apply(event)`。

## WHY
- `StreamCompiler` 内部含 `surface_initialized/blocks/dataset_to_block/table_cache` 等状态，天然是“会话级”状态，不应全局共享。
- 全局复用会导致不同 session 串状态，触发重复 create block、init_surface 被错误忽略。
- 每轮新建又会丢失同 session 的追加上下文，破坏增量渲染。

## HOW
- runtime 负责 session 生命周期：session state + session compiler。
- service 只接收并使用调用方传入 compiler，不再隐藏状态。
- 同 session 跨轮持续复用同一 compiler；不同 session 用不同 compiler 实例。
