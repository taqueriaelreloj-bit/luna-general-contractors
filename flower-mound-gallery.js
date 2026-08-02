(() => {
  const page = window.location.pathname.split("/").pop() || "index.html";
  if (!["kitchens.html", "carpentry.html"].includes(page)) return;

  const gallery = document.querySelector(".trade-gallery");
  if (!gallery) return;

  const readPhotoData = (parts) => parts.map((url) => {
    const request = new XMLHttpRequest();
    request.open("GET", url, false);
    request.send(null);
    if (request.status < 200 || request.status >= 300) {
      throw new Error(`Unable to load ${url}`);
    }
    return request.responseText.trim();
  }).join("");

  const photos = [
    {
      caption: "Flower Mound Kitchen — Before",
      alt: "Kitchen in Flower Mound before cabinet and kitchen remodeling",
      width: 500,
      height: 342,
      parts: [
        "assets/flower-mound/before-webp-01.txt",
        "assets/flower-mound/before-webp-02.txt"
      ]
    },
    {
      caption: "Flower Mound Kitchen — During",
      alt: "Cabinet and kitchen remodeling in progress in Flower Mound",
      width: 366,
      height: 500,
      parts: ["assets/flower-mound/during-webp.txt"]
    },
    {
      caption: "Flower Mound Kitchen — After",
      alt: "Finished white cabinet and quartz kitchen remodel in Flower Mound",
      width: 396,
      height: 500,
      parts: ["assets/flower-mound/after-webp.txt"]
    }
  ];

  const figures = photos.map((photo, index) => {
    const figure = document.createElement("figure");
    figure.className = `gallery-slot${index === 0 ? " is-active" : ""}`;

    const image = document.createElement("img");
    image.src = `data:image/webp;base64,${readPhotoData(photo.parts)}`;
    image.alt = photo.alt;
    image.loading = index === 0 ? "eager" : "lazy";
    image.width = photo.width;
    image.height = photo.height;

    const caption = document.createElement("figcaption");
    caption.textContent = photo.caption;

    figure.append(image, caption);
    return figure;
  });

  if (page === "carpentry.html") {
    gallery.replaceChildren(...figures);
  } else {
    gallery.querySelector(".is-active")?.classList.remove("is-active");
    gallery.prepend(...figures);
  }
})();
