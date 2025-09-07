from langchain_pymupdf4llm import PyMuPDF4LLMLoader

def parser_node(state):
    loader = PyMuPDF4LLMLoader(file_path=state["resume_path"])
    docs = [doc for doc in loader.lazy_load()]
    # docs is a list of LangChain Document objects; extract their content:
    content = "\n\n".join([doc.page_content for doc in docs])
    state["raw_resume_text"] = content
    return state
