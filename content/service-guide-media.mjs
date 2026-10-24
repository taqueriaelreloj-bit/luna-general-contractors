import profiles from './service-guide-profiles.mjs';
import {ownedMedia} from './page-owned-imagery.mjs';
export const targetServiceKeys=["insurance-claims", "kitchen-remodeling", "bathroom-remodeling", "shower-remodeling", "backsplash-installation", "cabinet-installation", "flooring", "painting", "drywall", "siding", "carpentry", "fencing", "commercial-construction", "concrete-driveways", "door-installation", "window-replacement", "foundation-repair", "outdoor-living", "patio-covers", "pergolas", "room-additions", "whole-home-remodeling", "general-contractor"];
export const cityGuideCaption=(serviceName,city)=>{if(!serviceName||!city)throw new Error('Service and city required');return `${serviceName} services — ${city}, Texas`;};
export default Object.defineProperties({},Object.fromEntries(targetServiceKeys.map(key=>[key,{enumerable:true,get:()=>ownedMedia(profiles[key].hub,key)}])));
