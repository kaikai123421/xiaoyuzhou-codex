# xiaoyuzhou-codex

一个 RSS 优先、以小宇宙为收听入口的播客雷达：每天筛选中英文优质节目，发送中文飞书日报，并支持回复“深挖 2、5”。

## 功能

- 追踪公开 RSS，保留小宇宙节目链接。
- 按 AI/科技、商业投资、心理认知、健康科学和人物访谈评分。
- 每天精选 5–8 期，不足时宁缺毋滥。
- 解析飞书中的深挖与偏好反馈指令。
- 优先使用发布方逐字稿，再按许可转写音频。
- 提供可安装的 Codex skill 和 GitHub Actions 定时模板。

## 本地试用

需要 Python 3.11 或更高版本：

```powershell
python -m pip install -e .
Copy-Item config/config.example.json config/config.json
Copy-Item config/private.example.json private/config.json
xyz-codex check-sources
xyz-codex daily
```

把示例订阅和飞书占位信息替换为自己的配置。`private/`、真实配置、状态和报告默认不会进入 Git。

## 命令

- `check-sources`：检查 RSS 可用性。
- `daily`：生成日报并按配置发送飞书。
- `daily --dry-run`：只预览，不写入状态或发送消息。
- `process-commands`：处理飞书回复。
- `deep-dive`：根据逐字稿、字幕、音频转写或节目笔记生成带证据标签的深挖提示。
- `discover`：输出待人工审核的候选节目。

## 自动运行

仓库工作流在北京时间 08:00 运行日报，并每小时处理一次飞书指令。配置 GitHub Secrets：

- `PUBLIC_CONFIG_JSON`：真实公开配置内容。
- `PRIVATE_CONFIG_JSON`：飞书及可选转写服务的私密配置。

状态通过 GitHub Actions 缓存跨运行保存。更推荐使用 Codex 自动任务调用 `skills/xiaoyuzhou-podcast-radar`，以便完成语义摘要和飞书知识库归档。

## 安全边界

项目不调用小宇宙私有接口，不绕过付费或访问控制，不把节目简介冒充完整听取结果。医疗、心理及投资信息仅作信息参考。

## License

MIT
