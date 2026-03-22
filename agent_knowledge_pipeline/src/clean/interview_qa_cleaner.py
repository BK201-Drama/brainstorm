from __future__ import annotations

from typing import List, Dict


# 面向前后端转型，强调工程落地，不讲重学术
QA_BANK = [
    ("rag", "RAG 的完整流程是什么？", "离线做切分+向量化+入库，在线做查询改写、召回、重排、拼提示词、生成与引用返回。"),
    ("rag", "Chunk 大小怎么选？", "先按语义段落切，再做 300~800 token 的窗口试验；看召回命中率和答案完整度来调。"),
    ("rag", "为什么召回到了还是答错？", "常见是 chunk 不完整、重排没生效、上下文被截断或提示词没要求‘仅依据检索内容回答’。"),
    ("rag", "什么时候要混合检索？", "当关键词精确匹配很重要时，用 BM25+向量混合，能同时保住术语命中和语义召回。"),
    ("rag", "如何降低幻觉？", "做证据引用、低温度、回答前检查证据覆盖、无证据时明确输出‘不知道’。"),
    ("rag", "RAG 怎么评估？", "离线看 Recall@k、MRR、答案正确率；在线看满意度、追问率、人工兜底率。"),

    ("langchain", "LangChain 在项目里主要解决什么？", "把模型调用、检索、工具、状态编排成可维护流水线，减少散乱脚本。"),
    ("langchain", "LCEL 的优势是什么？", "可组合、可复用、可观测，链路更清晰，方便并行和重试。"),
    ("langchain", "Runnable 并行适合什么场景？", "多路召回、多个工具独立查询、并发特征提取等 IO 密集场景。"),
    ("langchain", "LangChain 项目如何防止变成屎山？", "分层：prompt/retriever/tools/workflow；加 tracing、单测和配置化。"),
    ("langchain", "Memory 什么时候用？", "多轮任务需要上下文时用短期 memory；业务事实放数据库，不放对话内存。"),

    ("agent", "Agent 和 Workflow 区别？", "Workflow 路径固定，Agent 会按目标自主选工具和下一步。"),
    ("agent", "什么时候不该用 Agent？", "流程稳定、规则明确、可枚举分支时，直接工作流更稳更便宜。"),
    ("agent", "Tool Calling 需要做哪些保护？", "参数校验、权限白名单、超时重试、幂等键、审计日志。"),
    ("agent", "如何控制 Agent 乱调用？", "限制工具描述、缩小候选工具集、加计划-执行-检查三段式。"),
    ("agent", "多 Agent 协作核心点？", "职责单一、共享状态清晰、失败可回滚、人工兜底可插入。"),

    ("agentic_search", "什么是 Agentic Search？", "不是一次检索就回答，而是‘规划-检索-反思-再检索-归纳’循环。"),
    ("agentic_search", "什么时候停止搜索？", "当关键子问题都有证据覆盖，且新检索不再显著提升答案质量时停止。"),
    ("agentic_search", "如何做多跳问题分解？", "先拆成可验证子问题，再按依赖顺序检索，最后合并证据回答。"),
    ("agentic_search", "证据冲突怎么处理？", "按来源权威、时效、一致性打分；保留分歧并说明采信理由。"),
    ("agentic_search", "怎么控成本？", "限制最大轮数、每轮 top-k、结果缓存、相似问题复用。"),
]


def build_interview_qa(seed_materials: List[Dict]) -> List[Dict]:
    source_map = {
        "rag": "LangChain RAG Docs",
        "langchain": "LangChain Docs",
        "agent": "Lilian Weng Agent Blog",
        "agentic_search": "ProjectPro Agentic Workflow",
    }
    out: List[Dict] = []
    for topic, q, a in QA_BANK:
        out.append(
            {
                "topic": topic,
                "question": q,
                "answer": a,
                "level": "beginner",
                "source": source_map.get(topic, "curated"),
                "tags": ["interview", "八股", topic],
            }
        )
    return out
