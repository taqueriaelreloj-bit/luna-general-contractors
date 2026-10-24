import {ownedScenes} from './page-owned-imagery.mjs';
export default [
  {
    "file": "kitchens.html",
    "id": "additional-kitchen-imagery",
    "serviceTerm": "kitchen remodeling",
    "visibleCaption": "Kitchen remodeling services \u2014 Dallas\u2013Fort Worth",
    "title": "More Kitchen Remodeling Planning Scenes",
    "intro": "Generated illustrations support Dallas-Fort Worth kitchen remodeling planning. They are planning visuals, not product photographs or completed-project evidence; brand names and links below are reference information."
  },
  {
    "file": "bathrooms.html",
    "id": "additional-bathroom-imagery",
    "serviceTerm": "bathroom remodeling",
    "visibleCaption": "Bathroom remodeling services \u2014 Dallas\u2013Fort Worth",
    "title": "Bathroom Remodeling Planning Scene",
    "intro": "Generated illustrations support Dallas-Fort Worth bathroom remodeling planning. They are planning visuals, not completed-project photographs."
  },
  {
    "file": "carpentry.html",
    "id": "additional-carpentry-imagery",
    "serviceTerm": "carpentry",
    "visibleCaption": "Carpentry services \u2014 Dallas\u2013Fort Worth",
    "title": "Carpentry and Outdoor Structure Planning Scenes",
    "intro": "Generated illustrations support Dallas-Fort Worth carpentry planning, including built-ins and exterior wood structures. They are planning visuals, not completed-project photographs."
  },
  {
    "file": "painting.html",
    "id": "additional-painting-imagery",
    "serviceTerm": "painting",
    "visibleCaption": "Interior painting services \u2014 Dallas\u2013Fort Worth",
    "title": "Interior Painting Planning Scene",
    "intro": "Generated illustrations support Dallas-Fort Worth interior painting planning. They are planning visuals, not completed-project photographs."
  },
  {
    "file": "siding.html",
    "id": "additional-siding-imagery",
    "serviceTerm": "siding",
    "visibleCaption": "Siding services \u2014 Dallas\u2013Fort Worth",
    "title": "Siding and Trim Planning Scene",
    "intro": "Generated illustrations support Dallas-Fort Worth siding planning. They are planning visuals, not completed-project photographs."
  },
  {
    "file": "fencing.html",
    "id": "additional-fencing-imagery",
    "serviceTerm": "fencing",
    "visibleCaption": "Fencing services \u2014 Dallas\u2013Fort Worth",
    "title": "Cedar Fence Planning Scene",
    "intro": "Generated illustrations support Dallas-Fort Worth fencing planning. They are planning visuals, not completed-project photographs."
  },
  {
    "file": "index.html",
    "id": "additional-services-imagery",
    "serviceTerm": "general contracting",
    "visibleCaption": "General contracting services \u2014 Dallas\u2013Fort Worth",
    "title": "Additional General Contracting Planning Scenes",
    "intro": "Generated illustrations support Dallas-Fort Worth general contracting planning. They are planning visuals, not completed-project photographs."
  }
].map(page=>({...page,get images(){return ownedScenes(page.file).map(image=>({...image,alt:`AI-created illustrative concept for Dallas-Fort Worth ${page.serviceTerm}; not actual project evidence.`,caption:`${page.serviceTerm} — Dallas-Fort Worth`}));}}));
