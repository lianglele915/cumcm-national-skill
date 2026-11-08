# VS Code实际运行验收

本技能的用户要求：写出的代码须在VS Code检验能运行。此要求适用于预处理、求解、模型检验、绘图和论文生成程序。语法检查、打开编辑器、安装扩展均不等于运行通过。

## 环境与入口

1. 用VS Code打开用户项目根目录；检查已有 `.vscode` 配置，不覆盖无关配置。
2. Python项目选实际存在的解释器/虚拟环境，记录 `sys.executable`、Python版本与依赖；需要时在项目虚拟环境安装依赖。MATLAB等项目使用相应可用运行时与VS Code集成终端任务，不强转Python。
3. 工作目录设项目根，入口建议 `run_all.py` 或实际已有入口。采用项目相对路径；文件缺失应明确报错，不偷偷造附件。完整项目提供运行说明、依赖和匹配的 `.vscode/tasks.json`；可选debugpy调试配置，不能假设扩展已安装。

Python任务可从 [tasks.python.json](../assets/tasks.python.json) 复制后适配实际入口。它依赖VS Code Python扩展所选解释器；无扩展时用已核对的解释器路径，不把作者本机路径带给用户。

## 运行与检查

- 在VS Code集成终端或任务中实际执行。先快速样例检查导入、路径与基本逻辑，再运行用户正式输入与实际入口。小规模通过不等于全量完成。
- 保存命令/参数、工作目录、解释器、时间、退出码、stdout/stderr以及关键输出清单。记录是VS Code终端还是VS Code任务。
- 修复导入、编码、路径、缺依赖、数值或求解错误后，重新执行受影响入口及下游；不能仅修代码就宣布通过。
- 退出码0只代表进程成功，仍核对题目要求输出、样本/维度、NaN/Inf、约束与单位、图表和结果的基本合理性。模型数学验证按专用阶段另做。
- VS Code任务可用编辑器任务API执行并读取实际进程结束事件；该路径是真正编辑器内执行，而仅启动code命令不是。

## 诚实状态

`passed`：真实VS Code终端/任务执行、正常退出、输出检查完成，有日志与解释器记录。

`failed`：在VS Code实际执行但异常或输出不符，记录错误、已修复项与剩余问题。

`cli_equivalent`：只在外部命令行用相同解释器/目录执行；可报告命令行通过，但VS Code验收未完成。

`not_run`：环境缺失、只有代码审阅、缺输入或未执行，不能写通过。

受限环境无编辑器控制能力时先完成不依赖UI的工作，交付VS Code任务配置及精确操作和未完成状态；不要伪造编辑器运行日志。无需为了验收修改用户全局编辑器配置。

VS Code任务和自动化执行参考：[Task Provider](https://code.visualstudio.com/api/extension-guides/task-provider)、[Testing Extensions](https://code.visualstudio.com/api/working-with-extensions/testing-extension)。
