#!/bin/zsh
set -euo pipefail

script_dir=${0:A:h}
project_dir=${script_dir:h}
install=false
build=false
test_project=false
assume_yes=false

usage() {
  printf '%s\n' \
    'Usage: ./scripts/setup_macos.sh [--check] [--install] [--build] [--test] [--yes]' \
    '' \
    '  --check    Inspect this Mac and project without changing anything (default).' \
    '  --install  Install project dependencies inside this checkout.' \
    '  --build    Run the project build commands that are available.' \
    '  --test     Run the project test commands that are available.' \
    '  --yes      Accept prompts; intended for an already-reviewed command.'
}

for arg in "$@"; do
  case "$arg" in
    --check) ;;
    --install) install=true ;;
    --build) build=true ;;
    --test) test_project=true ;;
    --yes) assume_yes=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
  esac
done

[[ $(uname -s) == Darwin ]] || { printf '%s\n' 'This setup helper supports macOS only.' >&2; exit 2; }

memory_bytes=$(sysctl -n hw.memsize)
memory_gib=$((memory_bytes / 1024 / 1024 / 1024))
free_kib=$(df -Pk "$project_dir" | awk 'NR == 2 {print $4}')
free_gib=$((free_kib / 1024 / 1024))
printf 'macOS %s, %s, %s GiB memory, %s GiB free disk\n' \
  "$(sw_vers -productVersion)" "$(uname -m)" "$memory_gib" "$free_gib"
(( memory_gib >= 8 )) || printf '%s\n' 'Caution: less than 8 GiB memory may constrain local builds.'
(( free_gib >= 3 )) || printf '%s\n' 'Caution: keep at least 3 GiB free before installing or building.'

printf 'Python project: %s\n' "$(command -v python3 || echo 'python3 missing')"
printf 'uv: %s\n' "$(command -v uv || echo 'uv missing')"

if ! $install && ! $build && ! $test_project; then
  printf '%s\n' 'Check complete. No files or packages were changed.'
  exit 0
fi

confirm() {
  local prompt=$1
  if $assume_yes; then return 0; fi
  printf '%s [y/N] ' "$prompt"
  read -r reply
  [[ "$reply" == [Yy] || "$reply" == [Yy][Ee][Ss] ]]
}

cd "$project_dir"
if $install; then
  confirm 'Install dependencies inside this checkout?' || exit 0
  command -v uv >/dev/null 2>&1 || { printf '%s\n' 'uv is required. Install it with: brew install uv' >&2; exit 1; }
  uv sync --locked
fi

if $build; then
  confirm 'Run the available local build commands?' || exit 0
  command -v uv >/dev/null 2>&1 || { printf '%s\n' 'uv is required. Install it with: brew install uv' >&2; exit 1; }
  uv build
fi

if $test_project; then
  confirm 'Run the available local test commands?' || exit 0
  command -v uv >/dev/null 2>&1 || { printf '%s\n' 'uv is required. Install it with: brew install uv' >&2; exit 1; }
  uv run pytest -q
fi

printf '%s\n' 'Requested setup actions completed.'
