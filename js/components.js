// Shared chrome. Every page includes <script src="/js/components.js" defer> and
// drops <site-header> / <site-footer> into the body. Active nav state is derived
// from window.location.pathname, so all hrefs are absolute and extensionless.

const NAV_LINKS = [
	{ href: '/', label: 'Home' },
	{ href: '/services', label: 'Services' },
	{ href: '/projects', label: 'Projects' },
	{ href: '/about', label: 'About' },
	{ href: '/contact', label: 'Contact' },
];

// PLACEHOLDER. See CLAUDE.md > "Placeholders". Nothing here is confirmed.
const PHONE_DISPLAY = '(555) 555-5555';
const PHONE_TEL = '+15555555555';
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

function currentPath() {
	let p = window.location.pathname;
	if (p === '' || p === '/') return '/';
	return p.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
}

function activeClass(href) {
	return currentPath() === href ? 'active' : '';
}

class SiteHeader extends HTMLElement {
	connectedCallback() {
		const navItems = NAV_LINKS.map(
			(l) => `<li><a href="${l.href}" class="${activeClass(l.href)}">${l.label}</a></li>`
		).join('');

		const mobileNavItems = NAV_LINKS.map(
			(l) => `<li class="mobile-menu-li"><a href="${l.href}" class="${activeClass(l.href)}">${l.label}</a></li>`
		).join('');

		this.innerHTML = `
			<a href="#main-content" class="skip-link">Skip to main content</a>
			<header>
				<div id="headerContent">
					<a href="/" class="header-logo-link" aria-label="Happy Construction home">
						${logoPicture('dark', 'class="header-logo" fetchpriority="high"')}
					</a>

					<button class="hamburger-icon" aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="mobile-menu-container">
						<div class="bar1"></div>
						<div class="bar2"></div>
						<div class="bar3"></div>
					</button>

					<div class="desktop-menu">
						<nav aria-label="Primary">
							<ul>
								${navItems}
							</ul>
						</nav>
					</div>

					<a href="tel:${PHONE_TEL}" class="header-phone" aria-label="Call ${PHONE_DISPLAY}">${PHONE_DISPLAY}</a>

					<div class="mobile-menu-container" id="mobile-menu-container" aria-hidden="true">
						<button class="mobile-menu-outside" aria-label="Close navigation menu" tabindex="-1"></button>
						<div class="mobile-menu" id="mobile-menu">
							<nav class="mobile-menu-nav" aria-label="Mobile">
								<ul>
									${mobileNavItems}
									<li class="mobile-menu-cta"><a href="/contact" class="btn">Start a Project</a></li>
								</ul>
							</nav>
						</div>
					</div>
				</div>
			</header>
		`;

		const headerContent = this.querySelector('#headerContent');
		const hamburger = this.querySelector('.hamburger-icon');
		const menuContainer = this.querySelector('#mobile-menu-container');
		const outsideButton = this.querySelector('.mobile-menu-outside');

		const openMenu = () => {
			hamburger.setAttribute('aria-expanded', 'true');
			menuContainer.setAttribute('aria-hidden', 'false');
			headerContent.classList.add('hamburger-icon-click');
			document.body.style.overflow = 'hidden';
			const firstLink = this.querySelector('.mobile-menu-nav a');
			if (firstLink) firstLink.focus();
		};

		const closeMenu = () => {
			hamburger.setAttribute('aria-expanded', 'false');
			menuContainer.setAttribute('aria-hidden', 'true');
			headerContent.classList.remove('hamburger-icon-click');
			document.body.style.overflow = '';
			hamburger.focus();
		};

		hamburger.addEventListener('click', () => {
			const isOpen = hamburger.getAttribute('aria-expanded') === 'true';
			if (isOpen) closeMenu();
			else openMenu();
		});

		outsideButton.addEventListener('click', closeMenu);

		document.addEventListener('keydown', (e) => {
			if (e.key === 'Escape' && hamburger.getAttribute('aria-expanded') === 'true') {
				closeMenu();
			}
		});
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
						<p>Commercial general contractor. Placeholder positioning line, pending confirmation of scope and service area.</p>
					</div>
					<div class="footer-col">
						<h4>Explore</h4>
						<ul>
							<li><a href="/services">Services</a></li>
							<li><a href="/projects">Projects</a></li>
							<li><a href="/about">About</a></li>
							<li><a href="/contact">Contact</a></li>
						</ul>
					</div>
					<div class="footer-col">
						<h4>Contact</h4>
						<ul>
							<li><a href="tel:${PHONE_TEL}">${PHONE_DISPLAY}</a></li>
							<li><a href="mailto:${EMAIL}">${EMAIL}</a></li>
						</ul>
					</div>
					<div class="footer-col">
						<h4>Service Areas</h4>
						<ul>
							<li>Placeholder region</li>
							<li>Placeholder region</li>
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
