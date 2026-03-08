# Demo Video Recording Guide

This guide provides step-by-step instructions for recording a professional demo video for the Document Policy Processor.

---

## Table of Contents

1. [Pre-Recording Setup](#pre-recording-setup)
2. [Recording Software Options](#recording-software-options)
3. [Technical Setup](#technical-setup)
4. [Recording Process](#recording-process)
5. [Audio Recording](#audio-recording)
6. [Screen Recording Best Practices](#screen-recording-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Recording Setup

### 1. Environment Preparation

**Computer Setup**:
- [ ] Close all unnecessary applications
- [ ] Disable notifications (Windows: Focus Assist, Mac: Do Not Disturb)
- [ ] Clear desktop of sensitive/personal files
- [ ] Set desktop wallpaper to solid color or professional image
- [ ] Ensure battery is charged or plugged in
- [ ] Close email, Slack, and messaging apps

**Browser Setup**:
- [ ] Use Chrome or Firefox (most reliable)
- [ ] Clear browser cache and cookies
- [ ] Close all unnecessary tabs
- [ ] Disable browser extensions (especially ad blockers)
- [ ] Set zoom level to 100% or 125% for readability
- [ ] Bookmark the application URL for quick access
- [ ] Test the application works correctly

**Audio Setup**:
- [ ] Find a quiet room with minimal background noise
- [ ] Close windows to reduce outside noise
- [ ] Turn off fans, AC, or noisy appliances
- [ ] Silence your phone
- [ ] Test microphone levels
- [ ] Use headphones to monitor audio (optional)

### 2. Application Preparation

**Backend Verification**:
```bash
# Test API Gateway health endpoint
curl https://your-api-gateway-url.amazonaws.com/prod/api/health

# Expected response: {"status": "healthy"}
```

**Frontend Verification**:
- [ ] Navigate to your deployed frontend URL
- [ ] Verify page loads correctly
- [ ] Check that upload button works
- [ ] Verify no error messages appear
- [ ] Test with sample document (don't record yet)

**Data Preparation**:
- [ ] Have sample document ready on desktop
- [ ] Copy symptom description to clipboard or notepad
- [ ] Verify sample policies are in DynamoDB
- [ ] Confirm embeddings are in S3
- [ ] Test complete workflow once (don't record)

### 3. Script Preparation

- [ ] Print or display script on second monitor
- [ ] Practice reading script 2-3 times
- [ ] Time yourself (should be under 3 minutes)
- [ ] Mark breathing points and pauses
- [ ] Prepare backup phrases in case of mistakes
- [ ] Have water nearby (stay hydrated)

---

## Recording Software Options

### Option 1: OBS Studio (Free, Recommended)

**Pros**: Free, professional features, high quality, cross-platform
**Cons**: Requires setup and configuration

**Download**: https://obsproject.com/

**Setup Instructions**:
1. Download and install OBS Studio
2. Open OBS and create a new scene
3. Add source: "Display Capture" (for full screen) or "Window Capture" (for specific window)
4. Add audio source: Select your microphone
5. Go to Settings → Output:
   - Output Mode: Simple
   - Recording Quality: High Quality
   - Recording Format: MP4
6. Go to Settings → Video:
   - Base Resolution: 1920x1080
   - Output Resolution: 1920x1080
   - FPS: 30
7. Test recording with a short clip
8. Review test recording for quality

### Option 2: Loom (Easy, Web-Based)

**Pros**: Very easy to use, automatic upload, free tier available
**Cons**: Limited editing, requires internet, watermark on free tier

**Website**: https://www.loom.com/

**Setup Instructions**:
1. Sign up for free account
2. Install browser extension or desktop app
3. Click Loom icon to start recording
4. Select "Screen + Camera" or "Screen Only"
5. Choose full screen or specific window
6. Click "Start Recording"
7. Recording automatically uploads when done

### Option 3: Windows Game Bar (Windows Only)

**Pros**: Built-in, no installation, simple
**Cons**: Limited features, Windows only

**How to Use**:
1. Press `Windows + G` to open Game Bar
2. Click the record button (or press `Windows + Alt + R`)
3. Recording starts immediately
4. Press `Windows + Alt + R` again to stop
5. Video saved to Videos/Captures folder

### Option 4: QuickTime (Mac Only)

**Pros**: Built-in, simple, good quality
**Cons**: Mac only, limited features

**How to Use**:
1. Open QuickTime Player
2. File → New Screen Recording
3. Click record button
4. Choose full screen or drag to select area
5. Click "Start Recording"
6. Click stop button in menu bar when done

### Option 5: Camtasia (Paid, Professional)

**Pros**: Professional features, built-in editing, annotations
**Cons**: Expensive ($249), requires installation

**Website**: https://www.techsmith.com/video-editor.html

---

## Technical Setup

### Display Settings

**Resolution**:
- Record at 1920x1080 (1080p) minimum
- 2560x1440 (1440p) if you have a high-res display
- Never record below 1280x720 (720p)

**Browser Window**:
- Maximize browser window for recording
- Or set to specific size: 1600x900 for better text visibility
- Ensure all UI elements are visible
- Test that text is readable at recorded resolution

**Font Size**:
- Increase browser zoom to 125% if text is small
- Ensure all text is readable when recorded
- Test by recording a short clip and reviewing

### Audio Settings

**Microphone Selection**:
- Use external USB microphone if available (best quality)
- Laptop built-in microphone is acceptable
- Avoid using phone or earbuds microphone
- Test microphone before recording

**Audio Levels**:
- Speak at normal volume
- Microphone should capture at -12dB to -6dB (not too quiet, not clipping)
- Test recording and adjust input volume if needed
- Avoid background music (can be added in editing)

**Audio Quality Settings**:
- Sample Rate: 48kHz or 44.1kHz
- Bit Rate: 192kbps or higher
- Format: AAC or MP3

### Frame Rate

- **30 FPS**: Standard, recommended for most demos
- **60 FPS**: Smoother, but larger file size (optional)
- Avoid 24 FPS (too cinematic, not smooth enough)

---

## Recording Process

### Method 1: Single Take (Recommended for Beginners)

Record the entire demo in one continuous take.

**Steps**:
1. Start recording software
2. Wait 2 seconds (gives you buffer to edit)
3. Begin speaking and demonstrating
4. Follow script from start to finish
5. Wait 2 seconds at end
6. Stop recording

**Pros**: Simple, natural flow, less editing
**Cons**: Must redo entire video if you make a mistake

**Tips**:
- Practice 2-3 times before recording
- Don't worry about small mistakes (can be edited)
- Keep going even if you stumble on words
- Record 2-3 full takes and choose the best

### Method 2: Section-by-Section (Recommended for Quality)

Record each section separately and combine in editing.

**Sections**:
1. Introduction (title slide)
2. Document upload and input
3. Processing explanation
4. Results display
5. AWS services overview
6. Conclusion

**Steps for Each Section**:
1. Start recording
2. Record just that section
3. Stop recording
4. Review the clip
5. Re-record if needed
6. Move to next section

**Pros**: Easier to get perfect takes, more control
**Cons**: Requires video editing to combine

### Method 3: Separate Audio and Video

Record screen video and voiceover separately, then combine.

**Steps**:
1. Record screen actions without speaking
2. Record voiceover separately while watching video
3. Combine in video editor

**Pros**: Perfect audio, can adjust timing
**Cons**: Requires more editing skill, audio may not sync perfectly

---

## Audio Recording

### Recording Your Voiceover

**Preparation**:
- Sit up straight (improves voice quality)
- Stay 6-8 inches from microphone
- Speak clearly and at moderate pace
- Smile while speaking (makes voice sound friendlier)
- Take a deep breath before starting

**Delivery Tips**:
- Speak with enthusiasm but stay professional
- Vary your tone (avoid monotone)
- Pause briefly between sentences
- Emphasize key words: "AI-powered", "AWS", "instant"
- Don't rush - judges need to understand

**Common Mistakes**:
- ❌ Speaking too fast (slow down!)
- ❌ Monotone delivery (add energy!)
- ❌ Mumbling or unclear words
- ❌ Background noise (find quiet space)
- ❌ Popping "P" sounds (use pop filter or speak across mic)
- ❌ Breathing into microphone (turn head slightly)

### Audio Recording Checklist

- [ ] Quiet environment
- [ ] Microphone tested and working
- [ ] Audio levels checked (not too quiet, not clipping)
- [ ] Script ready and practiced
- [ ] Water nearby
- [ ] Phone silenced
- [ ] Notifications disabled

---

## Screen Recording Best Practices

### Mouse Movements

- Move mouse slowly and deliberately
- Highlight important elements by hovering
- Use mouse to draw attention to key information
- Avoid rapid or jerky movements
- Don't leave mouse in center of screen (distracting)

### Typing

- Type slowly enough to be readable
- Avoid typos (they look unprofessional)
- Consider typing in advance and pasting
- Or type slowly and speed up in editing

### Navigation

- Navigate smoothly between pages
- Avoid clicking wrong buttons
- Wait for pages to fully load before continuing
- Don't rush through screens

### Timing

- Pause briefly on important information
- Give viewers time to read text on screen
- Don't move too quickly through results
- Allow 2-3 seconds for each key point

### Visual Focus

- Keep important content in center of screen
- Avoid scrolling too fast
- Zoom in on small text if needed
- Use full screen mode when possible

---

## Recording Workflow

### Step-by-Step Recording Process

**1. Final Preparation** (5 minutes)
- [ ] Close all unnecessary apps
- [ ] Disable notifications
- [ ] Open recording software
- [ ] Open browser to application
- [ ] Have sample document ready
- [ ] Review script one last time

**2. Test Recording** (2 minutes)
- [ ] Record 10-second test clip
- [ ] Review for video quality
- [ ] Review for audio quality
- [ ] Adjust settings if needed

**3. Record Introduction** (3-5 takes)
- [ ] Start recording
- [ ] Show title slide or application
- [ ] Deliver introduction script
- [ ] Stop recording
- [ ] Review and re-record if needed

**4. Record Main Demo** (3-5 takes)
- [ ] Start recording
- [ ] Upload document
- [ ] Enter symptoms
- [ ] Click process
- [ ] Show processing
- [ ] Display results
- [ ] Stop recording
- [ ] Review and re-record if needed

**5. Record Conclusion** (2-3 takes)
- [ ] Start recording
- [ ] Show architecture or closing slide
- [ ] Deliver conclusion script
- [ ] Stop recording
- [ ] Review and re-record if needed

**6. Review All Clips** (10 minutes)
- [ ] Watch all recordings
- [ ] Check audio quality
- [ ] Check video quality
- [ ] Verify timing (under 3 minutes total)
- [ ] Select best takes

---

## Troubleshooting

### Video Issues

**Problem**: Text is blurry or unreadable
- **Solution**: Increase recording resolution to 1080p
- **Solution**: Increase browser zoom to 125%
- **Solution**: Use larger font sizes in application

**Problem**: Video is choppy or laggy
- **Solution**: Close other applications
- **Solution**: Reduce recording resolution to 720p
- **Solution**: Record in shorter segments

**Problem**: Colors look washed out
- **Solution**: Adjust display brightness
- **Solution**: Check recording software color settings
- **Solution**: Adjust in video editing

### Audio Issues

**Problem**: Audio is too quiet
- **Solution**: Increase microphone input volume
- **Solution**: Speak closer to microphone
- **Solution**: Boost audio in editing

**Problem**: Audio has background noise
- **Solution**: Find quieter location
- **Solution**: Use noise reduction in editing
- **Solution**: Use better microphone

**Problem**: Audio and video out of sync
- **Solution**: Use same software for both
- **Solution**: Sync in video editor
- **Solution**: Record audio and video separately

### Application Issues

**Problem**: Application is slow or unresponsive
- **Solution**: Test before recording
- **Solution**: Restart browser
- **Solution**: Check backend is running

**Problem**: Processing fails during recording
- **Solution**: Test with sample data first
- **Solution**: Have backup pre-recorded results
- **Solution**: Use screenshots as fallback

**Problem**: Results don't look impressive
- **Solution**: Adjust sample data
- **Solution**: Ensure policies are well-matched
- **Solution**: Pre-test to verify good results

---

## Recording Checklist

### Before Recording

- [ ] Environment is quiet
- [ ] Computer is prepared
- [ ] Browser is set up
- [ ] Application is tested
- [ ] Sample data is ready
- [ ] Recording software is configured
- [ ] Audio is tested
- [ ] Script is practiced
- [ ] Backup plan is ready

### During Recording

- [ ] Speak clearly and at moderate pace
- [ ] Move mouse slowly and deliberately
- [ ] Pause on important information
- [ ] Follow script timing
- [ ] Stay calm if mistakes happen
- [ ] Keep energy and enthusiasm

### After Recording

- [ ] Review all footage
- [ ] Check audio quality
- [ ] Check video quality
- [ ] Verify timing (under 3 minutes)
- [ ] Select best takes
- [ ] Save all files with clear names
- [ ] Back up recordings

---

## File Management

### Naming Convention

Use clear, descriptive names:
- `demo_intro_take1.mp4`
- `demo_intro_take2.mp4`
- `demo_main_take1.mp4`
- `demo_main_take2.mp4`
- `demo_conclusion_take1.mp4`

### File Organization

```
demo/
├── recordings/
│   ├── intro/
│   │   ├── take1.mp4
│   │   ├── take2.mp4
│   │   └── take3.mp4
│   ├── main/
│   │   ├── take1.mp4
│   │   └── take2.mp4
│   └── conclusion/
│       ├── take1.mp4
│       └── take2.mp4
├── final/
│   └── demo_final.mp4
└── assets/
    ├── title_slide.png
    └── architecture_diagram.png
```

### Backup

- [ ] Save recordings to multiple locations
- [ ] Upload to cloud storage (Google Drive, Dropbox)
- [ ] Keep original recordings until final video is complete
- [ ] Don't delete takes until video is uploaded

---

## Tips for Success

1. **Practice Makes Perfect**: Record 2-3 full practice runs before the "real" recording
2. **Stay Calm**: Mistakes happen - just keep going or start over
3. **Energy Matters**: Speak with enthusiasm - it's contagious
4. **Timing is Key**: Practice to stay under 3 minutes
5. **Quality Over Speed**: Take time to get good recordings
6. **Test Everything**: Test the complete workflow before recording
7. **Have Backups**: Prepare backup plans for technical issues
8. **Review Carefully**: Watch your recordings before moving to editing
9. **Get Feedback**: Show a draft to a friend or colleague
10. **Stay Professional**: This represents your work - make it polished

---

## Next Steps

After recording:
1. Review all footage
2. Select best takes
3. Proceed to video editing (see EDITING_CHECKLIST.md)
4. Add title slides and transitions
5. Export final video
6. Upload to YouTube (see UPLOAD_INSTRUCTIONS.md)

---

## Resources

- **OBS Studio Tutorial**: https://obsproject.com/wiki/
- **Loom Help Center**: https://support.loom.com/
- **Audio Recording Tips**: https://www.youtube.com/results?search_query=voiceover+recording+tips
- **Screen Recording Best Practices**: https://www.techsmith.com/blog/screen-recording-tips/

---

## Questions?

If you encounter issues not covered in this guide:
1. Check the troubleshooting section
2. Search online for specific error messages
3. Test with simpler setup (lower resolution, different software)
4. Ask for help in hackathon Discord/Slack channel

Good luck with your recording! 🎥
