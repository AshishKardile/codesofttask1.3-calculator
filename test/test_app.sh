#!/bin/bash
# ==============================================================================
# Automated CI Test & Lint Script for Premium Calculator Application
# ==============================================================================
set -e

echo "====================================================="
echo " Starting Automated Test & Syntax Validation Stage   "
echo "====================================================="

FAILED=0

# 1. Verify existence of all essential web assets
echo -n "[TEST 1/4] Checking required web asset files... "
REQUIRED_FILES=("index.html" "style.css" "script.js" "background.jpg")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "\n  [FAIL] Missing required file: $file"
        FAILED=1
    elif [ ! -s "$file" ]; then
        echo -e "\n  [FAIL] File is empty: $file"
        FAILED=1
    fi
done

if [ $FAILED -eq 0 ]; then
    echo "PASSED (all files exist and non-empty)"
fi

# 2. Validate HTML Structure & Essential DOM elements
echo -n "[TEST 2/4] Validating HTML structure and key DOM elements... "
if grep -qi "<!DOCTYPE html>" index.html && \
   grep -q 'id="display-value"' index.html && \
   grep -q 'class="calculator"' index.html && \
   grep -q 'script.js' index.html && \
   grep -q 'style.css' index.html; then
    echo "PASSED (DOCTYPE, calculator container, LCD screen & asset links verified)"
else
    echo "FAILED (Required HTML elements or bindings are missing)"
    FAILED=1
fi

# 3. JavaScript Syntax Validation
echo -n "[TEST 3/4] Checking JavaScript syntax validity... "
if command -v node >/dev/null 2>&1; then
    if node -c script.js; then
        echo "PASSED (Node.js syntax check passed)"
    else
        echo "FAILED (Syntax error found in script.js)"
        FAILED=1
    fi
elif command -v python3 >/dev/null 2>&1; then
    # Fallback to python3 basic validation
    python3 -c "
with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()
assert 'function' in content or '=>' in content or 'const' in content or 'let' in content, 'Script does not contain JS logic'
print('PASSED (Basic JS sanity check verified via Python)')
"
else
    echo "SKIPPED (neither node nor python3 available for deep AST check)"
fi

# 4. CSS File Sanity Check (matching braces)
echo -n "[TEST 4/4] Verifying CSS syntax (brace balance)... "
OPEN_BRACES=$(grep -o "{" style.css | wc -l)
CLOSE_BRACES=$(grep -o "}" style.css | wc -l)

if [ "$OPEN_BRACES" -eq "$CLOSE_BRACES" ] && [ "$OPEN_BRACES" -gt 0 ]; then
    echo "PASSED ($OPEN_BRACES selector blocks verified)"
else
    echo "FAILED (Unmatched CSS braces: { = $OPEN_BRACES, } = $CLOSE_BRACES)"
    FAILED=1
fi

echo "====================================================="
if [ $FAILED -eq 0 ]; then
    echo " ALL TESTS PASSED! Ready for Docker Build. "
    echo "====================================================="
    exit 0
else
    echo " TESTS FAILED! Build cannot proceed. "
    echo "====================================================="
    exit 1
fi
