# Gemini CLI Web Search - Issue Analysis & Fix

## Problem Identified

**Issue**: Gemini CLI returns no results when asked to perform web search/research
- Command: `gemini -m gemini-2.5-flash --approval-mode yolo -p "Perform a technical trend analysis regarding..."`
- Result: No web search results, only local knowledge

**Root Cause**: Gemini has web search capability (`google_web_search` tool) built-in, but it's NOT being triggered because:
1. The prompt doesn't explicitly request web search
2. Approval mode `yolo` auto-approves but doesn't force tool use
3. Gemini defaults to using local knowledge first

---

## Solution: Explicit Web Search Prompts

### Fix 1: Explicitly Request Web Search (RECOMMENDED)

Modify your prompt to explicitly tell Gemini to search:

```bash
gemini -m gemini-2.5-flash --approval-mode yolo \
  -p "Search the web for the latest technical trends regarding [topic].
       Use web search to find current information from 2025-2026.
       Provide recent examples and sources."
```

**Why this works**: When you explicitly request "search the web" or "use web search," Gemini knows to invoke the `google_web_search` tool.

---

### Fix 2: Use auto_edit or default Mode (SAFER)

For research tasks, use `auto_edit` instead of `yolo`:

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Search the web for technical trends. Find recent information about [topic]."
```

**Why this works**: `auto_edit` mode shows you each tool call, letting you see when Gemini uses web search. `yolo` silently executes without feedback.

---

### Fix 3: Interactive Mode for Research (BEST FOR EXPLORATION)

Use interactive mode for ongoing research:

```bash
# Load environment
set -a && source ~/.openclaw/.env && set +a

# Start interactive
gemini -m gemini-2.5-flash

# Then type:
# > Search for the latest AI trends in 2025-2026
# > Find information about [topic]
# > What are the recent developments in [field]?
```

**Why this works**: Interactive mode lets Gemini decide when to use web search based on your questions.

---

## Testing the Fix

### Test 1: Verify Web Search Works

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Search the web for the top technical trends of 2025. List at least 5 with sources."
```

**Expected output**:
- Multiple tool calls showing `google_web_search` being invoked
- Recent results from 2025-2026
- Citations/sources included

### Test 2: Compare Before/After

**Before (no search)**:
```bash
gemini -m gemini-2.5-flash --approval-mode yolo \
  -p "What are technical trends?"
```
Result: General knowledge only, no web search

**After (with explicit search request)**:
```bash
gemini -m gemini-2.5-flash --approval-mode yolo \
  -p "Search the web for technical trends in 2025-2026. What's new?"
```
Result: Current information with web search results

### Test 3: Check Tool Execution

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Use web search to find the latest data quality industry trends."
```

Watch for output like:
```
⏺ Tool Call: google_web_search(query="data quality industry trends 2025")
⏺ Result: [search results...]
```

---

## Complete Working Examples

### Example 1: Technical Trend Analysis (Your Original Use Case)

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Perform a technical trend analysis for 2025-2026.
       Search the web for:
       1. AI/ML innovations
       2. Data quality best practices
       3. Cloud infrastructure trends

       For each trend:
       - Explain what it is
       - Show recent examples (2025-2026)
       - List sources and links
       - Explain business impact"
```

### Example 2: Industry Research with Web Search

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Research the data quality industry in 2025.
       Use web search to find:
       - Major players and recent announcements
       - New products or features released
       - Industry statistics and market trends
       - Best practices and frameworks

       Include links to sources."
```

### Example 3: Comparison Research

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Compare modern data quality tools and frameworks.
       Search the web for current information about:
       - Collibra's latest offerings
       - Open-source alternatives
       - Cloud-native DQ solutions
       - Recent industry reports

       Provide 2025-2026 information with sources."
```

### Example 4: Interactive Research Session

```bash
# Start interactive mode
set -a && source ~/.openclaw/.env && set +a
gemini -m gemini-2.5-flash

# Then ask follow-up questions:
# > Search for data quality ROI statistics
# > What are companies reporting?
# > Find case studies
# > Look up implementation costs
```

---

## How Gemini Web Search Works

### Built-in Tool: `google_web_search`

Gemini 2.5 Flash has built-in access to Google's web search:

```
Trigger: When you ask Gemini to:
  - "Search for..."
  - "Find information about..."
  - "What's new in..."
  - "Recent trends in..."
  - "Find current information..."
  - Any research-oriented question

Gemini then invokes: google_web_search(query="...")
Returns: Recent search results from across the web
```

### Approval Modes and Web Search

| Mode | Behavior | Web Search |
|------|----------|-----------|
| `default` | Prompts for each tool | ✅ Asks before searching |
| `auto_edit` | Auto-approves edits, prompts others | ✅ Shows search calls, you approve |
| `yolo` | Auto-approves all | ✅ Silently searches (no feedback) |
| `plan` | Read-only, no execution | ❌ Refuses to search |

---

## Prompt Patterns for Web Search

### Pattern 1: Explicit Search Request (Most Reliable)

```bash
-p "Search the web for [topic]. Find [specific information]."
```

### Pattern 2: Research Task

```bash
-p "Research [topic]. Use web search to find current information about [details]."
```

### Pattern 3: Trend Analysis

```bash
-p "Analyze current trends in [field]. Search the web for 2025-2026 information."
```

### Pattern 4: Comparison

```bash
-p "Compare [items]. Search the web for current information on each."
```

### Pattern 5: News/Updates

```bash
-p "What's new in [field]? Search the web for recent announcements and updates."
```

---

## Troubleshooting Web Search

### Problem: "No results" or generic answers

**Cause**: Gemini isn't invoking web search
**Fix**:
- Add "Search the web for..." to your prompt
- Use `--approval-mode auto_edit` to see if tools are being called
- Check if your prompt is too vague

```bash
# ❌ Vague (might not trigger search)
-p "What are trends?"

# ✅ Explicit (will trigger search)
-p "Search the web for technical trends in 2025-2026"
```

### Problem: "Tool call blocked"

**Cause**: Using `--approval-mode plan` (read-only mode)
**Fix**: Change to `auto_edit` or `yolo`

```bash
# ❌ Plan mode (blocks tools)
gemini ... --approval-mode plan -p "Search for..."

# ✅ Auto-edit mode (allows search)
gemini ... --approval-mode auto_edit -p "Search for..."
```

### Problem: "Search returned nothing"

**Cause**: Query might be too specific or niche
**Fix**:
- Broaden the search query
- Add context
- Use simpler keywords

```bash
# ❌ Too specific
-p "Search for obscure esoteric data quality metrics from 2026"

# ✅ More general
-p "Search for data quality metrics and industry standards in 2025-2026"
```

---

## Recommended Prompting Strategy

For best results with web search in Gemini CLI:

1. **Use `auto_edit` mode** - See which tools are being called
2. **Explicitly request search** - Say "search the web" or "research"
3. **Specify time frame** - "2025-2026" or "recent"
4. **Ask for sources** - "Include links/citations"
5. **Be specific** - Clear topic focus works better than vague queries

### Template

```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Search the web for [TOPIC].
      Focus on: [SPECIFIC AREAS]
      Time period: 2025-2026
      Include: [SOURCES/LINKS/DATA]
      Summarize: [KEY INSIGHTS]"
```

---

## Integration with CDQ Skills

### Use Case: Research Before Creating DQ Rules

```bash
# Step 1: Research industry standards
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Search the web for data quality best practices for [domain].
      Find: frameworks, standards, common metrics, typical thresholds"

# Step 2: Use findings to inform CDQ rule creation
# Then run CDQ skill to implement rules
cdq-save-rule --dataset "MY_DATASET" --name "Rule Name" --sql "..."
```

### Use Case: Analyze DQ Results with Context

```bash
# Get DQ results
cdq-get-results --dataset "MY_DATASET" --run-id "2026-04-08"

# Research context
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Search for industry benchmarks for data quality scores.
      Context: I have 85% quality score
      Find: what's typical for [industry], how to improve"
```

---

## Wrapper Script Enhancement (Optional)

If you want to make web search automatic, you can modify `.claude/bin/gemini-wrapper.sh` to detect research keywords:

```bash
# Enhancement: Auto-add web search hint for research queries
if echo "$PROMPT" | grep -iE "research|trend|find|search|latest|recent|current" > /dev/null; then
    # Suggest using auto_edit mode for research
    if [ "$APPROVAL_MODE" = "yolo" ]; then
        echo "💡 Tip: Use --approval-mode auto_edit to see web search results"
    fi
fi
```

But this is optional - just explicitly requesting "search the web" in your prompt works perfectly.

---

## Summary

**Your Original Problem**:
```bash
gemini -m gemini-2.5-flash --approval-mode yolo \
  -p "Perform a technical trend analysis regarding..."
# Result: No web search (silently using local knowledge)
```

**The Fix**:
```bash
gemini -m gemini-2.5-flash --approval-mode auto_edit \
  -p "Search the web for technical trend analysis.
      Find current information about [topic]..."
# Result: Web search executed, current results returned
```

**Key Changes**:
1. Added "Search the web for" to prompt
2. Changed approval mode from `yolo` to `auto_edit` (better visibility)

**That's it!** Gemini CLI has web search built-in - you just need to ask for it explicitly.

---

## Additional Resources

- Gemini 2.5 Flash capabilities: https://ai.google.dev/docs
- Google Web Search tool: Part of Gemini's native tools
- Interactive mode: Better for exploration and follow-up questions
