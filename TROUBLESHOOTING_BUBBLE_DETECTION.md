# Bubble Detection Troubleshooting Guide

Quick reference for diagnosing and fixing bubble detection issues.

---

## 🔍 Reading the Debug Output

### Example Output
```
🔍 Bubble Count Validation:
   Expected: 100 bubbles (20 questions × 5 options)
   Detected: 95 bubbles
   ⚠️  WARNING: Detected fewer bubbles than expected!
   Missing: 5 bubbles

📊 Bubble Grouping Summary:
   Total bubbles: 95
   Rows detected: 19
   Row 1: 5 bubbles (Y avg: 245.3)
   Row 2: 5 bubbles (Y avg: 298.7)
   Row 15: 4 bubbles (Y avg: 1205.8)
   Row 16: 5 bubbles (Y avg: 1258.1)

⚠️  Row Count Mismatch:
   Expected rows: 20
   Detected rows: 19

⚠️  Question 15: Expected 5 options, found 4
```

---

## 🛠️ Common Issues & Solutions

### Issue 1: "Detected fewer bubbles than expected"
**Symptoms:** Missing X bubbles
**Possible Causes:**
- Poor image quality (blur, low contrast)
- Bubbles too small/large for area filter
- Occlusion (paper fold, shadow)
- Broken bubble outlines (poor print quality)

**Solutions:**
1. Check image quality - rescan if blurry
2. Adjust area range: `min_bubble_area` / `max_bubble_area`
3. Lower circularity threshold: `0.5 → 0.4`
4. Check CLAHE/preprocessing parameters

---

### Issue 2: "Detected more bubbles than expected"
**Symptoms:** Extra X bubbles
**Possible Causes:**
- Dust, smudges, or stray marks
- Text fragments detected as bubbles
- Loose filtering parameters

**Solutions:**
1. Increase minimum area: `100 → 150`
2. Increase circularity threshold: `0.5 → 0.6`
3. Check form for stray marks
4. Improve solidity filter: `0.7 → 0.75`

---

### Issue 3: "Row Count Mismatch"
**Symptoms:** Detected rows ≠ Expected rows
**Possible Causes:**
- Bubbles grouped into wrong rows
- Y-coordinate tolerance too strict/loose
- Severe form rotation

**Solutions:**
1. Check "Y avg" values in grouping summary
2. Adjust tolerance: `tolerance=20` → `tolerance=25` or `30`
3. Ensure perspective correction is working (check timing marks)
4. Look for large gaps in Y-coordinates

---

### Issue 4: "Expected 5 options, found 4"
**Symptoms:** Specific question missing bubble(s)
**Possible Causes:**
- Local occlusion or damage
- Bubble not meeting filter criteria
- Misalignment in that specific row

**Solutions:**
1. Visually inspect that question on the form
2. Check if bubble is visible but faint
3. Temporarily lower filtering thresholds for testing
4. Check for partial bubble outlines

---

### Issue 5: "Multiple marks detected"
**Symptoms:** `Question X: Multiple marks: A, C`
**Possible Causes:**
- Student actually marked multiple options
- Stray mark near correct answer
- Eraser residue

**Solutions:**
1. Visually verify the form
2. Adjust fill threshold if eraser marks detected: `0.65 → 0.70`
3. Check for smudges around bubbles
4. This is often a **valid detection** (student error)

---

## 📊 Parameter Tuning Guide

### When to Adjust Each Parameter

| Parameter | Default | Increase If... | Decrease If... |
|-----------|---------|---------------|----------------|
| **tolerance** | 20px | Rows splitting incorrectly | Bubbles from different rows grouping together |
| **min_bubble_area** | 100px | Too many false positives (dust) | Missing small bubbles |
| **max_bubble_area** | 2000px | Large bubbles rejected | Text/headers detected as bubbles |
| **circularity** | 0.5 | Irregular shapes passing | Regular bubbles rejected |
| **solidity** | 0.7 | Hollow shapes passing | Solid bubbles rejected |
| **fill_threshold** | 0.65 | Light marks detected | Heavy marks missed |

---

## 🧪 Testing Workflow

### Step 1: Initial Test
```python
# Use default parameters first
reader = AdvancedFormReader()
result = reader.read_form('test_form.jpg', 'lgs_20_20')
```

### Step 2: Review Output
- Check all ⚠️ warnings
- Note bubble count deviation
- Identify problematic questions

### Step 3: Diagnose
```
Missing bubbles → Filtering too strict → Lower thresholds
Extra bubbles → Filtering too loose → Raise thresholds
Row mismatch → Grouping issue → Adjust tolerance
```

### Step 4: Adjust & Retest
```python
# Example: Loosen filtering
reader.min_bubble_area = 80  # was 100
reader.circularity_threshold = 0.45  # was 0.5
```

### Step 5: Validate
- Bubble count should match exactly
- Row count should match questions
- Each row should have correct option count

---

## 🎯 Quick Checks

### Before Blaming the Algorithm
1. ✅ Is the image sharp and well-lit?
2. ✅ Are timing marks visible?
3. ✅ Is perspective correction working?
4. ✅ Are bubbles clearly printed?
5. ✅ Is the form type correct? (lgs_20_20 vs simple)

### Red Flags
- 🚩 Missing > 10% of bubbles → **Image quality issue**
- 🚩 Extra > 20% bubbles → **Filtering issue**
- 🚩 Row count off by > 2 → **Tolerance/alignment issue**
- 🚩 Every question has wrong count → **Template mismatch**

---

## 📞 Diagnostic Commands

### Print Current Parameters
```python
print(f"Area: {reader.min_bubble_area} - {reader.max_bubble_area}")
print(f"Aspect: {reader.aspect_ratio_range}")
print(f"Circularity: {reader.circularity_threshold}")
print(f"Solidity: {reader.solidity_threshold}")
print(f"Fill: {reader.filled_threshold}")
```

### Visualize Detected Bubbles
```python
# This will draw all detected bubbles on the image
cv2.drawContours(image, filtered_contours, -1, (0, 255, 0), 2)
cv2.imwrite('debug_bubbles.jpg', image)
```

### Check Timing Marks
```python
# Use the built-in visualization
visualized = reader.visualize_timing_marks(image_path)
cv2.imwrite('debug_timing_marks.jpg', visualized)
```

---

## 💡 Pro Tips

### Tip 1: Start with Perfect Test Form
Always test with a high-quality scan first to verify algorithm works correctly.

### Tip 2: Incremental Tuning
Change ONE parameter at a time and observe the effect.

### Tip 3: Document Your Changes
Keep notes on which parameters work best for your specific forms.

### Tip 4: Version Your Configurations
```python
# Create configuration presets
CONFIG_STRICT = {
    'min_area': 150,
    'max_area': 1500,
    'circularity': 0.6,
    'solidity': 0.75
}

CONFIG_LOOSE = {
    'min_area': 80,
    'max_area': 2500,
    'circularity': 0.4,
    'solidity': 0.65
}
```

### Tip 5: Use Validation Output
The validation messages tell you EXACTLY what's wrong:
- "Missing X bubbles" → Filtering too strict
- "Extra X bubbles" → Filtering too loose
- "Row count mismatch" → Tolerance issue
- "Expected 5, found 4" → Localized problem

---

## 🔬 Advanced Debugging

### Enable OpenCV Window Display
```python
# Show intermediate processing steps
cv2.imshow('Preprocessed', processed)
cv2.imshow('Contours', debug_image)
cv2.waitKey(0)
```

### Print Bubble Coordinates
```python
for i, bubble in enumerate(bubbles):
    print(f"Bubble {i}: x={bubble['x']}, y={bubble['y']}, "
          f"w={bubble['w']}, h={bubble['h']}, area={bubble['area']}")
```

### Save Debug Images
```python
cv2.imwrite('1_original.jpg', original)
cv2.imwrite('2_preprocessed.jpg', preprocessed)
cv2.imwrite('3_contours.jpg', contours_image)
cv2.imwrite('4_filtered.jpg', filtered_image)
cv2.imwrite('5_grouped.jpg', grouped_image)
```

---

## 📋 Checklist for Perfect Detection

- [ ] Bubble count matches exactly
- [ ] Row count matches question count
- [ ] Each row has correct option count
- [ ] No warnings in validation output
- [ ] Timing marks detected correctly
- [ ] Perspective correction applied
- [ ] No false positives (dust detected)
- [ ] No false negatives (bubbles missed)

---

## 🆘 Still Having Issues?

1. **Check the comprehensive documentation**: `BUBBLE_DETECTION_REVIEW.md`
2. **Review the changes**: `BUBBLE_DETECTION_CHANGES.md`
3. **Verify preprocessing**: `OMR_OPTIMIZASYONLARI.md`
4. **Check timing marks**: `TIMING_MARK_SISTEM.md`

If all else fails, the issue may be:
- Form template not matching actual form
- Image resolution too low (< 600 DPI)
- Severe physical damage to form
- Incompatible form format
