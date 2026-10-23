// Narrow page-level media overrides. Each entry is reserved for one canonical
// city-service file and can be rebuilt safely without changing other pages.
// Provenance remains internal; the public captions stay concise and identify
// only the service and page city.
const illustration=(id,src,sha,alt,sceneTags)=>({
 id,
 src,
 sha,
 alt,
 caption:'Dallas service planning image.',
 displayCaption:'Kitchen remodeling · Dallas',
 attribution:'AI-generated page-owned scene; internal provenance only.',
 kind:'representative-illustration',
 substantive:true,
 width:1536,
 height:1024,
 serviceKeys:['kitchen-remodeling'],
 sceneTags
});

const bathroomIllustration=(id,src,sha,alt,sceneTags)=>({
 id,
 src,
 sha,
 alt,
 caption:'Dallas service planning image.',
 displayCaption:'Bathroom remodeling · Dallas',
 attribution:'AI-generated page-owned scene; internal provenance only.',
 kind:'representative-illustration',
 substantive:true,
 width:1536,
 height:1024,
 serviceKeys:['bathroom-remodeling'],
 sceneTags
});

export default {
 'dallas-kitchen-remodeling.html':{
  pageOwned:true,
  serviceKey:'kitchen-remodeling',
  suppressVisibleGeneratedNotice:true,
  items:[
   illustration('dallas-kitchen-page-owned-01','assets/images/illustrations/page-owned/v1/dallas-kitchen-remodeling/scene-01.png','9cb940f9733daa58d5af627bd33d28fbaf002717','Warm oak kitchen with a pale stone island, pendant lights, and neutral cabinetry.',['kitchen','oak','island']),
   illustration('dallas-kitchen-page-owned-02','assets/images/illustrations/page-owned/v1/dallas-kitchen-remodeling/scene-02.png','caf8bcefb883c4077b6da8fd2fb9570bb8273aec','White galley kitchen with dark countertops, a farmhouse sink, and a tiled floor.',['kitchen','galley','cabinetry']),
   illustration('dallas-kitchen-page-owned-03','assets/images/illustrations/page-owned/v1/dallas-kitchen-remodeling/scene-03.png','b2390fcd7aad72fbd7980fd3827b24a02b033dd4','Contemporary walnut kitchen with dark stone counters and a large island.',['kitchen','walnut','stone']),
   illustration('dallas-kitchen-page-owned-04','assets/images/illustrations/page-owned/v1/dallas-kitchen-remodeling/scene-04.png','930a0487831b497d3be19558656f86fca869b8c6','Bright kitchen with a navy island, light countertops, and white cabinetry.',['kitchen','navy','island']),
   illustration('dallas-kitchen-page-owned-05','assets/images/illustrations/page-owned/v1/dallas-kitchen-remodeling/scene-05.png','ba137a2b49dc1c1fc0c99b5812c3b2f3776724f7','Compact kitchen with sage base cabinets, a tiled backsplash, and warm wood flooring.',['kitchen','sage','backsplash']),
   {
    id:'dallas-kitchen-dfw-portfolio-quartz-island',
    src:'dfw-kitchen-remodel-quartz-island-2018.jpg',
    alt:'Kitchen remodel with a quartz island from Luna\'s Dallas–Fort Worth portfolio.',
    caption:'Kitchen remodeling · Dallas',
    displayCaption:'Kitchen remodeling · Dallas',
    attribution:'Existing Luna General Contractors portfolio photograph from Dallas–Fort Worth.',
    kind:'genuine-portfolio-photo',
    substantive:true,
    width:669,
    height:891,
    serviceKeys:['kitchen-remodeling'],
    sceneTags:['kitchen','quartz-island','portfolio']
   }
  ]
 },
 'dallas-bathroom-remodeling.html':{
  pageOwned:true,
  serviceKey:'bathroom-remodeling',
  suppressVisibleGeneratedNotice:true,
  items:[
   bathroomIllustration('dallas-bathroom-page-owned-01','assets/images/illustrations/page-owned/v1/dallas-bathroom-remodeling/dallas-bathroom-remodeling-scene-01.png','cf9fbbba4d7cf848050af8cfd6eb07f2e9a18722','Bathroom with a glass shower, a wood vanity, and a light stone countertop.',['bathroom','glass-shower','vanity']),
   bathroomIllustration('dallas-bathroom-page-owned-02','assets/images/illustrations/page-owned/v1/dallas-bathroom-remodeling/dallas-bathroom-remodeling-scene-02.png','f7bf1dd171d120b1cde8e64e89c65da7517b516a','Bathroom with a green vanity, a tub-and-shower combination, and pale tile.',['bathroom','vanity','tub-shower']),
   bathroomIllustration('dallas-bathroom-page-owned-03','assets/images/illustrations/page-owned/v1/dallas-bathroom-remodeling/dallas-bathroom-remodeling-scene-03.png','c16d82ae1db6944c022d8006ccf838c7b8c9451b','Tiled shower wall with a recessed niche and an exposed wall edge during finish work.',['bathroom','tile','shower-detail']),
   bathroomIllustration('dallas-bathroom-page-owned-04','assets/images/illustrations/page-owned/v1/dallas-bathroom-remodeling/dallas-bathroom-remodeling-scene-04.png','4cdc8dc2564bed7dc6dc201ab081c3bd60b8799c','Bathroom with a freestanding tub, double vanity, and glass shower enclosure.',['bathroom','freestanding-tub','vanity']),
   bathroomIllustration('dallas-bathroom-page-owned-05','assets/images/illustrations/page-owned/v1/dallas-bathroom-remodeling/dallas-bathroom-remodeling-scene-05.png','7fef4b86ec26f1485c5f14865cb927de37f82263','Dark tile shower with a glass enclosure, built-in bench, and recessed shelf.',['bathroom','dark-tile','glass-shower'])
  ]
 }
};
