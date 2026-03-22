# agent_knowledge_pipeline

目标：构建一个“文章采集 → 清洗 → 本地入库 → 飞书机器人推送”的轻量流水线，用于给群友学八股。

## 功能范围

1. 获取 Agent 开发相关文章（RSS/网页）
2. 清洗正文（去导航、去广告、统一结构）
3. 转成本地数据（JSONL）
4. 生成可发送到飞书机器人的消息 payload（后续可直接接 webhook）

## 项目结构

```text
agent_knowledge_pipeline/
├─ src/
│  ├─ fetch/      # 抓取源
│  ├─ clean/      # 文本清洗
│  ├─ store/      # 本地存储
│  └─ deliver/    # 飞书消息构建
├─ data/
│  ├─ raw/        # 原始抓取
│  ├─ clean/      # 清洗结果
│  └─ local/      # 最终 JSONL 数据
├─ configs/       # 源配置
└─ scripts/       # 一键执行脚本
```

## 快速开始

```bash
cd /home/ubuntu/.openclaw/workspace/brainstorm/agent_knowledge_pipeline
python3 scripts/run_pipeline.py
```

执行后会生成：
- `data/raw/*.json`
- `data/clean/*.json`
- `data/local/articles.jsonl`
- `data/local/feishu_messages.jsonl`

## 下一步（你确认后我继续）

- 接入真实来源（如 OpenAI/Anthropic/Google/开源社区博客 RSS）
- 增加去重、标签、难度分级
- 直接接飞书 webhook 自动推送
