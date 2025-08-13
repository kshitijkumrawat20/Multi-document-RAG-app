from app.schemas.request_models import QuerySpec, LogicResult


def evaluate_with_llm(raw_query: str, top_clauses: list, llm):
    """
    Use the LLM to analyze retrieved clauses and return structured decision.
    """

    # Prepare context for the prompt
    context_clauses = []
    for i, c in enumerate(top_clauses, 1):
        context_clauses.append(f"{i}) [source:{c.doc_id} page:{c.page}] {c.text}")
    print(chr(10).join(context_clauses))
        
    # Build prompt
    prompt = f"""
        You are an insurance policy analyst. Question: "{raw_query}"

        Provided clauses (numbered):
        {chr(10).join(context_clauses)}

        Task:
        1) Decide: COVERED / NOT_COVERED / CONDITIONAL
        2) Summarize the exact clause(s) that justify your decision.
        3) List any conditions, waiting periods, sublimits, or exclusions relevant.
        4) Provide a concise final answer (1-2 sentences).

        Return JSON with these exact keys:
        {{
            "decision": "...",
            "evidence": [
                {{"doc_id": "...", "page": 0, "snippet": "...", "reason": "..."}}
            ],
            "confidence": 0.0,
            "rationale": "...",
            "answer": "..."
        }}
        """

    # Directly parse to LogicResult using structured output
    structured_llm = llm.with_structured_output(LogicResult)
    result: LogicResult = structured_llm.invoke(prompt)
    # print(f"result: {result}\n result_type{type(result)}")

    # Attach full text for each evidence
    enriched_evidence = []
    for ev in result.evidence:
        matched = next((c for c in top_clauses if c.doc_id == ev.doc_id and str(c.page) == str(ev.page)), None)
        if matched:
            ev.text = matched.text  # or use a different field if needed
        enriched_evidence.append(ev)

    result.evidence = enriched_evidence
    # print(enriched_evidence[0])
    return result
