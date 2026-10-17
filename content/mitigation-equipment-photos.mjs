// Display crops of the original, published project photographs. The JPEGs stay unchanged.
// Crop coordinates are in source pixels; every viewport has a 4:3 aspect ratio.
const base = 'assets/mitigation-projects/arlington-dry-out/';
export default {
 drying: {
  src: `${base}hallway-dehumidifier.jpg`, width: 1350, height: 1800,
  crop: {x: 110, y: 400, width: 800, height: 600},
  alt: 'Close view of the Phoenix R250 dehumidifier used on Luna’s Arlington mitigation project',
  caption: 'Phoenix R250 · Luna project photo',
  brand: 'Phoenix R250', referenceLabel: 'Phoenix R250',
  url: 'https://usephoenix.com/r250-lgr-dehumidifier/'
 },
 airflow: {
  src: `${base}interior-air-mover.jpg`, width: 1350, height: 1800,
  crop: {x: 210, y: 650, width: 320, height: 240},
  alt: 'Close view of the blue air mover used beside the exposed floor on Luna’s Arlington mitigation project',
  caption: 'Air mover · Luna project photo',
  brand: 'Air mover used on site', referenceLabel: 'Air-movement equipment reference',
  linkLabel: 'Air-movement equipment reference →',
  url: 'https://www.legendbrands.com/products'
 },
 meter: {
  src: `${base}initial-inspection-01.jpg`, width: 1536, height: 1152,
  crop: {x: 200, y: 380, width: 800, height: 600},
  alt: 'Close view of the FLIR moisture meter during Luna’s initial inspection in Arlington',
  caption: 'FLIR moisture meter · Luna project photo',
  brand: 'FLIR moisture meter', referenceLabel: 'FLIR moisture meters',
  url: 'https://www.flir.com/browse/portable-inspection-solutions/test--measurement/moisture-meters/'
 }
};
