window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}

const googleTag = document.createElement("script");
googleTag.async = true;
googleTag.src = "https://www.googletagmanager.com/gtag/js?id=G-3MGPLXSG14";
document.head.appendChild(googleTag);

gtag("js", new Date());
gtag("config", "G-3MGPLXSG14");

const isSpanishPage = document.documentElement.lang.toLowerCase().startsWith("es");
const isPrivacyPage = window.location.pathname.endsWith("/privacy.html");
const formCopy = isSpanishPage
  ? {
      photoLabel: "Suba fotos del proyecto",
      optional: "(Opcional)",
      photoHelp: "Elija fotos de cualquier tamaño · Se reducirán automáticamente",
      optimizing: "Optimizando fotos...",
      optimizingOne: (current, total) => `Optimizando foto ${current} de ${total}...`,
      preparing: "Preparando sus fotos y solicitud...",
      sending: "Enviando...",
      sendingRequest: "Enviando su solicitud...",
      success: "¡Gracias! Su solicitud y sus fotos se enviaron correctamente. Nos comunicaremos pronto.",
      error: "No pudimos enviar su solicitud. Intente con menos fotos o llame al (817) 784-5998."
    }
  : {
      photoLabel: "Upload Project Photos",
      optional: "(Optional)",
      photoHelp: "Choose photos of any size · They will be resized automatically",
      optimizing: "Optimizing photos...",
      optimizingOne: (current, total) => `Optimizing photo ${current} of ${total}...`,
      preparing: "Preparing your photos and request...",
      sending: "Sending...",
      sendingRequest: "Sending your request...",
      success: "Thank you! Your estimate request and photos were sent successfully. We will contact you soon.",
      error: "We could not send your request. Try fewer photos, or call (817) 784-5998."
    };
const isHomePage =
  window.location.pathname.endsWith("/") ||
  window.location.pathname.endsWith("/index.html") ||
  window.location.pathname.endsWith("/es.html");


// Use one consistent, realistic hero image on every Insurance Claims page.
if (window.location.pathname.toLowerCase().includes("insurance-claims")) {
  const insuranceHero = document.querySelector(".local-hero, .trade-hero");
  if (insuranceHero) {
    insuranceHero.style.setProperty(
      "background",
      "linear-gradient(90deg, rgba(3,5,7,.94) 0%, rgba(3,5,7,.79) 42%, rgba(3,5,7,.25) 72%, rgba(3,5,7,.18) 100%), url('/insurance-claims-hero.webp') center center / cover no-repeat",
      "important"
    );
  }
}

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
          <a href="reviews.html">Reviews</a>
          <a href="index.html#about">About</a>
          <a href="service-areas.html">Service Areas</a>
          <a href="articles.html">Resources</a>
          <a class="language-link" href="es.html" lang="es">Español</a>
          <a href="index.html#estimate-form">Contact</a>
        </nav>

        <div class="header-call">
          <small>Call Now for a Free Estimate</small>
          <a href="tel:+18177845998">☎ (817) 784-5998</a>
          <span>English · <a class="language-inline" href="es.html" lang="es">Español</a></span>
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


// Keep email calls-to-action inside the website instead of opening Outlook.
document.querySelectorAll('a[href^="mailto:"]').forEach((link) => {
  link.setAttribute("href", "#estimate-form");
  link.removeAttribute("target");
  if (/send email|email|lunabestcontractors/i.test(link.textContent)) {
    link.textContent = "Request Online";
  }
  link.setAttribute("aria-label", "Open the online estimate form");
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

/* Add a work slideshow related to each page while preserving the shared DFW gallery. */
const pageMainForWork = document.querySelector("main");
const pageHasItsOwnSlideshow = Boolean(pageMainForWork?.querySelector("[data-gallery]"));
const pageWorkContext = `${window.location.pathname} ${document.title} ${pageMainForWork?.querySelector("h1")?.textContent || ""}`.toLowerCase();
const pageWorkCategory = [
  ["insurance", /insurance|claim|storm damage|damage documentation|scope review/],
  ["mitigation", /mitigation|water damage|restoration|rebuild|fire damage/],
  ["bathroom", /bathroom|shower|bathtub|\btub\b|vanity/],
  ["kitchen", /kitchen|backsplash|cabinet installation/],
  ["flooring", /flooring|\bfloor\b|subfloor|tile installation/],
  ["roofing", /roofing|\broof\b|shingle|flashing|hail damage/],
  ["painting", /painting|\bpaint\b/],
  ["drywall", /drywall|sheetrock|ceiling repair|texture matching/],
  ["siding", /siding|exterior cladding/],
  ["fencing", /fencing|fence replacement|fence repair/],
  ["carpentry", /carpentry|door installation|trim|fireplace|wood slat|pergola|room addition/],
  ["commercial", /commercial|office remodel|tenant improvement|retail/]
].find(([, pattern]) => pattern.test(pageWorkContext))?.[0] || "general";
const pageWorkSlides = {"roofing":[{"src":"dfw-roof-replacement-brick-home-2019.jpg","alt":"Completed shingle roof on a brick home with chimney and backyard pergola","title":"Completed Shingle Roof","description":"Completed shingle roof on a brick home with chimney and backyard pergola"},{"src":"roofing-project-one.jpg","alt":"Shingle roof installation around dormers and intersecting rooflines","title":"Roofline Detail","description":"Shingle roof installation around dormers and intersecting rooflines"},{"src":"dfw-roof-eaves-pergola-2019.jpg","alt":"Finished asphalt shingle roof, gutter and eaves beside a wood pergola","title":"Roof, Gutter & Eaves","description":"Finished asphalt shingle roof, gutter and eaves beside a wood pergola"},{"src":"roofing-project-two.jpg","alt":"Completed residential roofing project by Luna General Contractors","title":"Completed Roof Project","description":"Completed residential roofing project by Luna General Contractors"}],"bathroom":[{"src":"dfw-bathroom-remodel-glass-shower-2020.jpg","alt":"Finished bathroom remodel with glass shower, custom vanity and crystal chandelier","title":"Glass Shower & Custom Vanity","description":"Finished remodel with coordinated tile, glass enclosure, cabinetry and lighting."},{"src":"dfw-bathroom-remodel-finished-2020.jpg","alt":"Custom bathroom vanity, herringbone accent wall and gray craftsman doors","title":"Complete Bathroom Finish","description":"Custom vanity, marble-look top, herringbone accent wall and detailed trim work."},{"src":"dfw-bathroom-remodel-vanity-2020.jpg","alt":"Bathroom vanity with marble countertop, herringbone tile and chrome lighting","title":"Vanity & Accent Wall","description":"Finished cabinetry, countertop, lighting and full-height herringbone tile."},{"src":"bathroom-before-after-shower.jpg.webp","alt":"Bathroom remodel before and after with a frameless glass shower in the DFW area","title":"Custom Shower Transformation","description":"Complete redesign featuring a spacious frameless-glass shower, custom tile and modern fixtures."},{"src":"bathroom-before-after-vanity.jpg.webp","alt":"Bathroom vanity remodel before and after in the DFW area","title":"Vanity & Accent Wall Remodel","description":"Updated vanity, marble-look countertop, new lighting and a full-height herringbone accent wall."},{"src":"bathroom-before-after-tub-shower.jpg.webp","alt":"Tub and walk-in shower remodel before and after in the DFW area","title":"Tub & Walk-In Shower Upgrade","description":"Old shower converted into an open tiled shower with glass enclosure and coordinated tub surround."},{"src":"bathroom-marble-project-progress.webp","alt":"Marble-look bathroom tile and shower installation in the DFW area","title":"Marble-Look Tile Installation","description":"Coordinated floor and wall tile installation with a custom shower bench and detailed layout."},{"src":"bathroom-subway-tile-tub.webp","alt":"White subway-tile bathtub surround remodel in the DFW area","title":"Subway Tile Tub Surround","description":"Bright tub surround with white subway tile, decorative niche and contrasting accent detail."},{"src":"bathroom-double-vanity-finished.webp","alt":"Finished double vanity bathroom remodel in the DFW area","title":"Complete Bathroom Finish","description":"Double vanity, round mirrors, updated fixtures and marble-look flooring create a clean modern finish."},{"src":"bathroom-marble-shower-tub.webp","alt":"Marble-look walk-in shower with black fixtures in the DFW area","title":"Custom Glass Shower","description":"Walk-in shower with marble-look walls, pebble floor, black fixtures and hinged glass door."},{"src":"bathroom-luxury-tub-original.webp","alt":"Luxury tiled soaking-tub bathroom project in the DFW area","title":"Luxury Soaking Tub","description":"Raised soaking tub platform with polished tile, decorative border and a wide curved entry step."},{"src":"bathroom-luxury-tub-enhanced.webp","alt":"Luxury soaking tub with columns and an arched window in the DFW area","title":"Architectural Tub Surround","description":"Custom columns, arched trim and tiled platform frame a bright centerpiece soaking tub."}],"kitchen":[{"src":"dfw-kitchen-remodel-quartz-island-2018.jpg","alt":"White and gray kitchen remodel with oversized quartz island and pendant lighting","title":"Quartz Island Kitchen","description":"White and gray kitchen remodel with oversized quartz island and pendant lighting"},{"src":"kitchen-project-one.jpg","alt":"Remodeled kitchen with white cabinets and large quartz island","title":"Kitchen Remodel","description":"Remodeled kitchen with white cabinets and large quartz island"},{"src":"kitchen-project-two.jpg","alt":"Completed kitchen with quartz countertops and pendant lighting","title":"Finished Kitchen","description":"Completed kitchen with quartz countertops and pendant lighting"},{"src":"kitchen-black-countertops.jpg","alt":"Kitchen remodel with black countertops, white cabinets and commercial-style range","title":"Black Countertop Kitchen","description":"Kitchen remodel with black countertops, white cabinets and commercial-style range"},{"src":"dfw-kitchen-remodel-wood-cabinets-2018.jpg","alt":"Kitchen remodel with wood cabinets, tile backsplash and center island","title":"Wood Cabinet Kitchen","description":"Kitchen remodel with wood cabinets, tile backsplash and center island"}],"flooring":[{"src":"dfw-gray-plank-flooring-installation-2018.jpg","alt":"Finished gray wood-look plank flooring through an open living area in Dallas-Fort Worth","title":"Gray Plank Flooring Installation","description":"Finished gray wood-look plank flooring through an open living area in Dallas-Fort Worth"},{"src":"flooring-before.jpg","alt":"Living area before flooring replacement by Luna General Contractors","title":"Before","description":"Living area before flooring replacement by Luna General Contractors"},{"src":"flooring-after.jpg","alt":"Living area after new flooring installation by Luna General Contractors","title":"After Flooring Installation","description":"Living area after new flooring installation by Luna General Contractors"},{"src":"flooring-tile-completed.jpg","alt":"Completed wood-look tile flooring installation in Dallas-Fort Worth","title":"Wood-Look Tile Floor","description":"Completed wood-look tile flooring installation in Dallas-Fort Worth"},{"src":"dfw-dark-wood-flooring-dining-room-2019.jpg","alt":"Dark wood-look plank flooring installed in a dining room in Dallas-Fort Worth","title":"Dark Wood-Look Dining Room Floor","description":"Dark wood-look plank flooring installed in a dining room in Dallas-Fort Worth"}],"painting":[{"src":"dfw-interior-painting-tray-ceiling-2019.jpg","alt":"Interior painting with crisp white crown molding and a finished tray ceiling in a Dallas-Fort Worth home","title":"Finished Walls, Trim & Tray Ceiling","description":"Interior painting with crisp white crown molding and a finished tray ceiling in a Dallas-Fort Worth home"},{"src":"dfw-interior-painting-surface-protection-2019.jpg","alt":"Protected floors and fixtures during interior painting and trim work in a Dallas-Fort Worth home","title":"Surface Protection & Painting Process","description":"Protected floors and fixtures during interior painting and trim work in a Dallas-Fort Worth home"}],"drywall":[{"src":"drywall-installation.jpg","alt":"Commercial sheetrock installation in progress","title":"Sheetrock Installation","description":"Commercial sheetrock installation in progress"},{"src":"drywall-commercial-project.jpg","alt":"Commercial drywall construction in progress","title":"Commercial Drywall","description":"Commercial drywall construction in progress"},{"src":"demolition-framing-damage.jpg","alt":"Exposed framing and damaged drywall during demolition","title":"Drywall Demolition","description":"Exposed framing and damaged drywall during demolition"}],"siding":[{"src":"siding-tree-damage.jpg","alt":"Tree damage affecting a residential siding project","title":"Tree Damage","description":"Tree damage affecting a residential siding project"},{"src":"siding-before.jpg","alt":"Home exterior during siding installation","title":"During Installation","description":"Home exterior during siding installation"},{"src":"siding-after.jpg","alt":"Home exterior after wood siding installation","title":"Completed Siding","description":"Home exterior after wood siding installation"}],"fencing":[{"src":"fencing-project-one.jpg","alt":"Wood privacy fence project by Luna General Contractors","title":"Wood Privacy Fence","description":"Wood privacy fence project by Luna General Contractors"},{"src":"fencing-project-two.jpg","alt":"Completed stained wood privacy fence","title":"Completed Fence","description":"Completed stained wood privacy fence"},{"src":"fencing-hardware-detail.jpg","alt":"Close-up of heavy-duty galvanized fence post and wood framing hardware","title":"Fence Hardware Detail","description":"Close-up of heavy-duty galvanized fence post and wood framing hardware"}],"carpentry":[{"src":"dfw-custom-media-wall-carpentry-2022.jpg","alt":"Custom black media wall with shaker cabinets and floating wood shelves in a Dallas-Fort Worth home","title":"Custom Media Wall & Floating Shelves","description":"Custom black media wall with shaker cabinets and floating wood shelves in a Dallas-Fort Worth home"},{"src":"dfw-built-in-entertainment-center-2023.jpg","alt":"Built-in entertainment center with base cabinets, vented doors and bookcase towers during installation","title":"Built-In Entertainment Center","description":"Built-in entertainment center with base cabinets, vented doors and bookcase towers during installation"},{"src":"dfw-custom-closet-carpentry-2018.jpg","alt":"White custom closet storage with built-in drawers, shelving and brass hardware","title":"Custom Closet Drawers & Shelving","description":"White custom closet storage with built-in drawers, shelving and brass hardware"},{"src":"dfw-stacked-stone-fireplace-finished-2018.jpg","alt":"Finished floor-to-ceiling stacked-stone fireplace surround in a Dallas-Fort Worth home","title":"Finished Stacked-Stone Fireplace Surround","description":"Finished floor-to-ceiling stacked-stone fireplace surround in a Dallas-Fort Worth home"},{"src":"dfw-stacked-stone-fireplace-progress-2018.jpg","alt":"Stacked-stone fireplace surround during installation with the upper feature wall prepared for completion","title":"Stacked-Stone Fireplace Installation in Progress","description":"Stacked-stone fireplace surround during installation with the upper feature wall prepared for completion"},{"src":"mansfield-fireplace-framing-progress.svg","alt":"Wood framing for a fireplace feature wall in Mansfield Texas by Luna General Contractors","title":"Framing in Progress • Mansfield, TX • Aug. 7, 2026","description":"Wood framing for a fireplace feature wall in Mansfield Texas by Luna General Contractors"},{"src":"mansfield-remodel-protection-progress.svg","alt":"Protected interior work area during fireplace remodeling in Mansfield Texas","title":"Interior Remodeling in Progress • Mansfield, TX • Aug. 7, 2026","description":"Protected interior work area during fireplace remodeling in Mansfield Texas"},{"src":"mansfield-fireplace-paneling-finished.svg","alt":"Finished modern wood slat paneling around an electric fireplace in Mansfield Texas","title":"Finished Wood Slat Paneling • Mansfield, TX • Aug. 7, 2026","description":"Finished modern wood slat paneling around an electric fireplace in Mansfield Texas"}],"mitigation":[{"src":"demolition-wall-opening.jpg","alt":"Interior demolition with wall sheathing and framing exposed","title":"Controlled Demolition","description":"Interior demolition with wall sheathing and framing exposed"},{"src":"dfw-commercial-ceiling-damage-inspection-2024.jpg","alt":"Damaged suspended ceiling opened to inspect wiring, ductwork and the repair scope in a commercial property","title":"Commercial Ceiling Damage Inspection","description":"Damaged suspended ceiling opened to inspect wiring, ductwork and the repair scope in a commercial property"},{"src":"demolition-framing-damage.jpg","alt":"Damaged interior framing exposed during demolition","title":"Damage Assessment","description":"Damaged interior framing exposed during demolition"},{"src":"dfw-interior-rebuild-framing-2018.jpg","alt":"Interior wall and floor framing exposed during a structural reconstruction project","title":"Structural Rebuild in Progress","description":"Interior wall and floor framing exposed during a structural reconstruction project"}],"insurance":[{"src":"dfw-commercial-ceiling-damage-documentation-2024.jpg","alt":"Commercial suspended ceiling damage with exposed wiring and mechanical systems documented for a repair scope","title":"Commercial Ceiling Damage Documentation","description":"Commercial suspended ceiling damage with exposed wiring and mechanical systems documented for a repair scope"},{"src":"dfw-commercial-ceiling-damage-inspection-2024.jpg","alt":"Opened commercial ceiling showing damaged tiles, wiring and ductwork during inspection","title":"Opened Ceiling Assembly for Scope Review","description":"Opened commercial ceiling showing damaged tiles, wiring and ductwork during inspection"},{"src":"dfw-interior-rebuild-framing-2018.jpg","alt":"Interior structural framing exposed during the reconstruction phase of a property repair","title":"Interior Reconstruction in Progress","description":"Interior structural framing exposed during the reconstruction phase of a property repair"}],"commercial":[{"src":"dfw-commercial-concrete-sitework-2020.jpg","alt":"Concrete wall and excavation equipment during commercial site work in Dallas-Fort Worth","title":"Commercial Concrete & Site Work","description":"Concrete wall and excavation equipment during commercial site work in Dallas-Fort Worth"},{"src":"commercial-interior.jpg","alt":"Commercial interior remodeling project by Luna General Contractors in Dallas-Fort Worth","title":"Commercial Interior","description":"Commercial interior remodeling project by Luna General Contractors in Dallas-Fort Worth"},{"src":"commercial-exterior.jpg","alt":"Commercial exterior construction project by Luna General Contractors","title":"Commercial Exterior","description":"Commercial exterior construction project by Luna General Contractors"},{"src":"dfw-commercial-deli-finish-out-2019.jpg","alt":"Deli service counter, cabinets, tile floor and lighting after a commercial finish-out","title":"Deli Counter & Tenant Finish-Out","description":"Deli service counter, cabinets, tile floor and lighting after a commercial finish-out"}],"general":[{"src":"roofing-project-one.jpg","alt":"Shingle roof installation around dormers and intersecting rooflines","title":"Roofline Detail","description":"Shingle roof installation around dormers and intersecting rooflines"},{"src":"dfw-bathroom-remodel-finished-2020.jpg","alt":"Custom bathroom vanity, herringbone accent wall and gray craftsman doors","title":"Complete Bathroom Finish","description":"Custom vanity, marble-look top, herringbone accent wall and detailed trim work."},{"src":"kitchen-project-two.jpg","alt":"Completed kitchen with quartz countertops and pendant lighting","title":"Finished Kitchen","description":"Completed kitchen with quartz countertops and pendant lighting"},{"src":"dfw-dark-wood-flooring-dining-room-2019.jpg","alt":"Dark wood-look plank flooring installed in a dining room in Dallas-Fort Worth","title":"Dark Wood-Look Dining Room Floor","description":"Dark wood-look plank flooring installed in a dining room in Dallas-Fort Worth"},{"src":"dfw-commercial-deli-finish-out-2019.jpg","alt":"Deli service counter, cabinets, tile floor and lighting after a commercial finish-out","title":"Deli Counter & Tenant Finish-Out","description":"Deli service counter, cabinets, tile floor and lighting after a commercial finish-out"}]};
const flooringPageProjects = {"waxahachie-flooring":{"city":"Waxahachie","src":"assets/flooring/floor-concept-01.jpg","alt":"Flooring project completed by Luna General Contractors in Waxahachie, Texas","title":"Flooring Project in Waxahachie, TX","description":"Completed Luna General Contractors flooring work in Waxahachie, Texas.","width":712,"height":960},"red-oak-flooring":{"city":"Red Oak","src":"assets/flooring/floor-concept-02.jpg","alt":"Flooring project completed by Luna General Contractors in Red Oak, Texas","title":"Flooring Project in Red Oak, TX","description":"Completed Luna General Contractors flooring work in Red Oak, Texas.","width":712,"height":960},"ovilla-flooring":{"city":"Ovilla","src":"assets/flooring/floor-concept-03.jpg","alt":"Flooring project completed by Luna General Contractors in Ovilla, Texas","title":"Flooring Project in Ovilla, TX","description":"Completed Luna General Contractors flooring work in Ovilla, Texas.","width":712,"height":960},"glenn-heights-flooring":{"city":"Glenn Heights","src":"assets/flooring/floor-concept-04.jpg","alt":"Flooring project completed by Luna General Contractors in Glenn Heights, Texas","title":"Flooring Project in Glenn Heights, TX","description":"Completed Luna General Contractors flooring work in Glenn Heights, Texas.","width":712,"height":960},"desoto-flooring":{"city":"DeSoto","src":"assets/flooring/floor-concept-05.jpg","alt":"Flooring project completed by Luna General Contractors in DeSoto, Texas","title":"Flooring Project in DeSoto, TX","description":"Completed Luna General Contractors flooring work in DeSoto, Texas.","width":712,"height":960},"lancaster-flooring":{"city":"Lancaster","src":"assets/flooring/floor-concept-06.jpg","alt":"Flooring project completed by Luna General Contractors in Lancaster, Texas","title":"Flooring Project in Lancaster, TX","description":"Completed Luna General Contractors flooring work in Lancaster, Texas.","width":712,"height":960},"cedar-hill-flooring":{"city":"Cedar Hill","src":"assets/flooring/floor-concept-07.jpg","alt":"Flooring project completed by Luna General Contractors in Cedar Hill, Texas","title":"Flooring Project in Cedar Hill, TX","description":"Completed Luna General Contractors flooring work in Cedar Hill, Texas.","width":712,"height":960},"duncanville-flooring":{"city":"Duncanville","src":"assets/flooring/floor-concept-08.jpg","alt":"Flooring project completed by Luna General Contractors in Duncanville, Texas","title":"Flooring Project in Duncanville, TX","description":"Completed Luna General Contractors flooring work in Duncanville, Texas.","width":712,"height":960},"grand-prairie-flooring":{"city":"Grand Prairie","src":"assets/flooring/floor-concept-09.jpg","alt":"Flooring project completed by Luna General Contractors in Grand Prairie, Texas","title":"Flooring Project in Grand Prairie, TX","description":"Completed Luna General Contractors flooring work in Grand Prairie, Texas.","width":712,"height":960},"mansfield-flooring":{"city":"Mansfield","src":"assets/flooring/floor-concept-10.jpg","alt":"Flooring project completed by Luna General Contractors in Mansfield, Texas","title":"Flooring Project in Mansfield, TX","description":"Completed Luna General Contractors flooring work in Mansfield, Texas.","width":712,"height":960},"arlington-flooring":{"city":"Arlington","src":"dfw-dark-wood-flooring-dining-room-2019.jpg","alt":"Dark wood-look flooring project completed by Luna General Contractors in Arlington, Texas","title":"Dark Wood-Look Flooring in Arlington, TX","description":"Completed Luna General Contractors dark wood-look flooring work in Arlington, Texas."},"dallas-flooring":{"city":"Dallas","src":"assets/flooring/floor-concept-12.jpg","alt":"Flooring project completed by Luna General Contractors in Dallas, Texas","title":"Flooring Project in Dallas, TX","description":"Completed Luna General Contractors flooring work in Dallas, Texas.","width":712,"height":960},"fort-worth-flooring":{"city":"Fort Worth","src":"assets/flooring/floor-concept-13.jpg","alt":"Flooring project completed by Luna General Contractors in Fort Worth, Texas","title":"Flooring Project in Fort Worth, TX","description":"Completed Luna General Contractors flooring work in Fort Worth, Texas.","width":712,"height":960},"irving-flooring":{"city":"Irving","src":"assets/flooring/floor-concept-14.jpg","alt":"Flooring project completed by Luna General Contractors in Irving, Texas","title":"Flooring Project in Irving, TX","description":"Completed Luna General Contractors flooring work in Irving, Texas.","width":712,"height":960},"keller-flooring":{"city":"Keller","src":"assets/flooring/floor-concept-15.jpg","alt":"Flooring project completed by Luna General Contractors in Keller, Texas","title":"Flooring Project in Keller, TX","description":"Completed Luna General Contractors flooring work in Keller, Texas.","width":712,"height":960},"lewisville-flooring":{"city":"Lewisville","src":"assets/flooring/floor-concept-16.jpg","alt":"Flooring project completed by Luna General Contractors in Lewisville, Texas","title":"Flooring Project in Lewisville, TX","description":"Completed Luna General Contractors flooring work in Lewisville, Texas.","width":712,"height":960},"mesquite-flooring":{"city":"Mesquite","src":"assets/flooring/floor-concept-17.jpg","alt":"Flooring project completed by Luna General Contractors in Mesquite, Texas","title":"Flooring Project in Mesquite, TX","description":"Completed Luna General Contractors flooring work in Mesquite, Texas.","width":712,"height":960},"garland-flooring":{"city":"Garland","src":"assets/flooring/floor-concept-18.jpg","alt":"Flooring project completed by Luna General Contractors in Garland, Texas","title":"Flooring Project in Garland, TX","description":"Completed Luna General Contractors flooring work in Garland, Texas.","width":712,"height":960},"richardson-flooring":{"city":"Richardson","src":"assets/flooring/floor-concept-19.jpg","alt":"Flooring project completed by Luna General Contractors in Richardson, Texas","title":"Flooring Project in Richardson, TX","description":"Completed Luna General Contractors flooring work in Richardson, Texas.","width":712,"height":960},"plano-flooring":{"city":"Plano","src":"assets/flooring/floor-concept-20.jpg","alt":"Flooring project completed by Luna General Contractors in Plano, Texas","title":"Flooring Project in Plano, TX","description":"Completed Luna General Contractors flooring work in Plano, Texas.","width":712,"height":960},"carrollton-flooring":{"city":"Carrollton","src":"assets/flooring/floor-concept-21.jpg","alt":"Flooring project completed by Luna General Contractors in Carrollton, Texas","title":"Flooring Project in Carrollton, TX","description":"Completed Luna General Contractors flooring work in Carrollton, Texas.","width":712,"height":960},"farmers-branch-flooring":{"city":"Farmers Branch","src":"assets/flooring/floor-concept-22.jpg","alt":"Flooring project completed by Luna General Contractors in Farmers Branch, Texas","title":"Flooring Project in Farmers Branch, TX","description":"Completed Luna General Contractors flooring work in Farmers Branch, Texas.","width":712,"height":960},"frisco-flooring":{"city":"Frisco","src":"assets/flooring/floor-concept-23.jpg","alt":"Flooring project completed by Luna General Contractors in Frisco, Texas","title":"Flooring Project in Frisco, TX","description":"Completed Luna General Contractors flooring work in Frisco, Texas.","width":712,"height":960},"mckinney-flooring":{"city":"McKinney","src":"assets/flooring/floor-concept-24.jpg","alt":"Flooring project completed by Luna General Contractors in McKinney, Texas","title":"Flooring Project in McKinney, TX","description":"Completed Luna General Contractors flooring work in McKinney, Texas.","width":712,"height":960},"allen-flooring":{"city":"Allen","src":"assets/flooring/floor-concept-25.jpg","alt":"Flooring project completed by Luna General Contractors in Allen, Texas","title":"Flooring Project in Allen, TX","description":"Completed Luna General Contractors flooring work in Allen, Texas.","width":712,"height":960},"rockwall-flooring":{"city":"Rockwall","src":"assets/flooring/floor-concept-26.jpg","alt":"Flooring project completed by Luna General Contractors in Rockwall, Texas","title":"Flooring Project in Rockwall, TX","description":"Completed Luna General Contractors flooring work in Rockwall, Texas.","width":712,"height":960},"rowlett-flooring":{"city":"Rowlett","src":"assets/flooring/floor-concept-27.jpg","alt":"Flooring project completed by Luna General Contractors in Rowlett, Texas","title":"Flooring Project in Rowlett, TX","description":"Completed Luna General Contractors flooring work in Rowlett, Texas.","width":712,"height":960},"bedford-flooring":{"city":"Bedford","src":"assets/flooring/floor-concept-28.jpg","alt":"Flooring project completed by Luna General Contractors in Bedford, Texas","title":"Flooring Project in Bedford, TX","description":"Completed Luna General Contractors flooring work in Bedford, Texas.","width":712,"height":960},"euless-flooring":{"city":"Euless","src":"assets/flooring/floor-concept-29.jpg","alt":"Flooring project completed by Luna General Contractors in Euless, Texas","title":"Flooring Project in Euless, TX","description":"Completed Luna General Contractors flooring work in Euless, Texas.","width":712,"height":960},"hurst-flooring":{"city":"Hurst","src":"assets/flooring/floor-concept-30.jpg","alt":"Flooring project completed by Luna General Contractors in Hurst, Texas","title":"Flooring Project in Hurst, TX","description":"Completed Luna General Contractors flooring work in Hurst, Texas.","width":712,"height":960},"north-richland-hills-flooring":{"city":"North Richland Hills","src":"assets/flooring/floor-concept-31.jpg","alt":"Flooring project completed by Luna General Contractors in North Richland Hills, Texas","title":"Flooring Project in North Richland Hills, TX","description":"Completed Luna General Contractors flooring work in North Richland Hills, Texas.","width":712,"height":960},"grapevine-flooring":{"city":"Grapevine","src":"assets/flooring/floor-concept-32.jpg","alt":"Flooring project completed by Luna General Contractors in Grapevine, Texas","title":"Flooring Project in Grapevine, TX","description":"Completed Luna General Contractors flooring work in Grapevine, Texas.","width":712,"height":960},"colleyville-flooring":{"city":"Colleyville","src":"assets/flooring/floor-concept-33.jpg","alt":"Flooring project completed by Luna General Contractors in Colleyville, Texas","title":"Flooring Project in Colleyville, TX","description":"Completed Luna General Contractors flooring work in Colleyville, Texas.","width":712,"height":960},"southlake-flooring":{"city":"Southlake","src":"assets/flooring/floor-concept-34.jpg","alt":"Flooring project completed by Luna General Contractors in Southlake, Texas","title":"Flooring Project in Southlake, TX","description":"Completed Luna General Contractors flooring work in Southlake, Texas.","width":712,"height":960},"coppell-flooring":{"city":"Coppell","src":"assets/flooring/floor-concept-35.jpg","alt":"Flooring project completed by Luna General Contractors in Coppell, Texas","title":"Flooring Project in Coppell, TX","description":"Completed Luna General Contractors flooring work in Coppell, Texas.","width":712,"height":960},"midlothian-flooring":{"city":"Midlothian","src":"assets/flooring/floor-concept-36.jpg","alt":"Flooring project completed by Luna General Contractors in Midlothian, Texas","title":"Flooring Project in Midlothian, TX","description":"Completed Luna General Contractors flooring work in Midlothian, Texas.","width":712,"height":960},"best-flooring-for-pets-grand-prairie":{"city":"Grand Prairie","src":"assets/flooring/floor-concept-37.jpg","alt":"Flooring project completed by Luna General Contractors in Grand Prairie, Texas","title":"Flooring Project in Grand Prairie, TX","description":"Completed Luna General Contractors flooring work in Grand Prairie, Texas.","width":712,"height":960},"flooring-options-mansfield":{"city":"Mansfield","src":"assets/flooring/floor-concept-38.jpg","alt":"Flooring project completed by Luna General Contractors in Mansfield, Texas","title":"Flooring Project in Mansfield, TX","description":"Completed Luna General Contractors flooring work in Mansfield, Texas.","width":712,"height":960},"flooring-subfloor-preparation-allen":{"city":"Allen","src":"assets/flooring/floor-concept-39.jpg","alt":"Flooring project completed by Luna General Contractors in Allen, Texas","title":"Flooring Project in Allen, TX","description":"Completed Luna General Contractors flooring work in Allen, Texas.","width":712,"height":960}};
if (!isHomePage && !isPrivacyPage && pageMainForWork && !pageHasItsOwnSlideshow) {
  const pageWorkSlug = window.location.pathname.split("/").pop().replace(/\.html?$/i, "").toLowerCase();
  const flooringProject = pageWorkCategory === "flooring" ? flooringPageProjects[pageWorkSlug] : null;
  const workImages = flooringProject ? [flooringProject] : (pageWorkSlides[pageWorkCategory] || pageWorkSlides.general);
  const categoryName = pageWorkCategory === "general"
    ? "DFW Project"
    : pageWorkCategory.charAt(0).toUpperCase() + pageWorkCategory.slice(1);
  const spanishWork = isSpanishPage;
  const escapeWorkText = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
  const slideMarkup = workImages.map((photo, index) => `
    <figure class="gallery-slot${index === 0 ? " is-active" : ""}" aria-hidden="${index === 0 ? "false" : "true"}">
      <img src="/${escapeWorkText(photo.src.replace(/^\/+/, ""))}" alt="${escapeWorkText(photo.alt)}" width="${photo.width || 1188}" height="${photo.height || 891}" loading="lazy" decoding="async" />
      <figcaption><strong>${escapeWorkText(photo.title)}</strong><small>${escapeWorkText(photo.description)}</small></figcaption>
    </figure>`).join("");
  const workGallery = document.createElement("section");
  workGallery.className = "section gallery-section page-work-showcase";
  workGallery.setAttribute("aria-labelledby", "page-work-gallery-heading");
  workGallery.innerHTML = `
    <div class="container">
      <div class="section-heading">
        <p class="eyebrow gold">${spanishWork ? "Portafolio de Luna" : "Luna Project Portfolio"}</p>
        <h2 id="page-work-gallery-heading">${spanishWork ? `Trabajos relacionados: ${escapeWorkText(categoryName)}` : `Related ${escapeWorkText(categoryName)} Project Photos`}</h2>
        <p class="gallery-intro">${spanishWork
          ? "Ejemplos reales de trabajos relacionados en Dallas–Fort Worth. Las ciudades aparecen en las descripciones cuando están documentadas."
          : "Examples of related work by Luna General Contractors across Dallas–Fort Worth. Cities appear in captions when documented."}</p>
      </div>
      <div class="project-showcase" data-gallery aria-label="${spanishWork ? "Galería de proyectos relacionados" : "Related project gallery"}">
        <div class="showcase-stage">
          <button class="showcase-arrow showcase-prev" type="button" aria-label="${spanishWork ? "Proyecto anterior" : "Previous project"}">‹</button>
          <div class="trade-gallery" aria-live="polite">${slideMarkup}</div>
          <button class="showcase-arrow showcase-next" type="button" aria-label="${spanishWork ? "Siguiente proyecto" : "Next project"}">›</button>
          <div class="showcase-counter" aria-hidden="true"><span data-current>1</span> / <span data-total>${workImages.length}</span></div>
        </div>
        <div class="showcase-thumbnails" role="tablist" aria-label="${spanishWork ? "Seleccionar un proyecto" : "Select a project"}"></div>
      </div>
      <p class="city-gallery-note">${spanishWork
        ? "Estas fotos pertenecen al portafolio de DFW; solo se atribuyen a una ciudad cuando la descripción lo indica."
        : "These photos come from Luna’s DFW portfolio; they are attributed to a city only when the caption identifies it."}</p>
    </div>`;
  const pageHeroForWork = pageMainForWork.querySelector(".city-hero, .local-hero, .seo-hero, .trade-hero, .service-hero, .hero");
  if (pageHeroForWork) pageHeroForWork.after(workGallery);
  else pageMainForWork.prepend(workGallery);
}

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
    image.alt = "";
    image.loading = "lazy";
    image.decoding = "async";
    const sourceWidth = sourceImage?.getAttribute("width");
    const sourceHeight = sourceImage?.getAttribute("height");
    if (sourceWidth && sourceHeight) {
      image.width = Number(sourceWidth);
      image.height = Number(sourceHeight);
    }
    image.src = sourceImage?.currentSrc || sourceImage?.src || "";
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
if (!isHomePage && !isPrivacyPage && !document.querySelector("#estimate-form")) {
  const globalEstimateSection = document.createElement("section");
  globalEstimateSection.className = "global-estimate-section";
  globalEstimateSection.id = "contact";
  globalEstimateSection.innerHTML = `
    <div class="container global-estimate-wrap">
      <aside class="estimate-card" aria-label="Free estimate form">
        <h2>Get Your Free Estimate</h2>
        <p>Fast, Easy & No Obligation</p>
        <form id="estimate-form" action="https://formspree.io/f/maqrzbol" method="POST">
          <label><span class="sr-only">Full name</span><input type="text" name="name" placeholder="Full Name*" autocomplete="name" required /></label>
          <label><span class="sr-only">Phone number</span><input type="tel" name="phone" placeholder="Phone Number*" autocomplete="tel" inputmode="tel" required /></label>
          <label><span class="sr-only">Email</span><input type="email" name="email" placeholder="Email*" autocomplete="email" required /></label>
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
          <label><span class="sr-only">Project address</span><input type="text" name="address" placeholder="Project Address (Optional)" autocomplete="street-address" /></label>
          <button class="btn btn-gold btn-full" type="submit">Get Free Estimate →</button>
          <small class="privacy">🔒 We respect your privacy. <a href="privacy.html">Privacy notice</a>.</small>
          <p class="form-message" role="status" aria-live="polite"></p>
        </form>
      </aside>
    </div>
  `;
  const main = document.querySelector("main");
  if (main) main.appendChild(globalEstimateSection);
}

// Put a page's single estimate form in its hero when that page has a hero.
const pageMain = document.querySelector("main");
const pageHero = pageMain?.querySelector(".city-hero, .local-hero, .seo-hero, .trade-hero, .service-hero, .hero");
const heroContainer = pageHero?.querySelector(".container");
const estimateAnchor = document.querySelector("#estimate-form");
const pageEstimateForm = estimateAnchor?.matches("form") ? estimateAnchor : estimateAnchor?.querySelector("form");
if (heroContainer && !pageHero.querySelector(".estimate-card") && pageEstimateForm) {
  const existingCard = pageEstimateForm.closest(".estimate-card");
  const card = existingCard || document.createElement("aside");
  if (!existingCard) {
    card.className = "estimate-card";
    card.setAttribute("aria-label", "Free estimate form");
    card.innerHTML = "<h2>Get Your Free Estimate</h2><p>Fast, Easy &amp; No Obligation</p>";
    pageEstimateForm.id = "estimate-form";
    pageEstimateForm.classList.remove("estimate-form");
    card.appendChild(pageEstimateForm);
    const oldEstimateSection = pageEstimateForm.closest(".local-form");
    if (oldEstimateSection?.id === "estimate-form") oldEstimateSection.removeAttribute("id");
  }
  const globalSection = card.closest(".global-estimate-section");
  const heroCopy = document.createElement("div");
  heroCopy.className = "global-hero-copy";
  while (heroContainer.firstChild) heroCopy.appendChild(heroContainer.firstChild);
  heroContainer.classList.add("global-estimate-hero");
  heroContainer.appendChild(heroCopy);
  heroContainer.appendChild(card);
  if (globalSection) globalSection.remove();
  if (!document.querySelector("#contact")) card.id = "contact";
}

// Add the same DFW portfolio gallery to internal pages that do not already have one.
if (!isHomePage && !isPrivacyPage && pageMain && !pageMain.querySelector(".city-gallery, .portfolio-proof, .shared-project-gallery")) {
  const projectGallery = document.createElement("section");
  projectGallery.className = "city-gallery";
  projectGallery.setAttribute("aria-labelledby", "site-project-gallery-heading");
  projectGallery.innerHTML = `
    <div class="container">
      <div class="city-gallery-heading">
        <p class="eyebrow gold">Luna Project Gallery</p>
        <h2 id="site-project-gallery-heading">Recent DFW Project Work</h2>
        <p>Examples of roofing, kitchen, bathroom and flooring work from Luna's Dallas–Fort Worth portfolio.</p>
      </div>
      <div class="city-gallery-grid">
        <figure class="city-gallery-card"><div class="city-gallery-image"><img src="/dfw-roof-replacement-brick-home-2019.jpg" alt="Completed shingle roof on a brick home by Luna General Contractors in DFW" width="1188" height="891" loading="lazy" decoding="async"><span class="city-gallery-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m3 11 9-7 9 7M5.5 9.5V20h13V9.5M10 20v-6h4v6"/></svg></span></div><figcaption><strong>Roof Replacement</strong><span>Completed shingle roof · DFW portfolio</span></figcaption></figure>
        <figure class="city-gallery-card"><div class="city-gallery-image"><img src="/dfw-kitchen-remodel-quartz-island-2018.jpg" alt="Kitchen remodel with quartz island from Luna's DFW portfolio" width="1188" height="891" loading="lazy" decoding="async"><span class="city-gallery-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 10h18M9 10v11M15 10v11"/></svg></span></div><figcaption><strong>Kitchen Remodel</strong><span>Quartz island and updated finishes · DFW portfolio</span></figcaption></figure>
        <figure class="city-gallery-card"><div class="city-gallery-image"><img src="/dfw-bathroom-remodel-glass-shower-2020.jpg" alt="Bathroom remodel with glass shower from Luna's DFW portfolio" width="1188" height="891" loading="lazy" decoding="async"><span class="city-gallery-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 12V6a3 3 0 0 1 6 0M8 6h4M3 12h18v3a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4zM6 19v2M18 19v2"/></svg></span></div><figcaption><strong>Bathroom Remodel</strong><span>Glass shower and coordinated finishes · DFW portfolio</span></figcaption></figure>
        <figure class="city-gallery-card"><div class="city-gallery-image"><img src="/dfw-gray-plank-flooring-installation-2018.jpg" alt="Gray plank flooring installation from Luna's DFW portfolio" width="1188" height="891" loading="lazy" decoding="async"><span class="city-gallery-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m12 3 9 5-9 5-9-5zM3 12l9 5 9-5M3 16l9 5 9-5"/></svg></span></div><figcaption><strong>Flooring Installation</strong><span>Plank flooring and transitions · DFW portfolio</span></figcaption></figure>
      </div>
      <p class="city-gallery-note">These photos show DFW portfolio work and are not represented as projects completed specifically on this page. <a href="projects.html"><strong>View more projects →</strong></a></p>
    </div>
  `;
  const localFormSection = pageMain.querySelector(".local-form");
  if (localFormSection) localFormSection.before(projectGallery);
  else pageMain.appendChild(projectGallery);
}
// Track high-intent lead actions across every page.
document.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (!link || typeof gtag !== "function") return;

  const href = link.getAttribute("href") || "";
  const eventDetails = {
    link_text: link.textContent.trim().replace(/\s+/g, " ").slice(0, 100),
    link_url: link.href,
    page_path: window.location.pathname
  };

  if (href.startsWith("tel:")) {
    event.preventDefault();
    let callOpened = false;
    const openCallLink = () => {
      if (callOpened) return;
      callOpened = true;
      window.location.href = link.href;
    };

    gtag("event", "click_phone", {
      ...eventDetails,
      transport_type: "beacon",
      event_callback: openCallLink
    });

    window.setTimeout(openCallLink, 350);
    return;
  }

  if (
    href === "#estimate-form" ||
    href === "#contact" ||
    href.includes("index.html#estimate-form") ||
    link.closest(".hero-actions, .contact-actions, .trade-cta")
  ) {
    gtag("event", "begin_lead", {
      ...eventDetails,
      event_category: "Lead CTA"
    });
  }
});

// Resize and compress project photos in the browser before upload.
async function optimizeProjectPhoto(file) {
  if (!file.type.startsWith("image/")) return file;

  let source;
  let sourceUrl;
  try {
    if ("createImageBitmap" in window) {
      source = await createImageBitmap(file, { imageOrientation: "from-image" });
    } else {
      sourceUrl = URL.createObjectURL(file);
      source = await new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = reject;
        image.src = sourceUrl;
      });
    }

    const maxDimension = 2000;
    const scale = Math.min(1, maxDimension / Math.max(source.width, source.height));
    const width = Math.max(1, Math.round(source.width * scale));
    const height = Math.max(1, Math.round(source.height * scale));
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    canvas.getContext("2d", { alpha: false }).drawImage(source, 0, 0, width, height);

    const blob = await new Promise((resolve, reject) => {
      canvas.toBlob(
        (result) => result ? resolve(result) : reject(new Error("Image conversion failed")),
        "image/jpeg",
        0.82
      );
    });

    const baseName = file.name.replace(/\.[^.]+$/, "") || "project-photo";
    return new File([blob], `${baseName}-optimized.jpg`, {
      type: "image/jpeg",
      lastModified: Date.now()
    });
  } catch (error) {
    // Keep the original when a browser cannot decode a newer image format.
    return file;
  } finally {
    if (source?.close) source.close();
    if (sourceUrl) URL.revokeObjectURL(sourceUrl);
  }
}

document.querySelectorAll('form[action*="formspree.io"]').forEach((form) => {
  form.enctype = "multipart/form-data";

  if (!form.querySelector('input[type="file"]')) {
    const photoField = document.createElement("label");
    photoField.className = "photo-upload-field";
    photoField.innerHTML = `
      <span>${formCopy.photoLabel} <small>${formCopy.optional}</small></span>
      <input type="file" name="project_photos" accept="image/*" multiple />
      <small class="photo-upload-help">${formCopy.photoHelp}</small>
    `;

    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) form.insertBefore(photoField, submitButton);
    else form.appendChild(photoField);
  }

  if (!isHomePage) {
    const reviewCard = document.createElement("aside");
    reviewCard.className = "form-review-card";
    reviewCard.setAttribute("aria-label", "Customer review");
    reviewCard.innerHTML = `
      <p class="eyebrow gold">Real Customer Review</p>
      <div class="form-review-rating"><strong>5.0</strong><span>★★★★★</span></div>
      <p class="form-review-count">Google rating · 38 reviews</p>
      <blockquote>“Fair price for great work. Definitely recommend them for general repairs and maintenance.”</blockquote>
      <p class="form-review-author">— Nextdoor Neighbor, Grand Prairie, TX</p>
      <a class="btn btn-outline-light" href="reviews.html">Read More Reviews →</a>
    `;

    const localGrid = form.closest(".local-grid");
    const globalWrap = form.closest(".global-estimate-wrap");

    if (localGrid && !localGrid.querySelector(".form-review-card")) {
      const reviewColumn = localGrid.firstElementChild;
      reviewColumn?.appendChild(reviewCard);
      reviewColumn?.classList.add("form-review-column");
    } else if (globalWrap && !globalWrap.querySelector(".form-review-card")) {
      globalWrap.insertBefore(reviewCard, form.closest(".estimate-card") || form);
    }
  }

  let formMessage = form.querySelector(".form-message");
  if (!formMessage) {
    formMessage = document.createElement("p");
    formMessage.className = "form-message";
    formMessage.setAttribute("role", "status");
    formMessage.setAttribute("aria-live", "polite");
    form.appendChild(formMessage);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton?.textContent || "Submit";
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = formCopy.optimizing;
    }
    formMessage.textContent = formCopy.preparing;

    try {
      const formData = new FormData(form);
      const photoInput = form.querySelector('input[type="file"]');
      const photos = [...(photoInput?.files || [])];
      formData.delete("project_photos");

      if (photos.length) {
        const optimizedPhotos = [];
        for (let index = 0; index < photos.length; index += 1) {
          if (submitButton) {
            submitButton.textContent = formCopy.optimizingOne(index + 1, photos.length);
          }
          optimizedPhotos.push(await optimizeProjectPhoto(photos[index]));
        }
        optimizedPhotos.forEach((photo) => formData.append("project_photos", photo, photo.name));
      }

      if (submitButton) submitButton.textContent = formCopy.sending;
      formMessage.textContent = formCopy.sendingRequest;

      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: { Accept: "application/json" }
      });

      if (!response.ok) throw new Error("Submission failed");

      formMessage.textContent = formCopy.success;
      form.reset();

      if (typeof gtag === "function") {
        gtag("event", "generate_lead", {
          event_category: "Estimate Form",
          event_label: "Website Estimate Request"
        });
      }
    } catch (error) {
      formMessage.textContent = formCopy.error;
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }
    }
  });
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
            <a href="reviews.html">Reviews</a>
            <a href="es.html" lang="es">Español</a>
            <a href="index.html#estimate-form">Contact</a>
          </div>

          <div>
            <h3>Service Areas</h3>
            <a href="service-areas.html">View All Service Areas</a>
            <a href="articles.html">Resources</a>
            <a href="dallas.html">Dallas, TX</a>
            <a href="fort-worth.html">Fort Worth, TX</a>
            <a href="midlothian.html">Midlothian, TX</a>
            <a href="mansfield.html">Mansfield, TX</a>
            <a href="arlington.html">Arlington, TX</a>
            <a href="grand-prairie.html">Grand Prairie, TX</a>
            <a href="keller.html">Keller, TX</a>
            <a href="irving.html">Irving, TX</a>
            <a href="lewisville.html">Lewisville, TX</a>
          </div>

          <div>
            <h3>Contact</h3>
            <a href="tel:+18177845998">☎ (817) 784-5998</a>
            <a href="#estimate-form" aria-label="Open the online estimate form">
              Request Online
            </a>
            <a href="https://www.google.com/maps/search/?api=1&amp;query=Luna%20General%20Contractors%2C%204906%20Red%20River%20Trail%2C%20Grand%20Prairie%2C%20TX%2075052" target="_blank" rel="noopener noreferrer">View Our Google Profile</a>
            <span>⌖ Dallas–Fort Worth, TX</span>
            <span>English · <a href="es.html" lang="es">Español</a></span>
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

// Make the mobile phone action explicit instead of relying on an icon alone.
const floatingCall = document.querySelector(".floating-call");
if (floatingCall) {
  floatingCall.dataset.label = isSpanishPage ? "Llamar ahora" : "Call now";
}

// Open every page at its beginning unless the user intentionally selected a homepage section.
window.addEventListener("load", () => {
  const hash = window.location.hash;
  const intentionalHomeSection = isHomePage && hash && !["#home", "#page-top"].includes(hash);
  if (!intentionalHomeSection) {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
  }
});
