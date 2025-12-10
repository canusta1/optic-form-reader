# Debug Image Output Guide

## Overview
The OMR system now automatically saves intermediate processing images to help you diagnose detection failures. All images are saved in the current working directory.

---

## 🖼️ Debug Images Generated

### 1. **debug_edges.jpg**
**What it shows:** Canny edge detection output
**Purpose:** Verify that form edges are being detected

**What to look for:**
- ✅ **Good**: Clear, continuous lines showing form boundaries
- ⚠️ **Bad**: Broken lines, missing edges, too much noise

**Canny Parameters:** 
- Lower threshold: 75
- Upper threshold: 200
- Optimized for paper documents

**Troubleshooting:**
- If edges are too weak → Image might be blurry or low contrast
- If too much noise → Try better lighting or higher resolution scan
- If form edges missing → Form might be outside camera view

---

### 2. **debug_contours.jpg**
**What it shows:** All detected contours drawn on original image (green lines)
**Purpose:** See what shapes the edge detection found

**What to look for:**
- ✅ **Good**: Large rectangular contour around the entire form
- ⚠️ **Bad**: No contour around form, or form broken into pieces

**How it's processed:**
- Edges dilated to connect broken lines
- RETR_EXTERNAL mode (only outer contours)
- Sorted by area (largest = form)

**Troubleshooting:**
- If no green rectangle around form → Perspective correction will fail
- If form split into multiple contours → Increase edge dilation
- If too many small contours → Check image quality

---

### 3. **debug_timing_marks.jpg** (if timing marks used)
**What it shows:** Detected timing marks with red rectangles and blue line
**Purpose:** Verify timing mark detection for perspective correction

**What to look for:**
- ✅ **Good**: Red rectangles on left-side timing marks, blue line vertical
- ⚠️ **Bad**: Missing marks, incorrect shapes detected, line not vertical

**Requirements:**
- Minimum 3 timing marks needed
- Must be vertically aligned (< 20px deviation)
- Regular spacing (spacing variance < 30%)

**Troubleshooting:**
- If marks not detected → Check left 15% of image is visible
- If wrong shapes detected → Adjust area filter (100-1000 pixels)
- If line tilted > 15° → Form too skewed, may fail correction

---

### 4. **debug_warped.jpg**
**What it shows:** Form after perspective correction
**Purpose:** Verify that form was straightened correctly

**What to look for:**
- ✅ **Good**: Form appears flat, rectangular, no distortion
- ⚠️ **Bad**: Still skewed, curved, or parts cut off

**Process:**
- Uses 4-corner detection or timing mark-based alignment
- Applies perspective transform with A4 ratio (1:1.41)
- White padding if needed

**Troubleshooting:**
- If still skewed → Check debug_corners or debug_timing_marks
- If parts missing → Original image doesn't show full form
- If distorted → Perspective calculation failed, check corners

---

### 5. **debug_preprocessed.jpg**
**What it shows:** Image after OMR preprocessing pipeline
**Purpose:** Verify preprocessing enhances bubble contrast

**What to look for:**
- ✅ **Good**: Bubbles clearly visible as dark/light regions, high contrast
- ⚠️ **Bad**: Low contrast, bubbles not distinct from background

**Pipeline:**
1. CLAHE (contrast enhancement)
2. Bilateral filter (noise reduction, edge preservation)
3. GaussianBlur (7×7)
4. Adaptive threshold (11×11 window)

**Troubleshooting:**
- If bubbles too faint → Lighting too dark, increase exposure
- If too noisy → Image quality poor, rescan at higher resolution
- If bubbles invisible → Check if marks are actually there!

---

### 6. **debug_morphed.jpg**
**What it shows:** After morphological operations (closing)
**Purpose:** See bubble gaps filled, contours cleaned

**What to look for:**
- ✅ **Good**: Bubbles appear as solid white regions
- ⚠️ **Bad**: Bubbles broken, gaps not closed

**Operations:**
- ELLIPSE kernel (5×5)
- MORPH_CLOSE operation
- 2 iterations

**Troubleshooting:**
- If bubbles still broken → Increase kernel size or iterations
- If bubbles merged → Decrease kernel size
- If text detected as bubbles → Check filtering parameters

---

### 7. **debug_bubbles.jpg**
**What it shows:** All detected bubbles with green rectangles
**Purpose:** Verify bubble detection and filtering

**What to look for:**
- ✅ **Good**: Green rectangles on all answer bubbles, no false detections
- ⚠️ **Bad**: Missing bubbles, or rectangles on text/dust

**Filtering criteria:**
- Area: 100-2000 pixels
- Aspect ratio: 0.5-2.0
- Circularity: > 0.5
- Solidity: > 0.7

**Count validation:**
- Console shows: "X bubbles detected"
- Compare with expected (questions × options)

**Troubleshooting:**
- If missing bubbles → Loosen filters (lower circularity/solidity)
- If too many detections → Tighten filters (increase thresholds)
- If no bubbles → Check debug_preprocessed and debug_morphed

---

### 8. **debug_rows.jpg**
**What it shows:** Bubbles grouped by row, color-coded with row numbers
**Purpose:** Verify row grouping algorithm

**What to look for:**
- ✅ **Good**: Each question row has distinct color, proper left-to-right order
- ⚠️ **Bad**: Bubbles from different rows same color, or wrong grouping

**Algorithm:**
1. Sort by Y-coordinate (top to bottom)
2. Group with tolerance ±20 pixels
3. Sort each row by X-coordinate (left to right)

**Colors cycle:** Red → Green → Blue → Yellow → Magenta

**Troubleshooting:**
- If rows mixed → Increase tolerance (e.g., 25-30 pixels)
- If one row split → Decrease tolerance (e.g., 15 pixels)
- If column order wrong → Check X-coordinates, may need preprocessing

---

## 📁 File Locations

All debug images are saved in the **current working directory** where the backend is running:

```
C:\Users\can\optic-form-reader-2\
├── debug_edges.jpg
├── debug_contours.jpg
├── debug_timing_marks.jpg (if applicable)
├── debug_warped.jpg
├── debug_preprocessed.jpg
├── debug_morphed.jpg
├── debug_bubbles.jpg
└── debug_rows.jpg
```

---

## 🔍 Diagnostic Workflow

### Step 1: Check Edge Detection
1. Open `debug_edges.jpg`
2. Verify form boundaries visible
3. If not → **Image quality issue**

### Step 2: Check Contour Detection
1. Open `debug_contours.jpg`
2. Look for green rectangle around form
3. If not → **Perspective correction will fail**

### Step 3: Check Perspective Correction
1. Open `debug_warped.jpg`
2. Verify form is straightened
3. If not → **Check timing marks or corners**

### Step 4: Check Preprocessing
1. Open `debug_preprocessed.jpg`
2. Verify high contrast bubbles
3. If not → **Lighting or quality issue**

### Step 5: Check Bubble Detection
1. Open `debug_bubbles.jpg`
2. Count green rectangles
3. Compare with expected count in console
4. If mismatch → **Adjust filtering**

### Step 6: Check Row Grouping
1. Open `debug_rows.jpg`
2. Verify each row has distinct color
3. Check bubbles ordered left-to-right
4. If wrong → **Adjust tolerance**

---

## 🐛 Common Issues & Solutions

### Issue 1: No debug images created
**Cause:** Code not executing or crashing before save
**Solution:** Check terminal for errors, verify file write permissions

### Issue 2: debug_edges.jpg is all black
**Cause:** No edges detected
**Solution:** 
- Check image is loaded correctly
- Verify image has content (not corrupted)
- Try lowering Canny threshold

### Issue 3: debug_contours.jpg has no green lines
**Cause:** No contours found
**Solution:**
- Check debug_edges.jpg first
- Increase edge dilation
- Lower minimum area threshold

### Issue 4: debug_warped.jpg is blank or distorted
**Cause:** Perspective transform failed
**Solution:**
- Check debug_contours.jpg for rectangle
- Verify 4 corners detected
- Check timing marks if using that method

### Issue 5: debug_bubbles.jpg shows very few rectangles
**Cause:** Filtering too strict
**Solution:**
- Lower circularity threshold (0.5 → 0.4)
- Lower solidity threshold (0.7 → 0.6)
- Increase area range (100-2000 → 80-2500)

### Issue 6: debug_bubbles.jpg shows too many rectangles
**Cause:** Filtering too loose
**Solution:**
- Increase circularity threshold (0.5 → 0.6)
- Increase solidity threshold (0.7 → 0.75)
- Decrease area range (100-2000 → 150-1500)

### Issue 7: debug_rows.jpg shows mixed colors per row
**Cause:** Row grouping tolerance too small
**Solution:**
- Increase tolerance in `group_bubbles_by_row()`: 20 → 25 or 30

---

## 💡 Pro Tips

### Tip 1: Sequential Viewing
Always check images in this order:
1. edges → 2. contours → 3. warped → 4. preprocessed → 5. bubbles → 6. rows

Each step depends on the previous one.

### Tip 2: Compare with Original
Keep the original uploaded image open to compare:
- Are bubbles actually visible?
- Is the form in frame?
- Is lighting adequate?

### Tip 3: Use Image Viewer Zoom
Zoom in on debug images to see fine details:
- Are bubbles solid or broken?
- Are edges continuous?
- Are spacing uniform?

### Tip 4: Save Good Examples
When you get perfect detection:
1. Save the debug images
2. Note the parameters used
3. Use as reference for future tuning

### Tip 5: Batch Testing
Test with multiple forms:
- Save debug images for each
- Compare patterns across failures
- Identify systematic issues

---

## 📊 Console Output Correlation

Debug images are generated alongside console output. Match them:

```
💾 Saved: debug_edges.jpg
💾 Saved: debug_contours.jpg
💾 Saved: debug_timing_marks.jpg
📐 Form köşeleri bulundu (timing mark bazlı)
💾 Saved: debug_warped.jpg
✅ Perspektif düzeltildi: 2100x2970
💾 Saved: debug_preprocessed.jpg
💾 Saved: debug_morphed.jpg
💾 Saved: debug_bubbles.jpg (85 bubbles detected)
📊 Bubble Grouping Summary:
   Total bubbles: 85
   Rows detected: 20
💾 Saved: debug_rows.jpg (rows color-coded)
```

Each `💾 Saved:` message tells you which debug image was created.

---

## 🚀 Using Debug Images for Bug Reports

When reporting issues, include:
1. ✅ All debug images (zip them)
2. ✅ Console output
3. ✅ Original uploaded image
4. ✅ Expected vs actual results

This gives complete visibility into the pipeline!

---

## 🔧 Disabling Debug Output

If you want to disable debug image saving (for production):

Comment out the `cv2.imwrite()` and `print()` lines in:
- `detect_form_corners()` - lines for edges/contours
- `apply_perspective_transform()` - line for warped
- `detect_answers()` - lines for preprocessed/bubbles/rows
- `find_form_contours()` - line for morphed
- `detect_form_corners_with_timing_marks()` - line for timing marks

Or add a `debug=False` parameter to control it globally.

---

## ✅ Success Criteria

You know detection is working when:
- ✅ debug_edges.jpg shows clear form boundaries
- ✅ debug_contours.jpg has green rectangle around form
- ✅ debug_warped.jpg shows flat, rectangular form
- ✅ debug_preprocessed.jpg has high-contrast bubbles
- ✅ debug_bubbles.jpg shows exactly expected bubble count
- ✅ debug_rows.jpg shows proper color grouping
- ✅ Console shows "✅ Perfect match!" for bubble count

When all these pass, your OMR detection is working correctly!
