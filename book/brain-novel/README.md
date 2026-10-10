# 《在我们理解大脑之前》 · GitHub Pages + Quarto 在线试读

本目录是以**前三章免费试读**为范围的独立 Quarto `book` 项目。完整24章、尚未审校完成的历史图片与完整 Word 文件**均未上传**。

## 访问方式

GitHub Pages 仓库：`zbyloveyj/BioAgentLab`。开启 Pages 后，在 **Settings → Pages → Build and deployment → Deploy from a branch → main /docs → Save**，访问：

https://zbyloveyj.github.io/BioAgentLab/brain-novel/

仓库源码：`book/brain-novel/`；编译后网页：`docs/brain-novel/`。`main` 分支上的其他 BioAgentLab 文件不会被替换。

## Quarto 本地重建

安装 [Quarto](https://quarto.org/docs/get-started/) 后执行：

```bash
cd book/brain-novel
quarto render
```

生成 `_book/` 后复制到仓库 `docs/brain-novel/`。仓库中也配置了 `.github/workflows/brain-novel-quarto.yml`：源码变更后自动使用 Quarto 重建公开子目录。若工作流写入失败，检查仓库 Settings → Actions → General 中的 Workflow permissions。

## 版权与读者声明

这是一部结合真实科学史与虚构故事的作品。部分文本由作者与AI协作生成，具体对话不是历史引文。待授权的图片尚未公开。请勿将现有试读视为科学史终审定稿。
