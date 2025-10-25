window.initAccessibilityToolbar = function () {
  try {
    const fontSelect  = document.getElementById("font-select");
    const themeSelect = document.getElementById("theme-select");
    const sizeRange   = document.getElementById("size-slider");
    const sizeDisplay = document.getElementById("size-display");
    const resetBtn    = document.getElementById("reset-default");

    // Always re-select everything fresh each time we apply styles
    function applyStyles(font, theme, size) {
      // Only apply theme + font class to the top-level containers
      const topLevelTargets = document.querySelectorAll(`
        .article-card.detail.article-view,
        .article-content,
        .small-text.article-content,
        .text
      `);

      topLevelTargets.forEach(el => {
        el.classList.remove(
          "font-arial", "font-comic", "font-opendyslexic",
          "theme-default", "theme-cream", "theme-pastelblue", "theme-darkmode"
        );
        el.classList.add(font, theme);

        // Set font size via CSS variable instead of inline style
        el.style.setProperty("--reader-font-size", size + "px");
      });

      // Update size label display
      const sizeDisplay = document.getElementById("size-display");
      if (sizeDisplay) sizeDisplay.textContent = size + "px";
    }


    // Load saved preferences
    const savedFont = localStorage.getItem("fontChoice")  || "font-arial";
    const savedTheme = localStorage.getItem("themeChoice") || "theme-default";
    const savedSize = parseInt(localStorage.getItem("fontSize") || "18", 10);

    if (fontSelect)  fontSelect.value  = savedFont;
    if (themeSelect) themeSelect.value = savedTheme;
    if (sizeRange)   sizeRange.value   = savedSize;

    applyStyles(savedFont, savedTheme, savedSize);

    function updateAndSave() {
      const font  = fontSelect?.value  || "font-arial";
      const theme = themeSelect?.value || "theme-default";
      const size  = parseInt(sizeRange?.value || "18", 10);

      localStorage.setItem("fontChoice",  font);
      localStorage.setItem("themeChoice", theme);
      localStorage.setItem("fontSize",    size);

      applyStyles(font, theme, size);
    }

    fontSelect?.addEventListener("input", updateAndSave);
    themeSelect?.addEventListener("input", updateAndSave);
    sizeRange?.addEventListener("input", updateAndSave);

    resetBtn?.addEventListener("click", () => {
      const defaults = { font: "font-arial", theme: "theme-default", size: 18 };
      localStorage.removeItem("fontChoice");
      localStorage.removeItem("themeChoice");
      localStorage.removeItem("fontSize");

      if (fontSelect)  fontSelect.value  = defaults.font;
      if (themeSelect) themeSelect.value = defaults.theme;
      if (sizeRange)   sizeRange.value   = defaults.size;

      applyStyles(defaults.font, defaults.theme, defaults.size);
    });
  } catch (err) {
    console.warn("Accessibility toolbar safely isolated:", err);
  }
};

// Run on page load
document.addEventListener("DOMContentLoaded", window.initAccessibilityToolbar);
