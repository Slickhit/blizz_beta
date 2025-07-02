"""Shadow evaluation utilities for comparing models."""

from langchain_openai import ChatOpenAI
from modules import event_logger


def compare(query: str, candidate_model: str = "gpt-4o", baseline_model: str = "gpt-3.5-turbo") -> str:
    base = ChatOpenAI(model=baseline_model)
    cand = ChatOpenAI(model=candidate_model)
    base_reply = base.invoke(query).content
    cand_reply = cand.invoke(query).content
    event_logger.log_event(
        "shadow_eval",
        {"query": query, "baseline": base_reply, "candidate": cand_reply},
    )
    return cand_reply

