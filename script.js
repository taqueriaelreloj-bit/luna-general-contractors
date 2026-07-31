window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}

const googleTag = document.createElement("script");
googleTag.async = true;
googleTag.src = "https://www.googletagmanager.com/gtag/js?id=G-3MGPLXSG14";
document.head.appendChild(googleTag);

gtag("js", new Date());
gtag("config", "G-3MGPLXSG14");const menuToggle = document.querySelector(".menu-toggle");
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
    window.location.href = destination.href;
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
  totalLabel.textContent = String(slides.length);

  const thumbnails = slides.map((slide, index) => {
    const sourceImage = slide.querySelector("img");
    const button = document.createElement("button");
    const image = document.createElement("img");
    button.type = "button";
    button.className = "showcase-thumbnail";
    button.setAttribute("role", "tab");
    button.setAttribute("aria-label", `View project ${index + 1}: ${sourceImage.alt}`);
    image.src = sourceImage.src;
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
    currentLabel.textContent = String(activeIndex + 1);
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
const lightbox = document.createElement("div");
lightbox.className = "gallery-lightbox";
lightbox.setAttribute("aria-hidden", "true");

lightbox.innerHTML = `
  <button class="lightbox-close" type="button" aria-label="Close gallery">×</button>
  <button class="lightbox-arrow lightbox-prev" type="button" aria-label="Previous photo">‹</button>

  <div class="lightbox-content">
    <img class="lightbox-image" src="" alt="" />
    <p class="lightbox-caption"></p>
  </div>

  <button class="lightbox-arrow lightbox-next" type="button" aria-label="Next photo">›</button>
`;

document.body.appendChild(lightbox);

const lightboxImage = lightbox.querySelector(".lightbox-image");
const lightboxCaption = lightbox.querySelector(".lightbox-caption");
const lightboxClose = lightbox.querySelector(".lightbox-close");
const lightboxPrevious = lightbox.querySelector(".lightbox-prev");
const lightboxNext = lightbox.querySelector(".lightbox-next");

let lightboxImages = [];
let lightboxIndex = 0;

function showLightboxPhoto() {
  const image = lightboxImages[lightboxIndex];
  const figure = image.closest(".gallery-slot");

  lightboxImage.src = image.src;
  lightboxImage.alt = image.alt;
  lightboxCaption.textContent =
    figure?.querySelector("figcaption")?.innerText || image.alt;
}

function openLightbox(images, index) {
  lightboxImages = images;
  lightboxIndex = index;
  showLightboxPhoto();

  lightbox.classList.add("is-open");
  lightbox.setAttribute("aria-hidden", "false");
  document.body.classList.add("lightbox-open");
  lightboxClose.focus();
}

function closeLightbox() {
  lightbox.classList.remove("is-open");
  lightbox.setAttribute("aria-hidden", "true");
  document.body.classList.remove("lightbox-open");
}

function changeLightboxPhoto(direction) {
  lightboxIndex =
    (lightboxIndex + direction + lightboxImages.length) %
    lightboxImages.length;

  showLightboxPhoto();
}

document.querySelectorAll("[data-gallery]").forEach((gallery) => {
  const images = [...gallery.querySelectorAll(".gallery-slot img")];

  images.forEach((image, index) => {
    image.tabIndex = 0;
    image.setAttribute("role", "button");
    image.setAttribute("aria-label", `Enlarge photo: ${image.alt}`);

    image.addEventListener("click", () => openLightbox(images, index));

    image.addEventListener("keydown", (event) => {
      if (event.key === "Enter") openLightbox(images, index);
    });
  });
});

lightboxClose.addEventListener("click", closeLightbox);
lightboxPrevious.addEventListener("click", () => changeLightboxPhoto(-1));
lightboxNext.addEventListener("click", () => changeLightboxPhoto(1));

lightbox.addEventListener("click", (event) => {
  if (event.target === lightbox) closeLightbox();
});

document.addEventListener("keydown", (event) => {
  if (!lightbox.classList.contains("is-open")) return;

  if (event.key === "Escape") closeLightbox();
  if (event.key === "ArrowLeft") changeLightboxPhoto(-1);
  if (event.key === "ArrowRight") changeLightboxPhoto(1);
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
  formMessage.textContent = "Sending your request...";

  try {
    const response = await fetch("https://formspree.io/f/maqrzbol", {
      method: "POST",
      body: new FormData(estimateForm),
      headers: {
        Accept: "application/json"
      }
    });

    if (!response.ok) throw new Error("Submission failed");

    formMessage.textContent =
      "Thank you! Your estimate request was sent successfully. We will contact you soon.";

    estimateForm.reset();

    if (typeof gtag === "function") {
      gtag("event", "generate_lead", {
        event_category: "Estimate Form",
        event_label: "Website Estimate Request"
      });
    }
  } catch (error) {
    formMessage.textContent =
      "We could not send your request. Please call (817) 784-5998 or try again.";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = originalText;
  }
});

document.querySelector("#year").textContent = new Date().getFullYear();

// Add the complete footer to every service page
const isHomePage =
  window.location.pathname.endsWith("/") ||
  window.location.pathname.endsWith("/index.html");

if (!isHomePage) {
  const existingFooter = document.querySelector("footer");

  if (existingFooter) {
    existingFooter.outerHTML = `
      <footer class="site-footer">
        <div class="container footer-grid">
          <div class="footer-brand">
            <a class="brand" href="index.html#home">
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
            <a href="index.html#projects">Projects</a>
            <a href="index.html#reviews">Reviews</a>
            <a href="index.html#estimate-form">Contact</a>
          </div>

          <div>
            <h3>Service Areas</h3>
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
