console.log("Candy Shop JS laddat ✅");

// main.js

document.addEventListener('DOMContentLoaded', () => {
  // MENU TOGGLE for mobile nav
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('active');
    });
  }

  // OPTIONAL: Dynamic insert (only if you use placeholders)
  const insertIfPlaceholderExists = (id, html) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  };

  // Main Navigation Bar
  insertIfPlaceholderExists('main-nav-placeholder', `
    <nav class="main-nav">
      <div class="main-nav-container">
        <div class="logo">
          <a href="/">Candy Shop</a>
        </div>
        <button class="menu-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="main-nav-links">
          &#9776;
        </button>
        <ul class="nav-links" id="main-nav-links">
          <li><a href="/">Home</a></li>
          <li><a href="/products/">Products</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
    </nav>
  `);

  // Secondary Navigation Bar
  insertIfPlaceholderExists('secondary-nav-placeholder', `
    <nav class="secondary-nav">
      <div class="secondary-nav-container">
        <ul class="icon-links">
          <li>
            <a href="/gift-certificates/">
              <span class="icon" aria-hidden="true">🎁</span><br />
              Gift Certificates
            </a>
          </li>
          <li>
            <a href="/account/login/">
              <span class="icon" aria-hidden="true">👤</span><br />
              Account
            </a>
          </li>
          <li>
            <a href="/cart/">
              <span class="icon" aria-hidden="true">🛒</span><br />
              Cart
            </a>
          </li>
        </ul>
        <form id="product-search-form" action="/products/" method="get" role="search" aria-label="Search products" class="secondary-search">
          <input type="search" id="search-query" name="q" placeholder="Search products..." required />
          <button type="submit" aria-label="Search">🔍</button>
        </form>
      </div>
    </nav>
  `);

  // Footer
  insertIfPlaceholderExists('footer-placeholder', `
    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-newsletter">
          <h3>Subscribe For Specials</h3>
          <form action="#" class="newsletter-form">
            <input type="email" placeholder="Email Address" aria-label="Email address" required />
            <button type="submit">Subscribe</button>
          </form>
        </div>

        <div class="footer-navs">
          <div class="footer-col">
            <h4>Candy Shop</h4>
            <ul>
              <li><a href="/about/">About Us</a></li>
              <li><a href="/contact/">Contact Us</a></li>
              <li><a href="/products/">Products</a></li>
              <li><a href="/privacy/">Privacy Policy</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Customer Care</h4>
            <ul>
              <li><a href="/shipping/">Shipping & Returns</a></li>
              <li><a href="/terms/">Terms & Conditions</a></li>
              <li><a href="/coupons/">Coupons & Promotions</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Resources</h4>
            <ul>
              <li><a href="/reviews/">Reviews</a></li>
              <li><a href="/blog/">Blog</a></li>
              <li><a href="/videos/">How To Videos</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h4>Follow Us</h4>
            <ul class="footer-social">
              <li><a href="#" aria-label="Facebook">Facebook</a></li>
              <li><a href="#" aria-label="Instagram">Instagram</a></li>
              <li><a href="#" aria-label="YouTube">YouTube</a></li>
            </ul>
          </div>
        </div>

        <div class="footer-credit">
          <p>&copy; 2025 Candy Shop. All rights reserved.</p>
        </div>
      </div>
    </footer>
  `);
});


