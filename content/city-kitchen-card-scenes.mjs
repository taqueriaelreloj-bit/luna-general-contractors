// Approved generated scenes for the three material cards on city kitchen pages.
// They are planning illustrations, not Luna project photographs or branded
// product photos. The deterministic rotation provides variety without
// suggesting that each city has a unique photographed project.
const variants={
 cabinet:[
  {
   src:'assets/images/illustrations/kitchens/generated-kitchen-cabinetry-representative-illustration-v1.png',
   alt:'Generated illustration of custom-style cabinetry and a wood island for kitchen remodeling planning.',
   scene:'custom-style cabinetry and a wood island',
   width:1536,height:1024,sha:'c3ae1522a467ce9c19fd77e32cc05ff3812c5129',className:'sg-card--scene sg-card--scene-cabinet'
  },
  {
   src:'assets/images/illustrations/cloud-approved-batch-v1/cabinetry-generated-illustration.png',
   alt:'Generated illustration of a finished cabinetry layout for kitchen remodeling planning.',
   scene:'a finished cabinetry layout and coordinated island',
   width:1536,height:1024,sha:'ce58eeb6100330390c9ebd2b05e6cb8cb6c42a83',className:'sg-card--scene sg-card--scene-cabinet'
  }
 ],
 quartz:[
  {
   src:'assets/images/illustrations/kitchens/generated-quartz-island-representative-illustration-v1.png',
   alt:'Generated illustration of a pale quartz-style island for kitchen remodeling planning.',
   scene:'a pale quartz-style island and coordinated kitchen surfaces',
   width:1672,height:941,sha:'e1d8760494f760d10d0a9fa7adcd5fe2ad78d818',className:'sg-card--scene sg-card--scene-quartz'
  },
  {
   src:'assets/images/illustrations/cloud-approved-batch-v1/quartz-generated-illustration.png',
   alt:'Generated illustration of a quartz-style countertop and island for kitchen remodeling planning.',
   scene:'a quartz-style countertop and island layout',
   width:1536,height:1024,sha:'3a5bdbfdded593c95bea79da925190ec03953d7e',className:'sg-card--scene sg-card--scene-quartz'
  }
 ],
 tile:[
  {
   src:'assets/images/illustrations/flooring/generated-porcelain-flooring-representative-illustration-v1.png',
   alt:'Generated illustration of large-format porcelain-style flooring in a finished residential interior.',
   scene:'large-format porcelain-style flooring in a finished residential interior',
   width:1536,height:1024,sha:'262b9840e3d344fa83a2e58fe30daed74ce7672d',className:'sg-card--scene sg-card--scene-porcelain'
  },
  {
   src:'assets/images/illustrations/cloud-approved-batch-v1/tile-flooring-generated-illustration.png',
   alt:'Generated illustration of porcelain-style tile flooring in a bright residential interior.',
   scene:'porcelain-style tile flooring with a finished residential transition',
   width:1536,height:1024,sha:'e2cc336f6c0d94c29d18572eec9b922f3234838e',className:'sg-card--scene sg-card--scene-porcelain'
  }
 ]
};

const select=(id,index)=>{
 const options=variants[id];
 if(!options)throw new Error(`No approved city kitchen card scene for ${id}`);
 const shift={cabinet:0,quartz:1,tile:2}[id];
 return options[Math.floor(index/(2**shift))%options.length];
};

export const cityKitchenCardScene=(id,city,index,brand)=>{
 if(!Number.isInteger(index)||index<0)throw new Error(`Invalid city index for ${id}`);
 if(!city||!brand)throw new Error(`City kitchen card scene needs city and brand for ${id}`);
 const scene=select(id,index);
 return {
  ...scene,
  caption:`Kitchen remodeling services — ${city}, Texas`,
  city,
  brand
 };
};

export const cityKitchenCardSceneSources=Object.freeze(Object.fromEntries(
 Object.entries(variants).map(([id,items])=>[id,items.map(item=>item.src)])
));

export const cityKitchenCardSceneAssets=Object.freeze(
 Object.values(variants).flatMap(items=>items.map(item=>Object.freeze({...item})))
);
