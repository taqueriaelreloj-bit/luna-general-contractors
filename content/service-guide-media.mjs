// Substantive imagery for the 23 city-service guide families.
// Every illustration is explicitly labeled at render time. Portfolio photos are
// genuine Luna DFW references and are never presented as work in a page's city.
import hubIllustrations from './service-hub-illustrations.mjs';

const hubByKey=new Map(hubIllustrations.map(hub=>[hub.key,hub]));
const illustration=(id,src,alt,caption,serviceKeys,sceneTags,sha,width=1536,height=1024)=>({
 id,src,alt,caption,serviceKeys,sceneTags,sha,
 kind:'representative-illustration',
 attribution:'Original representative illustration; not a Luna project photograph.',
 substantive:true,width,height
});
const portfolio=(id,src,alt,caption,serviceKeys,sceneTags,width,height)=>({
 id,src,alt,caption,serviceKeys,sceneTags,
 kind:'genuine-portfolio-photo',
 attribution:'Existing Luna General Contractors portfolio photograph from Dallas-Fort Worth.',
 substantive:true,width,height
});
const hubMedia=(serviceKey,hubKey,captionPrefix='')=>{
 const hub=hubByKey.get(hubKey);
 if(!hub)throw new Error(`Missing hub illustration family: ${hubKey}`);
 return hub.images.map((image,index)=>illustration(
  `${serviceKey}-hub-${index+1}`,
  image.file,
  image.alt,
  `${captionPrefix}${image.caption}`,
  [serviceKey],
  [hubKey,'service-planning'],
  image.sha
 ));
};
const hubItem=(serviceKey,hubKey,fileSuffix,caption)=>{
 const hub=hubByKey.get(hubKey);
 const image=hub?.images.find(item=>item.file.includes(fileSuffix));
 if(!image)throw new Error(`Missing ${hubKey} illustration containing ${fileSuffix}`);
 return illustration(`${serviceKey}-${hubKey}-${fileSuffix}`,image.file,image.alt,caption,[serviceKey],[hubKey,'service-planning'],image.sha);
};
const specialist=(serviceKey,id,file,sha,alt,caption,sceneTags,width,height)=>illustration(
 id,file,alt,caption,[serviceKey],sceneTags,sha,width,height
);

export const targetServiceKeys=[
 'insurance-claims','kitchen-remodeling','bathroom-remodeling','flooring','painting',
 'drywall','siding','carpentry','fencing','commercial-construction',
 'shower-remodeling','backsplash-installation','cabinet-installation','whole-home-remodeling','general-contractor',
 'concrete-driveways','door-installation','window-replacement','foundation-repair','pergolas','patio-covers','room-additions','outdoor-living'
];

const media={
 'insurance-claims':{items:hubMedia('insurance-claims','insurance-claims')},
 'kitchen-remodeling':{items:[
  ...hubMedia('kitchen-remodeling','kitchens'),
  portfolio('kitchen-remodeling-quartz-island','dfw-kitchen-remodel-quartz-island-2018.jpg','Kitchen remodel with a quartz island from Luna\'s DFW portfolio.','Finished kitchen and quartz-island reference from the Luna DFW portfolio.',['kitchen-remodeling'],['kitchen','quartz-island'],669,891)
 ]},
 'bathroom-remodeling':{items:hubMedia('bathroom-remodeling','bathrooms')},
 'flooring':{items:hubMedia('flooring','flooring')},
 'painting':{items:hubMedia('painting','painting')},
 'drywall':{items:hubMedia('drywall','drywall')},
 'siding':{items:hubMedia('siding','siding')},
 'carpentry':{items:hubMedia('carpentry','carpentry')},
 'fencing':{items:hubMedia('fencing','fencing')},
 'commercial-construction':{items:hubMedia('commercial-construction','commercial')},

 'shower-remodeling':{items:[
  hubItem('shower-remodeling','bathrooms','bathrooms-01-protection','Shower-area protection and work-area planning.'),
  hubItem('shower-remodeling','bathrooms','bathrooms-03-shower-finish','Tiled shower finish concept.'),
  hubItem('shower-remodeling','bathrooms','bathrooms-04-tile-palette','Shower tile and material palette concept.'),
  portfolio('shower-remodeling-waterproofing','bathroom-waterproofing-progress.jpg','Bathroom waterproofing progress from Luna\'s DFW portfolio.','Waterproofing progress from a Luna DFW bathroom project.',['shower-remodeling'],['shower','waterproofing'],1600,1200),
  portfolio('shower-remodeling-glass-shower','dfw-bathroom-remodel-glass-shower-2020.jpg','Finished glass shower from Luna\'s DFW portfolio.','Finished glass-shower reference from a Luna DFW bathroom project.',['shower-remodeling'],['shower','glass'],1188,891)
 ]},
 'backsplash-installation':{items:[
  hubItem('backsplash-installation','kitchens','kitchens-01-protected-work-area','Protected kitchen work area before backsplash installation.'),
  hubItem('backsplash-installation','kitchens','kitchens-03-countertop-detail','Countertop and wall-backsplash layout concept.'),
  hubItem('backsplash-installation','kitchens','kitchens-05-kitchen-concept','Kitchen finish concept showing backsplash context.'),
  portfolio('backsplash-installation-wood-cabinets','dfw-kitchen-remodel-wood-cabinets-2018.jpg','Finished wood cabinets from Luna\'s DFW kitchen portfolio.','Finished kitchen cabinetry reference from the Luna DFW portfolio.',['backsplash-installation'],['kitchen','cabinetry'],1188,891),
  portfolio('backsplash-installation-quartz-island','dfw-kitchen-remodel-quartz-island-2018.jpg','Kitchen remodel with a quartz island from Luna\'s DFW portfolio.','Finished kitchen and quartz-island reference from the Luna DFW portfolio.',['backsplash-installation'],['kitchen','quartz-island'],669,891)
 ]},
 'cabinet-installation':{items:[
  hubItem('cabinet-installation','kitchens','kitchens-05-kitchen-concept','Kitchen layout reference for cabinet planning; not installation evidence.'),
  hubItem('cabinet-installation','bathrooms','bathrooms-02-vanity-concept','Vanity design reference for cabinet planning; not installation evidence.'),
  hubItem('cabinet-installation','carpentry','carpentry-03-built-in-shelves','Built-in storage design reference for cabinet planning; not installation evidence.'),
  portfolio('cabinet-installation-wood-cabinets','dfw-kitchen-remodel-wood-cabinets-2018.jpg','Finished wood cabinets from Luna\'s DFW kitchen portfolio.','Finished kitchen cabinetry reference from the Luna DFW portfolio.',['cabinet-installation'],['cabinetry','kitchen'],1188,891),
  portfolio('cabinet-installation-quartz-island','dfw-kitchen-remodel-quartz-island-2018.jpg','Kitchen remodel with a quartz island from Luna\'s DFW portfolio.','Finished kitchen and quartz-island reference from the Luna DFW portfolio.',['cabinet-installation'],['cabinetry','kitchen'],669,891)
 ]},
 'whole-home-remodeling':{items:[
  hubItem('whole-home-remodeling','kitchens','kitchens-05-kitchen-concept','Kitchen finish concept for whole-home selection coordination.'),
  hubItem('whole-home-remodeling','bathrooms','bathrooms-05-room-concept','Bathroom finish concept for whole-home selection coordination.'),
  hubItem('whole-home-remodeling','flooring','flooring-05-finished-floor-concept','Finished-floor concept for whole-home selection coordination.'),
  hubItem('whole-home-remodeling','painting','painting-01-room-protection','Room protection concept for whole-home work sequencing.'),
  portfolio('whole-home-remodeling-framing','dfw-interior-rebuild-framing-2018.jpg','Related interior framing work from Luna\'s DFW portfolio.','Related DFW framing reference for construction sequencing; it is not evidence of a project in this page\'s city.',['whole-home-remodeling'],['framing','sequencing'],1188,891)
 ]},
 'general-contractor':{items:[
  hubItem('general-contractor','insurance-claims','insurance-claims-03-room-measurement','Room-measurement planning concept for coordinated construction; no insurer decision is implied.'),
  hubItem('general-contractor','painting','painting-01-room-protection','Room-protection concept for coordinated construction.'),
  hubItem('general-contractor','commercial','commercial-03-office-partitions','Partition-framing concept for trade coordination.'),
  hubItem('general-contractor','kitchens','kitchens-05-kitchen-concept','Kitchen finish concept for trade coordination.'),
  portfolio('general-contractor-framing','dfw-interior-rebuild-framing-2018.jpg','Related interior framing work from Luna\'s DFW portfolio.','Related DFW framing reference for scope coordination; it is not a claim or insurer decision.',['general-contractor'],['framing','coordination'],1188,891)
 ]},

 'concrete-driveways':{items:[
  specialist('concrete-driveways','concrete-driveways-finished-driveway','assets/images/illustrations/concrete-driveways/concrete-driveways-01-finished-driveway.webp','4ede2b7697b4791e464918e615a1b602aa7f2504','Illustration of a light-gray concrete driveway leading to a brick home\'s garage.','Finished concrete driveway with a broom-textured surface and control joints.',['driveway','concrete','finish']),
  specialist('concrete-driveways','concrete-driveways-base-forms','assets/images/illustrations/concrete-driveways/concrete-driveways-02-base-and-forms.webp','b46243c77389f9437d619c27bc01578f3e9bf901','Illustration of a gravel driveway base enclosed by timber forms.','Aggregate base and edge forms prepared for a residential driveway.',['driveway','base','forms'],1440,960),
  specialist('concrete-driveways','concrete-driveways-reinforcement','assets/images/illustrations/concrete-driveways/concrete-driveways-03-reinforcement-layout.webp','d8bcbeb4f9f365e2ff778bde58a2c5bd8ecda6c8','Illustration of steel reinforcement on supports within driveway forms.','Driveway reinforcement arranged before concrete placement; final design varies by project.',['driveway','reinforcement']),
  specialist('concrete-driveways','concrete-driveways-broom-finish','assets/images/illustrations/concrete-driveways/concrete-driveways-04-broom-finish-detail.webp','1c34450a2a8ef09af4c3acf20798a72840f8ae97','Illustration of broom-textured concrete with a finished edge and a joint.','Concrete finishing texture, edge detail, and a control joint.',['driveway','finish']),
  portfolio('concrete-driveways-commercial-sitework','dfw-commercial-concrete-sitework-2020.jpg','Related commercial concrete sitework from Luna\'s DFW portfolio.','Related DFW commercial concrete sitework reference; it is not a residential driveway.',['concrete-driveways'],['concrete','commercial-sitework'],1363,766)
 ]},
 'door-installation':{suppressLegacyPhoto:true,items:[
  specialist('door-installation','door-installation-opening-planning','assets/images/illustrations/door-installation/door-installation-01-opening-planning.webp','c5f9b3f00ae7ae60475dcd7b217d3454d3d929d9','Illustration of a clean doorway with measuring and leveling tools nearby.','Doorway planning and measurement tools before fitting a door.',['doorway','measurement']),
  specialist('door-installation','door-installation-frame-shims','assets/images/illustrations/door-installation/door-installation-02-frame-and-shims.webp','01d1bcbdfd15e35367ccdc639b7a6aa3dccad463','Illustration of wood shims behind a white door jamb beside a satin nickel hinge.','Door jamb, hinge, and shims during fitting.',['doorway','jamb','shims']),
  specialist('door-installation','door-installation-threshold-weatherseal','assets/images/illustrations/door-installation/door-installation-03-threshold-weatherseal.webp','dd003b0b8d2b48f05c9f9c8829f0ed0ec525194b','Illustration of a dark entry door above an aluminum threshold and flexible seal.','Exterior door threshold and weather-seal detail.',['doorway','threshold','weatherseal']),
  hubItem('door-installation','carpentry','carpentry-02-trim-joint','Doorway trim-joint reference.'),
  portfolio('door-installation-finished-door','dfw-bathroom-remodel-finished-2020.jpg','Finished interior door and vanity from Luna\'s DFW portfolio.','Finished interior door reference from a Luna DFW bathroom project.',['door-installation'],['door','interior'],1188,891)
 ]},
 'window-replacement':{items:[
  specialist('window-replacement','window-replacement-measurement','assets/images/illustrations/window-replacement/window-replacement-01-measurement-planning.webp','fe340d5b9c00802ee6d8e6850fcde952287caaf4','Illustration of a residential window with measuring tools on the sill.','Window measurement and fit planning before replacement.',['window','measurement']),
  specialist('window-replacement','window-replacement-sill-flashing','assets/images/illustrations/window-replacement/window-replacement-02-sill-flashing.webp','9997accdb5966dc871e30a5b1e8ac386e785d48c','Illustration of black sill flashing at the lower corner of a prepared window opening.','Sill and jamb flashing preparation; installation details vary by window and wall system.',['window','flashing']),
  specialist('window-replacement','window-replacement-operating-window','assets/images/illustrations/window-replacement/window-replacement-03-operating-window.webp','2c6aea4c7308df2435394e727ff9f358bab8b303','Illustration of a white window with one sash open above a wood sill.','Finished window with an operable sash and clean interior trim.',['window','operable-sash']),
  hubItem('window-replacement','siding','siding-05-window-trim','Window trim reference for exterior-envelope planning.'),
  hubItem('window-replacement','carpentry','carpentry-02-trim-joint','Interior trim-joint reference for window finishing.')
 ]},
 'foundation-repair':{suppressLegacyPhoto:true,items:[
  specialist('foundation-repair','foundation-repair-condition-documentation','assets/images/illustrations/foundation-repair/foundation-repair-01-condition-documentation.webp','87667c43cb2fce5b866cb51c5ebc71f9c39a66e5','Illustration of a brick wall and concrete foundation edge with a camera and notebook nearby.','Documenting visible conditions around a home\'s foundation perimeter; not a diagnosis.',['foundation','documentation'],1440,960),
  specialist('foundation-repair','foundation-repair-drainage-review','assets/images/illustrations/foundation-repair/foundation-repair-02-drainage-review.webp','da9e659ac89680bf6365f4ceae98e9a312d6c866','Illustration of a downspout extension and landscaping beside a concrete foundation edge.','Reviewing surface drainage and downspout routing near the foundation.',['foundation','drainage']),
  specialist('foundation-repair','foundation-repair-plan-review','assets/images/illustrations/foundation-repair/foundation-repair-03-plan-review.webp','12216e9d2696b852327c7297a2573049d0b7a226','Illustration of a simple foundation drawing, drafting tools, and a hard hat on a desk.','Foundation-plan review concept, not a stamped or project-specific engineering plan.',['foundation','plan-review']),
  specialist('foundation-repair','foundation-repair-support-model','assets/images/illustrations/foundation-repair/foundation-repair-04-support-concept-model.webp','c029c41e24190e5e21d505f656969a2597f91556','Conceptual tabletop cutaway model showing a concrete slab and a simplified vertical support.','Conceptual tabletop model of a generic slab-support arrangement, not a repair design or installation guide.',['foundation','concept-model']),
  specialist('foundation-repair','foundation-repair-monitoring-records','assets/images/illustrations/foundation-repair/foundation-repair-05-monitoring-records.webp','81c18b6bdba913962b9b12afc94fab0738fdbf77','Illustration of a room corner with a straightedge, closed record folder, and a level with its display off.','Tools and records for follow-up documentation; no repair result or measured condition is implied.',['foundation','monitoring'])
 ]},
 'pergolas':{items:[
  specialist('pergolas','pergolas-open-patio-shade','assets/images/illustrations/pergolas/pergolas-01-open-patio-shade.webp','92213a6afbbd2584f6bd5db42948b24719166784','Representative illustration of an open cedar pergola over a furnished paver patio beside a brick home.','Open pergola shade over a seating patio.',['pergola','shade']),
  specialist('pergolas','pergolas-open-slat-geometry','assets/images/illustrations/pergolas/pergolas-02-open-slat-geometry.webp','2013adeb39822e06abb836b1c49821949b4f9a8c','Representative illustration looking upward through the open cedar slats of a pergola.','Open slats and filtered shade.',['pergola','slats']),
  specialist('pergolas','pergolas-post-base-detail','assets/images/illustrations/pergolas/pergolas-03-post-base-detail.webp','f58fa04789fb78236f3501e97ca530abf0a2f731','Representative illustration of a cedar pergola post with a dark metal base on a paved patio.','Pergola post and patio base detail.',['pergola','post-base']),
  specialist('pergolas','pergolas-beam-connection','assets/images/illustrations/pergolas/pergolas-04-beam-connection-detail.webp','2c746e20c646c114e3a8a5411443461a174d7bff','Representative illustration of a cedar pergola beam connection with dark metal hardware and open rafters.','Pergola post and beam connection.',['pergola','beam-connection']),
  portfolio('pergolas-eaves-reference','dfw-roof-eaves-pergola-2019.jpg','Related pergola and eaves work from Luna\'s DFW portfolio.','Related DFW pergola and eaves reference.',['pergolas'],['pergola','eaves'],1188,891)
 ]},
 'patio-covers':{items:[
  specialist('patio-covers','patio-covers-solid-gabled-roof','assets/images/illustrations/patio-covers/patio-covers-01-solid-gabled-roof.webp','b332252c245de6a4c78817162dbe0775ceb1519e','Representative illustration of a solid gabled patio cover with cedar posts and shaded dining and lounge areas.','Solid-roof shade for dining and relaxing.',['patio-cover','solid-roof']),
  specialist('patio-covers','patio-covers-house-roof-interface','assets/images/illustrations/patio-covers/patio-covers-02-house-roof-interface.webp','03ca15fa52b041d2fe5b465834937621e4d077b5','Representative illustration of a dark solid metal patio-cover roof meeting a brick house wall.','Patio-cover roof meeting the home.',['patio-cover','roof-interface']),
  specialist('patio-covers','patio-covers-freestanding-pavilion','assets/images/illustrations/patio-covers/patio-covers-03-freestanding-pavilion.webp','2da47d5425283db66a60ab0d1121ea7d9cb02f5b','Representative illustration of a freestanding solid-roof cedar pavilion over a furnished backyard patio.','Freestanding covered patio.',['patio-cover','pavilion']),
  specialist('patio-covers','patio-covers-gutter-downspout','assets/images/illustrations/patio-covers/patio-covers-04-gutter-downspout-detail.webp','e837932475f3df855b7a7e25a715efa60e1b7340','Representative illustration of a gutter and downspout at the corner of a solid-roof patio cover.','Patio-cover gutter and downspout detail.',['patio-cover','gutter']),
  portfolio('patio-covers-eaves-reference','dfw-roof-eaves-pergola-2019.jpg','Related pergola and eaves work from Luna\'s DFW portfolio.','Related DFW pergola/eaves reference for outdoor-structure planning; not a solid-roof patio-cover project.',['patio-covers'],['pergola','eaves'],1188,891)
 ]},
 'room-additions':{items:[
  specialist('room-additions','room-additions-enclosed-framing','assets/images/illustrations/room-additions/room-additions-01-enclosed-framing.webp','4ec6ea5bba7a0d151b0e11104ce6394ccb2f1033','Representative illustration of an enclosed room addition with exposed framing, installed windows and an opening to the existing home.','An enclosed addition at the framing stage.',['room-addition','framing']),
  specialist('room-additions','room-additions-exterior-tie-in','assets/images/illustrations/room-additions/room-additions-02-exterior-house-tie-in.webp','d01c7b2ab56cfdf3496e2f44e767e4c333a9c35e','Representative illustration of a gabled room addition with cream siding connected to a brick home.','A new room connected to the existing home.',['room-addition','tie-in']),
  specialist('room-additions','room-additions-finished-family-room','assets/images/illustrations/room-additions/room-additions-03-finished-family-room.webp','031702b6dcc2451dcbef9142971099f6e3a089db','Representative illustration of a bright finished family-room addition seen through a wide opening in an existing brick wall.','A finished family-room addition.',['room-addition','interior']),
  hubItem('room-additions','painting','painting-01-room-protection','Room protection concept during addition work.'),
  portfolio('room-additions-framing-reference','dfw-interior-rebuild-framing-2018.jpg','Related interior framing work from Luna\'s DFW portfolio.','Related DFW framing reference for construction sequencing; it is not evidence of a completed room addition.',['room-additions'],['framing','sequencing'],1188,891)
 ]},
 'outdoor-living':{items:[
  specialist('outdoor-living','outdoor-living-pergola-patio-shade','assets/images/illustrations/pergolas/pergolas-01-open-patio-shade.webp','92213a6afbbd2584f6bd5db42948b24719166784','Representative illustration of an open cedar pergola over a furnished paver patio beside a brick home.','Open pergola shade over a seating patio.',['outdoor-living','pergola','shade']),
  specialist('outdoor-living','outdoor-living-pergola-slat-geometry','assets/images/illustrations/pergolas/pergolas-02-open-slat-geometry.webp','2013adeb39822e06abb836b1c49821949b4f9a8c','Representative illustration looking upward through the open cedar slats of a pergola.','Open slats and filtered shade.',['outdoor-living','pergola','slats']),
  specialist('outdoor-living','outdoor-living-solid-gabled-roof','assets/images/illustrations/patio-covers/patio-covers-01-solid-gabled-roof.webp','b332252c245de6a4c78817162dbe0775ceb1519e','Representative illustration of a solid gabled patio cover with cedar posts and shaded dining and lounge areas.','Solid-roof shade for dining and relaxing.',['outdoor-living','patio-cover','solid-roof']),
  specialist('outdoor-living','outdoor-living-freestanding-pavilion','assets/images/illustrations/patio-covers/patio-covers-03-freestanding-pavilion.webp','2da47d5425283db66a60ab0d1121ea7d9cb02f5b','Representative illustration of a freestanding solid-roof cedar pavilion over a furnished backyard patio.','Freestanding covered patio.',['outdoor-living','patio-cover','pavilion']),
  portfolio('outdoor-living-eaves-reference','dfw-roof-eaves-pergola-2019.jpg','Related pergola and eaves work from Luna\'s DFW portfolio.','Related DFW pergola and eaves reference.',['outdoor-living'],['pergola','eaves'],1188,891)
 ]}
};

for(const key of targetServiceKeys){
 const entry=media[key];
 if(!entry||entry.items.length<5)throw new Error(`Service media needs five substantive items: ${key}`);
}

export default media;
