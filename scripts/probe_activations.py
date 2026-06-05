#!/usr/bin/env python3
"""Probe model internals using PyTorch hooks.

Modes:
    gradient    — Check gradient flow: NaN/Inf/zero/mean/std per module
    activation  — Extract activation distributions per module
    dead-check  — Detect dead modules (zero activation or zero gradient)
    attention   — Extract attention weights from attention layers
    flow        — Track which modules are called during forward pass

Usage:
    # Gradient check after a forward+backward pass
    python probe_activations.py --mode gradient --model model.pt --input sample.pt

    # Activation distribution
    python probe_activations.py --mode activation --model model.pt --input sample.pt

    # Dead module detection
    python probe_activations.py --mode dead-check --model model.pt --input sample.pt

    # Attention extraction
    python probe_activations.py --mode attention --model model.pt --input sample.pt

    # Information flow tracking
    python probe_activations.py --mode flow --model model.pt --input sample.pt

    # Filter specific layers
    python probe_activations.py --mode gradient --model model.pt --input sample.pt \
        --layers encoder.conv1,decoder.fc

    # Use a custom forward function (for complex models)
    python probe_activations.py --mode gradient --model model.pt --input sample.pt \
        --forward-fn my_module.forward_fn

    # Output as JSON
    python probe_activations.py --mode gradient --model model.pt --input sample.pt --json
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import torch
    import torch.nn as nn
except ImportError:
    print("ERROR: PyTorch is required. Install with: pip install torch", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Hook registry
# ---------------------------------------------------------------------------

class HookRegistry:
    """Collects data from forward and backward hooks."""

    def __init__(self):
        self.activations = {}   # name -> tensor (output)
        self.inputs = {}        # name -> tensor (input)
        self.gradients = {}     # name -> tensor (grad_output)
        self.call_counts = {}   # name -> int
        self.handles = []

    def forward_hook(self, name):
        def hook(module, input, output):
            self.call_counts[name] = self.call_counts.get(name, 0) + 1
            if isinstance(output, torch.Tensor):
                self.activations[name] = output.detach()
            elif isinstance(output, (tuple, list)) and len(output) > 0 and isinstance(output[0], torch.Tensor):
                self.activations[name] = output[0].detach()
            if isinstance(input, (tuple, list)) and len(input) > 0 and isinstance(input[0], torch.Tensor):
                self.inputs[name] = input[0].detach()
        return hook

    def backward_hook(self, name):
        def hook(module, grad_input, grad_output):
            if isinstance(grad_output, (tuple, list)) and len(grad_output) > 0 and isinstance(grad_output[0], torch.Tensor):
                self.gradients[name] = grad_output[0].detach()
        return hook

    def register(self, name, module):
        self.handles.append(module.register_forward_hook(self.forward_hook(name)))
        self.handles.append(module.register_full_backward_hook(self.backward_hook(name)))

    def remove_all(self):
        for h in self.handles:
            h.remove()
        self.handles.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def tensor_stats(t):
    """Compute summary statistics for a tensor."""
    if t is None:
        return None
    t_flat = t.float().flatten()
    has_nan = torch.isnan(t_flat).any().item()
    has_inf = torch.isinf(t_flat).any().item()
    if has_nan or has_inf:
        return {
            "shape": list(t.shape),
            "has_nan": has_nan,
            "has_inf": has_inf,
            "nan_count": int(torch.isnan(t_flat).sum().item()),
            "inf_count": int(torch.isinf(t_flat).sum().item()),
        }
    return {
        "shape": list(t.shape),
        "mean": round(t_flat.mean().item(), 6),
        "std": round(t_flat.std().item(), 6),
        "min": round(t_flat.min().item(), 6),
        "max": round(t_flat.max().item(), 6),
        "abs_mean": round(t_flat.abs().mean().item(), 6),
        "zero_ratio": round((t_flat == 0).float().mean().item(), 4),
        "has_nan": False,
        "has_inf": False,
    }


def filter_layers(all_names, filter_str):
    """Filter layer names by comma-separated pattern."""
    if not filter_str:
        return all_names
    patterns = [p.strip() for p in filter_str.split(",")]
    matched = []
    for name in all_names:
        for pat in patterns:
            if pat in name:
                matched.append(name)
                break
    return matched


def load_model(model_path, device):
    """Load a model from .pt/.pth file."""
    path = Path(model_path)
    if not path.exists():
        print(f"ERROR: Model file not found: {model_path}", file=sys.stderr)
        sys.exit(1)
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    if isinstance(checkpoint, nn.Module):
        return checkpoint
    if isinstance(checkpoint, dict):
        if "model" in checkpoint and isinstance(checkpoint["model"], nn.Module):
            return checkpoint["model"]
        if "state_dict" in checkpoint:
            print("ERROR: Found state_dict but no model architecture. "
                  "Load the model class first, then load_state_dict.", file=sys.stderr)
            sys.exit(1)
    print(f"ERROR: Cannot auto-load model from {model_path}. "
          "Pass an nnModule instance or a checkpoint with 'model' key.", file=sys.stderr)
    sys.exit(1)


def load_input(input_path, device):
    """Load input tensor from .pt file."""
    path = Path(input_path)
    if not path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    data = torch.load(path, map_location=device, weights_only=False)
    if isinstance(data, torch.Tensor):
        return data
    if isinstance(data, (tuple, list)):
        return data
    if isinstance(data, dict):
        for key in ["input", "x", "data", "sample"]:
            if key in data:
                return data[key]
        print(f"ERROR: Dict input has no recognized key (input/x/data/sample). Keys: {list(data.keys())}", file=sys.stderr)
        sys.exit(1)
    print(f"ERROR: Unsupported input type: {type(data)}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Probe modes
# ---------------------------------------------------------------------------

def probe_gradient(model, input_data, layers_filter, device):
    """Check gradient flow through the model."""
    registry = HookRegistry()
    all_names = [n for n, _ in model.named_modules() if n]
    target_names = filter_layers(all_names, layers_filter)

    if not target_names:
        target_names = [n for n, _ in model.named_modules() if n]
        # Remove empty name (root module)
        target_names = [n for n in target_names if n]

    for name in target_names:
        module = dict(model.named_modules()).get(name)
        if module is not None:
            registry.register(name, module)

    # Forward + backward
    model.train()
    model.zero_grad()
    try:
        if isinstance(input_data, (tuple, list)):
            output = model(*input_data)
        else:
            output = model(input_data)
        if isinstance(output, torch.Tensor) and output.requires_grad:
            loss = output.sum()
            loss.backward()
        else:
            print("WARNING: Output does not require_grad. Gradients will not flow.", file=sys.stderr)
    except Exception as e:
        registry.remove_all()
        print(f"ERROR during forward/backward: {e}", file=sys.stderr)
        sys.exit(1)

    results = {}
    for name in target_names:
        grad = registry.gradients.get(name)
        stats = tensor_stats(grad)
        if stats is None:
            stats = {"status": "no_gradient", "reason": "grad_output not captured"}
        results[name] = stats

    registry.remove_all()
    return results


def probe_activation(model, input_data, layers_filter, device):
    """Extract activation distributions."""
    registry = HookRegistry()
    all_names = [n for n, _ in model.named_modules() if n]
    target_names = filter_layers(all_names, layers_filter)

    if not target_names:
        target_names = [n for n, _ in model.named_modules() if n]
        target_names = [n for n in target_names if n]

    for name in target_names:
        module = dict(model.named_modules()).get(name)
        if module is not None:
            registry.register(name, module)

    model.eval()
    with torch.no_grad():
        try:
            if isinstance(input_data, (tuple, list)):
                output = model(*input_data)
            else:
                output = model(input_data)
        except Exception as e:
            registry.remove_all()
            print(f"ERROR during forward: {e}", file=sys.stderr)
            sys.exit(1)

    results = {}
    for name in target_names:
        act = registry.activations.get(name)
        stats = tensor_stats(act)
        if stats is None:
            stats = {"status": "no_activation", "reason": "output not captured"}
        results[name] = stats

    registry.remove_all()
    return results


def probe_dead_check(model, input_data, layers_filter, device):
    """Detect dead modules (zero activation or zero gradient)."""
    # First check activations
    act_results = probe_activation(model, input_data, layers_filter, device)
    # Then check gradients
    grad_results = probe_gradient(model, input_data, layers_filter, device)

    results = {}
    all_names = set(act_results.keys()) | set(grad_results.keys())
    for name in all_names:
        act = act_results.get(name, {})
        grad = grad_results.get(name, {})

        act_dead = False
        grad_dead = False
        issues = []

        # Check activation
        if act.get("has_nan") or act.get("has_inf"):
            act_dead = True
            issues.append(f"activation has NaN={act.get('nan_count', 0)}, Inf={act.get('inf_count', 0)}")
        elif act.get("zero_ratio", 0) == 1.0:
            act_dead = True
            issues.append("activation is all zeros")
        elif act.get("std", 1) == 0 and act.get("mean", 0) == 0:
            act_dead = True
            issues.append("activation has zero mean and zero std")

        # Check gradient
        if grad.get("has_nan") or grad.get("has_inf"):
            grad_dead = True
            issues.append(f"gradient has NaN={grad.get('nan_count', 0)}, Inf={grad.get('inf_count', 0)}")
        elif grad.get("zero_ratio", 0) == 1.0:
            grad_dead = True
            issues.append("gradient is all zeros")
        elif grad.get("status") == "no_gradient":
            grad_dead = True
            issues.append("gradient not captured (no backward pass or detached)")

        status = "alive"
        if act_dead and grad_dead:
            status = "dead"
        elif act_dead or grad_dead:
            status = "warning"

        results[name] = {
            "status": status,
            "activation": act,
            "gradient": grad,
            "issues": issues,
        }

    return results


def probe_attention(model, input_data, layers_filter, device):
    """Extract attention weights from attention layers."""
    registry = HookRegistry()
    all_names = [n for n, _ in model.named_modules() if n]

    # Auto-detect attention layers if no filter
    if not layers_filter:
        attention_keywords = ["attn", "attention", "self_attn", "cross_attn", "mha"]
        target_names = [n for n in all_names if any(k in n.lower() for k in attention_keywords)]
        if not target_names:
            # Try to find MultiheadAttention modules
            target_names = [n for n, m in model.named_modules() if isinstance(m, nn.MultiheadAttention)]
        if not target_names:
            print("WARNING: No attention layers found. Use --layers to specify manually.", file=sys.stderr)
            print(f"Available layers: {all_names[:20]}...", file=sys.stderr)
            return {}
    else:
        target_names = filter_layers(all_names, layers_filter)

    for name in target_names:
        module = dict(model.named_modules()).get(name)
        if module is not None:
            registry.register(name, module)

    model.eval()
    with torch.no_grad():
        try:
            if isinstance(input_data, (tuple, list)):
                output = model(*input_data)
            else:
                output = model(input_data)
        except Exception as e:
            registry.remove_all()
            print(f"ERROR during forward: {e}", file=sys.stderr)
            sys.exit(1)

    results = {}
    for name in target_names:
        act = registry.activations.get(name)
        if act is None:
            results[name] = {"status": "not_captured"}
            continue
        stats = tensor_stats(act)
        # For attention, also check if it looks like attention weights
        if act.dim() >= 2:
            # Check if rows sum to ~1 (softmax attention)
            row_sums = act.float().sum(dim=-1)
            is_softmax = (row_sums - 1.0).abs().max().item() < 0.1
            stats["looks_like_attention"] = is_softmax
            stats["row_sum_mean"] = round(row_sums.mean().item(), 4)
        results[name] = stats

    registry.remove_all()
    return results


def probe_flow(model, input_data, layers_filter, device):
    """Track which modules are called during forward pass."""
    registry = HookRegistry()
    all_names = [n for n, _ in model.named_modules() if n]
    target_names = filter_layers(all_names, layers_filter)

    if not target_names:
        target_names = [n for n, _ in model.named_modules() if n]
        target_names = [n for n in target_names if n]

    for name in target_names:
        module = dict(model.named_modules()).get(name)
        if module is not None:
            registry.register(name, module)

    model.eval()
    with torch.no_grad():
        try:
            if isinstance(input_data, (tuple, list)):
                output = model(*input_data)
            else:
                output = model(input_data)
        except Exception as e:
            registry.remove_all()
            print(f"ERROR during forward: {e}", file=sys.stderr)
            sys.exit(1)

    results = {}
    for name in target_names:
        count = registry.call_counts.get(name, 0)
        act = registry.activations.get(name)
        stats = {
            "called": count > 0,
            "call_count": count,
        }
        if act is not None:
            stats["output_shape"] = list(act.shape)
        results[name] = stats

    registry.remove_all()
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(mode, results, as_json=False):
    """Print the probe report."""
    if as_json:
        print(json.dumps({"mode": mode, "results": results}, indent=2, ensure_ascii=False))
        return

    print(f"\n{'='*60}")
    print(f"  Probe Report: {mode}")
    print(f"{'='*60}\n")

    if not results:
        print("  No results. Check --layers filter or model structure.\n")
        return

    if mode == "gradient":
        print(f"  {'Layer':<40} {'Status':<10} {'Mean':<12} {'Std':<12} {'Zero%':<8}")
        print(f"  {'-'*40} {'-'*10} {'-'*12} {'-'*12} {'-'*8}")
        for name, stats in results.items():
            if stats.get("has_nan") or stats.get("has_inf"):
                status = "NAN/INF"
                print(f"  {name:<40} {status:<10} NaN={stats.get('nan_count',0)} Inf={stats.get('inf_count',0)}")
            elif stats.get("status") == "no_gradient":
                print(f"  {name:<40} {'NO_GRAD':<10} (not captured)")
            else:
                status = "OK" if stats.get("mean", 0) != 0 or stats.get("std", 0) != 0 else "ZERO"
                print(f"  {name:<40} {status:<10} {stats.get('mean','?'):<12} {stats.get('std','?'):<12} {stats.get('zero_ratio','?'):<8}")

    elif mode == "activation":
        print(f"  {'Layer':<40} {'Shape':<20} {'Mean':<12} {'Std':<12} {'Zero%':<8}")
        print(f"  {'-'*40} {'-'*20} {'-'*12} {'-'*12} {'-'*8}")
        for name, stats in results.items():
            if stats.get("has_nan") or stats.get("has_inf"):
                print(f"  {name:<40} {'NAN/INF':<20} NaN={stats.get('nan_count',0)} Inf={stats.get('inf_count',0)}")
            elif stats.get("status") == "no_activation":
                print(f"  {name:<40} {'NOT_CAPTURED':<20}")
            else:
                shape_str = str(stats.get("shape", "?"))
                print(f"  {name:<40} {shape_str:<20} {stats.get('mean','?'):<12} {stats.get('std','?'):<12} {stats.get('zero_ratio','?'):<8}")

    elif mode == "dead-check":
        dead_count = 0
        warning_count = 0
        alive_count = 0
        for name, stats in results.items():
            status = stats.get("status", "unknown")
            if status == "dead":
                dead_count += 1
                symbol = "✗ DEAD"
            elif status == "warning":
                warning_count += 1
                symbol = "⚠ WARN"
            else:
                alive_count += 1
                symbol = "✓ OK"
            print(f"  {symbol}  {name}")
            for issue in stats.get("issues", []):
                print(f"         └─ {issue}")
        print(f"\n  Summary: {alive_count} alive, {warning_count} warnings, {dead_count} dead")

    elif mode == "attention":
        for name, stats in results.items():
            print(f"  Layer: {name}")
            if stats.get("status") == "not_captured":
                print(f"    Status: not captured")
                continue
            if stats.get("has_nan") or stats.get("has_inf"):
                print(f"    Status: NAN/INF detected")
            else:
                print(f"    Shape: {stats.get('shape', '?')}")
                print(f"    Mean: {stats.get('mean', '?')}, Std: {stats.get('std', '?')}")
                if "looks_like_attention" in stats:
                    print(f"    Looks like attention (row sums ≈ 1): {stats['looks_like_attention']}")
            print()

    elif mode == "flow":
        called = [n for n, s in results.items() if s.get("called")]
        not_called = [n for n, s in results.items() if not s.get("called")]
        print(f"  Called ({len(called)}):")
        for name in called:
            s = results[name]
            shape_str = str(s.get("output_shape", "?"))
            print(f"    ✓ {name}  (×{s['call_count']})  output: {shape_str}")
        if not_called:
            print(f"\n  NOT called ({len(not_called)}):")
            for name in not_called:
                print(f"    ✗ {name}")
        print(f"\n  Summary: {len(called)} called, {len(not_called)} not called")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Probe model internals using hooks")
    parser.add_argument("--mode", required=True,
                        choices=["gradient", "activation", "dead-check", "attention", "flow"],
                        help="Probe mode")
    parser.add_argument("--model", required=True, help="Path to model file (.pt/.pth)")
    parser.add_argument("--input", required=True, help="Path to input tensor file (.pt)")
    parser.add_argument("--layers", default=None,
                        help="Comma-separated layer name patterns to probe (default: all)")
    parser.add_argument("--device", default="cpu", help="Device: cpu / cuda / cuda:0")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() or "cpu" in args.device else "cpu")

    print(f"Loading model from {args.model} ...")
    model = load_model(args.model, device)
    model.to(device)

    print(f"Loading input from {args.input} ...")
    input_data = load_input(args.input, device)
    if isinstance(input_data, torch.Tensor):
        input_data = input_data.to(device)

    print(f"Probing mode: {args.mode}")
    print(f"Device: {device}")
    if args.layers:
        print(f"Layers filter: {args.layers}")
    print()

    mode_fn = {
        "gradient": probe_gradient,
        "activation": probe_activation,
        "dead-check": probe_dead_check,
        "attention": probe_attention,
        "flow": probe_flow,
    }

    results = mode_fn[args.mode](model, input_data, args.layers, device)
    print_report(args.mode, results, as_json=args.json)


if __name__ == "__main__":
    main()
