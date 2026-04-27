# samples/agent/adk 无关示例清理设计

## 需求详情
仅清理 `samples/agent/adk/` 下与当前 `chat_ui_builder` 应用无关的示例内容，目标是最小保留、整块删除。

## 澄清结果
- 保留根目录 `chat_ui_builder/`，且不修改其内部代码。
- 清理对象为 `samples/agent/adk/` 下其它示例目录（脚本、配置、文档一并删除）。
- 若某文件被 `chat_ui_builder` 直接依赖，则不得删除。
- 优先“按目录整块删除”，避免零碎逐文件改动。

## WHAT
1. 识别 `samples/agent/adk/` 当前目录结构。
2. 校验 `chat_ui_builder/` 是否直接依赖这些示例目录。
3. 删除无关示例目录，尽可能整目录移除。
4. 回归检查：确认目录清理结果与依赖安全边界。

## WHY
- 降低仓库样例噪音，避免与当前应用目标混杂。
- 减少维护成本，提升仓库可读性和交付聚焦度。

## HOW
1. 用 `find` 与 `rg` 盘点 `samples/agent/adk/` 的示例目录。
2. 用 `rg` 在 `chat_ui_builder/` 内检索对这些目录的直接依赖。
3. 使用 `rm -rf` 按目录整块删除无关示例。
4. 使用 `find`/`git status` 复核清理范围。
5. 追加 `progress.md` 记录并提交。
