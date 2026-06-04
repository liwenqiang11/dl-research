# Evidence Probe Toolkit

Use probes in the **Evidence** phase to test whether an algorithm behaves as the Design hypothesis predicts. Probes are not decoration: each probe should answer a specific uncertainty from Discovery or Design.

When `references/mechanistic-model-analyst.md` is active, every probe should map to a mechanistic question: information path, gradient path, shortcut behavior, bottleneck, objective/metric mismatch, or subgroup failure. A visually plausible probe is not enough; state what root cause it supports or rejects.

## Probe Selection

| Question | Probe | Evidence |
|----------|-------|----------|
| Are features spatially or semantically meaningful? | Feature map visualization | Activated regions or channels match the intended signal |
| Is attention/routing using the expected context? | Attention/routing map | Weights concentrate on plausible tokens, views, or regions |
| Does the model rely on the intended input evidence? | CAM, saliency, or perturbation | Important regions/features align with the hypothesis |
| Do gradients reach the intended module? | Gradient flow check | Non-zero, finite gradient norms in trainable paths |
| Is training drifting or collapsing? | Weight/output histograms | Distributions remain finite and non-degenerate |
| Where does the method fail? | Error slicing | Failures cluster by interpretable subgroup or condition |
| Is a proposed mechanism causally used? | Probe plus one-factor ablation | Probe changes consistently when the mechanism is removed |
| Is the model learning a shortcut? | Perturbation or counterfactual slice | Output changes follow shortcut cues rather than intended evidence |

## Common Setup

```python
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
```

Use `model.eval()` for interpretability probes unless the goal is to inspect training-time behavior. Always detach tensors before plotting, and save probes under the experiment artifact directory.

## 1. Feature Map Visualization

```python
def save_feature_maps(feature_map, layer_name, step, save_dir, num_channels=8):
    """Save a compact feature visualization for a 2D or 4D activation tensor."""
    save_dir = Path(save_dir) / "feature_maps" / layer_name
    save_dir.mkdir(parents=True, exist_ok=True)

    fmap = feature_map.detach().float().cpu()
    if fmap.dim() == 2:
        values = fmap[0, :num_channels].numpy()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(np.arange(len(values)), values)
        ax.set_title(f"{layer_name} features - step {step}")
        fig.tight_layout()
        fig.savefig(save_dir / f"step_{step:06d}.png", dpi=120)
        plt.close(fig)
        return

    if fmap.dim() != 4:
        raise ValueError(f"Expected feature_map dim 2 or 4, got {fmap.dim()}")

    channels = min(num_channels, fmap.size(1))
    fig, axes = plt.subplots(1, channels, figsize=(3 * channels, 3))
    axes = np.atleast_1d(axes)
    for idx in range(channels):
        axes[idx].imshow(fmap[0, idx].numpy(), cmap="viridis")
        axes[idx].axis("off")
    fig.suptitle(f"{layer_name} - step {step}")
    fig.tight_layout()
    fig.savefig(save_dir / f"step_{step:06d}.png", dpi=120)
    plt.close(fig)
```

## 2. Attention or Routing Map

```python
def save_attention_map(attn_weights, layer_name, step, save_dir):
    """Save attention heatmap. Supports (B, H, Q, K) or (B, Q, K)."""
    save_dir = Path(save_dir) / "attention_maps" / layer_name
    save_dir.mkdir(parents=True, exist_ok=True)

    attn = attn_weights.detach().float().cpu()
    if attn.dim() == 4:
        attn = attn[0].mean(dim=0)
    elif attn.dim() == 3:
        attn = attn[0]
    else:
        raise ValueError(f"Expected attention dim 3 or 4, got {attn.dim()}")

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(attn.numpy(), cmap="hot", interpolation="nearest")
    ax.set_title(f"{layer_name} attention - step {step}")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(save_dir / f"step_{step:06d}.png", dpi=120)
    plt.close(fig)
```

## 3. Grad-CAM for Classification-Like Outputs

```python
class GradCAMHook:
    def __init__(self):
        self.activations = None
        self.gradients = None

    def forward_hook(self, module, inputs, output):
        self.activations = output

    def backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]


def generate_gradcam(model, target_layer, input_tensor, target_index=None):
    """Generate a normalized Grad-CAM heatmap for classification-style outputs."""
    hook = GradCAMHook()
    handle_fwd = target_layer.register_forward_hook(hook.forward_hook)
    handle_bwd = target_layer.register_full_backward_hook(hook.backward_hook)

    try:
        model.zero_grad(set_to_none=True)
        output = model(input_tensor)
        if target_index is None:
            target_index = output.argmax(dim=1)

        score = output[torch.arange(output.size(0), device=output.device), target_index].sum()
        score.backward()

        activations = hook.activations.detach()
        gradients = hook.gradients.detach()
        weights = gradients.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * activations).sum(dim=1, keepdim=True))
        cam = F.interpolate(cam, size=input_tensor.shape[2:], mode="bilinear", align_corners=False)
        cam = cam / (cam.amax(dim=(2, 3), keepdim=True) + 1e-8)
        return cam.squeeze(1).detach().cpu().numpy()
    finally:
        handle_fwd.remove()
        handle_bwd.remove()
```

For regression, dense prediction, or sequence tasks, replace `score` with the scalar target that corresponds to the hypothesis, such as a selected coordinate, token logit, loss component, or region score.

## 4. Gradient Flow Check

```python
def check_gradient_flow(model, logger=None):
    """Return per-parameter gradient norms and alert on common gradient failures."""
    grad_norms = {}
    alerts = []

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if param.grad is None:
            alerts.append(f"WARNING: missing gradient for {name}")
            continue

        norm = param.grad.detach().data.norm(2).item()
        grad_norms[name] = norm
        if logger:
            logger.info("%s grad_norm=%.6e", name, norm)
        if not np.isfinite(norm):
            alerts.append(f"WARNING: non-finite gradient for {name}")
        elif norm == 0.0:
            alerts.append(f"WARNING: zero gradient for {name}")

    total_norm = float(sum(norm * norm for norm in grad_norms.values()) ** 0.5)
    if total_norm < 1e-7:
        alerts.append("WARNING: possible vanishing gradients (total norm < 1e-7)")
    if total_norm > 1e3:
        alerts.append("WARNING: possible exploding gradients (total norm > 1e3)")

    if logger:
        logger.info("total_grad_norm=%.6e", total_norm)
        for alert in alerts:
            logger.warning(alert)

    return grad_norms, total_norm, alerts
```

## 5. Weight and Output Distribution

```python
def save_histogram(values, name, step, save_dir, bins=50):
    """Save a histogram for weights, logits, predictions, or errors."""
    save_dir = Path(save_dir) / "histograms"
    save_dir.mkdir(parents=True, exist_ok=True)

    array = values.detach().float().cpu().numpy().reshape(-1)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(array, bins=bins)
    ax.set_title(f"{name} - step {step}")
    fig.tight_layout()
    fig.savefig(save_dir / f"{name}_step_{step:06d}.png", dpi=120)
    plt.close(fig)
```

## 6. Error Slicing

```python
def summarize_error_slices(records, group_key, error_key):
    """Summarize errors by subgroup. records is a list of dictionaries."""
    groups = {}
    for record in records:
        groups.setdefault(record[group_key], []).append(float(record[error_key]))

    summary = {}
    for group, errors in groups.items():
        arr = np.asarray(errors, dtype=np.float64)
        summary[group] = {
            "count": int(arr.size),
            "mean": float(arr.mean()),
            "median": float(np.median(arr)),
            "p90": float(np.percentile(arr, 90)),
        }
    return summary
```

## Integration Pattern

```python
probe_every = 5

for epoch in range(num_epochs):
    train_metrics = train_one_epoch(...)
    val_metrics = validate(...)

    if epoch % probe_every == 0 or epoch == num_epochs - 1:
        if "features" in train_metrics:
            save_feature_maps(train_metrics["features"], "selected_layer", epoch, probe_dir)
        if hasattr(model, "get_attention_weights"):
            save_attention_map(model.get_attention_weights(), "attention", epoch, probe_dir)
        grad_norms, total_norm, alerts = check_gradient_flow(model, logger)
        for name, param in model.named_parameters():
            if param.requires_grad and param.ndim > 1:
                save_histogram(param, name.replace(".", "_"), epoch, probe_dir)
```

## Evidence Interpretation Rules

- Link every probe to a hypothesis or failure mode.
- Compare probes between baseline, full model, and at least one ablation when possible.
- Treat pretty visualizations as weak evidence unless they align with quantitative results.
- Mark uncertainty when probes are missing, noisy, or task-inappropriate.
