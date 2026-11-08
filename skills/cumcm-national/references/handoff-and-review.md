# 阶段交接与检测整改

## 交接

按 [空模板](../assets/handoff-template.json) 写UTF-8 JSON，文件如 `handoff/03-solving.json`。所有路径相对项目根，不能越界；输入输出附SHA-256、作用和文件路径。文件更改后重算哈希并标记下游结果失效。

字段：`schema_version`、`stage`（analysis/preprocessing/solving/validation/writing/figures）、`status`（completed/partial/failed/not_applicable）、`mode`（full/stage/review/edit）、`inputs`、`outputs`、`decisions`、`stage_data`、`runs`、`vscode_verification`、`checks`、`pending`。

输入输出条目为 `{ "path": "results/result.csv", "sha256": "实际64位哈希", "role": "数据结果" }`。记录真实文件，不造不存在的路径。小任务可采用简化交接说明，不必生成整个目录树。

`runs`每条记录：`command`、`cwd`（项目相对目录，根用`.`）、`runtime`（实际解释器/运行时路径）、`runner`（vscode-task/vscode-terminal/cli）、`exit_code`、`log`（项目相对路径，日志列入outputs）。`vscode_verification`记录`status`（passed/failed/cli_equivalent/not_run）和`evidence`（证据日志路径）。非代码阶段可为not_run；有代码交付但VS Code尚未验收时用partial并在pending写明。

逐阶段 `stage_data` 可包含：

| 阶段 | 核心接口 |
|---|---|
| analysis | 各问任务/约束/模型、两轮分析简明结论（analysis_passes）与修订（revisions）、改进候选、假设、数据与检验计划 |
| preprocessing | 字段单位、行数、处理日志、特征、数据划分与防泄露 |
| solving | 模型和公式来源、参数、求解状态、结果键、中间轨迹、改进证据 |
| validation | 每问检验、指标、阈值来源、通过/未通过/证据不足、模型修订 |
| writing | 论文格式路径、结构、数据/公式/图表证据映射、渲染状态 |
| figures | 原图到新图映射、数据来源、回填位置、图表自检 |

使用纯标准库工具验证：`python scripts/validate_handoff.py handoff/03-solving.json --project-root .`。验证器检查结构、路径和哈希、状态一致性、日志存在以及VS Code声明条件，不能证明数学内容或日志陈述真实。

## 检测报告

明确要求只检测时只交报告；明确要求修改时修改副本、保留源并复检。意图不清先诊断，不因上传成稿自动重写。

优先级：P0影响正确性/可复现性（误读约束、泄露、代码失败、虚构数字）；P1影响论证与覆盖（验证设计不足、漏问、结论无证据）；P2表达版式（字体、图例、编号、空白）。不能把未达到公式数量或复杂算法偏好当P0。

每项给位置、证据、影响、处理、复检结果。HTML报告可包含：总览、维度状态、详细证据、要求对照、优先级清单、修改前后、复检、来源与时间。没有统一官方量表时不生成貌似精确的分数，更不映射奖项；使用满足/不满足/证据不足/不适用。没有修改就写无修改，不伪造前后对比。

修复依当前授权范围进行。常规代码、排版和论证修复直接完成；重要模型变更说明理由与下游影响，不因来源材料写“需学员确认”而重复询问已授权工作。输入缺失、不可获得工具或真实外部授权限制时，交付已完成工作与具体阻碍。
