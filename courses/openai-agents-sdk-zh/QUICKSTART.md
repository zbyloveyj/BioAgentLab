# 五分钟快速上手

1. `git clone https://github.com/zbyloveyj/BioAgentLab.git`
2. `cd BioAgentLab/courses/openai-agents-sdk-zh`
3. `python -m venv .venv` 并激活虚拟环境。
4. `python -m pip install -e ".[notebook,dev]"`。
5. `python lessons/00_environment_check.py`、`pytest -q`：**先验证本地代码**。
6. 复制 `.env.example` 到 `.env`，填入 `OPENAI_API_KEY`。
7. `python lessons/01_first_agent.py`。
8. `python lessons/02_function_tools.py`。
9. `python -m jupyter lab`，打开 `notebooks/00_开始之前.ipynb`。

有 API Key ≠ 已经运行过代码；必须在本机执行并查看输出。没有 Key 时可先阅读 Notebook、完成离线脚本与测试。

## Git 日常更新

进入 `BioAgentLab` 仓库根目录后执行 `git pull` 获取后续课程更新。请始终在 `courses/openai-agents-sdk-zh` 目录运行脚本。
