from app.utils.model_loader import ModelLoader
from app.schemas.request_models import QuerySpec
from app.prompts.prompts import PARSER_PROMPT

def parsing_query(query:str, llm) -> QuerySpec:
    # Bind the schema to the model
    # model_loader = ModelLoader(model_provider = "gemini")
    # llm = model_loader.load_llm()

    structured_llm = llm.with_structured_output(QuerySpec)

    # Compose the full prompt with instructions and user question
    full_prompt = PARSER_PROMPT + "\n" + query

    # Invoke the model to get structured output parsed as QuerySpec
    result: QuerySpec = structured_llm.invoke(full_prompt)
    return result
    # print(result.json())  # This will print the JSON output matching your schema
