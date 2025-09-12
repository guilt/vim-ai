#!/bin/bash

# vim-ai Test Runner - Python 3.4+ compatibility testing
set -e

# Activate mise environment if available
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)"
    # Ensure mise shims are in PATH
    export PATH="$HOME/.local/share/mise/shims:$PATH"
fi

PYTHONS=(
        "python3.4" "python3.5" "python3.6" "python3.7" "python3.8"
        "python3.9" "python3.10" "python3.11" "python3.12" "python3.13"
)

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_VERSIONS=()

echo "🚀 vim-ai Test Runner - Testing Python 3.4+ compatibility"
echo

# Allow running specific Python version
if [[ $1 ]]; then
    PYTHONS=("$1")
    echo "🎯 Testing single version: $1"
    echo
fi

for python in "${PYTHONS[@]}"; do
    if ! command -v "$python" &> /dev/null; then
        echo "⚠️  Skipping $python - not found"
        continue
    fi
    
    version=$($python --version 2>&1 | cut -d' ' -f2)
    echo "🐍 Testing Python $version..."
    
    # Install pytest if needed
    if ! $python -c "import pytest" 2>/dev/null; then
        echo "   📦 Installing pytest..."
        if [[ "$version" == 3.5.* ]]; then
            $python -m pip install "pytest>=3.0.0,<4.0.0" -q 2>/dev/null || \
            echo "   ⚠️  pytest install failed"
        else
            $python -m pip install pytest -q 2>/dev/null || \
            $python -m pip install pytest --user --break-system-packages -q 2>/dev/null || \
            echo "   ⚠️  pytest install failed"
        fi
    fi
    
    # Run tests and capture results
    if output=$(PYTHONPATH=vim_ai:tests/mocks VIMAI_DUMMY_IMPORT=1 $python -m pytest tests/ -q --tb=no 2>/dev/null); then
        test_count=$(echo "$output" | grep -o '[0-9]\+ passed' | grep -o '[0-9]\+' || echo "0")
        echo "✅ Python $version: $test_count tests pass"
        PASSED_TESTS=$((PASSED_TESTS + test_count))
        TOTAL_TESTS=$((TOTAL_TESTS + test_count))
    else
        echo "❌ Python $version: tests failed"
        FAILED_VERSIONS+=("$version")
    fi
    
    echo
done

echo "📊 RESULTS:"
echo "   Tests passed: $PASSED_TESTS/$TOTAL_TESTS"
if [[ $TOTAL_TESTS -gt 0 ]]; then
    echo "   Success rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
fi

if [[ ${#FAILED_VERSIONS[@]} -eq 0 ]]; then
    echo "🎉 ALL TESTS PASS!"
    exit 0
else
    echo "💥 Failed: ${FAILED_VERSIONS[*]}"
    exit 1
fi
