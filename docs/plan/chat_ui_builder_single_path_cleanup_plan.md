# chat_ui_builder 单路径收敛开发计划

## Stage 1：主链路收敛与代码清理

### Task 1.1 收敛 service 控制流
- 移除 IntentPlan fallback 分支。
- 移除 legacy line-by-line fallback 分支。
- 保留 loading + planning 解析 + skeleton 编译 + error 反馈。

### Task 1.2 清理 fallback 专用模块
- 删除仅由 fallback 使用且已无主链依赖的模块文件。
- 清理对应 import 与辅助函数。

### Task 1.3 补充测试
- 新增 service 流式测试，验证 planning 主链。
- 新增失败测试，验证非 planning 输出触发 error surface。

### Task 1.4 验证与收尾
- 运行目标 pytest。
- 更新 progress.md（追加）。
- 完成 git 提交。
