import cloudApproved from './cloud-approved-images.mjs';

const cloudDirectory = 'assets/images/illustrations/cloud-approved-batch-v1';
const cloudByFilename = new Map(cloudApproved.images.map(image => [image.filename, image]));

function cloud(filename) {
  const image = cloudByFilename.get(filename);
  if (!image) throw new Error(`Missing approved cloud image metadata: ${filename}`);
  return {
    file: `${cloudDirectory}/${filename}`,
    width: image.width,
    height: image.height,
    gitBlobSha: image.blobSha,
    title: image.title,
    alt: image.alt,
    caption: image.caption
  };
}

function local({ file, width, height, sha256, title, alt, caption }) {
  return { file, width, height, sha256, title, alt, caption };
}

export default [
  {
    file: 'kitchens.html',
    id: 'additional-kitchen-imagery',
    serviceTerm: 'kitchen remodeling',
    title: 'More Kitchen Remodeling Planning Scenes',
    intro: 'These representative generated illustrations support Dallas-Fort Worth kitchen remodeling planning. They are not Luna project photos, product photographs, or evidence of work in a particular city.',
    images: [
      cloud('cabinetry-generated-illustration.png'),
      cloud('quartz-generated-illustration.png'),
      cloud('tile-flooring-generated-illustration.png'),
      local({
        file: 'assets/images/illustrations/interior-services-local-batch-v1/03-tile-backsplash-craftsmanship.png',
        width: 1536,
        height: 1024,
        sha256: 'd72c6828cdd2ba77daee75819ded31e1e9a965c49031e50c8079247bfa208656',
        title: 'Tile backsplash planning',
        alt: 'Representative generated illustration of tile backsplash craftsmanship for Dallas-Fort Worth kitchen remodeling planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth kitchen remodeling planning - a backsplash-work context, not a Luna project photo or a product photograph.'
      })
    ]
  },
  {
    file: 'bathrooms.html',
    id: 'additional-bathroom-imagery',
    serviceTerm: 'bathroom remodeling',
    title: 'Bathroom Remodeling Planning Scene',
    intro: 'This representative generated illustration supports Dallas-Fort Worth bathroom remodeling planning. It is not a Luna project photo or evidence of work in a particular city.',
    images: [
      local({
        file: 'assets/images/illustrations/interior-services-local-batch-v1/02-bathroom-remodel-not-hero.png',
        width: 1672,
        height: 941,
        sha256: '246b729f6c5120e22a8e75448d696ad30c5c5de6ac5df7ace48cde5896bdf735',
        title: 'Bathroom remodeling planning',
        alt: 'Representative generated illustration of a secondary bathroom remodeling scene for Dallas-Fort Worth bathroom remodeling planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth bathroom remodeling planning - not a Luna project photo or evidence of work in a particular city.'
      })
    ]
  },
  {
    file: 'carpentry.html',
    id: 'additional-carpentry-imagery',
    serviceTerm: 'carpentry',
    title: 'Carpentry and Outdoor Structure Planning Scenes',
    intro: 'These representative generated illustrations support Dallas-Fort Worth carpentry planning, including built-ins and exterior wood structures. They are not Luna project photos or evidence of work in a particular city.',
    images: [
      local({
        file: 'assets/images/illustrations/interior-services-local-batch-v1/04-built-in-cabinetry-bookcases.png',
        width: 1672,
        height: 941,
        sha256: '13dd0590c46891ac69f17064d2d76684ac523539bbc9ee8f022999a587c67893',
        title: 'Built-in cabinetry planning',
        alt: 'Representative generated illustration of built-in cabinetry and bookcases for Dallas-Fort Worth carpentry planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth carpentry planning - built-in cabinetry context, not a Luna project photo or evidence of work in a particular city.'
      }),
      local({
        file: 'assets/images/illustrations/exterior-services-local-batch-v1/covered-patio-structure-01.png',
        width: 1536,
        height: 1024,
        sha256: 'fb88557c16ed90496f44c1ea81ba610158d8e4cc8618e3b68dbfe8cc8be2c0af',
        title: 'Covered patio structure planning',
        alt: 'Representative generated illustration of a covered patio structure for Dallas-Fort Worth carpentry planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth carpentry planning - covered-patio structure context, not a Luna project photo or evidence of work in a particular city.'
      }),
      local({
        file: 'assets/images/illustrations/exterior-services-local-batch-v1/cedar-pergola-01.png',
        width: 1536,
        height: 1024,
        sha256: '257b4ca75d5efd00c7a2c9ea6bd27ab9427a4a99f290bab1f1664315adcda8c3',
        title: 'Cedar pergola planning',
        alt: 'Representative generated illustration of a cedar pergola for Dallas-Fort Worth carpentry planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth carpentry planning - pergola context, not a Luna project photo or evidence of work in a particular city.'
      })
    ]
  },
  {
    file: 'painting.html',
    id: 'additional-painting-imagery',
    serviceTerm: 'painting',
    title: 'Interior Painting Planning Scene',
    intro: 'This representative generated illustration supports Dallas-Fort Worth interior painting planning. It is not a Luna project photo or evidence of work in a particular city.',
    images: [
      local({
        file: 'assets/images/illustrations/interior-services-local-batch-v1/05-finished-painted-room.png',
        width: 1536,
        height: 1024,
        sha256: '04494ab8feea98aa8d5570103d1ba6c3ea90d3d8fbd2583c082a87ca5a2046d8',
        title: 'Finished-room planning',
        alt: 'Representative generated illustration of a finished painted room for Dallas-Fort Worth interior painting planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth interior painting planning - a finished-room context, not a Luna project photo or evidence of work in a particular city.'
      })
    ]
  },
  {
    file: 'siding.html',
    id: 'additional-siding-imagery',
    serviceTerm: 'siding',
    title: 'Siding and Trim Planning Scene',
    intro: 'This representative generated illustration supports Dallas-Fort Worth siding planning. It is not a Luna project photo or evidence of work in a particular city.',
    images: [
      local({
        file: 'assets/images/illustrations/exterior-services-local-batch-v1/siding-and-trim-house-01.png',
        width: 1536,
        height: 1024,
        sha256: '03fe309612fd4a91d9a1480ad1040d93e2a53b4806a9d1d1fcaebb11bddfe88e',
        title: 'Siding and trim planning',
        alt: 'Representative generated illustration of siding and trim for Dallas-Fort Worth siding planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth siding planning - siding-and-trim context, not a Luna project photo or evidence of work in a particular city.'
      })
    ]
  },
  {
    file: 'fencing.html',
    id: 'additional-fencing-imagery',
    serviceTerm: 'fencing',
    title: 'Cedar Fence Planning Scene',
    intro: 'This representative generated illustration supports Dallas-Fort Worth fencing planning. It is not a Luna project photo or evidence of work in a particular city.',
    images: [
      local({
        file: 'assets/images/illustrations/exterior-services-local-batch-v1/cedar-privacy-fence-01.png',
        width: 1672,
        height: 941,
        sha256: '244a94ba0919b1af911fb15c1feb37d2ed545ff92239a448b48cc3b0a4d40aed',
        title: 'Cedar privacy-fence planning',
        alt: 'Representative generated illustration of a cedar privacy fence for Dallas-Fort Worth fencing planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth fencing planning - privacy-fence context, not a Luna project photo or evidence of work in a particular city.'
      })
    ]
  },
  {
    file: 'index.html',
    id: 'additional-services-imagery',
    serviceTerm: 'general contracting',
    title: 'Additional General Contracting Planning Scenes',
    intro: 'These representative generated illustrations support Dallas-Fort Worth general contracting planning. They are not Luna project photos or evidence of work in a particular city.',
    images: [
      local({
        file: 'assets/images/illustrations/interior-services-local-batch-v1/01-whole-home-living-dining-remodel.png',
        width: 1672,
        height: 941,
        sha256: 'a2525be028738d33769b8d96f56963c5285526dcc27f89decc49eb7011fd42cc',
        title: 'Whole-home remodeling planning',
        alt: 'Representative generated illustration of an open living and dining remodel for Dallas-Fort Worth general contracting planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth general contracting planning - whole-home remodeling context, not a Luna project photo or evidence of work in a particular city.'
      }),
      local({
        file: 'assets/images/illustrations/exterior-services-local-batch-v1/concrete-patio-drainage-01.png',
        width: 1536,
        height: 1024,
        sha256: '1d8d312083dcbd1aaa4a9bb09041faf9c837f3b634de468bda452a8a1e827dc8',
        title: 'Concrete patio and drainage planning',
        alt: 'Representative generated illustration of a concrete patio and drainage context for Dallas-Fort Worth general contracting planning.',
        caption: 'Representative generated illustration for Dallas-Fort Worth general contracting planning - patio and drainage context, not a Luna project photo or evidence of work in a particular city.'
      })
    ]
  }
];
