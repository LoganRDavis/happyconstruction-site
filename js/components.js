// Shared chrome. The page includes <script src="/js/components.js" defer> and
// drops <site-header> / <site-footer> into the body. The site is a single
// landing page, so there is no nav: the header carries the phone and a jump to
// #contact. Hrefs are absolute so the 404 page could reuse this later.

// Also set in index.html (contact section and JSON-LD); change all three together.
const PHONE_DISPLAY = '(877) 624-2637';
const PHONE_TEL = '+18776242637';
const EMAIL = 'info@happyconstructionar.com';

// Horizontal lockup, no tagline. Two variants: the default black wordmark for
// the white header, a knockout white wordmark for the charcoal footer. Rasters
// are 256w (1x) and 512w (2x); intrinsic size is 256x78 for both. Regenerate
// from brand/. See brand/README.md.
const LOGO_W = 256;
const LOGO_H = 78;
const LOGO_ALT = 'Happy Construction';

// WebP first with a PNG fallback. `attrs` lands on the <img>, which is what the
// stylesheet targets; the <picture> is a transparent wrapper.
function logoPicture(variant, attrs = '') {
	const base = `/images/logo-horizontal${variant === 'light' ? '-light' : ''}`;
	return `
		<picture>
			<source type="image/webp" srcset="${base}-256.webp 1x, ${base}-512.webp 2x">
			<img src="${base}-256.png" srcset="${base}-512.png 2x" alt="${LOGO_ALT}" width="${LOGO_W}" height="${LOGO_H}" ${attrs}>
		</picture>`;
}

class SiteHeader extends HTMLElement {
	connectedCallback() {
		this.innerHTML = `
			<a href="#main-content" class="skip-link">Skip to main content</a>
			<header>
				<div id="headerContent">
					<a href="/" class="header-logo-link" aria-label="Happy Construction home">
						${logoPicture('dark', 'class="header-logo" fetchpriority="high"')}
					</a>
					<div class="header-actions">
						<a href="tel:${PHONE_TEL}" class="header-phone" aria-label="Call ${PHONE_DISPLAY}">${PHONE_DISPLAY}</a>
						<a href="/#contact" class="btn header-cta">Contact</a>
					</div>
				</div>
			</header>
		`;
	}
}

class SiteFooter extends HTMLElement {
	connectedCallback() {
		const year = new Date().getFullYear();
		this.innerHTML = `
			<footer>
				<div class="footer-container">
					<div class="footer-brand">
						<a href="/">
							${logoPicture('light', 'loading="lazy" decoding="async"')}
						</a>
						<p>General contractor for retail and commercial interiors, serving clients across the U.S. Building with a smile.</p>
					</div>
					<div class="footer-col">
						<h2>Contact</h2>
						<ul>
							<li><a href="tel:${PHONE_TEL}">${PHONE_DISPLAY}</a></li>
							<li><a href="mailto:${EMAIL}">${EMAIL}</a></li>
						</ul>
					</div>
				</div>
				<div class="footer-bottom">
					<div>&copy; ${year} Happy Construction. All rights reserved.</div>
					<a href="https://www.loganrdavis.com" target="_blank" rel="noopener noreferrer" aria-label="Built by Logan R. Davis">
						<img src="/images/lrd-tag.svg" alt="www.loganrdavis.com" width="2338" height="1080" loading="lazy" decoding="async">
					</a>
				</div>
			</footer>
		`;
	}
}

customElements.define('site-header', SiteHeader);
customElements.define('site-footer', SiteFooter);
