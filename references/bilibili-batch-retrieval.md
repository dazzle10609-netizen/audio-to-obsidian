# B站系列批量检索 — 探索记录

用户需求：给一个系列/UP主主页 URL，自动拉取所有视频列表后逐条处理。

## 已验证可行的方案

### ✅ yt-dlp --flat-playlist on season/collection URLs

```
yt-dlp --flat-playlist --dump-json "https://space.bilibili.com/<uid>/lists/<id>?type=season"
→ 成功返回全部视频 JSON（零反爬，秒出）
```

关键发现（2026-06-22）：
- yt-dlp 对 B站**单个视频下载**被 WBI 反爬拦截（HTTP 412）
- 但对 B站 **season/合集页面**的 flat playlist 提取完全不受影响
- 原因是 playlist extractor 调用的是合集元数据 API，不触发 WBI 反爬
- 验证案例：姜Dora 合集 `space.bilibili.com/16385920/lists/598302?type=season`，108 条视频全部拉出

每条 JSON 包含字段：
- `id`: BV 编号
- `url`: 视频链接
- `playlist_index`: 序号（1=最新）
- `playlist_count`: 合集总数
- `playlist_title`: 合集名称

### ✅ you-get 下载单条 B站视频

```
you-get --format=dash-flv360-AV1 -o . "https://www.bilibili.com/video/<BV>"
→ 下载视频流，无登录可获取 360P/480P DASH 格式
```

配合 ffmpeg 抽音轨后删除视频文件。

## 已探索的死胡同

### ❌ yt-dlp --flat-playlist on space pages

```
yt-dlp --flat-playlist --dump-json "https://space.bilibili.com/<uid>/video"
→ ERROR: Request is blocked by server (412)
```

### ❌ WBI 签名 API（未跑通）

B站 API `x/space/wbi/arc/search` 需要 WBI 签名。尝试步骤：
1. 从 `api.bilibili.com/x/web-interface/nav` 获取 `img_key` + `sub_key`
2. 拼接后按固定位置表提取 mixin key
3. 对参数排序 → MD5 → 附加 `w_rid`
4. 结果：`-352 风控校验失败` — mixin key 位置表可能已更新

结论：WBI 签名路径不稳定（密钥位置周期性更新），不推荐作为主要方案。

### ❌ curl 刮 HTML（合集页/空间页）

B站空间页为 JS 动态渲染，`__INITIAL_STATE__` 中不含视频列表。合集页 curl 也无法获取视频数据。

## 推荐的工作流

1. **用户提供合集链接**（`space.bilibili.com/<uid>/lists/<id>?type=season`）
2. `yt-dlp --flat-playlist --dump-json` 拉取全部 BV 列表
3. 展示最新 10-20 条给用户确认
4. 逐条 you-get 下载 → ffmpeg 抽音轨 → faster-whisper 转写 → 写 Obsidian 笔记
5. 每条视频结束后清理工作文件

## 跨平台对比

| 平台 | 单视频下载 | 批量列表拉取 | 工具 |
|---|---|---|---|
| B站 | ✅ you-get | ✅ yt-dlp flat (season URL) | you-get + yt-dlp |
| 抖音 | ✅ yt-dlp | 待验证 | yt-dlp |
| YouTube | ✅ yt-dlp | ✅ yt-dlp flat | yt-dlp |
