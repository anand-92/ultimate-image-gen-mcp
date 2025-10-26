# Fix Verification Test Plan

**Purpose:** Verify that all critical fixes from commit `efa6a4d` are working correctly
**Date Created:** October 25, 2025
**Prerequisites:** MCP client must be restarted to load updated code

---

## Test Categories

1. [Gemini Image Generation](#1-gemini-image-generation-critical)
2. [Seed Parameter Handling](#2-seed-parameter-handling)
3. [Person Generation Policy Warnings](#3-person-generation-policy-warnings)
4. [Aspect Ratio Support (Gemini)](#4-aspect-ratio-support-gemini)
5. [Regression Tests](#5-regression-tests)

---

## 1. Gemini Image Generation (CRITICAL)

**Issue Fixed:** Gemini API was returning no image data due to missing `responseModalities` config

### Test 1.1: Basic Gemini Generation

**Objective:** Verify basic image generation works with default settings

**Steps:**
```python
generate_image(
    prompt="a red apple on a wooden table",
    model="gemini-2.5-flash-image",
    enhance_prompt=False
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Image file created in `generated_images/`
- ✅ File size > 0 bytes
- ✅ Response includes `path` and `filename`
- ✅ No error messages

**Failure Criteria:**
- ❌ Error: "No image data found in Gemini API response"
- ❌ `success: false`

---

### Test 1.2: Gemini with Prompt Enhancement

**Objective:** Verify prompt enhancement doesn't break generation

**Steps:**
```python
generate_image(
    prompt="a futuristic robot in a neon city",
    model="gemini-2.5-flash-image",
    enhance_prompt=True
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Image generated successfully
- ✅ Response includes `enhanced_prompt` in metadata
- ✅ Enhanced prompt is significantly longer than original

**Failure Criteria:**
- ❌ Enhancement breaks image generation
- ❌ No enhanced_prompt in response

---

### Test 1.3: Gemini Image Editing

**Objective:** Verify image editing with input image works

**Prerequisites:** Input image file exists at root directory

**Steps:**
```python
generate_image(
    prompt="add a red border around this image",
    model="gemini-2.5-flash-image",
    input_image_path="/Users/nikhilanand/Desktop/ultimate gemini mcp/ultimate-gemini-mcp/thisimage.png"
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Output image is modified version of input
- ✅ Red border visible in output

**Failure Criteria:**
- ❌ Error: "No image data found"
- ❌ Original image unchanged

---

### Test 1.4: Gemini Complex Prompt

**Objective:** Verify Gemini handles complex, detailed prompts

**Steps:**
```python
generate_image(
    prompt="A photorealistic portrait of a wise old wizard with a long white beard, wearing a purple robe with gold embroidery, holding a crystal staff, dramatic lighting from the left side, mystical atmosphere, high detail",
    model="gemini-2.5-flash-image",
    enhance_prompt=True
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Image reflects detailed prompt elements
- ✅ Enhancement adds cinematic/photographic terms

**Failure Criteria:**
- ❌ Generic or low-quality output
- ❌ Generation fails

---

## 2. Seed Parameter Handling

**Issue Fixed:** Imagen API returns 400 error when seed is provided; now handled gracefully

### Test 2.1: Seed Parameter with Warning

**Objective:** Verify seed parameter triggers warning but doesn't fail

**Steps:**
```python
generate_image(
    prompt="a colorful abstract pattern",
    model="imagen-4",
    seed=12345
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Image generated successfully
- ✅ Warning logged: "seed parameter is not currently supported"
- ✅ Seed is NOT sent to API (no 400 error)

**Failure Criteria:**
- ❌ Error: "Setting seed is not supported" (400 from API)
- ❌ Generation fails
- ❌ No warning message

---

### Test 2.2: Same Prompt Without Seed

**Objective:** Verify removal of seed doesn't affect normal operation

**Steps:**
```python
generate_image(
    prompt="a colorful abstract pattern",
    model="imagen-4",
    seed=None  # or omit parameter
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Image generated successfully
- ✅ No warning about seed

**Failure Criteria:**
- ❌ Any errors
- ❌ Unexpected warnings

---

### Test 2.3: Seed Documentation Check

**Objective:** Verify tool documentation reflects seed limitation

**Steps:**
- Inspect the tool's docstring/help text

**Expected Result:**
- ✅ Seed parameter description includes: "NOT SUPPORTED - will be ignored"
- ✅ Clear indication that seed won't work

**Failure Criteria:**
- ❌ Documentation claims seed works for reproducibility
- ❌ No warning about limitation

---

## 3. Person Generation Policy Warnings

**Issue Fixed:** Added validation to warn when prompt conflicts with person_generation policy

### Test 3.1: Conflict Detection - "dont_allow" with Person Keywords

**Objective:** Verify warning when prompt mentions people with restrictive policy

**Steps:**
```python
generate_image(
    prompt="a crowd of people walking in a busy street",
    model="imagen-4",
    person_generation="dont_allow"
)
```

**Expected Result:**
- ✅ Warning logged: "Prompt contains person-related keywords but person_generation is set to 'dont_allow'"
- ✅ Warning mentions: "may result in the API blocking image generation"
- ⚠️ May succeed or fail depending on API behavior
- ✅ User is warned BEFORE API call

**Failure Criteria:**
- ❌ No warning issued
- ❌ Silent failure without explanation

---

### Test 3.2: Conflict Detection - Multiple Person Keywords

**Objective:** Verify detection of various person-related terms

**Test Cases:**
| Prompt | Should Warn |
|--------|-------------|
| "a portrait of a woman" | ✅ Yes |
| "human face close-up" | ✅ Yes |
| "child playing in park" | ✅ Yes |
| "man standing alone" | ✅ Yes |
| "a landscape with trees" | ❌ No |
| "abstract geometric shapes" | ❌ No |

**Steps:**
Test each prompt with `person_generation="dont_allow"`

**Expected Result:**
- ✅ Warnings issued only for prompts with person keywords
- ✅ No false positives on landscape/abstract prompts

---

### Test 3.3: No Warning with "allow_adult"

**Objective:** Verify no warning when policy allows people

**Steps:**
```python
generate_image(
    prompt="a person walking in a park",
    model="imagen-4",
    person_generation="allow_adult"  # default
)
```

**Expected Result:**
- ✅ `success: true`
- ✅ Image generated with person
- ✅ No conflict warning (policy allows people)

**Failure Criteria:**
- ❌ Warning issued despite permissive policy
- ❌ Generation blocked

---

## 4. Aspect Ratio Support (Gemini)

**Issue Fixed:** Added `imageConfig` with `aspectRatio` to Gemini requests

### Test 4.1: Gemini 1:1 (Default)

**Steps:**
```python
generate_image(
    prompt="a simple geometric shape",
    model="gemini-2.5-flash-image",
    aspect_ratio="1:1"
)
```

**Expected Result:**
- ✅ Image is square (1:1 ratio)
- ✅ `imageConfig.aspectRatio: "1:1"` sent to API

---

### Test 4.2: Gemini 16:9 (Wide)

**Steps:**
```python
generate_image(
    prompt="a panoramic mountain landscape",
    model="gemini-2.5-flash-image",
    aspect_ratio="16:9"
)
```

**Expected Result:**
- ✅ Image is wide (16:9 ratio)
- ✅ Landscape composition utilized

---

### Test 4.3: Gemini 9:16 (Tall)

**Steps:**
```python
generate_image(
    prompt="a tall skyscraper reaching into clouds",
    model="gemini-2.5-flash-image",
    aspect_ratio="9:16"
)
```

**Expected Result:**
- ✅ Image is tall/vertical (9:16 ratio)
- ✅ Composition emphasizes height

---

### Test 4.4: Gemini Multiple Aspect Ratios

**Objective:** Test all supported aspect ratios

**Test Matrix:**
| Aspect Ratio | Expected Orientation | Test Prompt |
|--------------|---------------------|-------------|
| 1:1 | Square | "a perfect circle" |
| 2:3 | Portrait | "a vertical portrait" |
| 3:2 | Landscape | "a wide landscape" |
| 4:3 | Classic horizontal | "a classic photo" |
| 16:9 | Widescreen | "an ultra-wide panorama" |
| 9:16 | Mobile portrait | "a tall mobile wallpaper" |

**Expected Result:**
- ✅ All ratios generate successfully
- ✅ Output images match requested ratios

---

## 5. Regression Tests

**Objective:** Ensure fixes didn't break existing functionality

### Test 5.1: Imagen Still Works

**Steps:**
```python
generate_image(
    prompt="a beautiful sunset",
    model="imagen-4"
)
```

**Expected Result:**
- ✅ Imagen generation still works perfectly
- ✅ No changes to Imagen behavior

---

### Test 5.2: Negative Prompt Still Works

**Steps:**
```python
generate_image(
    prompt="a forest landscape",
    model="imagen-4",
    negative_prompt="people, buildings, cars"
)
```

**Expected Result:**
- ✅ Negative prompts still applied correctly
- ✅ Excluded elements don't appear

---

### Test 5.3: Prompt Enhancement Still Works

**Steps:**
```python
generate_image(
    prompt="a simple scene",
    model="imagen-4",
    enhance_prompt=True
)
```

**Expected Result:**
- ✅ Enhancement still adds detailed photography terms
- ✅ Enhanced prompt visible in response metadata

---

### Test 5.4: Input Validation Still Works

**Steps:**
```python
# Test invalid model
generate_image(
    prompt="test",
    model="invalid-model-999"
)

# Test invalid aspect ratio
generate_image(
    prompt="test",
    model="imagen-4",
    aspect_ratio="999:1"
)
```

**Expected Result:**
- ✅ Validation errors for invalid inputs
- ✅ Clear error messages with available options

---

## Debug Logging Verification

**Issue Fixed:** Added comprehensive debug logging

### Test 6.1: Debug Logs Present (if LOG_LEVEL=DEBUG)

**Steps:**
1. Set environment variable: `LOG_LEVEL=DEBUG`
2. Run any Gemini generation
3. Check logs

**Expected Log Entries:**
- ✅ "Sending request to [url]"
- ✅ "Request body: {...}"
- ✅ "Response status: 200"
- ✅ "Response data: {...}"
- ✅ "Extracted image data of length: [bytes]"

**Failure Criteria:**
- ❌ No debug logs visible
- ❌ Missing request/response details

---

### Test 6.2: Error Logging Improvements

**Steps:**
Force an error (e.g., invalid API key) and check logs

**Expected Log Entries:**
- ✅ "No images extracted from response. Response structure: [keys]"
- ✅ "Candidates: [candidate data]" (if candidates present)
- ✅ Detailed error context

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] MCP client restarted (to load new code)
- [ ] `GEMINI_API_KEY` environment variable set
- [ ] Input images available at root directory (`thisimage.png`, `thisOnetoo.png`)
- [ ] `generated_images/` directory exists

### Critical Tests (Must Pass)
- [ ] Test 1.1: Basic Gemini Generation ⭐
- [ ] Test 1.2: Gemini with Prompt Enhancement ⭐
- [ ] Test 1.3: Gemini Image Editing ⭐
- [ ] Test 2.1: Seed Parameter with Warning ⭐
- [ ] Test 3.1: Person Policy Conflict Warning ⭐
- [ ] Test 4.2: Gemini 16:9 Aspect Ratio ⭐

### Important Tests (Should Pass)
- [ ] Test 1.4: Complex Prompt
- [ ] Test 2.3: Seed Documentation Check
- [ ] Test 3.2: Multiple Person Keywords
- [ ] Test 4.4: All Aspect Ratios

### Regression Tests (Must Pass)
- [ ] Test 5.1: Imagen Still Works
- [ ] Test 5.2: Negative Prompt Still Works
- [ ] Test 5.3: Prompt Enhancement Still Works
- [ ] Test 5.4: Input Validation Still Works

### Optional Tests
- [ ] Test 6.1: Debug Logging
- [ ] Test 6.2: Error Logging

---

## Success Criteria

### Minimum Acceptable (MVP)
- ✅ All 6 Critical Tests pass
- ✅ At least 3 out of 4 Important Tests pass
- ✅ All 4 Regression Tests pass
- ✅ Zero P0 (critical) bugs found

### Full Success
- ✅ All Critical Tests pass (100%)
- ✅ All Important Tests pass (100%)
- ✅ All Regression Tests pass (100%)
- ✅ Optional Tests pass (bonus)
- ✅ No bugs found

### Partial Success
- ⚠️ 4-5 Critical Tests pass (80%+)
- ⚠️ Most Regression Tests pass
- ⚠️ New issues documented for follow-up

---

## Issue Tracking Template

If tests fail, document using this template:

```markdown
### Issue: [Brief Description]

**Test Failed:** [Test Number and Name]
**Severity:** Critical | High | Medium | Low
**Status:** New | In Progress | Fixed

**Steps to Reproduce:**
1.
2.
3.

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Error Messages:**
```
[Paste error output]
```

**Additional Context:**
[Logs, screenshots, etc.]

**Proposed Fix:**
[If known]
```

---

## Post-Test Actions

### If All Tests Pass ✅
1. Update `TEST_RESULTS.md` with verification results
2. Mark issues as "FIXED" in documentation
3. Update project status to "Stable"
4. Consider bumping version to v1.1.0

### If Tests Fail ❌
1. Document failures using Issue Tracking Template
2. Prioritize by severity
3. Create fix plan for critical issues
4. Re-run tests after fixes

### Partial Success ⚠️
1. Document which tests passed/failed
2. Assess if partial fix is better than no fix
3. Decide: rollback or proceed with known issues
4. Update documentation with limitations

---

## Notes

- **Test Execution Order:** Run Critical tests first, then Regression, then Important
- **Parallel Testing:** Regression tests can run in parallel with fix verification
- **Time Estimate:** ~20-30 minutes for full test suite
- **Quick Verification:** Run Critical Tests only (~5 minutes)

---

## Appendix: Quick Test Commands

### Minimal Verification (2 minutes)
```python
# Test 1: Gemini works
generate_image(prompt="a red apple", model="gemini-2.5-flash-image", enhance_prompt=False)

# Test 2: Seed handled gracefully
generate_image(prompt="abstract art", model="imagen-4", seed=123)
```

### Full Verification Script
See `run_verification_tests.py` (to be created) for automated testing.

---

**Document Version:** 1.0
**Last Updated:** October 25, 2025
**Next Review:** After test execution
