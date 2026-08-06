from ddgs import DDGS

def web_search(query: str, max_results: int = 3):
    """Search the web. Returns (formatted_text, success: bool)."""
    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:
        return f"Web search failed: {e}", False

    if not results:
        return "No results found.", False

    formatted = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        formatted.append(f"- {title}: {body} (source: {href})")

    return "\n".join(formatted), True