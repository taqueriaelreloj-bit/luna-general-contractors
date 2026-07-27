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

estimateForm?.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!estimateForm.checkValidity()) {
    estimateForm.reportValidity();
    return;
  }

  const data = new FormData(estimateForm);
  const name = data.get("name");
  const phone = data.get("phone");
  const email = data.get("email");
  const service = data.get("service");
  const address = data.get("address");
  const subject = `Free Estimate Request — ${service}`;
  const body = [
    "New estimate request from the Luna General Contractors website",
    "",
    `Full Name: ${name}`,
    `Phone Number: ${phone}`,
    `Email Address: ${email}`,
    `Service Needed: ${service}`,
    `Project Address: ${address}`
  ].join("\n");

  formMessage.textContent =
    "Your estimate request is ready. Please send the email that opens next.";

  window.location.href =
    `mailto:lunabestcontractors@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
});

document.querySelector("#year").textContent = new Date().getFullYear();
