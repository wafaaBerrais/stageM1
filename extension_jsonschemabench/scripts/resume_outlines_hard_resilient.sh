#!/usr/bin/env bash
set -u

ROOT="/home/berrais/stage/jsonschemabench"
PY="$ROOT/.venv/bin/python"
DATA_DIR="$ROOT/maskbench/data"
SCRIPT_DIR="$ROOT/extension_jsonschemabench/scripts"
DATASET="${OUTLINES_DATASET:-Github_hard}"
RUN_DIR="$ROOT/extension_jsonschemabench/results/per_dataset_runs/outlines/$DATASET"
START_AT="${1:-$DATASET---o13401.json}"
DRIVER_LOG="$RUN_DIR/resilient_bash_driver_20260706.log"
CHILD_LOG="$RUN_DIR/resilient_bash_child_20260706.log"
CHILD_VMEM_KB="${OUTLINES_CHILD_VMEM_KB:-12000000}"

mkdir -p "$RUN_DIR"
echo "selected start=$START_AT" >> "$DRIVER_LOG"

started=0
index=0
while IFS= read -r schema; do
  name="$(basename "$schema")"
  if [[ "$started" -eq 0 ]]; then
    if [[ "$name" != "$START_AT" ]]; then
      continue
    fi
    started=1
  fi
  index=$((index + 1))

  if ! "$PY" "$SCRIPT_DIR/outlines_hard_resilient_helper.py" status "$schema"; then
    echo "[$index] $name: skipped done/timeout/no-tests" >> "$DRIVER_LOG"
    continue
  fi

  echo "[$index] $name: running" >> "$DRIVER_LOG"
  start_seconds="$(date +%s)"
  setsid /bin/bash -lc "ulimit -v $CHILD_VMEM_KB; exec '$PY' '$SCRIPT_DIR/run_dataset_with_timeouts.py' \
    --framework outlines \
    --dataset '$DATASET' \
    --timeout-minutes 10 \
    --progress-interval-minutes 1 \
    --profile-timings \
    --profile-checkpoint-interval-seconds 10 \
    --trace-stages \
    --continue-on-error \
    '$schema'" >> "$CHILD_LOG" 2>&1 &
  child_pid="$!"
  wait "$child_pid"
  rc="$?"
  end_seconds="$(date +%s)"
  elapsed="$((end_seconds - start_seconds))"

  if "$PY" "$SCRIPT_DIR/outlines_hard_resilient_helper.py" status "$schema"; then
    "$PY" "$SCRIPT_DIR/outlines_hard_resilient_helper.py" mark "$schema" "$elapsed" "$rc"
    echo "[$index] $name: marked terminated rc=$rc elapsed=${elapsed}s" >> "$DRIVER_LOG"
  else
    echo "[$index] $name: completed-or-recorded rc=$rc elapsed=${elapsed}s" >> "$DRIVER_LOG"
  fi
done < <(find "$DATA_DIR" -maxdepth 1 -type f -name "$DATASET---*.json" | sort)

echo "done" >> "$DRIVER_LOG"
