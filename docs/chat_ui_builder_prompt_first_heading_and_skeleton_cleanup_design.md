# Chat UI Builder：标题规则前移到 Prompt 与骨架死代码清理设计

## 需求详情
- 把“页面唯一 h1 / hero 不重复标题”的主约束前移到 `SYSTEM_PROMPT`。
- 后端仅保留轻量去重兜底，避免过度改写模型意图。
- 清理 `skeleton_compiler.py` 中无用 bucket 旧逻辑与伪分支。

## 澄清结果
- 本次不改 loading / beginRendering / auto overview 主流程。
- 仅修改：`prompting.py`、`skeleton_compiler.py` 及相关测试。
- 需真正删除 `_build_role_buckets()`，不是仅不调用。

## WHAT
1. Prompt 中新增明确规则：
   - 页面标题是唯一 h1；
   - hero 不应重复页面主标题；
   - hero 更适合摘要/关键信息（body/h2）；
   - role 语义职责清晰化（hero/summary/details/list/workflow/supporting）。
2. 后端 hero 标题兜底收紧为“仅明显重复才丢弃”，不再一刀切降级 h1。
3. 删除 `_build_role_buckets()` 与无意义 parent context 伪分支。
4. 同步测试，验证新兜底行为与懒创建逻辑。

## WHY
- 标题层级是规划语义，应由模型在 prompt 侧主导，后端只做防错。
- 清理死代码可降低维护成本，减少“逻辑看起来存在但实际无意义”的误导。

## HOW
1. 重写 `SYSTEM_PROMPT` 的标题层级与 role 责任段落。
2. 在 `skeleton_compiler.py`：
   - 删除 `_build_role_buckets()`；
   - `_ensure_bucket_for_role()` 直接 `parent_id='root'`；
   - hero h1 仅在与页面标题近重复时丢弃，其余不改写。
3. 更新 `test_region_archetypes.py` 对 hero h1 兜底的断言。
