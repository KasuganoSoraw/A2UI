# chat_ui_builder streaming ws 协议收敛（round_complete/complete）设计

## 需求详情
定向修改 `/api/chat/ws/stream` 的消息协议语义，拆分“本轮结束”与“整条流结束”。

## 澄清结果
- `a2ui_frame` 只表示单帧，不再携带 `final`。
- `streaming_final` 更名为 `streaming_round_complete`，只表示“本轮处理完成”。
- 当且仅当本次输入 `final=true` 且本轮处理完成后，额外发送 `complete`。
- `streaming_status` 保留但去掉 `final`，避免歧义。
- 本次仅改 ws 协议映射层，不改两阶段主逻辑。

## WHAT
1. `a2ui_frame` 回包改为：`type/session_id/frame`。
2. runtime item `type=final` 时：
   - 先发 `streaming_round_complete`
   - 若本次输入 `is_final=True`，再发 `complete`
3. `streaming_status` 回包去掉 `final` 字段。
4. 调整日志文案：使用 round_complete/complete，不再用旧 `streaming_final` 语义。

## WHY
- `a2ui_frame` 上带 `final` 会在一轮多帧场景里制造错误语义。
- `streaming_round_complete` 与 `complete` 分离可明确表达两层结束语义。

## HOW
- 保持 runtime item 不变（仍是 `frame/final/status`）。
- 在 app.py 层进行协议翻译并按顺序发送：
  1) 全部 frame
  2) streaming_round_complete
  3) 若 is_final=true 再发 complete
