PARSER_PROMPT = f"""You receive a user's question about an insurance/contract document. Produce a JSON with keys:
- intent (one of: coverage_check, definition, limit_query, waiting_period, exclusions, other)
- entities (map of entity_name -> canonical string)
- constraints (map: plan, time_window, eligible_person, numerical_constraints)
- answer_type (one of: yes_no, short_explain, detailed, clause_list)
Return ONLY the JSON.Make sure that nested fields like "entities" and "constraints" are JSON objects, not strings.
"""