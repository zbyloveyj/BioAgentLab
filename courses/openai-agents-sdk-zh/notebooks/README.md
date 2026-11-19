# 按顺序学习 Jupyter Notebook

在本项目根目录打开 Jupyter：

```bash
python -m jupyter lab
```

从 `00_开始之前.ipynb` 开始，每课一个 Notebook，按数字顺序进入下一课。

## 常见问题

- **找不到 agent_course**：必须从课程根目录启动 Jupyter，且已安装 `pip install -e ".[notebook,dev]"`。
- **找不到 agents**：确保 Notebook 内核属于已安装 openai-agents 的虚拟环境。
- **没有 API Key**：先运行 00 与 12 课程、离线测试；不要强行运行联网示例。
- **运行中收费**：每个 `Runner.run` / `run_streamed` 都有可能发起模型请求，使用前检查 API 额度。
- **需要真实文献**：05 / 11 通过 NCBI 官方接口查询，需自己设置真实 `NCBI_EMAIL`。
