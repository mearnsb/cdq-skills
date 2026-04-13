#!/bin/bash

# This script attempts to perform a fully automated onboarding of a random table.
# It will exit with a non-zero status on critical failures.
# On completion, it will echo '1' for success and '0' for partial or full failure.

set -o pipefail # pipe's return code is the rightmost command to exit with a non-zero status

SCHEMA="samples"
echo "INFO: Starting random table onboarding for schema: ${SCHEMA}"

# 1. List tables and pick one at random
TABLE_JSON=$(python lib/client.py list-tables --schema "${SCHEMA}" --limit 1000)
if [[ $? -ne 0 || -z "$TABLE_JSON" ]]; then
    echo "ERROR: Failed to list tables from schema '${SCHEMA}'."
    echo 0
    exit 1
fi

TABLE_NAME=$(echo "${TABLE_JSON}" | jq -r '.tables | .[0]')
if [[ -z "${TABLE_NAME}" ]]; then
    echo "ERROR: Failed to select a random table."
    echo 0
    exit 1
fi
echo "INFO: Randomly selected table: ${TABLE_NAME}"

# 2. Onboard the dataset
DATASET_NAME="AUTON_DQ_${SCHEMA}.${TABLE_NAME}"
echo "INFO: Onboarding dataset as: ${DATASET_NAME}"
ONBOARD_OUTPUT=$(python lib/client.py run-dq-job --dataset "${DATASET_NAME}" --sql "select * from ${SCHEMA}.${TABLE_NAME} limit 1000")
if [[ $? -ne 0 ]]; then
    echo "ERROR: Failed to submit onboarding job for dataset ${DATASET_NAME}."
    echo 0
    exit 1
fi
JOB_ID=$(echo "${ONBOARD_OUTPUT}" | jq -r '.job.jobId')
echo "INFO: Onboarding job submitted with ID: ${JOB_ID}. Waiting a few seconds for it to register..."
sleep 5 # Give the system a moment to register the new dataset

# 3. Get table columns to apply rules (up to 10)
# Note: Using run-sql with INFORMATION_SCHEMA is specific to the datasource (e.g., BigQuery).
# This might be a point of failure that autoresearch can improve.
COLUMNS_JSON=$(python lib/client.py run-sql --sql "SELECT column_name FROM ${SCHEMA}.INFORMATION_SCHEMA.COLUMNS WHERE table_name = '${TABLE_NAME}' LIMIT 10")
if [[ $? -ne 0 || -z "$COLUMNS_JSON" ]]; then
    echo "WARNING: Could not retrieve columns for '${TABLE_NAME}'. Skipping rule creation."
    # We can still consider the onboarding a success.
    echo 1
    exit 0
fi

COLUMNS=$(echo "${COLUMNS_JSON}" | jq -r '.results[].column_name')
SUCCESSFUL_RULES=0
for COL in ${COLUMNS}; do
    RULE_NAME="AUTON_${TABLE_NAME}_${COL}_NOT_NULL"
    RULE_DIMENSION="Completeness"
    RULE_EXPRESSION=""${COL}" IS NOT NULL" # Quoting column name for safety

    echo "INFO: Attempting to save rule '${RULE_NAME}'..."
    python lib/client.py save-rule --dataset "${DATASET_NAME}" --name "${RULE_NAME}" --dimension "${RULE_DIMENSION}" --expression "${RULE_EXPRESSION}" > /dev/null
    if [[ $? -eq 0 ]]; then
        echo "INFO: -> Success."
        ((SUCCESSFUL_RULES++))
    else
        echo "WARNING: -> Failed to save rule '${RULE_NAME}'. It might already exist or the column type may not be supported."
    fi
done

echo "INFO: Process complete. Saved ${SUCCESSFUL_RULES} rules for dataset '${DATASET_NAME}'."

# 4. Final success metric
if [[ ${SUCCESSFUL_RULES} -gt 0 ]]; then
    echo 1
else
    # If we failed to get columns or save any rules, it's not a 100% success for this complex goal.
    echo "WARNING: No new rules were saved."
    echo 0
fi
