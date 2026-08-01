window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}

const googleTag = document.createElement("script");
googleTag.async = true;
googleTag.src = "https://www.googletagmanager.com/gtag/js?id=G-3MGPLXSG14";
document.head.appendChild(googleTag);

gtag("js", new Date());
gtag("config", "G-3MGPLXSG14");

const isHomePage =
  window.location.pathname.endsWith("/") ||
  window.location.pathname.endsWith("/index.html");

// Prevent browsers from restoring an old scroll position halfway down a page.
if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}

// Every internal page uses the same complete header and navigation.
if (!isHomePage) {
  const existingHeader = document.querySelector("header.site-header, body > header");
  const standardHeader = `
    <header class="site-header" id="page-top">
      <div class="topbar container">
        <a class="brand" href="index.html" aria-label="Luna General Contractors home">
          <span class="brand-moon" aria-hidden="true"></span>
          <span class="brand-copy">
            <strong>LUNA</strong>
            <small>GENERAL CONTRACTORS</small>
            <em>Roofing • Remodeling • Restoration</em>
          </span>
        </a>

        <button class="menu-toggle" aria-label="Open navigation menu" aria-expanded="false">
          <span></span><span></span><span></span>
        </button>

        <nav class="main-nav" aria-label="Main navigation">
          <a href="index.html">Home</a>
          <a href="index.html#services">Services</a>
          <a href="projects.html">Projects</a>
          <a href="index.html#reviews">Reviews</a>
          <a href="index.html#about">About</a>
          <a href="service-areas.html">Service Areas</a>
          <a href="articles.html">Resources</a>
          <a href="index.html#estimate-form">Contact</a>
        </nav>

        <div class="header-call">
          <small>Call Now for a Free Estimate</small>
          <a href="tel:+18177845998">☎ (817) 784-5998</a>
          <span>English & Spanish</span>
        </div>
      </div>
      <nav class="trade-bar" aria-label="Trade pages">
        <div class="trade-bar-inner">
          <a href="roofing.html">Roofing</a>
          <a href="mitigation.html">Mitigation</a>
          <a href="insurance-claims.html">Insurance Claims</a>
          <a href="kitchens.html">Kitchen</a>
          <a href="bathrooms.html">Bathroom</a>
          <a href="flooring.html">Flooring</a>
          <a href="painting.html">Painting</a>
          <a href="drywall.html">Drywall</a>
          <a href="siding.html">Siding</a>
          <a href="carpentry.html">Carpentry</a>
          <a href="fencing.html">Fencing</a>
          <a href="commercial.html">Commercial</a>
        </div>
      </nav>
    </header>
  `;

  if (existingHeader) {
    existingHeader.outerHTML = standardHeader;
  } else {
    document.body.insertAdjacentHTML("afterbegin", standardHeader);
  }
}

// Links to another HTML page always open at that page's beginning.
document.querySelectorAll('a[href*=".html#"]').forEach((link) => {
  const rawHref = link.getAttribute("href");
  if (!rawHref) return;
  const [page, fragment] = rawHref.split("#");

  // Keep intentional homepage section links, but never attach a gallery/photo fragment
  // to a separate service, city, article or project page.
  if (page && page !== "index.html") {
    link.setAttribute("href", page);
  } else if (page === "index.html" && ["gallery", "photos", "projects-gallery"].includes(fragment)) {
    link.setAttribute("href", "index.html");
  }
});

const menuToggle = document.querySelector(".menu-toggle");
const mainNav = document.querySelector(".main-nav");
const navLinks = document.querySelectorAll(".main-nav a");

document.querySelectorAll('a[href="index.html#contact"]').forEach((link) => {
  link.setAttribute("href", "index.html#estimate-form");
});

menuToggle?.addEventListener("click", () => {
  const isOpen = mainNav.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    mainNav.classList.remove("open");
    menuToggle?.setAttribute("aria-expanded", "false");
  });
});

document.querySelectorAll(".service-card").forEach((card) => {
  const destination = card.querySelector('a[href$=".html"]');
  if (!destination) return;

  card.classList.add("clickable-card");
  card.setAttribute("role", "link");
  card.setAttribute("tabindex", "0");
  card.setAttribute("aria-label", `Open ${card.querySelector("h3")?.textContent || "service"} page`);

  const openServicePage = () => {
    window.location.href = destination.href.split("#")[0];
  };

  card.addEventListener("click", (event) => {
    if (event.target.closest("a")) return;
    openServicePage();
  });

  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openServicePage();
    }
  });
});

document.querySelectorAll("[data-gallery]").forEach((gallery) => {
  const slides = [...gallery.querySelectorAll(".gallery-slot")];
  const previousButton = gallery.querySelector(".showcase-prev");
  const nextButton = gallery.querySelector(".showcase-next");
  const thumbnailRow = gallery.querySelector(".showcase-thumbnails");
  const currentLabel = gallery.querySelector("[data-current]");
  const totalLabel = gallery.querySelector("[data-total]");
  let activeIndex = 0;
  let autoplayTimer;

  if (!slides.length || !thumbnailRow) return;
  if (totalLabel) totalLabel.textContent = String(slides.length);

  const thumbnails = slides.map((slide, index) => {
    const sourceImage = slide.querySelector("img");
    const button = document.createElement("button");
    const image = document.createElement("img");
    button.type = "button";
    button.className = "showcase-thumbnail";
    button.setAttribute("role", "tab");
    button.setAttribute("aria-label", `View project ${index + 1}: ${sourceImage?.alt || "project image"}`);
    image.src = sourceImage?.src || "";
    image.alt = "";
    button.appendChild(image);
    button.addEventListener("click", () => showSlide(index, true));
    thumbnailRow.appendChild(button);
    return button;
  });

  function showSlide(index, restartAutoplay = false) {
    activeIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === activeIndex;
      slide.classList.toggle("is-active", isActive);
      slide.setAttribute("aria-hidden", String(!isActive));
    });
    thumbnails.forEach((thumbnail, thumbnailIndex) => {
      const isActive = thumbnailIndex === activeIndex;
      thumbnail.classList.toggle("is-active", isActive);
      thumbnail.setAttribute("aria-selected", String(isActive));
      thumbnail.tabIndex = isActive ? 0 : -1;
    });
    if (currentLabel) currentLabel.textContent = String(activeIndex + 1);
    thumbnails[activeIndex].scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
    if (restartAutoplay) startAutoplay();
  }

  function startAutoplay() {
    window.clearInterval(autoplayTimer);
    autoplayTimer = window.setInterval(() => showSlide(activeIndex + 1), 6500);
  }

  previousButton?.addEventListener("click", () => showSlide(activeIndex - 1, true));
  nextButton?.addEventListener("click", () => showSlide(activeIndex + 1, true));
  gallery.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") showSlide(activeIndex - 1, true);
    if (event.key === "ArrowRight") showSlide(activeIndex + 1, true);
  });
  gallery.addEventListener("mouseenter", () => window.clearInterval(autoplayTimer));
  gallery.addEventListener("mouseleave", startAutoplay);
  gallery.addEventListener("focusin", () => window.clearInterval(autoplayTimer));
  gallery.addEventListener("focusout", startAutoplay);

  showSlide(0);
  startAutoplay();
});

const sections = [...document.querySelectorAll("main section[id], header[id]")];

function updateActiveNav() {
  const scrollPosition = window.scrollY + 130;
  let currentId = "home";

  sections.forEach((section) => {
    if (section.offsetTop <= scrollPosition) {
      currentId = section.id;
    }
  });

  navLinks.forEach((link) => {
    link.classList.toggle(
      "active",
      link.getAttribute("href") === `#${currentId}`
    );
  });
}

window.addEventListener("scroll", updateActiveNav, { passive: true });
updateActiveNav();

const filterButtons = document.querySelectorAll(".project-filters button");
const projectCards = document.querySelectorAll(".project-card");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const selected = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");

    projectCards.forEach((card) => {
      const match = selected === "all" || card.dataset.category === selected;
      card.classList.toggle("hidden", !match);
    });
  });
});

// Make the complete lead form available on every internal page.
if (!isHomePage && !document.querySelector("#estimate-form")) {
  const globalEstimateSection = document.createElement("section");
  globalEstimateSection.className = "global-estimate-section";
  globalEstimateSection.id = "contact";
  globalEstimateSection.innerHTML = `
    <div class="container global-estimate-wrap">
      <aside class="estimate-card" aria-label="Free estimate form">
        <h2>Get Your Free Estimate</h2>
        <p>Fast, Easy & No Obligation</p>
        <form id="estimate-form" action="https://formspree.io/f/maqrzbol" method="POST">
          <label><span class="sr-only">Full name</span><input type="text" name="name" placeholder="Full Name*" required /></label>
          <label><span class="sr-only">Phone number</span><input type="tel" name="phone" placeholder="Phone Number*" required /></label>
          <label><span class="sr-only">Email</span><input type="email" name="email" placeholder="Email*" required /></label>
          <label>
            <span class="sr-only">Service needed</span>
            <select name="service" required>
              <option value="">Service Needed*</option>
              <option>Roofing</option><option>Remodeling</option><option>Kitchen Remodeling</option>
              <option>Bathroom Remodeling</option><option>Water Damage Mitigation</option>
              <option>Insurance Claims</option><option>Flooring</option><option>Painting</option>
              <option>Drywall</option><option>Siding</option><option>Carpentry</option>
              <option>Fencing</option><option>Concrete</option><option>Commercial</option><option>Other</option>
            </select>
          </label>
          <label><span class="sr-only">Project address</span><input type="text" name="address" placeholder="Project Address*" required /></label>
          <button class="btn btn-gold btn-full" type="submit">Get Free Estimate →</button>
          <small class="privacy">🔒 We respect your privacy.</small>
          <p class="form-message" role="status" aria-live="polite"></p>
        </form>
      </aside>
    </div>
  `;
  const main = document.querySelector("main");
  if (main) main.appendChild(globalEstimateSection);
}

const estimateForm = document.querySelector("#estimate-form");
const formMessage = document.querySelector(".form-message");

estimateForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!estimateForm.checkValidity()) {
    estimateForm.reportValidity();
    return;
  }

  const submitButton = estimateForm.querySelector('button[type="submit"]');
  const originalText = submitButton.textContent;

  submitButton.disabled = true;
  submitButton.textContent = "Sending...";
  if (formMessage) formMessage.textContent = "Sending your request...";

  try {
    const response = await fetch("https://formspree.io/f/maqrzbol", {
      method: "POST",
      body: new FormData(estimateForm),
      headers: {
        Accept: "application/json"
      }
    });

    if (!response.ok) throw new Error("Submission failed");

    if (formMessage) {
      formMessage.textContent =
        "Thank you! Your estimate request was sent successfully. We will contact you soon.";
    }

    estimateForm.reset();

    if (typeof gtag === "function") {
      gtag("event", "generate_lead", {
        event_category: "Estimate Form",
        event_label: "Website Estimate Request"
      });
    }
  } catch (error) {
    if (formMessage) {
      formMessage.textContent =
        "We could not send your request. Please call (817) 784-5998 or try again.";
    }
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = originalText;
  }
});

const year = document.querySelector("#year");
if (year) year.textContent = new Date().getFullYear();

// Add the complete footer to every service page
if (!isHomePage) {
  const existingFooter = document.querySelector("footer");

  if (existingFooter) {
    existingFooter.outerHTML = `
      <footer class="site-footer">
        <div class="container footer-grid">
          <div class="footer-brand">
            <a class="brand" href="index.html">
              <span class="brand-moon" aria-hidden="true"></span>
              <span class="brand-copy">
                <strong>LUNA</strong>
                <small>GENERAL CONTRACTORS</small>
                <em>Roofing • Remodeling • Restoration</em>
              </span>
            </a>

            <p>
              Quality construction and restoration for homes and
              businesses across Dallas–Fort Worth.
            </p>

            <small>
              © <span id="footer-year"></span> Luna General Contractors.
              All rights reserved.
            </small>
          </div>

          <div>
            <h3>Services</h3>
            <a href="roofing.html">Roofing</a>
            <a href="kitchens.html">Kitchens</a>
            <a href="bathrooms.html">Bathrooms</a>
            <a href="flooring.html">Flooring</a>
            <a href="mitigation.html">Mitigation</a>
            <a href="insurance-claims.html">Insurance Claims</a>
            <a href="painting.html">Painting</a>
            <a href="drywall.html">Drywall</a>
            <a href="siding.html">Siding</a>
            <a href="carpentry.html">Carpentry</a>
            <a href="fencing.html">Fencing</a>
            <a href="commercial.html">Commercial</a>
          </div>

          <div>
            <h3>Company</h3>
            <a href="index.html#about">About Us</a>
            <a href="projects.html">Projects</a>
            <a href="index.html#reviews">Reviews</a>
            <a href="index.html#estimate-form">Contact</a>
          </div>

          <div>
            <h3>Service Areas</h3>
            <a href="service-areas.html">View All Service Areas</a>
            <a href="articles.html">Resources</a>
            <a href="index.html#estimate-form">Dallas, TX</a>
            <a href="index.html#estimate-form">Fort Worth, TX</a>
            <a href="index.html#estimate-form">Midlothian, TX</a>
            <a href="index.html#estimate-form">Mansfield, TX</a>
            <a href="index.html#estimate-form">Arlington, TX</a>
            <a href="index.html#estimate-form">Grand Prairie, TX</a>
            <a href="index.html#estimate-form">Keller, TX</a>
            <a href="index.html#estimate-form">Irving, TX</a>
            <a href="index.html#estimate-form">Lewisville, TX</a>
          </div>

          <div>
            <h3>Contact</h3>
            <a href="tel:+18177845998">☎ (817) 784-5998</a>
            <a href="mailto:lunabestcontractors@gmail.com">
              ✉ lunabestcontractors@gmail.com
            </a>
            <span>⌖ Dallas–Fort Worth, TX</span>
            <span>English & Spanish</span>
          </div>
        </div>
      </footer>
    `;

    const footerYear = document.querySelector("#footer-year");
    if (footerYear) {
      footerYear.textContent = new Date().getFullYear();
    }
  }
}

// Open every page at its beginning unless the user intentionally selected a homepage section.
window.addEventListener("load", () => {
  const hash = window.location.hash;
  const intentionalHomeSection = isHomePage && hash && !["#home", "#page-top"].includes(hash);
  if (!intentionalHomeSection) {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
  }
});
