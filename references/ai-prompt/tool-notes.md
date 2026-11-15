# Tool Notes (non-exhaustive, check for updates)

This file is a quick-reference cheat sheet, not a source of truth — AI video tools change
their features constantly. If live web search is available and the user named a specific
tool, it's worth a quick check for anything that's changed since this was written.

## General patterns across most tools (as of when this was written)
- Most clips are generated in short segments, roughly 4–10 seconds each.
- Image-to-video (starting from a reference image) is generally more reliable for consistent
  subject appearance than pure text-to-video.
- Few tools reliably lip-sync to arbitrary pre-recorded audio — that usually needs a
  dedicated avatar/lip-sync tool instead of a general video-gen prompt.
- Negative prompts (listing what to avoid) are supported by some tools and not others —
  if supported, common entries are: morphing limbs, extra fingers, flickering, warped text,
  unnatural blinking.

## Runway (Gen-series)
- Supports both text-to-video and image-to-video.
- Has historically supported camera-motion controls (pan, zoom, tilt) as explicit parameters
  separate from the text prompt — check current UI for whether to put camera direction in
  the prompt text or a separate control.

## Kling
- Known for comparatively strong physical motion realism.
- Supports image-to-video; prompt should focus on motion/camera when starting from an image.

## Sora / Veo
- Known for relatively strong temporal consistency (objects/characters staying put across
  the clip) compared to earlier-generation tools.
- Longer prompts with more scene detail tend to be well-tolerated by these two.

## Pika / Luma / Hailuo / Hunyuan / Wan and others
- Broadly follow the same natural-language prompt structure described in the main SKILL.md.
- Check the specific tool's documentation for max clip length and whether it supports
  image-to-video, since this varies and changes often.

## When in doubt
Write the prompt in plain, structured natural language (per the main SKILL.md template) and
let the user paste it into whichever tool they're using. This degrades gracefully across
virtually every current and future text-to-video tool.
