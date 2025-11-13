from typing import List, List as ListType

class Embeddings:
    """Text embeddings placeholder (Torch/ONNX/BentoML-friendly)."""

    def encode(self, texts: List[str]) -> ListType[ListType[float]]:
        return [[0.0] * 16 for _ in texts]