# chat_ui_builder 去 bucket / 去全局 order 开发计划

## Stage 1：设计确认
### Task 1.1
- 固化重构边界：Skeleton 去 bucket，Compiler 去页面级全局 order。

## Stage 2：Skeleton 收敛
### Task 2.1
- 删除 runtime bucket 状态与配方方法。
### Task 2.2
- RegionHandler 直接使用页面主父容器，不再 ensure bucket。
### Task 2.3
- PlanHandler 初始化去除 bucket 相关状态。

## Stage 3：FrameCompiler 顺序策略调整
### Task 3.1
- 删除 child_order/insertion_counter 全局排序状态。
### Task 3.2
- 页面主容器按 append 顺序；局部容器保留 order 稳定性。

## Stage 4：测试与收尾
### Task 4.1
- 更新 bucket 相关测试预期。
### Task 4.2
- 运行最小检查并追加 progress。
