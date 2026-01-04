from __future__ import annotations

import contextlib
import inspect
import io
import random
from typing import Any, Callable, Optional

from . import generator as _g


def _maybe_int(x: Any, default: int) -> int:
    try:
        return int(x)
    except Exception:
        return default


def _call_capture(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    if isinstance(out, str) and out.strip():
        return out.strip()
    printed = buf.getvalue().strip()
    return printed


def _call_compatible(fn: Callable[..., Any], *, seed: Optional[int], paragraphs: Optional[int]) -> Optional[str]:
    sig = None
    try:
        sig = inspect.signature(fn)
    except Exception:
        sig = None

    rng = random.Random(seed)
    n = paragraphs if paragraphs is not None else 2

    # If we can't introspect, try the simplest call and capture stdout.
    if sig is None:
        try:
            return _call_capture(fn)
        except Exception:
            return None

    params = sig.parameters
    kwargs: dict[str, Any] = {}

    # common parameter names
    if "seed" in params:
        kwargs["seed"] = seed
    if "paragraphs" in params:
        kwargs["paragraphs"] = n
    if "n_paragraphs" in params:
        kwargs["n_paragraphs"] = n
    if "count" in params:
        kwargs["count"] = n
    if "n" in params:
        kwargs["n"] = n
    if "num" in params:
        kwargs["num"] = n
    if "num_paragraphs" in params:
        kwargs["num_paragraphs"] = n

    # rng/random objects
    if "rng" in params:
        kwargs["rng"] = rng
    if "random" in params:
        kwargs["random"] = rng

    # argv-style entrypoints
    if "argv" in params and len(params) == 1:
        argv = []
        if seed is not None:
            argv += ["--seed", str(seed)]
        if paragraphs is not None:
            argv += ["--paragraphs", str(n)]
        try:
            return _call_capture(fn, argv)
        except Exception:
            return None

    # Try calling with kwargs we know about
    try:
        return _call_capture(fn, **kwargs)
    except Exception:
        # fall back to no-arg call
        try:
            return _call_capture(fn)
        except Exception:
            return None


def _instantiate(cls: type, *, seed: Optional[int], paragraphs: Optional[int]) -> Optional[Any]:
    try:
        sig = inspect.signature(cls)
    except Exception:
        sig = None

    rng = random.Random(seed)
    n = paragraphs if paragraphs is not None else 2

    if sig is None:
        try:
            return cls()
        except Exception:
            return None

    params = sig.parameters
    kwargs: dict[str, Any] = {}

    if "seed" in params:
        kwargs["seed"] = seed
    if "rng" in params:
        kwargs["rng"] = rng
    if "random" in params:
        kwargs["random"] = rng
    if "paragraphs" in params:
        kwargs["paragraphs"] = n

    try:
        return cls(**kwargs)
    except Exception:
        try:
            return cls()
        except Exception:
            return None


def generate(*, seed: Optional[int] = None, paragraphs: Optional[int] = None) -> str:
    # 0) If generator already has a callable that looks right, try it.
    for fn_name in ("generate", "generate_text", "generate_paragraphs", "render", "make", "build"):
        fn = getattr(_g, fn_name, None)
        if callable(fn):
            s = _call_compatible(fn, seed=seed, paragraphs=paragraphs)
            if s:
                return s

    # 1) Try main()-style function (prints to stdout commonly)
    main_fn = getattr(_g, "main", None)
    if callable(main_fn):
        s = _call_compatible(main_fn, seed=seed, paragraphs=paragraphs)
        if s:
            return s

    # 2) Try classes with common method names
    method_candidates = ("generate", "render", "make", "build", "text", "paragraphs", "run")
    for _, obj in vars(_g).items():
        if inspect.isclass(obj):
            inst = _instantiate(obj, seed=seed, paragraphs=paragraphs)
            if inst is None:
                continue
            for m in method_candidates:
                meth = getattr(inst, m, None)
                if callable(meth):
                    s = _call_compatible(meth, seed=seed, paragraphs=paragraphs)
                    if s:
                        return s

    raise ImportError(
        "emptygpt.api.generate() couldn't find a usable generator entrypoint in emptygpt.generator. "
        "Add a top-level generate(seed=None, paragraphs=None) in generator.py or expose a callable/class."
    )
