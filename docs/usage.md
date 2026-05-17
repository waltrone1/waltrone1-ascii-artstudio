# Usage Guide

This document explains the basic usage of **waltrone1 ASCII ArtStudio**.

waltrone1 ASCII ArtStudio is a Windows ASCII art generator and export tool by **WALTRONE**.

It helps users convert images into colorful ASCII artwork and export the result as HTML, SVG or PNG.

The tool can help create retro visuals, terminal-style artwork, browser previews, transparent PNG exports, vector exports and shareable ASCII graphics for websites, documentation, posts or creative projects.

---

## Basic Usage

1. Download the latest release.
2. Extract the ZIP file completely.
3. Start the application.
4. Load an image.
5. Choose an ASCII character set.
6. Select a palette and effect.
7. Adjust output width, font size, line height and letter spacing if needed.
8. Open the live browser preview if required.
9. Export the result as HTML, SVG or PNG.
10. Review the exported file before publishing or sharing it.

---

## Start the Application

After downloading the release package, extract the ZIP file completely.

Start the application by running:

```text
waltrone1-ASCII-ArtStudio.exe
```

If you run the tool from source, start it with:

```text
python run.py
```

Depending on your environment, Python dependencies may need to be installed first:

```text
pip install -r requirements.txt
```

---

## Main Workflow

The typical workflow is:

1. Start waltrone1 ASCII ArtStudio.
2. Load an image file.
3. Select the ASCII width.
4. Choose a character set.
5. Choose a color palette.
6. Select an output effect.
7. Select an export mode.
8. Adjust font size, line height and letter spacing.
9. Enable or disable transparency options if needed.
10. Open the live browser preview.
11. Fine-tune the settings.
12. Export the result as HTML, SVG or PNG.
13. Check the exported file before using it publicly.

---

## Supported Image Types

The application can work with common image formats supported by Pillow.

Typical examples:

```text
.jpg
.jpeg
.png
.bmp
.gif
.webp
```

Possible image sources include:

- Logos
- Product images
- Pixel art
- Illustrations
- Screenshots
- Icons
- Retro graphics
- Simple photos
- Social media graphics
- Documentation images

For best results, use images with clear contrast and recognizable shapes.

---

## Load an Image

Use the image loading button in the application to select a file.

After loading an image, the program generates ASCII output based on the selected settings.

Large images can take longer to process, especially when high detail settings are used.

For faster testing, start with smaller images or lower ASCII width values.

---

## ASCII Width

The ASCII width controls how many characters are used horizontally.

Lower values usually create faster and simpler output.

Higher values usually create more detailed output.

Typical workflow:

1. Start with a medium width.
2. Check the preview.
3. Increase the width for more detail.
4. Decrease the width if the output becomes too large or slow.

---

## Character Sets

waltrone1 ASCII ArtStudio includes multiple character presets.

Character sets influence the visual style of the generated ASCII artwork.

Possible uses:

- Fine detail output
- Blocky retro output
- Matrix-like output
- Minimal text output
- Custom branded character output

The application can also use a custom character set.

This is useful when you want the output to be built from a name, handle, brand or repeated custom text.

---

## Custom Character Set

Custom character sets can be useful for branded or personalized ASCII output.

Examples:

```text
WALTRONE
waltrone1
ASCII
RETRO
01
```

Tips:

- Short custom strings create strong repeated patterns.
- Longer custom strings create more variation.
- High contrast images usually work better.
- Test different output widths to find the best result.

---

## Palettes

The application can use original image colors or retro color palettes.

Typical palette styles may include:

- Original colors
- Matrix green
- Amber monitor
- Ice terminal
- Neon cyber
- Fire CRT
- Arcade 80s
- Neon Miami
- Random retro palettes

Palettes can strongly change the final look.

For realistic image-based output, use original colors.

For retro artwork, use one of the stylized palettes.

---

## Effects

Effects change the visual appearance of HTML and preview output.

Typical effects may include:

- CRT
- CRT scanlines
- Retro glow
- Neon terminal
- Neon pink
- Neon cyan
- Neon lime
- Matrix background
- Glitch
- Amber monitor
- Arcade 80s
- Pixel candy
- Electric blue
- Laser red
- Metallic or shine-style effects

Some effects are mainly visible in HTML output and browser preview.

Always check the exported file in a browser before publishing it.

---

## Export Modes

The application can use different export modes.

Possible modes include:

```text
Nur ASCII-Bild
Bild + Programmname
Terminal-Frame
Embed
```

### Nur ASCII-Bild

This mode creates a clean ASCII output without additional frame elements.

It is useful when you want only the artwork.

### Bild + Programmname

This mode creates ASCII output with discreet WALTRONE branding.

It is useful for public examples, previews or community releases.

### Terminal-Frame

This mode creates a retro terminal-style frame around the output.

It is useful for screenshots, nostalgic designs and retro project pages.

### Embed

This mode creates HTML that can be embedded into another page.

It is useful for websites, documentation pages or custom landing pages.

---

## Export Formats

waltrone1 ASCII ArtStudio can export several formats.

Available export options may include:

- HTML export
- SVG export
- PNG export
- Transparent PNG export

---

## HTML Export

HTML export is useful for browser-based presentation.

A HTML export may include:

- ASCII artwork
- CSS styling
- Retro effects
- Terminal frame
- Branding footer depending on export mode
- Copy function for raw ASCII output
- Embed-ready markup depending on export mode

HTML output is useful for:

- Websites
- Project pages
- Documentation
- GitHub Pages
- Retro landing pages
- Browser previews
- Shareable visual examples

HTML output may look slightly different depending on browser, font rendering and local system settings.

---

## SVG Export

SVG export is useful when scalable vector output is needed.

Examples:

- Documentation graphics
- High-resolution layouts
- Web graphics
- Design workflows
- Further processing in vector tools

SVG files can become large when very detailed settings are used.

---

## PNG Export

PNG export is useful when the result should be shared as a normal image.

Examples:

- Social posts
- Documentation screenshots
- Preview images
- Design mockups
- Overlays
- Blog images

Transparent PNG export can be useful when the ASCII artwork should be placed over another background.

Always check transparent output before using it in a final design.

---

## Live Browser Preview

The live browser preview helps review the HTML output while changing settings.

It is useful for:

- Checking effects
- Checking spacing
- Checking font size
- Checking readability
- Checking terminal frame output
- Reviewing browser rendering
- Testing output before export

If the preview does not update as expected, export the file and open it manually in a browser.

---

## Screenshots

Screenshots are available in the repository under:

```text
screenshots/
```

The main README includes this screenshot reference:

```text
screenshots/ascii-artstudio-main.png
```

When uploading through the GitHub web interface, place the screenshot file in the `screenshots/` folder with exactly this file name.

---

## Recommended Export Workflow

Before publishing or sharing files, use a controlled workflow.

Recommended steps:

1. Load the source image.
2. Choose the ASCII width.
3. Select character set and palette.
4. Check the live preview.
5. Test different effects.
6. Choose the export mode.
7. Export as HTML, SVG or PNG.
8. Open the exported file manually.
9. Check readability and layout.
10. Check file size.
11. Verify that you are allowed to use the original image.
12. Publish or share only the final checked export.

---

## Safety Notes

waltrone1 ASCII ArtStudio is primarily a creative image conversion and export tool.

It should be used carefully when working with copyrighted, private or internal images.

Important safety notes:

- Always check exported files before publishing.
- Do not publish images you are not allowed to use.
- Be careful with screenshots that contain private information.
- Be careful with internal company images or paths.
- Large exports may create large HTML, SVG or PNG files.
- Browser rendering can differ between systems.
- Fonts can affect the final appearance.
- Keep original images backed up separately.
- Use the tool only on systems and images you are authorized to use.

---

## What ASCII ArtStudio Does Not Do Automatically

ASCII ArtStudio does not automatically publish images.

It does not automatically upload exported files.

It does not replace copyright checks for source images.

It does not guarantee identical rendering in every browser, font or operating system.

Publishing decisions remain the responsibility of the user.

---

## Typical Use Cases

waltrone1 ASCII ArtStudio can be useful for:

- Creating retro ASCII art from images
- Creating matrix-style graphics
- Creating neon terminal visuals
- Creating transparent PNG ASCII overlays
- Creating SVG ASCII artwork
- Creating HTML embeds for project pages
- Preparing visual README examples
- Producing nostalgic graphics for posts or pages
- Creating fun artwork for personal projects
- Testing custom text-based character sets
- Building retro website elements
- Creating visual examples for documentation

---

## Build / Source Notes

The source files are available in the repository for transparency and review.

If the project is started from source, use:

```text
python run.py
```

Install requirements first if needed:

```text
pip install -r requirements.txt
```

Build-related files are located in:

```text
py2exe/
```

Generated build output such as `.exe`, `.zip`, `build/`, `dist/` or release folders should not be committed directly to the repository.

Final release packages should be published through GitHub Releases.

---

## Troubleshooting

### The application does not start

Try the following:

- Extract the ZIP file completely.
- Start the EXE from a local folder.
- Check whether Windows SmartScreen blocks the file.
- Check whether antivirus software quarantined the file.
- Test the tool in a separate folder.
- Run as Administrator if required.

If running from source, install requirements:

```text
pip install -r requirements.txt
```

Then start:

```text
python run.py
```

---

### Image loading fails

Try the following:

- Check whether the file is a supported image format.
- Try a PNG or JPG version of the same image.
- Move the file to a simple local path.
- Avoid very long paths.
- Check whether the image file is damaged.
- Try a smaller image first.

---

### Preview is slow

Large images or high ASCII width settings can slow down preview generation.

Try the following:

- Reduce ASCII width.
- Use a smaller source image.
- Disable very heavy effects while testing.
- Close other heavy applications.
- Export only after the final settings are selected.

---

### HTML output looks different in another browser

HTML rendering depends on browser, font rendering and system settings.

Try the following:

- Test in another browser.
- Use a common monospace font.
- Reduce font size.
- Adjust line height and letter spacing.
- Export again after checking the preview.

---

### PNG output is too large

High detail settings can create large PNG files.

Try the following:

- Reduce ASCII width.
- Reduce export scale.
- Reduce font size.
- Use HTML or SVG if that better fits the use case.

---

### Transparent PNG does not look right

Transparent output depends on image brightness, dark-pixel handling and background use.

Try the following:

- Test the PNG on different backgrounds.
- Adjust transparency-related options.
- Increase contrast in the source image.
- Use a simpler source image.
- Export again with different settings.

---

## Security and Transparency

The tool is provided as a Windows utility and may be distributed as an EXE inside a ZIP file.

Some antivirus tools may occasionally flag small or packaged EXE tools as false positives.

Recommended checks:

- Download only from the official release source.
- Verify the GitHub repository.
- Check release notes.
- Check the ZIP file before use if required.
- Test in a virtual machine or test environment if needed.
- Use VirusTotal or similar services if a public hash/link is provided.

---

## Project Information

```text
Project: waltrone1 ASCII ArtStudio
Brand: WALTRONE
GitHub / Handle: waltrone1
Repository: waltrone1-ascii-artstudio
Type: Windows ASCII art generator and export tool
Status: Public community release
```

---

## Disclaimer

This tool is provided as-is, without warranty of any kind.

Use it at your own risk.

The author is not responsible for data loss, incorrect exports, browser rendering differences, publishing decisions, copyright issues caused by user-provided images, system issues or damages caused by the use of this software.
