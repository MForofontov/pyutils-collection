#!/bin/bash

# Propagate test and reporting failures to callers, including CI.
set -euo pipefail

# Default directories
DEFAULT_TEST_DIR="pytest/unit"
DEFAULT_ALLURE_RESULTS_DIR="pytest_run_tests/allure-results"
DEFAULT_ALLURE_REPORT_DIR="pytest_run_tests/allure-report"
DEFAULT_COVERAGE_REPORT_DIR="pytest_run_tests/coverage-report"

# Allow overriding default directories via command-line arguments
TEST_DIR=${1:-$DEFAULT_TEST_DIR}
ALLURE_RESULTS_DIR=${2:-$DEFAULT_ALLURE_RESULTS_DIR}
ALLURE_REPORT_DIR=${3:-$DEFAULT_ALLURE_REPORT_DIR}
GENERATE_ALLURE=${4:-true}  # New option to control Allure report generation
RUN_PARALLEL=${5:-false}    # Option to run tests in parallel with pytest-xdist
EXTRA_ARGS=${6:-"-m 'not performance'"}
ENABLE_COVERAGE=${7:-false} # Option to enable coverage reporting
COVERAGE_REPORT_DIR=${8:-$DEFAULT_COVERAGE_REPORT_DIR}

# Function to print messages with timestamps
log_with_time() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_with_time "[Info] Running tests in: $TEST_DIR"

# Build pytest command with optional parallel execution and extra args
PYTEST_CMD=(python -m pytest "$TEST_DIR")

# Add parallel execution if enabled
if [ "$RUN_PARALLEL" = "true" ]; then
    log_with_time "[Info] Running tests in parallel mode (-n auto)"
    PYTEST_CMD+=(-n auto)
fi

# Add coverage if enabled
if [ "$ENABLE_COVERAGE" = "true" ]; then
    log_with_time "[Info] Coverage reporting enabled"
    PYTEST_CMD+=(--cov=pyutils_collection --cov-report=term-missing "--cov-report=html:$COVERAGE_REPORT_DIR" --cov-report=xml:coverage.xml)
fi

# Add extra arguments if provided
if [ -n "$EXTRA_ARGS" ]; then
    log_with_time "[Info] Using extra pytest arguments: $EXTRA_ARGS"
    # Parse quoted pytest expressions without evaluating shell commands.
    PARSED_ARGS=$(python -c 'import shlex, sys; print("\n".join(shlex.split(sys.argv[1])))' "$EXTRA_ARGS")
    EXTRA_ARGV=()
    while IFS= read -r extra_arg; do
        EXTRA_ARGV+=("$extra_arg")
    done <<< "$PARSED_ARGS"
    PYTEST_CMD+=("${EXTRA_ARGV[@]}")
fi

if [ "$GENERATE_ALLURE" = "true" ]; then
    log_with_time "[Info] Storing Allure results in: $ALLURE_RESULTS_DIR"
    log_with_time "[Info] Generating Allure report in: $ALLURE_REPORT_DIR"

    # Run pytest with Allure results
    "${PYTEST_CMD[@]}" "--alluredir=$ALLURE_RESULTS_DIR"

    log_with_time "[Info] Allure results generated successfully in $ALLURE_RESULTS_DIR!"

    if command -v allure >/dev/null 2>&1; then
        log_with_time "[Info] Generating Allure report..."
        # Generate the Allure report in the specified directory
        allure generate "$ALLURE_RESULTS_DIR" -o "$ALLURE_REPORT_DIR" --clean
        log_with_time "[Info] Allure report generated successfully in $ALLURE_REPORT_DIR!"

        # Only open report if not in CI environment
        if [ -z "${CI:-}" ]; then
            allure open "$ALLURE_REPORT_DIR"
        else
            log_with_time "[Info] Skipping report opening in CI environment"
        fi
    else
        log_with_time "[Warn] Allure CLI not found. Skipping report generation."
    fi
else
    log_with_time "[Info] Skipping Allure report generation"
    # Run pytest without Allure
    "${PYTEST_CMD[@]}"
fi

# Display coverage report location if generated
if [ "$ENABLE_COVERAGE" = "true" ]; then
    log_with_time "[Info] Coverage HTML report generated in: $COVERAGE_REPORT_DIR"
    log_with_time "[Info] Open it with: open $COVERAGE_REPORT_DIR/index.html"
fi
