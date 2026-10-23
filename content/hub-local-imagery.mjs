import cloudApproved from './cloud-approved-images.mjs';

const cloudPath = filename => `assets/images/illustrations/cloud-approved-batch-v1/${filename}`;
const cloudImage = image => ({
  file: cloudPath(image.filename),
  width: image.width,
  height: image.height,
  gitBlobSha: image.blobSha,
  alt: image.alt,
  title: image.title,
  caption: image.caption
});
const cloudFor = service => cloudApproved.images.filter(image => image.service === service).map(cloudImage);

export default [
  {
    key: 'roofing',
    file: 'roofing.html',
    sectionId: 'roofing-system-imagery',
    start: '<!-- roofing-hub-illustrations:start -->',
    end: '<!-- roofing-hub-illustrations:end -->',
    context: 'Dallas-Fort Worth',
    serviceTerm: 'roofing',
    eyebrow: '',
    title: 'Roofing Options for Different Building Conditions',
    intro: '',
    visibleCaption: 'Roofing services — Dallas–Fort Worth',
    images: [
      {
        file: 'assets/images/illustrations/roofing-local-batch-v1/standing-seam-limestone-01.png',
        width: 1536,
        height: 1024,
        sha256: 'f02d8b93c414a1c8a27d9ded8379dfd7c481594f29970541cf4604ed3d5f5a50',
        alt: 'Representative generated illustration of a light limestone home with a charcoal standing-seam roof for Dallas-Fort Worth roofing planning.',
        title: 'Standing-seam metal roof',
        caption: 'Representative generated illustration for Dallas-Fort Worth roofing material planning - standing-seam metal shown as a material reference, not a Luna project photo.'
      },
      {
        file: 'assets/images/illustrations/roofing-local-batch-v1/tpo-white-commercial-01.png',
        width: 1536,
        height: 1024,
        sha256: 'b6ad01b88e4961de9964517500f180dc4e71047bb208f1c2dd1e37d2abcbd7f3',
        alt: 'Representative generated illustration of a white single-ply roof with drainage details for Dallas-Fort Worth commercial roofing planning.',
        title: 'White single-ply membrane',
        caption: 'Representative generated illustration for Dallas-Fort Worth roofing material planning - a low-slope membrane reference, not a Luna project photo.'
      },
      {
        file: 'assets/images/illustrations/roofing-local-batch-v1/architectural-shingles-brick-01.png',
        width: 1536,
        height: 1024,
        sha256: 'd9dab423d075756bc4909a624e75b38c7a13e13a1c262bca9194b99418b45379',
        alt: 'Representative generated illustration of a brick home with gray architectural asphalt shingles for Dallas-Fort Worth roofing planning.',
        title: 'Architectural asphalt shingles',
        caption: 'Representative generated illustration for Dallas-Fort Worth roofing material planning - architectural shingles shown as a material reference, not a Luna project photo.'
      },
      {
        file: 'assets/images/illustrations/roofing-local-batch-v1/modified-bitumen-commercial-01.png',
        width: 1672,
        height: 941,
        sha256: '25cc47fc5d82f77bce0e7a05ed2f8d231456a578c3ba37e07fd2314b43e6b4d7',
        alt: 'Representative generated illustration of a granulated modified-bitumen roof for Dallas-Fort Worth commercial roofing planning.',
        title: 'Modified-bitumen roofing',
        caption: 'Representative generated illustration for Dallas-Fort Worth roofing material planning - a granulated low-slope roof reference, not a Luna project photo.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/roofing-local-batch-v1/concrete-tile-residential-01.png',
        width: 1536,
        height: 1024,
        sha256: '921bc846dce2921a0d548035cd8fd2749b3ef0e78c0f1f0d678554027b6329ce',
        alt: 'Representative generated illustration of a stucco home with a terracotta concrete-tile roof for Dallas-Fort Worth roofing planning.',
        title: 'Concrete-tile roof',
        caption: 'Representative generated illustration for Dallas-Fort Worth roofing material planning - concrete tile shown as a material reference, not a Luna project photo.'
      },
      ...cloudFor('roofing')
    ]
  },
  {
    key: 'mitigation',
    file: 'mitigation.html',
    sectionId: 'mitigation-illustrations',
    start: '<!-- mitigation-illustrations:start -->',
    end: '<!-- mitigation-illustrations:end -->',
    context: 'Dallas-Fort Worth',
    serviceTerm: 'water mitigation',
    eyebrow: 'Generated planning illustrations',
    title: 'What Water Mitigation Work Can Involve',
    intro: 'Generated illustrations show Dallas-Fort Worth water mitigation planning contexts. They are not client photos or a diagnosis, work scope, certification, or drying result; equipment and scope depend on site conditions.',
    visibleCaption: 'Water damage mitigation — Dallas–Fort Worth',
    images: [
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/01-living-room-water-extraction.png',
        width: 1672,
        height: 941,
        sha256: '1433d93cbf19acb456fc607de2e29364c08e76554dd1437df2fc80d6fa10f61a',
        alt: 'Representative generated illustration of water-extraction equipment arranged for Dallas-Fort Worth water mitigation planning.',
        title: 'Water extraction planning',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a possible living-room extraction setup, not a Luna project photo or a completed drying result.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/02-bedroom-controlled-drying.png',
        width: 1672,
        height: 941,
        sha256: '2ba36178b59dedad49596cf8f35adfc8c7c386b466781343e96bc8bd05248e11',
        alt: 'Representative generated illustration of air movers and drying equipment for Dallas-Fort Worth water mitigation planning.',
        title: 'Controlled drying setup',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a possible bedroom drying setup; actual equipment and duration depend on site conditions.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/03-kitchen-under-cabinet-drying.png',
        width: 1672,
        height: 941,
        sha256: 'f34feb82bbdb57c1df4a027f581ca79d6e772f48c0fb9988d01d28d2218f6792',
        alt: 'Representative generated illustration of a kitchen with access below cabinetry for Dallas-Fort Worth water mitigation planning.',
        title: 'Under-cabinet access',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a possible under-cabinet drying access concept, not a Luna project photo.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/04-hardwood-drying-mat-system.png',
        width: 1672,
        height: 941,
        sha256: 'ce7911b9ba639dc44632d163ea8ad11bcb234e01a99bb91c263af07280a61769',
        alt: 'Representative generated illustration of a floor-drying mat setup for Dallas-Fort Worth water mitigation planning.',
        title: 'Floor-drying mat setup',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a floor-drying equipment concept; it does not establish a drying result.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/05-laundry-isolated-leak.png',
        width: 1536,
        height: 1024,
        sha256: '656f42b9c8bffc4254c482f291af3f6f2103e6a67fc903cbea2f04d3b10a174b',
        alt: 'Representative generated illustration of an isolated laundry leak area for Dallas-Fort Worth water mitigation planning.',
        title: 'Isolated laundry-area leak',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - an isolated leak-area concept, not a diagnosis or a Luna project photo.'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/06-moisture-meter-inspection.png',
        width: 1536,
        height: 1024,
        sha256: '3d8cc024264e68398cb5e6df82287185f2fce5ba22bf6e1c3374750a36ad6e44',
        alt: 'Representative generated illustration of a meter near an interior surface for Dallas-Fort Worth water mitigation documentation planning.',
        title: 'Moisture documentation',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a documentation reference only, not a diagnosis or measurement result.'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/07-controlled-lower-drywall-opening.png',
        width: 1536,
        height: 1024,
        sha256: 'afcb5ba860e3245812f3587dfa4c1e813845eeda7267d1cbc98c4ea5f14b730e',
        alt: 'Representative generated illustration of a controlled lower-wall opening for Dallas-Fort Worth water mitigation planning.',
        title: 'Lower-wall access',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - an access concept; actual opening and repair scope depend on site conditions.'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/08-ceiling-leak-access-opening.png',
        width: 1672,
        height: 941,
        sha256: '701991908f1e82da27410c6dfe3c4baabbf055aec959659d740d34b402b6c536',
        alt: 'Representative generated illustration of a ceiling access opening for Dallas-Fort Worth water mitigation planning.',
        title: 'Ceiling access opening',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - an access concept, not a diagnosis, repair result, or Luna project photo.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/09-contained-hepa-work-zone.png',
        width: 1672,
        height: 941,
        sha256: '6b44fc9b5de7c770caae3d2fd7c3fb0284031ae1b7ac16e3676b08ef391a8810',
        alt: 'Representative generated illustration of a contained work zone for Dallas-Fort Worth water mitigation planning.',
        title: 'Contained work-zone concept',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a contained work-zone concept, not remediation certification or a Luna project photo.',
        className: 'mi-card--wide'
      },
      {
        file: 'assets/images/illustrations/mitigation-local-batch-v1/10-commercial-corridor-drying.png',
        width: 1672,
        height: 941,
        sha256: '9a4d7132ece20cf1fd7134caf4a7c56e780a9dadda6d8fdaab317301eb3e920e',
        alt: 'Representative generated illustration of drying equipment in a commercial corridor for Dallas-Fort Worth water mitigation planning.',
        title: 'Commercial-corridor drying',
        caption: 'Representative generated illustration for Dallas-Fort Worth water mitigation planning - a possible commercial drying setup; actual conditions and scope vary.',
        className: 'mi-card--wide'
      },
      ...cloudFor('water-mitigation')
    ]
  }
];
