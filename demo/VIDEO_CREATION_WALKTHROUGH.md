# Video Creation Walkthrough - Step by Step

**Complete guide for creating your demo video from start to finish**

---

## 📋 Overview

This guide walks you through the entire video creation process in order:
1. **Preparation** (30 minutes)
2. **Recording** (1-2 hours)
3. **Editing** (2-3 hours)
4. **Upload & Verification** (30 minutes)

**Total Time**: 4-6 hours

---

## Phase 1: Preparation (30 minutes)

### Step 1.1: Install Recording Software

**Option A: OBS Studio (Recommended - Free)**

1. Download from https://obsproject.com/
2. Run installer (OBSStudio-XX.X.X-Full-Installer-x64.exe)
3. Follow installation wizard
4. Launch OBS Studio

**Initial OBS Setup**:
```
1. First launch: Auto-Configuration Wizard appears
2. Select "Optimize for recording"
3. Base Resolution: 1920x1080
4. FPS: 30
5. Click "Next" → "Apply Settings"
```

**Configure OBS for Screen Recording**:
```
1. In "Sources" panel, click "+"
2. Select "Display Capture"
3. Name it "Screen"
4. Click OK → Select your monitor → OK
5. In "Sources" panel, click "+" again
6. Select "Audio Input Capture"
7. Name it "Microphone"
8. Select your microphone → OK
```

**Test Recording**:
```
1. Click "Start Recording" button
2. Speak: "Testing 1, 2, 3"
3. Click "Stop Recording"
4. Click "File" → "Show Recordings"
5. Play the video to verify audio and video quality
```

**Option B: Windows Game Bar (Built-in - Quick)**

1. Press `Win + G` to open Game Bar
2. Click "Yes, this is a game" if prompted
3. Click the record button (circle icon)
4. Test recording and playback

**Option C: Loom (Easy - Web-based)**

1. Go to https://www.loom.com/
2. Sign up for free account
3. Install desktop app or browser extension
4. Test recording with their interface

### Step 1.2: Test Your Application

**Before recording, verify everything works**:

1. **Start your frontend**:
   ```cmd
   cd document-policy-processor\frontend
   streamlit run app.py
   ```

2. **Open browser** to http://localhost:8501

3. **Test complete flow**:
   - Upload `demo/sample_documents/sample_medical_report.txt`
   - Enter symptoms: "Diagnosed with Type 2 diabetes, requiring insulin therapy and regular monitoring"
   - Click "Process Document"
   - Verify results appear correctly

4. **If anything fails**:
   - Check backend is running
   - Check API Gateway URL is correct
   - Check AWS credentials are configured
   - Review error messages

### Step 1.3: Prepare Your Environment

**Clean up your desktop**:
- [ ] Close all unnecessary applications
- [ ] Close extra browser tabs
- [ ] Clear browser history/cache
- [ ] Disable notifications (Windows: Settings → System → Notifications)
- [ ] Set "Do Not Disturb" mode

**Prepare browser**:
- [ ] Set zoom to 125% for better readability
- [ ] Bookmark your application URL
- [ ] Have sample document ready in Downloads folder
- [ ] Clear any autofill data that might show personal info

**Prepare recording area**:
- [ ] Good lighting (if showing face)
- [ ] Quiet environment
- [ ] Microphone positioned correctly
- [ ] Test audio levels

### Step 1.4: Practice the Script

1. Open `DEMO_SCRIPT.md`
2. Read through entire script 2-3 times
3. Practice with timer - aim for 2:50 (leaves 10s buffer)
4. Practice mouse movements and clicks
5. Identify any tongue-twisters or difficult sections

**Practice Tips**:
- Speak at moderate pace (not too fast)
- Pause briefly between sections
- Emphasize key points (AI-powered, AWS services)
- Smile when speaking (it shows in your voice)

---

## Phase 2: Recording (1-2 hours)

### Step 2.1: Set Up Recording Session

**OBS Studio Setup**:
```
1. Launch OBS Studio
2. Check audio levels (speak normally, green bars should peak at -12dB)
3. If too quiet: Right-click "Microphone" → Filters → Add "Gain"
4. Position recording window to capture full screen
5. Close OBS preview to reduce CPU usage during recording
```

**Browser Setup**:
```
1. Open browser in fullscreen (F11)
2. Navigate to your application
3. Have sample document ready
4. Have script visible on second monitor or printed
```

### Step 2.2: Record Introduction (0:00-0:20)

**What to record**: Title slide with narration

**Option A: Create title slide in PowerPoint**:
```
1. Open PowerPoint
2. Create slide with:
   - Title: "Document Policy Processor"
   - Subtitle: "AI-Powered Insurance Policy Analysis"
   - Footer: "Built for AWS AI for Bharat Hackathon"
3. Add AWS logo (optional)
4. Set to fullscreen (F5)
```

**Option B: Use browser with HTML**:
Create simple HTML file:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        h1 { font-size: 48px; margin: 20px; }
        h2 { font-size: 32px; margin: 20px; }
        p { font-size: 24px; margin: 20px; }
    </style>
</head>
<body>
    <div>
        <h1>Document Policy Processor</h1>
        <h2>AI-Powered Insurance Policy Analysis</h2>
        <p>Built for AWS AI for Bharat Hackathon</p>
    </div>
</body>
</html>
```

**Recording**:
```
1. Display title slide
2. Start OBS recording
3. Wait 2 seconds (buffer)
4. Speak introduction script (see DEMO_SCRIPT.md)
5. Wait 2 seconds
6. Stop recording
7. Save as "01-introduction.mp4"
```

### Step 2.3: Record Document Upload (0:20-0:50)

**What to record**: Application interface with document upload

**Recording**:
```
1. Open your application in browser
2. Start OBS recording
3. Wait 2 seconds
4. Speak: "Let's see it in action..."
5. Click "Browse files" button (slowly)
6. Select sample_medical_report.txt
7. Type symptoms (slowly, clearly visible)
8. Speak: "Now I'll click Process Document"
9. Click "Process Document" button
10. Wait for processing indicator to appear
11. Wait 2 seconds
12. Stop recording
13. Save as "02-upload.mp4"
```

**Tips**:
- Move mouse slowly and deliberately
- Pause briefly after each action
- Ensure text is readable on screen
- If you make a mistake, just start over

### Step 2.4: Record Processing Explanation (0:50-1:20)

**What to record**: Processing screen with narration

**Option A: Record processing screen**:
```
1. Show processing spinner/progress bar
2. Start recording
3. Narrate the processing explanation
4. Stop recording
5. Save as "03-processing.mp4"
```

**Option B: Use architecture diagram**:
```
1. Open architecture diagram image
2. Display fullscreen
3. Start recording
4. Narrate while highlighting different parts
5. Stop recording
6. Save as "03-processing.mp4"
```

**Narration Script**:
> "Behind the scenes, AWS Textract extracts text from the document using OCR. Then, a sentence-transformer model generates semantic embeddings - that's a numerical representation of the meaning. These embeddings are matched against our policy database using cosine similarity. Finally, GPT-3.5 validates each match and checks for exclusions, ensuring accuracy."

### Step 2.5: Record Results Display (1:20-2:20)

**What to record**: Results page with detailed walkthrough

**This is the most important section - take your time!**

**Recording**:
```
1. Wait for results to load completely
2. Start recording
3. Wait 2 seconds
4. Speak: "And here are the results!"
5. Scroll slowly through recommendations
6. Pause on first recommendation
7. Highlight confidence score (use mouse)
8. Speak about first recommendation
9. Scroll to second recommendation
10. Highlight exclusion warning
11. Speak about second recommendation
12. Speak final summary
13. Wait 2 seconds
14. Stop recording
15. Save as "04-results.mp4"
```

**Full Narration** (see DEMO_SCRIPT.md for complete text):
- Introduce results
- Explain first recommendation (94% confidence)
- Explain second recommendation (exclusions)
- Summarize value proposition

**Tips**:
- Scroll very slowly
- Pause on important information
- Use mouse cursor to highlight key text
- Ensure all text is readable

### Step 2.6: Record AWS Services Section (2:20-2:50)

**What to record**: Architecture diagram or AWS console

**Option A: Architecture diagram**:
```
1. Open architecture diagram
2. Display fullscreen
3. Start recording
4. Narrate AWS services used
5. Stop recording
6. Save as "05-aws-services.mp4"
```

**Option B: AWS Console**:
```
1. Open AWS Console
2. Show Lambda functions, S3 buckets, etc.
3. Start recording
4. Narrate while showing services
5. Stop recording
6. Save as "05-aws-services.mp4"
```

### Step 2.7: Record Conclusion (2:50-3:00)

**What to record**: Closing slide with links

**Create closing slide** (similar to title slide):
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        h1 { font-size: 48px; margin: 20px; }
        p { font-size: 28px; margin: 15px; }
        .links { font-size: 24px; margin: 30px; }
    </style>
</head>
<body>
    <div>
        <h1>Document Policy Processor</h1>
        <div class="links">
            <p>GitHub: github.com/yourusername/document-policy-processor</p>
            <p>Live Demo: your-demo-url.com</p>
        </div>
        <p>Thank you!</p>
    </div>
</body>
</html>
```

**Recording**:
```
1. Display closing slide
2. Start recording
3. Wait 2 seconds
4. Speak conclusion
5. Wait 3 seconds (let viewers read links)
6. Stop recording
7. Save as "06-conclusion.mp4"
```

### Step 2.8: Review All Recordings

**Check each recording**:
- [ ] Audio is clear and audible
- [ ] Video is smooth (no lag)
- [ ] Text is readable
- [ ] No personal information visible
- [ ] No errors or mistakes
- [ ] Timing is appropriate

**If any recording has issues, re-record that section**

---

## Phase 3: Editing (2-3 hours)

### Step 3.1: Install Editing Software

**Option A: DaVinci Resolve (Recommended - Free)**

1. Download from https://www.blackmagicdesign.com/products/davinciresolve
2. Choose "DaVinci Resolve" (free version)
3. Fill out form and download
4. Install (requires ~3GB space)
5. Launch DaVinci Resolve

**Option B: Windows Video Editor (Built-in)**

1. Press `Win` key
2. Type "Video Editor"
3. Open "Video Editor" app
4. Click "New video project"

**Option C: Kapwing (Web-based - No install)**

1. Go to https://www.kapwing.com/
2. Sign up for free account
3. Click "Start editing"

### Step 3.2: Import Recordings (DaVinci Resolve)

**Create new project**:
```
1. Launch DaVinci Resolve
2. Click "New Project"
3. Name it "Document Policy Processor Demo"
4. Click "Create"
```

**Import clips**:
```
1. Click "Media" tab at bottom
2. Click "Import Media" button
3. Select all your recorded clips:
   - 01-introduction.mp4
   - 02-upload.mp4
   - 03-processing.mp4
   - 04-results.mp4
   - 05-aws-services.mp4
   - 06-conclusion.mp4
4. Click "Open"
```

### Step 3.3: Arrange Clips on Timeline

**Switch to Edit tab**:
```
1. Click "Edit" tab at bottom
2. Drag clips from Media Pool to timeline in order:
   - 01-introduction.mp4
   - 02-upload.mp4
   - 03-processing.mp4
   - 04-results.mp4
   - 05-aws-services.mp4
   - 06-conclusion.mp4
```

**Trim clips**:
```
1. Click on a clip in timeline
2. Drag edges to trim dead space at start/end
3. Remove any mistakes or long pauses
4. Ensure smooth transitions between clips
```

### Step 3.4: Add Text Overlays (Optional)

**Add text for key points**:
```
1. Click "Effects Library" (top left)
2. Search for "Text"
3. Drag "Text" effect to timeline above video
4. In Inspector panel (top right):
   - Type your text (e.g., "AWS Textract → OCR")
   - Adjust font size, color, position
   - Set duration to match narration
5. Repeat for other key points:
   - "94% Confidence"
   - "No Exclusions Found"
   - "Proceed with Claim"
```

### Step 3.5: Adjust Audio Levels

**Normalize audio**:
```
1. Click on each clip in timeline
2. In Inspector panel, find "Volume"
3. Adjust to consistent level (around -12dB)
4. If audio is too quiet, increase volume
5. If audio has background noise:
   - Right-click clip → "Fairlight" tab
   - Apply noise reduction filter
```

### Step 3.6: Add Transitions (Optional)

**Add smooth transitions**:
```
1. Click "Effects Library"
2. Search for "Cross Dissolve"
3. Drag between clips for smooth transitions
4. Keep transitions short (0.5-1 second)
5. Don't overuse - simple is better
```

### Step 3.7: Check Total Duration

**Verify timing**:
```
1. Play entire video from start
2. Check duration in timeline (should be ≤ 3:00)
3. If over 3 minutes:
   - Trim processing explanation
   - Shorten AWS services section
   - Remove any redundant content
4. If under 2:30:
   - Add more detail to results section
   - Slow down narration pace
```

### Step 3.8: Export Video

**Export settings (DaVinci Resolve)**:
```
1. Click "Deliver" tab at bottom
2. In "Render Settings":
   - Format: MP4
   - Codec: H.264
   - Resolution: 1920x1080
   - Frame Rate: 30 fps
   - Quality: High
3. In "Filename":
   - Name: "Document-Policy-Processor-Demo"
   - Location: Choose folder
4. Click "Add to Render Queue"
5. Click "Render All"
6. Wait for export to complete (5-15 minutes)
```

**Export settings (Windows Video Editor)**:
```
1. Click "Finish video"
2. Select "High 1080p"
3. Click "Export"
4. Choose location and filename
5. Wait for export
```

---

## Phase 4: Upload & Verification (30 minutes)

### Step 4.1: Create YouTube Account (if needed)

```
1. Go to https://www.youtube.com/
2. Click "Sign In"
3. Use Google account or create new one
4. Verify email address
```

### Step 4.2: Upload to YouTube

**Upload process**:
```
1. Go to https://studio.youtube.com/
2. Click "Create" button (camera icon)
3. Click "Upload videos"
4. Drag your exported video file
5. Wait for upload to complete
```

**Video details**:
```
Title:
Document Policy Processor - AI-Powered Insurance Policy Analysis

Description:
An AI-powered solution that helps users understand which insurance policies apply to their medical situation. Built entirely on AWS, it combines OCR, semantic matching, and large language models to provide instant, accurate policy recommendations.

🔗 GitHub: https://github.com/yourusername/document-policy-processor
🔗 Live Demo: https://your-demo-url.com

Built for AWS AI for Bharat Hackathon

AWS Services Used:
- AWS Lambda (Serverless compute)
- API Gateway (REST API)
- S3 (Document storage)
- DynamoDB (Policy database)
- Textract (OCR)
- CloudWatch (Monitoring)

Tags:
AWS, AI, Machine Learning, Hackathon, Insurance, Policy Analysis, OCR, NLP, Serverless, Lambda, Python
```

**Privacy settings**:
```
1. Select "Unlisted" (recommended for hackathon)
   - Unlisted: Only people with link can view
   - Public: Anyone can find and view
2. Click "Next"
```

**Video elements** (optional):
```
1. Skip "Add video elements"
2. Click "Next"
```

**Checks**:
```
1. Wait for processing to complete
2. YouTube will check for copyright issues
3. Click "Next"
```

**Visibility**:
```
1. Confirm "Unlisted" is selected
2. Click "Save"
```

### Step 4.3: Wait for Processing

**YouTube processing**:
```
- Upload completes immediately
- Processing takes 5-30 minutes
- HD quality (1080p) takes longer
- Check "Video details" page for status
```

**Processing stages**:
```
1. "Processing HD version" - Wait
2. "Checks complete" - Good!
3. "1080p available" - Ready!
```

### Step 4.4: Verify Video

**Test the video**:
```
1. Click "View on YouTube" button
2. Watch entire video
3. Check:
   - [ ] Video plays smoothly
   - [ ] Audio is clear
   - [ ] Duration is ≤ 3:00
   - [ ] All sections are present
   - [ ] No errors or glitches
```

**Test link in incognito**:
```
1. Copy video URL
2. Open incognito window (Ctrl+Shift+N)
3. Paste URL and press Enter
4. Verify video loads and plays
```

**Test on mobile**:
```
1. Open YouTube app on phone
2. Paste video URL
3. Verify video plays correctly
```

### Step 4.5: Save Video URL

**Copy the URL**:
```
1. In YouTube Studio, click "Copy link"
2. Save URL in a text file
3. Format: https://youtu.be/XXXXXXXXXXX
```

**Update your documentation**:
```
1. Add URL to README.md
2. Add URL to SUBMISSION.md
3. Test URL one more time
```

---

## 🎯 Quality Checklist

Before considering the video complete:

### Content
- [ ] Shows complete workflow (upload → process → results)
- [ ] Demonstrates AI-powered features
- [ ] Highlights all AWS services used
- [ ] Includes GitHub and demo links
- [ ] Duration is ≤ 3 minutes (180 seconds)

### Technical Quality
- [ ] Video resolution is 1080p
- [ ] Audio is clear and audible
- [ ] No background noise or echo
- [ ] Text on screen is readable
- [ ] No lag or stuttering

### Professional Polish
- [ ] Title slide at beginning
- [ ] Closing slide at end
- [ ] Smooth transitions between sections
- [ ] Consistent audio levels
- [ ] No personal information visible
- [ ] No errors or mistakes

### Accessibility
- [ ] Video link works in incognito mode
- [ ] Video link works on mobile
- [ ] Video plays without issues
- [ ] YouTube processing complete (1080p available)

---

## 🆘 Troubleshooting

### Recording Issues

**Problem**: Audio is too quiet
```
Solution:
1. In OBS: Right-click "Microphone" → Filters → Add "Gain"
2. Increase gain by +10dB
3. Test recording again
```

**Problem**: Video is laggy
```
Solution:
1. Close unnecessary applications
2. In OBS: Settings → Output → Recording Quality: "High Quality"
3. Reduce recording resolution to 720p if needed
```

**Problem**: Application is slow during recording
```
Solution:
1. Record in sections (not all at once)
2. Close OBS preview window
3. Restart application between recordings
```

### Editing Issues

**Problem**: DaVinci Resolve won't import video
```
Solution:
1. Check video format (should be MP4)
2. Try converting with VLC or HandBrake
3. Use Windows Video Editor as alternative
```

**Problem**: Export takes too long
```
Solution:
1. Lower export quality slightly
2. Close other applications
3. Be patient - 1080p export takes time
```

### Upload Issues

**Problem**: Upload fails or stalls
```
Solution:
1. Check internet connection
2. Try different browser
3. Compress video file if >2GB
4. Upload during off-peak hours
```

**Problem**: Video stuck processing
```
Solution:
1. Wait - HD processing can take 30+ minutes
2. Check YouTube Studio for status
3. If stuck >1 hour, re-upload
```

---

## 📝 Final Notes

**Time Management**:
- Don't rush - quality matters
- Take breaks between phases
- Record multiple takes if needed
- Get feedback before uploading

**Best Practices**:
- Save project files frequently
- Keep original recordings as backup
- Test everything before final upload
- Have a backup plan if something fails

**Remember**:
- The video represents your hard work
- Judges will watch many videos - make yours stand out
- Clear, professional presentation matters
- Show enthusiasm for your project!

---

**Good luck with your demo video! 🚀**

You've got this! Follow these steps carefully, and you'll create a professional, impressive demo that showcases your Document Policy Processor effectively.
