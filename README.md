# 数模国赛 Skill · cumcm-national

面向全国大学生数学建模竞赛（CUMCM）的中文 Codex Skill：从赛题分析、数据预处理、建模求解、模型检验，到论文写作与图表美化。支持全流程、单阶段、只检测和修改已有成果。

依据六份阶段提示词、24个论文PDF（去重后23篇）整理，其中包含8篇2026年展示论文。学习论文的结构与证据组织，按题目的数学本质选模板。

## 安装

在 Codex 中输入：

```text
$skill-installer 安装 https://github.com/lianglele915/cumcm-national-skill/tree/main/skills/cumcm-national
```

也可将 `skills/cumcm-national` 整个文件夹复制到项目的 `.agents/skills/` 下。技能需以完整文件夹安装，不能只复制 `SKILL.md`。本机若采用自定义 `CODEX_HOME/skills`，也可放到对应用户技能目录。

## 使用

```text
使用 $cumcm-national 分析这份国赛题目和附件。
先给逐问分析、八列速查表、基线与改进方案，不写论文。
```

```text
使用 $cumcm-national 完成这份题目的预处理、求解和检验。
代码在 VS Code 所选环境中实际运行，附任务配置、依赖、运行日志与输出检查。
```

```text
使用 $cumcm-national，参考2026展示论文中适合本题的结构整理我的论文。
所有数字使用现有结果，缺失实验列出来；请交付Word版。
```

```text
使用 $cumcm-national 只检测这篇论文，列出问题和证据，不修改原稿。
```

```text
使用 $cumcm-national 美化这几张图，保持数据与统计含义，附可复现绘图代码。
```

## 论文模板

- 机理与几何：坐标、机理、控制方程、数值求解及物理检验。
- 确定性优化：变量、目标、完整约束、求解状态与可行方案。
- 随机与风险优化：不确定性来源、决策信息、场景、风险和独立验证。
- 统计预测与决策：数据侧写、防泄露、模型验证、预测到行动。
- 2026专项：热质耦合、有界误差定位/覆盖、预测驱动滚动调度、周期冲突与最优性界、广告预算与效益。

[技能入口](skills/cumcm-national/SKILL.md) · [论文示例索引](skills/cumcm-national/references/paper-examples.md) · [2026参考卡](skills/cumcm-national/references/papers-2026.md) · [来源与修订](skills/cumcm-national/references/source-notes.md)

## VS Code运行要求

交付的预处理、求解、检验、绘图等代码须在 VS Code 集成终端或任务中实际运行。记录解释器、工作目录、命令参数、退出码、日志和结果检查。仅审阅代码或在外部终端执行，不能称为完成 VS Code 验收。

完整项目可适配随附的 [Python任务模板](skills/cumcm-national/assets/tasks.python.json)。模型正确性、可行性、数值稳定性和论文版式还需分别检查；进程退出码0不是全部验收。

## 交接工具与测试

`validate_handoff.py` 只使用 Python 标准库，建议 Python 3.10及以上：

```text
python skills/cumcm-national/scripts/validate_handoff.py 项目/handoff/03-solving.json --project-root 项目
python -m unittest discover -s tests -v
```

工具检查交接结构、文件路径、SHA-256、状态和运行证据的一致性，能阻止把只有命令行记录的代码交付误标为 VS Code 已完成。它不代替真实执行和数学判断。

## 资源边界

仓库包含提炼后的指导、结构模板、论文参考卡、文件来源哈希和校验代码，不包含原始论文PDF、微信临时路径、赛题数据和现成答案。扫描论文按已记录页码阅读，不宣称逐页复核或复算所有论文。

模型选择依题意与证据，不绑定A/B/C/D/E题号，不保证获奖，不强凑公式、创新点和图表数量。篇幅与格式在执行时核对当届官方模板。

验证范围与实际执行记录见 [验证说明](docs/VALIDATION.md)。
