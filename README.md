# Audio to Obsidian

`audio-to-obsidian` 是一个 AI agent skill，把播客 / 视频 / 公开音频链接整理成 Obsidian 结构化笔记，可选导出 PDF。

它的目标不是做一个"很会总结"的摘要器，而是尽量保留原文的框架、对话和金句，产出一份你后续还愿意回看的笔记——不是替你理解，是帮你留住值得回看的东西。

参考了 [podcast-to-obsidian](https://github.com/1111cecream/podcast-to-obsidian) 的 README 写法。

## 这个 skill 做什么

- 贴一个链接（B站 / YouTube / 小宇宙 / 抖音 / 任意公开音频），自动下载音频。
- 本地处理音频，产出带时间戳的逐字稿和结构化笔记。
- 笔记保留对话原文、核心框架、金句，不是 AI 味的三段式摘要。
- 自动存入 Obsidian vault，按「频道 → 单集」嵌套文件夹组织，同步更新全局索引。
- 可选：一键导出干净 PDF，方便分享和离线阅读。
- 支持 B站合集 / YouTube 播放列表的批量排队处理。

## 使用前提

你需要准备这些东西：

- 一个公开的音频/视频链接（B站 / YouTube / 小宇宙 / 抖音 / 直接音频 URL）。
- 如果要做本地音频处理，需要安装 `ffmpeg`。
- 如果要做 PDF 导出，需要安装 `pandoc` 和 `wkhtmltopdf`（可选）。
- 一个支持 skill 工作流的 AI 环境（Codex / Claude Code / Hermes Agent）。

AI agent 首次运行时会自动检测缺失依赖并安装，零手动配置。

## 主要笔记规范

当前默认的笔记风格大致是这样：

- 默认产出详细笔记，不是短摘要。4 小时访谈 ≈ 10–15 KB 笔记。
- 尽量保留播客原本的展开顺序，按对话阶段分节，带对话原文和说话人标注。
- 每个阶段末尾标注 **金句**。
- 全文结束后有 **核心洞察**（跨章节的深层连接）、**可落地的动作**（3–5 条）、**思考题**（5–7 个开放问题）。
- 头部信息保留：来源链接、频道/播客名、嘉宾、时长、整理日期。
- 会主动删掉寒暄、重复铺垫、口播广告、低信息量过渡句。
- 不把正文写成"这一段讲了什么""为什么重要"这种模板腔。

## 这套风格的边界

这里的笔记规范，更多是作者当前的个人习惯，不是某种唯一正确的 Obsidian 笔记标准。你可能觉得太详细、或某些部分太啰嗦——这是正常的。笔记是为自己写的，不是为别人写的。后面大概率还会继续改。

播客还是要自己听，哪怕是二倍速；这个 skill 更像是帮你生成一份内容较多的笔记草稿，让你不用从零开始对着空白文档发呆。

## 仓库结构

```text
audio-to-obsidian/
├── README.md
├── SKILL.md
├── transcribe.py
└── references/
    ├── bilibili-anti-bot.md
    ├── bilibili-batch-retrieval.md
    ├── bilibili-subtitle-login.md
    └── xiaoyuzhou-extraction.md
```

## License

本仓库使用 MIT License，方便别人学习、复用和继续修改。
