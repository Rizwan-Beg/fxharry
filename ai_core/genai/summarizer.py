from typing import List

class Summarizer:
    """Summarize news and research extracts for downstream models."""

    def summarize(self, texts: List[str]) -> List[str]:
        return [t[:256] for t in texts]