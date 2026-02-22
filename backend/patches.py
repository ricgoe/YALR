import sys; sys.argv.extend(["",""])
import numpy as np
np.float = float
np.int = int
import av_hubert.avhubert

import torch
_original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    """Default torch.load to weights_only=False for legacy checkpoints."""
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)

torch.load = patched_torch_load