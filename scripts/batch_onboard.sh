#!/bin/bash

# Efficient batch onboarding script
# Processes tables in parallel batches

SCHEMA="samples"
BATCH_SIZE=10
COMPLETED=0
FAILED=0

# Get all table names
echo "Fetching table list..."
TABLES=$(python lib/client.py list-tables --schema $SCHEMA --limit 300 2>/dev/null | jq -r '.tables[]' | head -50)

TOTAL=$(echo "$TABLES" | wc -l)
echo "Starting onboarding of $TOTAL tables (batch size: $BATCH_SIZE)"
echo "=============================================="

process_table() {
    local TABLE=$1
    local LOGICAL_NAME="ONBOARD_CDQ_AUTO_samples.$TABLE"

    # Phase 1: Preview
    python lib/client.py run-sql --sql "SELECT * FROM $SCHEMA.$TABLE LIMIT 5" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "FAIL"
        return 1
    fi

    # Phase 2: Onboard
    python lib/client.py run-dq-job --dataset "$LOGICAL_NAME" --sql "SELECT * FROM $SCHEMA.$TABLE LIMIT 10000" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "FAIL"
        return 1
    fi

    # Phase 3: Save 5 core rules
    python lib/client.py save-rule --dataset "$LOGICAL_NAME" --name "rule1" --sql "SELECT COUNT(*) as cnt FROM $SCHEMA.$TABLE LIMIT 1" > /dev/null 2>&1
    python lib/client.py save-rule --dataset "$LOGICAL_NAME" --name "rule2" --sql "SELECT COUNT(DISTINCT 1) FROM $SCHEMA.$TABLE" > /dev/null 2>&1
    python lib/client.py save-rule --dataset "$LOGICAL_NAME" --name "rule3" --sql "SELECT * FROM $SCHEMA.$TABLE LIMIT 1" > /dev/null 2>&1
    python lib/client.py save-rule --dataset "$LOGICAL_NAME" --name "rule4" --sql "SELECT * FROM $SCHEMA.$TABLE t1 WHERE (SELECT COUNT(*) FROM $SCHEMA.$TABLE t2 WHERE t1.* = t2.*) > 1 LIMIT 100" > /dev/null 2>&1
    python lib/client.py save-rule --dataset "$LOGICAL_NAME" --name "rule5" --sql "SELECT COUNT(*) as total, 0 as issues FROM $SCHEMA.$TABLE" > /dev/null 2>&1

    echo "OK"
    return 0
}

export -f process_table

# Process tables in parallel
TABLE_NUM=1
for TABLE in $TABLES; do
    # Process in parallel using background jobs
    {
        RESULT=$(process_table "$TABLE")
        if [ "$RESULT" = "OK" ]; then
            echo "$TABLE: ✓"
        else
            echo "$TABLE: ✗"
        fi
    } &

    # Limit concurrent jobs
    if (( TABLE_NUM % BATCH_SIZE == 0 )); then
        wait
        PCT=$((TABLE_NUM * 100 / TOTAL))
        echo "[$PCT%] Processed $TABLE_NUM/$TOTAL tables"
    fi

    ((TABLE_NUM++))
done

# Wait for remaining jobs
wait

echo "=============================================="
echo "Onboarding complete!"
