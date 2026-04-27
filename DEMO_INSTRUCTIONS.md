# Demo Walkthrough Instructions

You need to create a demo showing your system running end-to-end. Choose **ONE** of these methods:

---

## Option 1: Loom Video (RECOMMENDED - Takes 5-10 minutes)

### Why Loom?
- **Free** and easy to use
- Records your screen + optional webcam/audio
- Automatically uploads and gives you a shareable link
- Professors prefer video demos because they can see the system actually working

### Steps:

1. **Sign up for Loom** (free):
   - Go to [loom.com](https://www.loom.com/)
   - Create a free account (can use your ASU email)

2. **Install Loom desktop app or Chrome extension**:
   - Desktop: Download from loom.com
   - Chrome: Install from Chrome Web Store

3. **Prepare your demo** (before recording):
   ```bash
   # Make sure your environment is activated
   .venv\Scripts\activate
   
   # Start Streamlit
   streamlit run streamlit_app.py
   ```

4. **Recording Checklist** (2-3 minutes total):
   
   **[0:00-0:15] Introduction (15 seconds)**
   - Say: "This is my Social Music Recommender system"
   - Briefly explain what it does
   
   **[0:15-1:00] Existing User Demo (45 seconds)**
   - Select "Existing user" view in sidebar
   - Choose "Ava (u1)" 
   - Show her profile (preferred genres: pop, edm)
   - Point out the top 3 recommendations
   - Highlight the confidence scores
   - Show one explanation ("Why it appeared")
   
   **[1:00-1:45] New User Onboarding Demo (45 seconds)**
   - Select "New user onboarding" view
   - Choose "Zara (u9)"
   - Show the 4-step onboarding walkthrough
   - Point out "cold-start mode" in the recommendations
   - Show how social signals help with limited history
   
   **[1:45-2:15] Comparison View (30 seconds)**
   - Select "Compare both" view
   - Show side-by-side differences
   - Point out different recommendation strategies
   
   **[2:15-2:30] Reliability Checks (15 seconds)**
   - Scroll to bottom
   - Show "Checks Passed: 4 / 4"
   - Briefly mention what each check validates
   
   **[2:30-2:45] Wrap-up (15 seconds)**
   - Say: "This demonstrates my reliability-focused AI system"
   - (Optional) Show pytest tests passing

5. **After Recording**:
   - Click "Share" button in Loom
   - Copy the public link
   - Paste it in your README.md:
     ```markdown
     🎥 **Watch the system in action:** [Loom Demo Video](https://www.loom.com/share/YOUR_ACTUAL_LINK)
     ```

6. **Test the link**:
   - Open it in an incognito/private browser window
   - Make sure it's publicly viewable (not restricted)

---

## Option 2: Screenshots + GIF (Alternative - Takes 15-20 minutes)

### Tools Needed:
- **Windows Snipping Tool** (for screenshots) - Built-in
- **ScreenToGif** (for animated GIF) - Free: https://www.screentogif.com/

### Steps:

1. **Run your Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Take Screenshots** (save to `assets/demo-screenshots/`):

   **Screenshot 1: Existing User View**
   - View: "Existing user"
   - User: "Ava (u1)"
   - Save as: `01-existing-user-ava.png`
   - Make sure to capture:
     - Profile card on left
     - Top 3 recommendations on right
     - Confidence scores visible

   **Screenshot 2: New User Onboarding**
   - View: "New user onboarding"
   - User: "Zara (u9)"
   - Save as: `02-new-user-zara-onboarding.png`
   - Capture:
     - 4-step onboarding walkthrough
     - Profile card
     - Recommendations showing "cold-start mode"

   **Screenshot 3: Comparison View**
   - View: "Compare both"
   - Save as: `03-comparison-view.png`
   - Show both users side-by-side

   **Screenshot 4: Reliability Checks**
   - Scroll to bottom
   - Save as: `04-reliability-checks.png`
   - Show "Checks Passed: 4 / 4"

3. **Create an Animated GIF** (Optional but impressive):
   - Open ScreenToGif
   - Click "Recorder"
   - Position the recording frame over your Streamlit window
   - Record yourself clicking through all 3 views (30-60 seconds)
   - Stop recording
   - Delete any frames where you're just navigating
   - Save as: `assets/demo-full-walkthrough.gif`

4. **Update README.md**:
   ```markdown
   ## Demo Walkthrough

   ### Full System Walkthrough
   ![Demo GIF](assets/demo-full-walkthrough.gif)

   ### Detailed Screenshots

   **Existing User Flow:**
   ![Existing User](assets/demo-screenshots/01-existing-user-ava.png)

   **New User Onboarding:**
   ![New User Onboarding](assets/demo-screenshots/02-new-user-zara-onboarding.png)

   **Comparison View:**
   ![Comparison](assets/demo-screenshots/03-comparison-view.png)

   **Reliability Checks:**
   ![Reliability](assets/demo-screenshots/04-reliability-checks.png)
   ```

---

## Quick Comparison

| Method | Time | Pros | Cons |
|--------|------|------|------|
| **Loom Video** | 5-10 min | ✅ Easy<br>✅ Shows real interaction<br>✅ Can add narration | ❌ Requires sign-up |
| **Screenshots + GIF** | 15-20 min | ✅ No account needed<br>✅ Loads faster | ❌ More manual work<br>❌ Less dynamic |

---

## After You're Done

1. **Update README.md** with your demo link/screenshots
2. **Delete this file** (`DEMO_INSTRUCTIONS.md`) - it's just for you
3. **Test your demo** by viewing it as if you were the grader
4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add demo walkthrough with Loom video"
   git push
   ```

---

## Troubleshooting

**Q: Streamlit won't start**
```bash
# Activate environment first
.venv\Scripts\activate
# Then run
streamlit run streamlit_app.py
```

**Q: My Loom link says "Private video"**
- Go to Loom → Video Settings → Privacy → Set to "Anyone with the link"

**Q: Screenshots are too large**
- Use Windows Snipping Tool → Save as PNG
- Or use an online compressor: tinypng.com

**Q: Should I show my face in the Loom video?**
- Optional! Webcam is not required. Screen recording is enough.

**Q: Can I use both methods?**
- Yes! But **one is required** for full credit.

---

## Final Checklist

Before submitting, verify:
- [ ] Demo shows at least 2-3 different user inputs/scenarios
- [ ] Demo shows the AI system actually running (not just code)
- [ ] Demo shows the reliability checks passing
- [ ] Link/screenshots are embedded in README.md
- [ ] Link is publicly accessible (test in incognito mode)
- [ ] Total demo length is 2-4 minutes (if video)

---

Good luck! This should take less than 10 minutes with Loom. 🎥
