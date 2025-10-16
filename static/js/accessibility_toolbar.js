document.addEventListener("DOMContentLoaded", () => {
  try {
    const textEls = document.querySelectorAll(".article-content, .text");
    const articleWrappers = document.querySelectorAll(".article-card.detail.article-view");
    if (!textEls.length && !articleWrappers.length) return;

    const fontSelect = document.getElementById("font-select");
    const themeSelect = document.getElementById("theme-select");
    const sizeRange = document.getElementById("size-slider");
    const sizeDisplay = document.getElementById("size-display");
    const resetBtn = document.getElementById("reset-default");

    function applyStyles(font, theme, size) {
      const targets = [...textEls, ...articleWrappers];
      targets.forEach(el => {
        el.classList.remove(
          "font-arial", "font-comic", "font-opendyslexic",
          "theme-default", "theme-cream", "theme-pastelblue", "theme-darkmode"
        );
        el.classList.add(font, theme);
        if (el.classList.contains("article-content") || el.classList.contains("text")) {
          el.style.setProperty("font-size", size + "px", "important");
        }
      });
      if (sizeDisplay) sizeDisplay.textContent = size + "px";
    }

    const savedFont = localStorage.getItem("fontChoice") || "font-arial";
    const savedTheme = localStorage.getItem("themeChoice") || "theme-default";
    const savedSize = parseInt(localStorage.getItem("fontSize") || "18", 10);

    if (fontSelect) fontSelect.value = savedFont;
    if (themeSelect) themeSelect.value = savedTheme;
    if (sizeRange) sizeRange.value = savedSize;

    applyStyles(savedFont, savedTheme, savedSize);

    function updateAndSave() {
      const font = fontSelect?.value || "font-arial";
      const theme = themeSelect?.value || "theme-default";
      const size = parseInt(sizeRange?.value || "18", 10);
      localStorage.setItem("fontChoice", font);
      localStorage.setItem("themeChoice", theme);
      localStorage.setItem("fontSize", size);
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
      if (fontSelect) fontSelect.value = defaults.font;
      if (themeSelect) themeSelect.value = defaults.theme;
      if (sizeRange) sizeRange.value = defaults.size;
      applyStyles(defaults.font, defaults.theme, defaults.size);
    });

  } catch (err) {
    console.warn("Accessibility toolbar safely isolated:", err);
  }
});
