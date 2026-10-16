// Commercial product references, reviewed against the linked primary sources.
// Product eligibility and installation authorization are project-specific.
export const gafWarranty = 'https://www.gaf.com/en-us/document-library/documents/warranties%2C-guarantees-%26-addendums/limited-warranty-on-gaf-single-ply-roofing-materials-comts715.pdf';
export const membranes = [
  {
    id: 'tpo', name: 'TPO', fullName: 'Thermoplastic polyolefin', brand: 'GAF EverGuard TPO',
    description: 'A thermoplastic sheet membrane with heat-welded seams. The roof assembly may use mechanical attachment, approved adhesives or another specified fastening system. White is one available finish; identify the actual product rather than choosing by color alone.',
    detail: 'Compare membrane thickness, attachment, insulation, cover board and perimeter details as one assembly.',
    warranty: 'GAF’s published limited material warranty lists standard EverGuard TPO 45 / 60 / 80 mil membranes at 15 / 20 / 25 years, respectively, subject to its terms. Other EverGuard lines have different periods.',
    warrantyLabel: '15–25 years · listed standard TPO materials',
    source: 'https://www.gaf.com/en-us/roofing-materials/commercial-single-ply', warrantyUrl: gafWarranty,
    image: 'assets/commercial-roofing/tpo-reference.svg', alt: 'Illustration of a light TPO membrane roll and an overlapped sheet seam'
  },
  {
    id: 'pvc', name: 'PVC & PVC KEE', fullName: 'Polyvinyl chloride membranes', brand: 'GAF EverGuard PVC / PVC KEE',
    description: 'PVC is another heat-welded thermoplastic membrane family. KEE-modified products are distinct formulations. Where exhaust, oils or process chemicals may reach the roof, request the manufacturer’s compatibility guidance for the actual exposure.',
    detail: 'Name the formulation and accessory system; PVC and TPO are not interchangeable simply because both may look white.',
    warranty: 'GAF’s limited material warranty lists standard EverGuard PVC 50 mil at 15 years and 60 / 80 mil at 20 years. Listed PVC KEE 50 / 60 / 80 mil periods are 15 / 20 / 25 years. Terms and product identity control.',
    warrantyLabel: '15–25 years · varies by PVC / KEE product',
    source: 'https://www.gaf.com/en-us/roofing-materials/commercial-single-ply', warrantyUrl: gafWarranty,
    image: 'assets/commercial-roofing/pvc-reference.svg', alt: 'Illustration of a PVC membrane roll with a welded overlap; generic material reference'
  },
  {
    id: 'epdm', name: 'EPDM', fullName: 'Synthetic rubber membrane', brand: 'Carlisle Sure-Seal EPDM',
    description: 'A thermoset rubber membrane used in adhered, mechanically fastened and ballasted assemblies, depending on the selected system. Field seams use specified tapes or adhesives rather than the hot-air welding used for TPO and PVC.',
    detail: 'Compare seam accessories, attachment, surfacing and service access together. Confirm the exact membrane and approved assembly.',
    warranty: 'Carlisle publishes EPDM system submittal options from 5 through 30 years, with different membrane, attachment and project requirements. A proposed period requires manufacturer eligibility and approval; it is not automatic coverage for every EPDM roof.',
    warrantyLabel: '5–30 years · eligible system programs',
    source: 'https://www.carlislesyntec.com/en/Roofing-Products/Membranes/EPDM',
    warrantyUrl: 'https://www.carlislesyntec.com/Professionals/Estimator-Resources',
    image: 'assets/commercial-roofing/epdm-reference.svg', alt: 'Illustration of a dark EPDM rubber membrane roll and taped overlap'
  }
];

export const otherSystems = [
  {
    id: 'sbs', name: 'SBS modified bitumen', family: 'Asphalt-based sheets',
    description: 'Reinforced asphalt sheets modified with styrene-butadiene-styrene. Base and cap sheets form a specified assembly, with application methods that vary by product, including approved self-adhered, cold-applied or heat-applied systems.',
    ask: 'Identify every ply and its application method. Coordinate the work process with the occupied building below.',
    sourceName: 'Johns Manville SBS systems', source: 'https://www.jm.com/en/commercial-roofing/sbs-roofing-systems/'
  },
  {
    id: 'app', name: 'APP modified bitumen', family: 'Asphalt-based sheets',
    description: 'Asphalt modified with atactic polypropylene and manufactured as reinforced roofing sheets. Many APP systems use heat application; the approved method depends on the exact sheet and specification.',
    ask: 'Compare the complete base-and-cap assembly, substrate and flashing details. Include the required work controls in the proposal.',
    sourceName: 'Johns Manville APP systems', source: 'https://www.jm.com/en/commercial-roofing/app-roofing-systems/'
  },
  {
    id: 'bur', name: 'Built-up roofing (BUR)', family: 'Multiple-ply asphalt roofing',
    description: 'A roof membrane built on site from alternating layers of bitumen and reinforcing felts. Surfacing is specified as part of the system; gravel is one possible finish, not the definition of every BUR roof.',
    ask: 'Record the number of plies, surfacing, existing layers and removal plan. Review the assembly weight and the condition of the supporting deck.',
    sourceName: 'Johns Manville BUR systems', source: 'https://www.jm.com/en/commercial-roofing/bur-roofing-systems/'
  },
  {
    id: 'metal', name: 'Commercial metal roofing', family: 'Panel systems',
    description: 'Standing-seam and exposed-fastener panels serve different roof designs. A structural panel system, an architectural panel over a deck and an insulated metal roof panel are distinct assemblies.',
    ask: 'Confirm the panel’s slope, support, attachment and thermal-movement requirements. Include curbs, transitions and drainage in the comparison.',
    sourceName: 'MBCI metal roof systems', source: 'https://www.mbci.com/products/roof/'
  },
  {
    id: 'spf', name: 'Spray polyurethane foam (SPF)', family: 'Spray-applied insulation & roofing',
    description: 'Roofing-grade foam is applied on site and paired with a protective surfacing system. Elastomeric coatings are commonly used to protect the foam from ultraviolet exposure and routine surface wear.',
    ask: 'Define substrate preparation, foam and coating specifications, application conditions and future inspection or recoating responsibilities.',
    sourceName: 'SPFA roofing technical resources', source: 'https://www.sprayfoam.org/technical-documents/'
  },
  {
    id: 'liquid', name: 'Reinforced liquid-applied membranes', family: 'Polyurethane, PMMA & related resins',
    description: 'Compatible resin and reinforcement cure into a continuous waterproofing membrane. Product families include polyurethane and PMMA, with different primers, cure conditions and detailing requirements.',
    ask: 'Ask whether the proposal is a complete reinforced waterproofing system, localized flashing or a maintenance coating. Specify the intended use and required build-up.',
    sourceName: 'Sika roofing and waterproofing resins', source: 'https://usa.sika.com/sarnafil/en/products-systems/liquid-applied-products/roof-coatings.html'
  },
  {
    id: 'coatings', name: 'Silicone, acrylic & urethane coatings', family: 'Restoration of suitable existing roofs',
    description: 'Coatings may form part of a restoration system over a compatible existing roof. Product chemistry, substrate condition, moisture, adhesion and drainage determine whether the proposal is appropriate.',
    ask: 'Identify wet or damaged areas and required repairs before coating. A coating proposal should explain preparation and coverage, not conceal an unsuitable substrate.',
    sourceName: 'GAF commercial roof coatings', source: 'https://www.gaf.com/en-us/roofing-materials/commercial-roofing-materials/coatings'
  },
  {
    id: 'steep', name: 'Shingles, tile, slate & other sloped coverings', family: 'Steep-slope commercial roofs',
    description: 'Offices, shops and other commercial buildings can have sloped roofs using asphalt shingles, clay or concrete tile, slate, wood or synthetic coverings where suitable. The building’s use alone does not determine its roof covering.',
    ask: 'Select for the measured slope, deck, load and manufacturer instructions. Evaluate transitions to any adjoining low-slope membrane separately.',
    sourceName: 'NRCA roofing-material guidance', source: 'https://www.nrca.net/roofing-guidelines/roofing-materials'
  },
  {
    id: 'overburden', name: 'Protected membranes, roof gardens & pavers', family: 'Specialty assemblies above waterproofing',
    description: 'Vegetation, pavers or protective layers are placed above an underlying waterproofing assembly. These are complete roof configurations; plants, ballast or paving do not replace the waterproofing membrane.',
    ask: 'Review structural capacity, drainage, access to the membrane and maintenance. Coordinate any solar equipment with the selected roof system as well.',
    sourceName: 'Carlisle roof garden and paver systems', source: 'https://www.carlislesyntec.com/en/Roofing-Products/Specialty/Roof-Garden'
  }
];
