# Agentic RL 调研报告文件

由于当前代码审查/PR 流程不支持直接提交二进制 `.pptx` 文件，仓库里改为提交文本安全的 Base64 文件：

1. `agentic_rl_survey_cn.pptx.base64`：仓库根目录副本，方便直接下载。
2. `reports/agentic_rl_survey_cn.pptx.base64`：报告目录内的同内容副本。


如果你只是想快速看 PPTX 长什么样，不想先处理 Base64，可以先看预览文件：

```text
reports/agentic_rl_survey_cn_preview_first6.svg
reports/agentic_rl_survey_cn_preview.svg
reports/agentic_rl_survey_cn_preview.html
```

`agentic_rl_survey_cn_preview_first6.svg` 是 6 页快速预览；`agentic_rl_survey_cn_preview.svg` 可以在 GitHub 里直接点开看完整图；`agentic_rl_survey_cn_preview.html` 下载后用浏览器打开。两个预览都包含全部 30 页，布局接近生成的 PPTX。

下载 `.base64` 文件后，在仓库根目录运行下面任意一种方式即可还原出可打开的 PowerPoint 文件 `agentic_rl_survey_cn.pptx`：

```bash
python3 tools/decode_agentic_rl_pptx.py
```

或：

```bash
base64 -d agentic_rl_survey_cn.pptx.base64 > agentic_rl_survey_cn.pptx
```

也可以直接从 Markdown 源稿重新生成 PPTX：

```bash
python3 tools/build_agentic_rl_pptx.py
```

Markdown 源稿在 `reports/agentic_rl_survey_cn_slides.md`，参考文献在 `reports/agentic_rl_references.md`。
