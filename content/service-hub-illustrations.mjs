import {ownedScenes} from './page-owned-imagery.mjs';
export default [
  {
    "key": "drywall",
    "hub": "drywall.html",
    "service": "Drywall"
  },
  {
    "key": "painting",
    "hub": "painting.html",
    "service": "Painting"
  },
  {
    "key": "siding",
    "hub": "siding.html",
    "service": "Siding"
  },
  {
    "key": "kitchens",
    "hub": "kitchens.html",
    "service": "Kitchen remodeling"
  },
  {
    "key": "bathrooms",
    "hub": "bathrooms.html",
    "service": "Bathroom remodeling"
  },
  {
    "key": "insurance-claims",
    "hub": "insurance-claims.html",
    "service": "Insurance claim repair support"
  },
  {
    "key": "carpentry",
    "hub": "carpentry.html",
    "service": "Carpentry"
  },
  {
    "key": "commercial",
    "hub": "commercial.html",
    "service": "Commercial construction"
  },
  {
    "key": "fencing",
    "hub": "fencing.html",
    "service": "Fencing"
  },
  {
    "key": "flooring",
    "hub": "flooring.html",
    "service": "Flooring"
  }
].map(hub=>({...hub,get images(){return ownedScenes(hub.hub);}}));
