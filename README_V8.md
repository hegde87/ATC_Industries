# ATC Industries — V8 Interactive Local Preview

Built from the previously approved ATC Industries V6.4 website, retaining the existing pages, products, certifications, machinery and images.

## Test on Windows

1. Extract the ZIP file.
2. Open the **ATC_Industries_V8_Interactive** folder (the one containing `index.html`).
3. Double-click `START_WEBSITE.bat` or open PowerShell there and run `python -m http.server 8000`.
4. Visit `http://localhost:8000/` in Chrome/Edge.
5. Keep the terminal open while browsing. Use Ctrl+C to stop.

If port 8000 is occupied, run `python -m http.server 8080` and visit `http://localhost:8080/`.

## New V8 features

- **Homepage**: auto-rotating carousel of ATC machinery photos for the five processes, arrows, indicators, pause/play, keyboard navigation and mobile swipe. Approved extrusion-machine hero remains intact.
- **Contact Us**: original ATC factory/solar building photo as a subdued background with a dark translucent overlay. Existing contact details and enquiry form preserved.
- **Quality**: industrial machinery/inspection-themed hero and an animated showcase made from ATC's supplied machinery photographs. Existing certificate images retained.
- **Responsive**: CSS adjustments for mobile and tablet. Motion-reduction support.

## Important limitations

- The quality showcase is **animated still photographs**, **not a real robotics or inspection video**. No verified ATC robotics footage was supplied. Replace this with actual ATC footage when available. The reference screen recording is NOT embedded as if it were ATC manufacturing footage.
- The enquiry form still opens the user's email client. It is not a server-backed submission form.
- Review all business facts, ISO certificate scope, images and environmental claims before public deployment.
- All website files are static HTML, CSS, JavaScript and local images; no npm build or external libraries are required. Google Fonts may need internet, but the site still functions without them.
