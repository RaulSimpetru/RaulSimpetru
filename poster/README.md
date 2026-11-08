# The profile poster

`../assets/poster.svg`, the image the profile README shows, is made from `poster.html`.

1. Edit `poster.html`. Open it in a browser to see the result; the pictures are in `img/` and the fonts (Source Serif 4, Geist Mono) load from Google Fonts.
2. Run `python3 poster/build.py`. It needs Google Chrome and `pdftocairo` (`brew install poppler`). It rewrites `assets/poster.svg`.
3. Commit and push. The whole poster links to the website (the `<a>` in the README).

The SVG is plain vector art: the text becomes outlines and the pictures are embedded, so it looks the same in every browser and both GitHub themes. The build adds the dashed ring around the drawn hand as an animated circle; if you move the drawing, the ring follows it.

`img/drawing.jpg` is the lab demo photo redrawn with OpenAI Codex (gpt-6-astra); `img/hand.jpg` is the hand close-up drawn the same way. Full-size originals and the exact prompts are in the website repository, under `art/`.
