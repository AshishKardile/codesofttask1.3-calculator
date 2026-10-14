#!/usr/bin/env python3
"""
Automated CI Test Suite for Premium Desktop Calculator
Validates:
1. File assets integrity
2. HTML structure & DOM IDs
3. JavaScript syntax sanity
4. CSS brace balancing
"""
import sys
from pathlib import Path

def test_files_exist():
    required_files = ["index.html", "style.css", "script.js", "background.jpg"]
    for filename in required_files:
        p = Path(filename)
        assert p.exists(), f"Missing required file: {filename}"
        assert p.stat().st_size > 0, f"File is empty: {filename}"
    print("[PASS] 1. All web asset files exist and are non-empty.")

def test_html_structure():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    assert "<!DOCTYPE html>" in html or "<!doctype html>" in html, "Missing <!DOCTYPE html>"
    assert 'id="display-value"' in html, "Missing display-value DOM element"
    assert 'class="calculator"' in html, "Missing calculator class container"
    assert 'script.js' in html, "Missing script.js script tag"
    assert 'style.css' in html, "Missing style.css stylesheet link"
    print("[PASS] 2. HTML structure and key DOM elements verified.")

def test_css_syntax():
    with open("style.css", "r", encoding="utf-8") as f:
        css = f.read()
    open_braces = css.count("{")
    close_braces = css.count("}")
    assert open_braces > 0, "No CSS rules found"
    assert open_braces == close_braces, f"Mismatched braces in CSS: {open_braces} != {close_braces}"
    print(f"[PASS] 3. CSS brace balance verified ({open_braces} rule blocks).")

def test_js_content():
    with open("script.js", "r", encoding="utf-8") as f:
        js = f.read()
    assert len(js.strip()) > 100, "JavaScript file too short"
    assert "addEventListener" in js or "document." in js, "No DOM listener bindings found in script.js"
    print("[PASS] 4. JavaScript logic bindings verified.")

if __name__ == "__main__":
    print("==================================================")
    print(" Running Calculator CI Test Suite ")
    print("==================================================")
    try:
        test_files_exist()
        test_html_structure()
        test_css_syntax()
        test_js_content()
        print("==================================================")
        print(" ALL TESTS PASSED SUCCESSFULLY! ")
        print("==================================================")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] Test assertion failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
