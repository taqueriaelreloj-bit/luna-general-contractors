import {pageImagery,ownedScenes} from './page-owned-imagery.mjs';
const slots={cabinet:2,quartz:3,tile:4};
const classes={cabinet:'cabinet',quartz:'quartz',tile:'porcelain'};
const pages=Object.entries(pageImagery).filter(([file,page])=>file.endsWith('-kitchen-remodeling.html')&&page.category==='kitchen-remodeling');
const pageFor=city=>{const match=pages.filter(([,page])=>page.city===city);if(match.length!==1)throw new Error(`No unique kitchen page for ${city}`);return match[0][0];};
export const kitchenCardScene=(id,file)=>{
 if(!slots[id])throw new Error(`Unknown kitchen scene ${id}`);
 const scene=ownedScenes(file).find(image=>image.slot===slots[id]);
 if(!scene)throw new Error(`Missing ${file} kitchen slot ${slots[id]}`);
 return {...scene,scene:'kitchen remodeling planning concept',context:'Dallas-Fort Worth kitchen remodeling',className:`sg-card--scene sg-card--scene-${classes[id]}`};
};
export const cityKitchenCardScene=(id,city,index,brand)=>{
 if(!Number.isInteger(index)||index<0||!city||!brand)throw new Error('Invalid city kitchen context');
 return {...kitchenCardScene(id,pageFor(city)),caption:`Kitchen remodeling services — ${city}, Texas`,city,brand};
};
export const cityKitchenCardSceneSources=Object.freeze(Object.fromEntries(Object.keys(slots).map(id=>[id,pages.map(([file,page])=>page.images.find(image=>image.slot===slots[id]).src)])));
export const cityKitchenCardSceneAssets=Object.freeze(pages.flatMap(([file])=>Object.keys(slots).map(id=>kitchenCardScene(id,file))));
