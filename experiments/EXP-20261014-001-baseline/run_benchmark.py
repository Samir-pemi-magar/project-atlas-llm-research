#!/usr/bin/env python3
"""Reproducible llama.cpp chat-completion baseline harness.

This script is intentionally standard-library-only. It records raw responses and
telemetry before deriving summary statistics. It does not score answer quality.
Do not run the full workload until the protocol and configuration are approved.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MODEL_REVISION = "daeb8e2d528a760970442092f6bf1e55c3b659eb"
MODEL_SHA256 = "d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5"
IMAGE_ID = "sha256:b0baccbe2e00b5d74e63f85f9f023c93d61d0f329475269e1e7002e87eb875ea"
SERVER_VERSION_EXPECTED = "0.6.0-dev (build 11610, commit 091b6a7fc)"

CONFIG = {
    "endpoint": "/v1/chat/completions",
    "model": "atlas-qwen3-verbose-test",
    "max_tokens": 96,
    "temperature": 0.0,
    "top_k": 1,
    "top_p": 1.0,
    "min_p": 0.0,
    "seed": 42,
    "stream": False,
    "cache_prompt": False,
    "chat_template_kwargs": {"enable_thinking": False},
    "context_length": 4096,
    "request_timeout_seconds": 120,
    "telemetry_interval_seconds": 0.5,
}

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def percentile(values: list[float], p: float) -> float | None:
    """Linear-interpolated percentile (p in [0, 100])."""
    if not values:
        return None
    xs = sorted(float(v) for v in values)
    if len(xs) == 1:
        return xs[0]
    position = (len(xs) - 1) * p / 100.0
    lo = int(position)
    hi = min(lo + 1, len(xs) - 1)
    fraction = position - lo
    return xs[lo] + (xs[hi] - xs[lo]) * fraction

def describe(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "median": None, "q1": None, "q3": None, "iqr": None}
    q1 = percentile(values, 25)
    q3 = percentile(values, 75)
    med = statistics.median(values)
    return {"n": len(values), "median": med, "q1": q1, "q3": q3, "iqr": q3 - q1}

def request_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 10) -> tuple[int, dict[str, Any], float]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method="GET" if data is None else "POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            return response.status, json.loads(body.decode("utf-8")), elapsed_ms
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"error_body": body}
        return exc.code, parsed, elapsed_ms

def meminfo_snapshot() -> dict[str, int] | None:
    path = Path("/proc/meminfo")
    if not path.exists():
        return None
    values: dict[str, int] = {}
    try:
        for line in path.read_text().splitlines():
            key, value = line.split(":", 1)
            fields = value.strip().split()
            if fields and fields[0].isdigit():
                values[key] = int(fields[0])  # kB
        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        if total is None or available is None:
            return None
        return {
            "total_ram_mib": total // 1024,
            "available_ram_mib": available // 1024,
            "used_ram_mib_estimate": (total - available) // 1024,
        }
    except (OSError, ValueError):
        return None

def gpu_snapshot() -> dict[str, float | int] | None:
    if shutil.which("nvidia-smi") is None:
        return None
    command = [
        "nvidia-smi",
        "--query-gpu=memory.used,utilization.gpu,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=2, check=True)
        first = result.stdout.strip().splitlines()[0]
        fields = [field.strip() for field in first.split(",")]
        if len(fields) != 4:
            return None
        def numeric(field: str) -> float | None:
            try:
                return float(field)
            except ValueError:
                return None
        memory, util, temperature, power = (numeric(field) for field in fields)
        return {
            "gpu_memory_used_mib": int(memory) if memory is not None else -1,
            "gpu_utilization_percent": util if util is not None else -1,
            "gpu_temperature_c": temperature if temperature is not None else -1,
            "gpu_power_w": power if power is not None else -1,
        }
    except (OSError, subprocess.SubprocessError, IndexError):
        return None

class TelemetryMonitor:
    def __init__(self, output_path: Path, interval: float) -> None:
        self.output_path = output_path
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    def _run(self) -> None:
        with self.output_path.open("a", encoding="utf-8") as stream:
            while not self.stop_event.is_set():
                row: dict[str, Any] = {"timestamp_utc": utc_now()}
                gpu = gpu_snapshot()
                ram = meminfo_snapshot()
                row["gpu"] = gpu
                row["ram"] = ram
                stream.write(json.dumps(row, sort_keys=True) + "\n")
                stream.flush()
                self.stop_event.wait(self.interval)

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run, name="atlas-telemetry", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=5)

def extract_timings(response: dict[str, Any]) -> dict[str, Any]:
    timings = response.get("timings")
    if not isinstance(timings, dict):
        verbose = response.get("__verbose", {})
        timings = verbose.get("timings", {}) if isinstance(verbose, dict) else {}
    verbose = response.get("__verbose", {})
    generation = verbose.get("generation_settings", {}) if isinstance(verbose, dict) else {}
    return {"timings": timings if isinstance(timings, dict) else {}, "generation_settings": generation}

def make_payload(prompt_text: str) -> dict[str, Any]:
    return {
        "model": CONFIG["model"],
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": CONFIG["max_tokens"],
        "temperature": CONFIG["temperature"],
        "top_k": CONFIG["top_k"],
        "top_p": CONFIG["top_p"],
        "min_p": CONFIG["min_p"],
        "seed": CONFIG["seed"],
        "cache_prompt": CONFIG["cache_prompt"],
        "chat_template_kwargs": CONFIG["chat_template_kwargs"],
        "stream": CONFIG["stream"],
    }

def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:3002", help="Base URL for the isolated ATLAS server")
    parser.add_argument("--prompts", type=Path, default=Path(__file__).with_name("prompts_v1.json"))
    parser.add_argument("--out-dir", type=Path, default=None, help="New output directory; defaults to a UTC timestamp under results/raw")
    parser.add_argument("--plan-only", action="store_true", help="Validate workload/configuration and print the plan without contacting the server")
    args = parser.parse_args()

    prompt_data = json.loads(args.prompts.read_text(encoding="utf-8"))
    prompts = prompt_data["prompts"]
    if len(prompts) != 20 or len({p["id"] for p in prompts}) != 20:
        raise SystemExit("Expected exactly 20 uniquely identified prompts.")
    if args.plan_only:
        print(json.dumps({
            "dataset_id": prompt_data["dataset_id"],
            "prompt_count": len(prompts),
            "warmup_requests": 3,
            "measured_requests": len(prompts) * 3,
            "total_requests": 3 + len(prompts) * 3,
            "config": CONFIG,
            "base_url": args.base_url,
            "output_policy": "new raw-results directory; no existing data overwritten",
        }, indent=2))
        return 0

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir or (Path(__file__).resolve().parent / "results" / "raw" / f"baseline-{timestamp}")
    out_dir.mkdir(parents=True, exist_ok=False)
    raw_path = out_dir / "requests.jsonl"
    telemetry_path = out_dir / "telemetry.jsonl"
    summary_path = out_dir / "summary.json"
    metadata_path = out_dir / "metadata.json"

    metadata = {
        "experiment_id": "EXP-20261014-001",
        "run_id": out_dir.name,
        "started_utc": utc_now(),
        "base_url": args.base_url.rstrip("/"),
        "endpoint": CONFIG["endpoint"],
        "model_revision": MODEL_REVISION,
        "model_sha256": MODEL_SHA256,
        "llama_cpp_image_id": IMAGE_ID,
        "expected_server_version": SERVER_VERSION_EXPECTED,
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "prompt_dataset": prompt_data["dataset_id"],
        "prompt_dataset_version": prompt_data["version"],
        "config": CONFIG,
        "protocol": {
            "warmups": 3,
            "measured_repetitions_per_prompt": 3,
            "measured_requests": 60,
            "ordering": "three deterministic round-robin passes, rotated by 7 prompt positions each pass",
            "cache_policy": "request cache_prompt=false; run aborts before measured requests if cache_n is nonzero or unavailable",
            "quality": "raw outputs retained; no automatic quality score",
        },
    }
    write_json(metadata_path, metadata)

    health_status, health_body, health_ms = request_json(args.base_url.rstrip("/") + "/health", timeout=10)
    if health_status != 200 or health_body.get("status") != "ok":
        write_json(summary_path, {"status": "aborted", "reason": "health_check_failed", "health_status": health_status, "health_body": health_body})
        return 2

    monitor = TelemetryMonitor(telemetry_path, float(CONFIG["telemetry_interval_seconds"]))
    monitor.start()
    records: list[dict[str, Any]] = []
    errors = 0
    try:
        # Three global warmups; use different workload types.
        by_id = {p["id"]: p for p in prompts}
        warmup_ids = ["P01", "P10", "P20"]
        for index, prompt_id in enumerate(warmup_ids, start=1):
            prompt = by_id[prompt_id]
            run_one(args.base_url, prompt, "warmup", index, raw_path, records)
        # Do not start formal measurements unless cache behavior and sampling are verified.
        for row in records:
            validate_runtime_config(row)
        for row in records:
            cache_n = row.get("timings", {}).get("cache_n")
            if cache_n != 0:
                raise RuntimeError(f"Prompt-cache behavior is not verified disabled (warmup cache_n={cache_n!r}); refusing to begin measured requests.")
        for pass_index in range(3):
            ordered = prompts[pass_index * 7 % len(prompts):] + prompts[:pass_index * 7 % len(prompts)]
            for prompt in ordered:
                run_one(args.base_url, prompt, "measured", pass_index + 1, raw_path, records)
    except Exception as exc:
        errors += 1
        with raw_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"timestamp_utc": utc_now(), "type": "harness_abort", "error": repr(exc)}) + "\n")
    finally:
        monitor.stop()

    measured = [r for r in records if r.get("phase") == "measured" and not r.get("error")]
    all_request_errors = [r for r in records if r.get("error")]
    telemetry = []
    if telemetry_path.exists():
        for line in telemetry_path.read_text(encoding="utf-8").splitlines():
            try:
                telemetry.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    gpu_samples = [row["gpu"] for row in telemetry if isinstance(row.get("gpu"), dict)]
    ram_samples = [row["ram"] for row in telemetry if isinstance(row.get("ram"), dict)]
    metrics: dict[str, list[float]] = {
        "client_wall_ms": [r["client_wall_ms"] for r in measured],
        "prompt_tokens_per_second": [r["timings"]["prompt_per_second"] for r in measured if is_number(r.get("timings", {}).get("prompt_per_second"))],
        "decode_tokens_per_second": [r["timings"]["predicted_per_second"] for r in measured if is_number(r.get("timings", {}).get("predicted_per_second"))],
        "prompt_tokens": [float(r["prompt_tokens"]) for r in measured if is_number(r.get("prompt_tokens"))],
        "output_tokens": [float(r["output_tokens"]) for r in measured if is_number(r.get("output_tokens"))],
    }
    summary = {
        "status": "complete" if len(measured) == 60 and not all_request_errors and errors == 0 else "incomplete",
        "finished_utc": utc_now(),
        "expected_measured_requests": 60,
        "successful_measured_requests": len(measured),
        "warmup_requests_recorded": sum(r.get("phase") == "warmup" for r in records),
        "request_errors": len(all_request_errors),
        "harness_errors": errors,
        "metrics": {name: describe(values) for name, values in metrics.items()},
        "telemetry": {
            "sample_count": len(telemetry),
            "peak_gpu_memory_used_mib": max((g.get("gpu_memory_used_mib", -1) for g in gpu_samples), default=None),
            "max_gpu_utilization_percent": max((g.get("gpu_utilization_percent", -1) for g in gpu_samples), default=None),
            "max_gpu_temperature_c": max((g.get("gpu_temperature_c", -1) for g in gpu_samples), default=None),
            "max_gpu_power_w": max((g.get("gpu_power_w", -1) for g in gpu_samples), default=None),
            "peak_estimated_ram_used_mib": max((r.get("used_ram_mib_estimate", -1) for r in ram_samples), default=None),
            "minimum_available_ram_mib": min((r.get("available_ram_mib", -1) for r in ram_samples), default=None),
            "limitation": "0.5-second polling may miss short peaks; WSL /proc/meminfo measures the WSL VM, not Windows process-level RAM",
        },
        "quality_assessment": "Not automatically scored. Review raw outputs separately; repeated deterministic output is not proof of correctness.",
        "raw_requests_file": raw_path.name,
        "telemetry_file": telemetry_path.name,
    }
    write_json(summary_path, summary)
    write_csv(out_dir / "measured_requests.csv", measured)
    print(json.dumps({"output_directory": str(out_dir), "summary": summary}, indent=2))
    return 0 if summary["status"] == "complete" else 3

def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def validate_runtime_config(row: dict[str, Any]) -> None:
    if row.get("error"):
        raise RuntimeError(f"Warmup request failed: {row['error']}")
    settings = row.get("generation_settings", {})
    expected = {"temperature": 0.0, "top_k": 1, "top_p": 1.0, "min_p": 0.0}
    missing = [key for key in expected if key not in settings]
    if missing:
        raise RuntimeError(f"Server did not expose effective generation settings: {missing}")
    for key, wanted in expected.items():
        got = settings[key]
        if abs(float(got) - float(wanted)) > 1e-6:
            raise RuntimeError(f"Effective setting mismatch for {key}: expected {wanted}, got {got}")
    if row.get("finish_reason") == "length" or not row.get("output_text", "").strip():
        raise RuntimeError("Warmup output was empty or truncated; refusing to start formal measurements.")

def run_one(base_url: str, prompt: dict[str, Any], phase: str, repetition: int, raw_path: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    payload = make_payload(prompt["text"])
    status, response, elapsed_ms = request_json(base_url.rstrip("/") + CONFIG["endpoint"], payload, int(CONFIG["request_timeout_seconds"]))
    extracted = extract_timings(response)
    choices = response.get("choices", [])
    choice = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = choice.get("message", {}) if isinstance(choice.get("message", {}), dict) else {}
    output_text = message.get("content", "")
    if not isinstance(output_text, str):
        output_text = str(output_text)
    usage = response.get("usage", {}) if isinstance(response.get("usage", {}), dict) else {}
    timings = extracted["timings"]
    record: dict[str, Any] = {
        "timestamp_utc": utc_now(),
        "phase": phase,
        "repetition": repetition,
        "prompt_id": prompt["id"],
        "category": prompt["category"],
        "prompt_text": prompt["text"],
        "http_status": status,
        "client_wall_ms": elapsed_ms,
        "prompt_tokens": usage.get("prompt_tokens", timings.get("prompt_n")),
        "output_tokens": usage.get("completion_tokens", timings.get("predicted_n")),
        "finish_reason": choice.get("finish_reason"),
        "output_text": output_text,
        "timings": timings,
        "generation_settings": extracted["generation_settings"],
        "cache_prompt_requested": CONFIG["cache_prompt"],
        "response_id": response.get("id"),
    }
    if status != 200:
        record["error"] = f"HTTP {status}: {response}"
    if not output_text.strip():
        record["error"] = record.get("error", "empty assistant content")
    records.append(record)
    with raw_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record

def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["phase", "repetition", "prompt_id", "category", "http_status", "client_wall_ms",
              "prompt_tokens", "output_tokens", "finish_reason", "prompt_per_second",
              "predicted_per_second", "prompt_ms", "predicted_ms", "cache_n", "output_text"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            timings = row.get("timings", {})
            flat = dict(row)
            flat.update({
                "prompt_per_second": timings.get("prompt_per_second"),
                "predicted_per_second": timings.get("predicted_per_second"),
                "prompt_ms": timings.get("prompt_ms"),
                "predicted_ms": timings.get("predicted_ms"),
                "cache_n": timings.get("cache_n"),
            })
            writer.writerow(flat)

if __name__ == "__main__":
    raise SystemExit(main())
