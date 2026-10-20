/* ATC Industries — progressive enhancement. The site works without this file. */
(function () {
  "use strict";

  var EMAIL = "atcgoa@gmail.com";
  var desktopNav = window.matchMedia("(min-width: 70rem)");
  var params = new URLSearchParams(window.location.search);

  /* ------------------------------------------------------------ legacy product links */
  var legacy = document.querySelector("[data-legacy-product]");
  if (legacy) {
    var legacyId = params.get("id");
    if (legacyId && /^[a-z0-9-]+$/.test(legacyId)) {
      window.location.replace("product-" + legacyId + ".html");
      return;
    }
  }

  /* ------------------------------------------------------------ header */
  var header = document.querySelector("[data-header]");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ------------------------------------------------------------ navigation */
  var nav = document.querySelector(".nav");
  var toggle = document.querySelector("[data-nav-toggle]");
  var panel = document.querySelector("[data-nav-panel]");
  var triggers = Array.prototype.slice.call(document.querySelectorAll(".nav__trigger"));

  function closeSubs(except) {
    triggers.forEach(function (t) {
      if (t === except) return;
      t.setAttribute("aria-expanded", "false");
      t.parentElement.classList.remove("is-open");
    });
  }

  function setMenu(open) {
    if (!nav || !toggle) return;
    if (open && header) {
      document.documentElement.style.setProperty("--header-bottom", header.getBoundingClientRect().bottom + "px");
    }
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.querySelector(".nav__toggle-label").textContent = open ? "Close" : "Menu";
    document.body.classList.toggle("is-locked", open);
    if (open) {
      var first = panel.querySelector("a, button");
      if (first) first.focus({ preventScroll: true });
    } else {
      closeSubs();
    }
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
  }

  triggers.forEach(function (trigger) {
    trigger.addEventListener("click", function () {
      var open = trigger.getAttribute("aria-expanded") !== "true";
      closeSubs(trigger);
      trigger.setAttribute("aria-expanded", String(open));
      trigger.parentElement.classList.toggle("is-open", open);
    });
  });

  document.addEventListener("click", function (event) {
    if (!desktopNav.matches) return;
    if (!event.target.closest(".nav__item.has-sub")) closeSubs();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    var openTrigger = triggers.filter(function (t) {
      return t.getAttribute("aria-expanded") === "true";
    })[0];
    if (openTrigger) {
      closeSubs();
      openTrigger.focus();
    } else if (nav && nav.classList.contains("is-open")) {
      setMenu(false);
      toggle.focus();
    }
  });

  desktopNav.addEventListener("change", function () {
    setMenu(false);
  });

  /* ------------------------------------------------------------ product filter */
  var grid = document.querySelector("[data-filterable]");
  if (grid) {
    var chips = Array.prototype.slice.call(document.querySelectorAll("[data-filter]"));
    var search = document.querySelector("[data-product-search]");
    var count = document.querySelector("[data-product-count]");
    var empty = document.querySelector("[data-product-empty]");
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".pcard"));
    var active = "all";

    var apply = function () {
      var q = search ? search.value.trim().toLowerCase() : "";
      var shown = 0;
      cards.forEach(function (card) {
        var match = (active === "all" || card.dataset.cat === active) && (!q || card.dataset.search.indexOf(q) !== -1);
        card.hidden = !match;
        if (match) shown++;
      });
      if (count) count.textContent = shown === cards.length ? "Showing all " + shown + " products" : "Showing " + shown + " of " + cards.length + " products";
      if (empty) empty.hidden = shown !== 0;
    };

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        active = chip.dataset.filter;
        chips.forEach(function (c) {
          c.setAttribute("aria-pressed", String(c === chip));
        });
        apply();
      });
    });
    if (search) search.addEventListener("input", apply);
    apply();
  }

  /* ------------------------------------------------------------ enquiry forms */
  var interest = params.get("interest");
  var interestSelect = document.getElementById("interest");
  if (interest && interestSelect) {
    var exists = Array.prototype.some.call(interestSelect.options, function (o) {
      return o.value.toLowerCase() === interest.toLowerCase();
    });
    if (!exists) {
      var option = document.createElement("option");
      option.textContent = interest.slice(0, 120);
      interestSelect.insertBefore(option, interestSelect.firstChild);
    }
    Array.prototype.forEach.call(interestSelect.options, function (o) {
      if (o.value.toLowerCase() === interest.toLowerCase()) interestSelect.value = o.value;
    });
  }

  function labelFor(control) {
    var label = document.querySelector('label[for="' + control.id + '"]');
    return label ? label.childNodes[0].textContent.trim() : control.name;
  }

  function messageFor(control) {
    if (control.validity.valueMissing) {
      var label = labelFor(control).toLowerCase();
      return "Please enter " + (label.indexOf("your ") === 0 ? label : "your " + label) + ".";
    }
    if (control.validity.typeMismatch && control.type === "email") return "Please enter a valid email address, like name@company.com.";
    return "Please check this field.";
  }

  function showError(control, message) {
    var error = document.getElementById(control.id + "-error");
    control.setAttribute("aria-invalid", message ? "true" : "false");
    if (!error) return;
    error.textContent = message || "";
    error.hidden = !message;
  }

  Array.prototype.forEach.call(document.querySelectorAll("[data-mail-form]"), function (form) {
    var status = form.querySelector("[data-form-status]");
    var lastBody = "";
    var controls = Array.prototype.slice.call(form.querySelectorAll("input, select, textarea"));

    controls.forEach(function (control) {
      control.addEventListener("blur", function () {
        if (control.getAttribute("aria-invalid") === "true" || control.value) {
          showError(control, control.checkValidity() ? "" : messageFor(control));
        }
      });
      control.addEventListener("input", function () {
        if (control.getAttribute("aria-invalid") === "true" && control.checkValidity()) showError(control, "");
      });
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var firstInvalid = null;
      controls.forEach(function (control) {
        var ok = control.checkValidity();
        showError(control, ok ? "" : messageFor(control));
        if (!ok && !firstInvalid) firstInvalid = control;
      });
      if (firstInvalid) {
        firstInvalid.focus();
        return;
      }

      var lines = controls
        .filter(function (c) {
          return c.value.trim() && c.tagName !== "TEXTAREA";
        })
        .map(function (c) {
          return labelFor(c) + ": " + c.value.trim();
        });
      var details = controls.filter(function (c) {
        return c.tagName === "TEXTAREA";
      })[0];
      var isPartner = form.dataset.mailForm === "partner";
      var company = (form.querySelector("#company, #partnerCompany") || {}).value || "";
      var subject = (isPartner ? "Business partner enquiry" : "Request for quotation") + " — " + company.trim();
      lastBody = lines.join("\n") + "\n\n" + (details ? labelFor(details) + ":\n" + details.value.trim() : "") + "\n\nSent from the ATC Industries website";

      window.location.href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lastBody);
      if (status) {
        status.hidden = false;
        status.focus({ preventScroll: false });
      }
    });

    var copyBtn = form.querySelector("[data-copy-enquiry]");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var label = copyBtn.querySelector("span");
        var done = function (text) {
          label.textContent = text;
          setTimeout(function () {
            label.textContent = "Copy enquiry";
          }, 2400);
        };
        if (navigator.clipboard) {
          navigator.clipboard.writeText(lastBody).then(
            function () {
              done("Copied");
            },
            function () {
              done("Copy failed — select and copy manually");
            }
          );
        } else {
          done("Copy not supported");
        }
      });
    }
  });

  /* ------------------------------------------------------------ maps (load on request) */
  Array.prototype.forEach.call(document.querySelectorAll("[data-map]"), function (map) {
    var button = map.querySelector("[data-map-load]");
    if (!button) return;
    button.addEventListener("click", function () {
      var frame = document.createElement("iframe");
      frame.src = map.dataset.map;
      frame.title = map.dataset.mapTitle || "Map";
      frame.loading = "lazy";
      frame.referrerPolicy = "no-referrer-when-downgrade";
      frame.allowFullscreen = true;
      map.replaceChildren(frame);
    });
  });

  /* ------------------------------------------------------------ lightbox */
  var links = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox]"));
  if (links.length && typeof HTMLDialogElement === "function") {
    var dialog, img, caption, counter, group = [], index = 0, opener = null;

    var icon = function (path) {
      return '<svg class="icon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + path + "</svg>";
    };

    var build = function () {
      dialog = document.createElement("dialog");
      dialog.className = "lightbox";
      dialog.setAttribute("aria-label", "Image viewer");
      dialog.innerHTML =
        '<div class="lightbox__frame"><div class="lightbox__bar"><span class="lightbox__count" aria-live="polite"></span>' +
        '<button class="lightbox__btn" type="button" data-lb-close aria-label="Close image viewer">' + icon('<path d="M6 6l12 12M18 6 6 18"/>') + "</button></div>" +
        '<div class="lightbox__stage"><img alt=""></div>' +
        '<div><p class="lightbox__caption"></p><div class="lightbox__nav">' +
        '<button class="lightbox__btn" type="button" data-lb-prev aria-label="Previous image">' + icon('<path d="M19 12H5M11 18l-6-6 6-6"/>') + "</button>" +
        '<button class="lightbox__btn" type="button" data-lb-next aria-label="Next image">' + icon('<path d="M5 12h14M13 6l6 6-6 6"/>') + "</button>" +
        "</div></div></div>";
      document.body.appendChild(dialog);
      img = dialog.querySelector("img");
      caption = dialog.querySelector(".lightbox__caption");
      counter = dialog.querySelector(".lightbox__count");
      dialog.querySelector("[data-lb-close]").addEventListener("click", function () {
        dialog.close();
      });
      dialog.querySelector("[data-lb-prev]").addEventListener("click", function () {
        show(index - 1);
      });
      dialog.querySelector("[data-lb-next]").addEventListener("click", function () {
        show(index + 1);
      });
      dialog.addEventListener("click", function (event) {
        if (event.target === dialog || event.target.classList.contains("lightbox__stage")) dialog.close();
      });
      dialog.addEventListener("keydown", function (event) {
        if (event.key === "ArrowRight") show(index + 1);
        if (event.key === "ArrowLeft") show(index - 1);
      });
      dialog.addEventListener("close", function () {
        document.body.classList.remove("is-locked");
        if (opener) opener.focus();
      });
    };

    var show = function (i) {
      index = (i + group.length) % group.length;
      var link = group[index];
      var thumb = link.querySelector("img");
      var fig = link.closest("figure");
      var cap = fig && fig.querySelector("figcaption");
      img.src = link.href;
      img.alt = thumb ? thumb.alt : "";
      caption.textContent = cap ? cap.textContent : img.alt;
      counter.textContent = group.length > 1 ? index + 1 + " / " + group.length : "";
      dialog.querySelector(".lightbox__nav").hidden = group.length < 2;
    };

    links.forEach(function (link) {
      link.addEventListener("click", function (event) {
        if (event.metaKey || event.ctrlKey || event.shiftKey) return;
        event.preventDefault();
        if (!dialog) build();
        opener = link;
        group = links.filter(function (l) {
          return l.dataset.lightbox === link.dataset.lightbox;
        });
        show(group.indexOf(link));
        dialog.showModal();
        document.body.classList.add("is-locked");
      });
    });
  }
})();
