# B站 CC 字幕登录限制

## 问题

B站部分视频的 CC 字幕（AI 生成字幕/创作者上传字幕）需要登录才能访问。程序化拉取时返回空列表。

## API 调用链

### 1. 获取 cid
```
GET https://api.bilibili.com/x/web-interface/view?bvid=<BV>
→ data.cid = 36527867256
```

### 2. 尝试拉取字幕
```
GET https://api.bilibili.com/x/player/v2?bvid=<BV>&cid=<cid>
→ data.subtitle = {
    "allow_submit": false,
    "lan": "",
    "lan_doc": "",
    "subtitles": [],           ← 空的！
    "subtitle_position": null,
    "font_size_type": 0
  }
→ data.need_login_subtitle: True   ← 关键字段
```

## 判断标准

如果 `player/v2` 返回同时满足：
- `subtitles: []`（空列表）
- `need_login_subtitle: True`

→ 字幕被登录墙挡住，无法程序化获取。

## 已知案例

| BV | 视频 | need_login_subtitle |
|---|---|---|
| BV1vFNwzfEoA | 马兆远×姜Dora：AI时代的新变化 | True |

## 解决方案

1. **要求用户提供 B站 cookies.txt**：导出浏览器 cookies 后，所有 API 请求带上 cookies
2. **用户手动校对**：让用户在视频里直接看原文确认
3. **不要猜测**：tiny 模型的转写错误不可靠，没有原始字幕时不要自行"修正"

## 与 you-get .cmt.xml 的区别

- `.cmt.xml`：弹幕文件（用户评论），不含 CC 字幕
- CC 字幕：独立 JSON，通过 player API 获取
- 两者完全无关——不要用弹幕校对转写
