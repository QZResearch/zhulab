/* Lightbox for the gallery album pages.
   Blowfish's medium-zoom measures an image's rendered box, which is a square
   CSS crop here — so gallery images carry .nozoom and use this instead.
   Gives full-size viewing plus prev/next, which medium-zoom doesn't do. */
(function () {
  "use strict";

  var grid = document.querySelector(".yu-gallery");
  if (!grid) return;

  var shots = Array.prototype.slice.call(grid.querySelectorAll(".yu-shot"));
  if (!shots.length) return;

  var items = shots.map(function (fig) {
    var img = fig.querySelector("img");
    var cap = fig.querySelector("figcaption");
    return {
      src: img.getAttribute("data-full") || img.currentSrc || img.src,
      alt: img.getAttribute("alt") || "",
      caption: cap ? cap.textContent.trim() : ""
    };
  });

  var index = 0;
  var box = null;
  var lastFocus = null;

  function build() {
    box = document.createElement("div");
    box.className = "yu-lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.innerHTML =
      '<button class="yu-lb-close" aria-label="Close">&times;</button>' +
      '<button class="yu-lb-nav yu-lb-prev" aria-label="Previous photo">&#8249;</button>' +
      '<button class="yu-lb-nav yu-lb-next" aria-label="Next photo">&#8250;</button>' +
      '<figure class="yu-lb-stage">' +
      '<img alt="" />' +
      '<figcaption><span class="yu-lb-caption"></span><span class="yu-lb-count"></span></figcaption>' +
      "</figure>";
    document.body.appendChild(box);

    box.querySelector(".yu-lb-close").addEventListener("click", close);
    box.querySelector(".yu-lb-prev").addEventListener("click", function (e) {
      e.stopPropagation();
      step(-1);
    });
    box.querySelector(".yu-lb-next").addEventListener("click", function (e) {
      e.stopPropagation();
      step(1);
    });
    box.addEventListener("click", function (e) {
      if (e.target === box || e.target.classList.contains("yu-lb-stage")) close();
    });
  }

  function render() {
    var item = items[index];
    var img = box.querySelector("img");
    img.src = item.src;
    img.alt = item.alt;
    box.querySelector(".yu-lb-caption").textContent = item.caption;
    box.querySelector(".yu-lb-count").textContent = index + 1 + " / " + items.length;
    var single = items.length < 2;
    box.querySelector(".yu-lb-prev").hidden = single;
    box.querySelector(".yu-lb-next").hidden = single;
  }

  function open(i) {
    if (!box) build();
    index = i;
    lastFocus = document.activeElement;
    render();
    document.body.classList.add("yu-lb-open");
    box.classList.add("is-open");
    box.querySelector(".yu-lb-close").focus();
    document.addEventListener("keydown", onKey);
  }

  function close() {
    if (!box) return;
    box.classList.remove("is-open");
    document.body.classList.remove("yu-lb-open");
    document.removeEventListener("keydown", onKey);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function step(delta) {
    index = (index + delta + items.length) % items.length;
    render();
  }

  function onKey(e) {
    if (e.key === "Escape") close();
    else if (e.key === "ArrowLeft") step(-1);
    else if (e.key === "ArrowRight") step(1);
  }

  shots.forEach(function (fig, i) {
    var img = fig.querySelector("img");
    img.setAttribute("tabindex", "0");
    img.setAttribute("role", "button");
    img.addEventListener("click", function () {
      open(i);
    });
    img.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        open(i);
      }
    });
  });
})();
