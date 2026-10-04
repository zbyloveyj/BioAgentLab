# 构建、验证与发布

## 环境

核心程序：Python 3.10+，无必需第三方运行依赖。开发测试安装 `.[dev]`。

PDF构建需要系统的Pandoc、XeLaTeX、ctex和字体，Python侧需要PyMuPDF。Ubuntu参考：

```bash
sudo apt-get update
sudo apt-get install -y pandoc texlive-xetex texlive-lang-chinese \
  texlive-latex-extra fonts-noto-cjk fonts-dejavu-core fonts-liberation
python -m pip install -e ".[dev,book,notebooks]"
```

字体通过系统安装，不复制字体文件到仓库或发布ZIP。PDF中用于正常阅读的字体嵌入不等于分发原始字体文件。

## 顺序

```bash
python scripts/build_notebooks.py --execute
python scripts/build_book.py --min-pages 200
python scripts/verify_release.py
python scripts/package_release.py
```

Notebook逐个使用新内核运行，全部是离线合成材料。构建器运行三遍XeLaTeX以解析目录与页码；源文件按 `book/zh/` 文件名排序。`--min-pages`仅作验收，不改变字号或插页。

`verify_release.py`运行测试，检查PDF、目录、Notebook执行记录，并保存 `docs/verification.json`。布局仍需人工查看实际页图，不能只靠文字提取。

## GitHub Actions

`book-build.yml`可手动触发；提交信息包含 `[build-book]`且改变书籍或构建相关文件时也会触发。通过后将PDF、构建记录、Notebook、目录与验证记录提交回仓库，并上传完整发布产物。

`source-export.yml`通过 `[export-source]`提交导出文本源码，服务于构建和复核。`tests.yml`执行快速单元/集成测试。自动化使用最小必要仓库权限，不读取其他仓库或个人数据。

## 产物与范围

PDF：`docs/pdf/AI_Agent_for_Biology_ZH.pdf`。
完整本地发布包：`dist/BioAgentLab_2026_10.zip`。
验证记录：`docs/verification.json`。

代码测试、Notebook执行与PDF编译不代表真实生物学发现获得验证。在线适配器未进行真实服务调用时，验证记录明确标注。
