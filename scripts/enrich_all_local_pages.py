from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path

MANIFEST = Path("seo-generated-manifest.txt")
FAQ_ANCHOR = '<section class="seo-section seo-faq">'
BLOG_CLASS = "seo-section seo-mini-blog"

SERVICE_SUFFIXES = {
    "bathroom-remodeling": "Bathroom Remodeling",
    "carpentry": "Carpentry",
    "commercial-construction": "Commercial Construction",
    "drywall": "Drywall",
    "fencing": "Fencing",
    "flooring": "Flooring",
    "general-contractor": "General Contracting",
    "insurance-claims": "Insurance Claim Restoration",
    "kitchen-remodeling": "Kitchen Remodeling",
    "painting": "Painting",
    "roofing": "Roofing",
    "siding": "Siding",
    "water-damage-restoration": "Water Damage Restoration",
}

# These pages are hubs or long-form articles and already have a different editorial purpose.
EXCLUDED = {
    "articles.html",
    "service-areas.html",
    "services-by-city.html",
    "bathroom-remodeling-cost-waxahachie.html",
    "best-general-contractor-midlothian.html",
    "commercial-construction-planning-dallas.html",
    "drywall-repair-after-water-damage-grand-prairie.html",
    "fence-replacement-cost-cedar-hill.html",
    "flooring-options-mansfield.html",
    "kitchen-remodeling-ideas-texas.html",
    "roof-replacement-cost-dallas.html",
    "roofing-insurance-claim-fort-worth.html",
    "water-damage-insurance-claims-arlington.html",
}

SERVICE_TOPICS = {
    "Bathroom Remodeling": [
        ("Waterproofing Before Tile", "A bathroom can look finished while still depending on details hidden behind the tile. Substrate preparation, shower-pan slope, wall waterproofing, penetrations, and transitions should be planned before finish materials go in.", "We also review fixture locations, ventilation, lighting, storage, and clearances so the room works well after the remodel, not only on the day it is completed."),
        ("Layout Changes and Trade Coordination", "Moving a vanity, toilet, shower, or tub can affect plumbing, electrical work, framing, drywall, and flooring at the same time. Coordinating those trades early helps avoid cutting into newly completed work later.", "A clear layout also makes it easier to select tile sizes, glass, faucets, cabinetry, and lighting that fit the actual dimensions of the room."),
        ("Shower Details That Protect the Remodel", "The shower is one of the most detail-sensitive parts of a bathroom remodel. Drain location, slope, waterproofing, niches, curbs, corners, and glass attachment points all need to work together.", "Planning those items before tile installation gives the finish crew better control of cuts and alignment and gives the homeowner a clearer idea of the final layout."),
        ("Planning for Daily Use", "A bathroom should be designed around the people who use it every day. Counter space, storage, mirror height, lighting, shower access, and fixture clearances can matter as much as the finish selections.", "We review those practical items before construction so the remodel improves function while still matching the style of the home."),
        ("What Should Be Checked After Demolition", "Demolition can reveal conditions that were impossible to confirm from the finished room, including framing changes, old plumbing, moisture damage, or uneven surfaces. Those discoveries should be evaluated before new finishes cover them again.", "Documenting the condition at that stage helps separate necessary repairs from optional upgrades and keeps the revised scope easier to understand."),
        ("Tile Planning Starts Before Installation", "Tile size, pattern, grout joints, niches, corners, and transitions should be considered before the first tile is set. Small layout adjustments can reduce awkward cuts and create cleaner lines around fixtures and openings.", "The installation also depends on a flat, properly prepared surface, so correcting the substrate first is often more important than rushing into finish work."),
    ],
    "Carpentry": [
        ("Finish Carpentry Depends on the Base", "Trim, casing, doors, built-ins, and other finish carpentry look best when the openings and surfaces behind them are straight and secure. Small framing or alignment issues can become very visible after paint or stain.", "Checking measurements, fastening, material movement, and transitions before installation helps the completed work look intentional and consistent with the rest of the property."),
        ("Repair the Cause Before the Trim", "Damaged exterior or interior wood can sometimes be the visible result of a moisture, movement, or fastening problem. Replacing only the finish piece may leave the original cause in place.", "A better repair starts by checking the surrounding area, correcting the underlying condition when accessible, and then installing and sealing the replacement material."),
        ("Door and Opening Details", "Door work can involve more than changing the slab. Jamb condition, rough-opening size, floor height, hinges, strike alignment, casing, and weather sealing can all affect how the finished door operates.", "Reviewing those items before installation helps reduce sticking, uneven reveals, and trim corrections after the door is already painted."),
        ("Built-Ins Need Accurate Field Measurements", "Built-ins and custom carpentry should be designed from actual field dimensions rather than assumed room sizes. Walls, floors, and ceilings are not always perfectly square, especially after previous remodeling.", "Taking those conditions into account helps improve fit, reveals, countertop alignment, and the way the new work connects to nearby trim and finishes."),
        ("Exterior Wood Needs Water Management", "Exterior trim and wood repairs should be planned around how water moves across the wall. Caulk joints, flashing, clearances, end cuts, and penetrations can all affect how long a repair lasts.", "Sealing and coating the new material correctly is important, but keeping repeated moisture away from the repair is just as important."),
        ("Framing and Finish Work Should Be Sequenced", "Carpentry often sits between structural work and final finishes. If framing, blocking, cabinets, doors, or trim are installed in the wrong sequence, later trades may have to remove or alter completed work.", "A simple sequence plan helps keep dimensions consistent and gives drywall, tile, paint, and fixture installers the backing and clearances they need."),
    ],
    "Commercial Construction": [
        ("Plan Work Around Building Operations", "Commercial improvements often have to share space with employees, customers, deliveries, and normal business activity. Access, dust control, noise, shutdowns, and material staging should be discussed before work begins.", "A phased plan can make the scope easier to manage and reduce unnecessary interruptions while still allowing inspections and trade coordination to happen in the right order."),
        ("Field Conditions Drive the Scope", "Commercial spaces frequently contain previous tenant improvements, concealed utilities, and finishes installed at different times. A walkthrough can identify visible conflicts, but some conditions only become clear after selective demolition.", "Documenting those discoveries and updating the scope before covering them again helps keep the project organized and reduces confusion between trades."),
        ("Coordinate Trades Before Closing Walls", "Electrical, plumbing, HVAC, framing, blocking, data, and fire-related components can all compete for the same wall or ceiling space. Closing an area before those systems are coordinated can create expensive rework.", "Reviewing rough-in locations and required access first gives each trade a clearer path and helps the finish phase move more efficiently."),
        ("Durability Matters in High-Traffic Areas", "Commercial finishes are often exposed to more foot traffic, cleaning, carts, furniture movement, and daily wear than residential surfaces. Material selection should account for that use rather than appearance alone.", "Flooring, wall protection, paint, trim, doors, and hardware can all be chosen with maintenance and replacement cycles in mind."),
        ("Small Scope Changes Can Affect Scheduling", "A commercial project may depend on inspections, specialty materials, business hours, and several subcontractors. Even a small layout or finish change can affect more than one part of the schedule.", "Recording decisions quickly and keeping a clear written scope helps everyone understand what changed and what work must happen next."),
        ("Closeout Starts Before the Last Day", "Punch-list work, final cleaning, hardware adjustments, touch-up paint, labels, and owner walkthrough items are easier to manage when they are tracked throughout the project.", "Keeping those items organized as work progresses can shorten the final closeout period and make the completed space easier to turn over."),
    ],
    "Drywall": [
        ("A Good Patch Is More Than New Board", "Drywall repair includes the board, but the visible result depends heavily on fastening, tape, joint compound, sanding, texture, primer, and paint. A repair can be structurally sound and still stand out if those finish stages are rushed.", "We look at the surrounding surface and existing texture before deciding how large the blend area should be so the repair connects more naturally with the room."),
        ("Moisture Damage Should Be Dry First", "When drywall was affected by a leak, the source and moisture condition should be addressed before the wall is closed. Installing new board over damp framing or insulation can hide a problem rather than solve it.", "Once the area is ready, the repair can be rebuilt in sequence and finished to match the surrounding texture and paint as closely as practical."),
        ("Texture Matching Takes Planning", "Orange peel, knockdown, hand texture, and other finishes can vary from room to room and even from wall to wall. Matching the existing appearance often requires a test area and enough blending space around the patch.", "Primer is also important because new joint compound and old painted surfaces can absorb finish paint differently if they are not prepared consistently."),
        ("Ceiling Repairs Need Extra Attention", "Ceiling drywall repairs can reveal seams, fasteners, or texture differences more easily because light travels across the surface. Proper support, flat finishing, and a wide blend area can make a noticeable difference.", "Before closing the ceiling, it is also useful to confirm that any leak, mechanical, or framing issue above the repair has been addressed."),
        ("Repair Size Should Follow the Damage", "The visible opening is not always the correct final repair size. Soft edges, wet material, unsupported seams, or damaged backing can require the opening to be squared and extended to solid material.", "Creating clean edges and reliable backing first gives the new drywall a better base and makes the finishing stages more predictable."),
        ("Paint Sheen Can Reveal the Repair", "Higher-sheen paint can make surface differences easier to see, especially near windows or strong lighting. That is why sanding, feathering, texture, and primer should be evaluated before the finish coat is applied.", "Sometimes painting a larger wall or ceiling area produces a more consistent appearance than touching up only the immediate patch."),
    ],
    "Fencing": [
        ("Fence Life Starts at the Posts", "A fence can have new pickets and rails but still perform poorly if the posts are loose, undersized, or set incorrectly. Post spacing, depth, alignment, and drainage around the base all influence long-term stability.", "Checking the frame first helps determine whether a section can be repaired or whether rebuilding that portion will provide a better result."),
        ("Gates Need Their Own Plan", "Gates carry more movement and concentrated weight than a normal fence panel. Hinge placement, post strength, frame bracing, latch alignment, and ground clearance should be planned as a system.", "A properly supported gate is less likely to sag or drag as the wood moves and weather conditions change."),
        ("Wood Movement Is Normal", "Fence boards expand, contract, and dry over time, so installation details should allow for normal movement while keeping the line of the fence consistent. Fastener choice and spacing also affect how the boards age.", "Sealing or staining after the material is ready can help with appearance and moisture exposure, but it does not replace sound framing and installation."),
        ("Repair Versus Replacement", "Storm damage, rot, leaning posts, and repeated patching can make it difficult to decide whether a fence section should be repaired or replaced. The answer usually depends on the condition of the structural frame, not only the pickets.", "Inspecting posts, rails, gates, and transitions first helps create a scope that addresses the weak areas instead of repeatedly repairing the same symptoms."),
        ("Property Transitions Need Clean Details", "Fence lines often meet driveways, retaining walls, neighboring fences, gates, and changes in grade. Those transitions can become weak or awkward if they are treated as an afterthought.", "Field-measuring the actual slope and connection points helps keep panel heights, gaps, and gate clearances more consistent."),
        ("Fasteners and Hardware Matter", "Exterior fasteners and gate hardware are exposed to moisture and repeated movement. Using components intended for exterior service can reduce staining, corrosion, and premature loosening.", "Hardware placement should also be coordinated with the fence framing so loads transfer into solid material rather than only through thin pickets."),
    ],
    "Flooring": [
        ("The Subfloor Controls the Finish", "New flooring follows the surface beneath it. High spots, low spots, movement, moisture, old adhesive, or damaged subfloor can affect the appearance and performance of the finished installation.", "Checking and preparing the base before material goes down can reduce hollow areas, uneven transitions, movement, and premature wear."),
        ("Choose Flooring for the Room", "A product that works well in a bedroom may not be the best choice near an exterior door, kitchen, laundry, or other area exposed to water and heavy traffic. Material selection should reflect how the space is actually used.", "We also consider cleaning, pets, furniture, sunlight, and the way the new floor will transition into nearby rooms."),
        ("Transitions Should Be Planned Early", "Floor height can change when old material is removed or a different product is installed. Door clearance, reducers, thresholds, baseboards, quarter round, cabinets, and appliances can all be affected.", "Measuring those relationships before installation helps avoid improvised transitions at the end of the job."),
        ("Moisture Checks Protect the Installation", "Wood, concrete, and some flooring products respond differently to moisture. When conditions call for it, checking the substrate and following the product requirements can help avoid cupping, adhesive problems, or movement.", "The goal is to match the installation method to both the product and the surface underneath it."),
        ("Layout Affects the Final Appearance", "Plank direction, tile layout, starting points, and focal areas can change how a room looks. A small shift in layout can also reduce narrow cuts at walls or awkward pieces at doorways.", "Reviewing the visible lines before installation gives the homeowner and installer a common plan for the finished appearance."),
        ("Removal Can Reveal Needed Repairs", "Old flooring sometimes hides cracked underlayment, damaged subfloor, uneven patches, or previous repairs. Those conditions are easier to address after demolition and before new material is installed.", "Treating that stage as part of preparation, rather than an unexpected delay, helps create a more reliable base for the new floor."),
    ],
    "General Contracting": [
        ("A Clear Scope Connects the Trades", "Remodeling work often overlaps between framing, plumbing, electrical, drywall, flooring, cabinets, paint, and finish carpentry. A written scope helps show where one trade stops and another begins.", "That coordination is especially useful when hidden conditions are discovered, because the project can be adjusted without losing track of the original plan."),
        ("Sequence Matters as Much as the Work", "Even good workmanship can be damaged when tasks happen in the wrong order. Rough-ins, inspections, wall close-up, cabinets, flooring, trim, fixtures, and paint should be sequenced around the actual project.", "Planning that order before work starts can reduce rework and helps materials arrive when the job is ready for them."),
        ("Unknown Conditions Should Be Documented", "Existing homes and commercial spaces can contain previous repairs, concealed damage, or construction that differs from what is visible. Some of those conditions cannot be confirmed until an area is opened.", "Documenting what is found and explaining the effect on scope, cost, or schedule gives the owner a clearer basis for decisions."),
        ("Material Decisions Affect Multiple Trades", "Changing a countertop, flooring thickness, cabinet layout, fixture, or door can affect measurements and work performed by several trades. Late selections can therefore create more than a simple purchasing delay.", "Identifying key decisions early helps keep dimensions coordinated and reduces last-minute changes in finished areas."),
        ("Site Protection Is Part of the Plan", "Construction inside an occupied property requires more than completing the repair itself. Dust paths, floor protection, access, debris removal, material storage, and daily cleanup all affect how manageable the project feels.", "Planning those items up front helps protect areas outside the work zone and gives crews a more organized place to work."),
        ("A Final Walkthrough Should Match the Scope", "The closeout stage is easier when the original scope, approved changes, and finish expectations have been documented throughout the project. Punch-list items can then be separated from new requests.", "A structured final walkthrough helps confirm operation, appearance, cleanup, and any remaining corrections before the project is considered complete."),
    ],
    "Insurance Claim Restoration": [
        ("Document Before Reconstruction", "Photos, measurements, visible damage notes, and a written repair scope create a useful record before damaged areas are rebuilt. The documentation should describe observed conditions without assuming what cannot yet be confirmed.", "When several trades are affected by the same event, organizing the damage by room and trade can make the reconstruction plan easier to review."),
        ("One Loss Can Affect Several Trades", "Water, wind, hail, or another event may involve roofing, drywall, flooring, cabinets, paint, trim, or mechanical components at the same property. Looking at only one visible area can miss connected repair work.", "A coordinated scope helps show the sequence needed to return the damaged areas to a finished condition."),
        ("Hidden Damage Needs Field Verification", "Some conditions cannot be confirmed until damaged finishes are removed. Wet insulation, deteriorated backing, damaged framing, or additional affected materials may become visible during demolition.", "Recording those discoveries before reconstruction gives the owner and claim professionals a clearer explanation of why the scope changed."),
        ("Measurements Support the Repair Scope", "Room dimensions, affected surface areas, linear footage, material quantities, and photographs help connect the written scope to the actual property. Consistent measurements can also reduce confusion when estimates are compared.", "The goal is to make each requested repair traceable to a documented condition rather than relying on a generic allowance."),
        ("Emergency Work and Reconstruction Are Different", "Stopping active damage, drying, demolition, and temporary protection are different phases from rebuilding drywall, flooring, cabinets, paint, and other finishes. Keeping those scopes separated can make the project easier to understand.", "Once the structure is ready for reconstruction, the repair sequence can be planned around the materials and trades needed to restore the affected areas."),
        ("Changes Should Be Explained Clearly", "If additional damage is discovered or an original allowance does not match the actual repair needed, the difference should be documented with measurements, photos, and a description of the work.", "Clear supporting information helps distinguish a legitimate scope change from an unrelated upgrade requested by the property owner."),
    ],
    "Kitchen Remodeling": [
        ("Layout Changes Affect More Than Cabinets", "Moving an island, sink, range, refrigerator, or dishwasher can affect plumbing, electrical work, ventilation, flooring, lighting, and countertops. Reviewing those connections before demolition can prevent conflicts after materials are ordered.", "A practical kitchen plan starts with clear walkways and appliance use, then builds the finish selections around that layout."),
        ("Cabinet Measurements Drive the Room", "Cabinet dimensions affect countertop fabrication, appliance openings, fillers, trim, plumbing locations, and backsplash layout. Small measurement errors can create large problems once several trades depend on the same line.", "Field verification before ordering helps keep the cabinet plan connected to the actual walls, floor, and appliance specifications."),
        ("Island Planning Needs Utilities and Clearances", "A new or enlarged island may need power, plumbing, seating space, appliance access, and comfortable walking clearance around every side. Those requirements should be coordinated before the floor and cabinets are finished.", "The best island size is the one that improves use of the room without creating tight circulation or blocking nearby doors and appliances."),
        ("Backsplash Layout Starts at the Countertop", "Outlets, cabinet bottoms, windows, corners, and countertop changes can all affect backsplash cuts and pattern alignment. Reviewing those points before tile installation can create a cleaner finished layout.", "It is also useful to confirm wall flatness and any drywall repair before setting tile so the finish does not have to compensate for an uneven base."),
        ("Lighting Should Follow the Work Areas", "Kitchen lighting can include general ceiling light, task lighting at counters, pendants, and accent lighting. Fixture placement works best when it follows the actual cabinet, island, sink, and appliance layout.", "Coordinating lighting before drywall and finish work reduces patching and helps place switches and fixtures where they are convenient to use."),
        ("Finish Selections Need a Common Plan", "Cabinet color, countertop pattern, backsplash, hardware, flooring, paint, and fixtures all meet in the same room. Selecting them independently can create transitions that were not obvious from samples.", "Reviewing the group together before final orders helps keep undertones, scale, maintenance needs, and installation details aligned."),
    ],
    "Painting": [
        ("Preparation Changes the Final Result", "Fresh paint highlights the condition of the surface underneath it. Nail holes, failed caulk, glossy areas, stains, cracks, and uneven texture should be addressed before the finish coat is applied.", "Cleaning, patching, sanding, caulking, and priming where needed can improve adhesion and create a more consistent appearance."),
        ("Sheen Should Match the Use", "Walls, bathrooms, kitchens, trim, doors, and exterior surfaces can have very different moisture and wear conditions. The same paint sheen is not always the best choice for every area.", "Selecting the coating around cleaning needs, light reflection, and traffic helps the finished work perform better after the project is complete."),
        ("Repairs Should Be Finished Before Color", "Drywall patches, trim repairs, water stains, and old caulk can remain visible through new paint if they are not properly prepared. Primer and surface correction should be considered part of the finish system.", "A consistent base also helps the selected color and sheen look more uniform across repaired and existing areas."),
        ("Exterior Paint Depends on the Substrate", "Exterior coating performance depends on the condition of siding, trim, masonry, caulk joints, and previously painted surfaces. Loose material and moisture-related damage should be corrected before recoating.", "Proper preparation gives the new finish a better surface to bond to and can reveal areas that need repair rather than paint alone."),
        ("Light Can Expose Surface Differences", "Natural and artificial light can make patches, roller marks, texture changes, and sheen differences easier to see. The most visible walls may need wider blending or a complete coat instead of a small touch-up.", "Reviewing the room under normal lighting conditions helps set a more realistic finish plan before painting begins."),
        ("Color Is Only One Part of the Specification", "Paint selection also includes product type, sheen, primer needs, number of coats, and which surfaces are included. Clarifying doors, trim, ceilings, closets, and accent areas prevents gaps in the scope.", "A written finish schedule can make the work easier to inspect and helps keep different rooms consistent."),
    ],
    "Roofing": [
        ("Storm Checks Should Cover the Whole System", "After hail, wind, or heavy rain, visible shingle damage is only one part of a roof review. Flashing, vents, penetrations, edges, drainage, and interior signs of moisture may also provide useful information.", "Looking at the system as a whole helps separate isolated repairs from conditions that may justify a broader roofing scope."),
        ("Flashing Details Matter", "Roof leaks often develop around transitions and penetrations rather than in the middle of an open shingle field. Walls, chimneys, vents, pipes, valleys, and roof-to-roof intersections deserve careful attention.", "Repairing those areas correctly requires understanding how water should move across and away from each connection."),
        ("Replacement Includes More Than Shingles", "A roof replacement can involve underlayment, decking repairs, ventilation, flashing, drip edge, penetrations, accessories, and cleanup in addition to the visible shingles.", "Reviewing those components before installation gives the homeowner a clearer scope and reduces surprises once the old roofing is removed."),
        ("Interior Stains Do Not Always Identify the Entry Point", "Water can travel along decking, framing, fasteners, or other surfaces before it becomes visible on a ceiling. The stain location therefore may not be directly below the exterior opening.", "A roof inspection should trace likely paths and check surrounding components rather than assuming the first visible spot is the complete problem."),
        ("Ventilation Works With the Roof Assembly", "Attic ventilation can affect heat and moisture conditions beneath the roof. Intake and exhaust components should be considered together rather than adding vents without a plan.", "When replacement work is scheduled, it is a useful time to review whether existing vents and penetrations fit the roofing system and attic configuration."),
        ("Decking Condition Is Confirmed After Tear-Off", "Some roof decking conditions cannot be fully seen until the existing roofing materials are removed. Soft, deteriorated, or previously patched areas may require repair before the new system is installed.", "Explaining that possibility in advance helps the owner understand why final decking quantities may depend on field conditions."),
    ],
    "Siding": [
        ("Siding Is Part of the Weather Barrier", "Siding affects appearance, but it also helps protect the wall assembly from wind-driven rain and daily weather exposure. Cracks, loose pieces, failed joints, and damaged trim can allow moisture to reach concealed areas.", "A repair should consider both the visible finish and the way water is managed behind and around it."),
        ("Transitions Need Careful Sealing", "Windows, doors, penetrations, corners, roof lines, and changes between materials are common places for siding details to become important. Caulk alone is not always the complete water-management solution.", "Reviewing flashing, clearances, and the condition of adjacent trim helps create a repair that addresses the connection rather than only the surface."),
        ("Match the Existing Profile Before Ordering", "Siding profiles, textures, exposures, and trim details can vary even when materials look similar from a distance. Measuring and comparing the existing product before ordering can reduce mismatched repairs.", "When an exact match is unavailable, the scope should identify where transitions will occur so the finished appearance can be planned deliberately."),
        ("Moisture Damage Should Be Traced", "Soft trim, swollen siding, peeling paint, or staining can indicate repeated moisture exposure. Replacing the damaged finish without checking the source may allow the same condition to return.", "Opening the affected area when appropriate can help determine whether backing, framing, or flashing also needs attention."),
        ("Clearances Help Siding Last", "Siding and trim often need space from roofing, soil, paving, and other surfaces that can hold or redirect water. Incorrect clearances can keep materials wet and accelerate deterioration.", "A repair is a good opportunity to review those nearby conditions instead of simply matching the old installation detail."),
        ("Paint Preparation Starts With Sound Material", "Paint can protect many siding and trim products, but it cannot stabilize rotten, loose, or water-damaged material. Repairs and fastening should be completed before final caulk, primer, and paint.", "Creating a sound base first helps the coating system perform more consistently and makes the finished repair look cleaner."),
    ],
    "Water Damage Restoration": [
        ("Water Can Travel Beyond the First Stain", "Moisture can move through wall cavities, flooring layers, cabinets, insulation, and framing farther than the first visible mark suggests. The source should be controlled before reconstruction begins.", "Moisture readings, access openings, and visible condition checks can help define which materials may dry in place and which may require removal."),
        ("Dry Before Rebuilding", "New drywall, flooring, trim, or cabinets should not be used to cover an area that is still holding excess moisture. Drying and verification are separate steps from cosmetic reconstruction.", "Once the affected structure is ready, the rebuild can be sequenced so repaired finishes connect cleanly with surrounding areas."),
        ("Cabinets and Flooring Can Hide Moisture", "Water can move under toe kicks, behind cabinets, beneath floating floors, or into underlayment without remaining visible at the surface. Those concealed paths should be considered when defining the affected area.", "Selective access and moisture checks can provide better information before deciding how much material needs to be removed."),
        ("Reconstruction Requires Trade Sequencing", "After mitigation, the property may need drywall, texture, paint, flooring, trim, cabinets, plumbing fixtures, or other finishes. Those repairs overlap and should be completed in a practical order.", "A coordinated rebuild plan can reduce repeated removals and helps the final repaired area blend with the rest of the room."),
        ("The Source and the Damage Are Separate Issues", "Stopping a plumbing leak or other water source prevents additional damage, but it does not automatically restore materials that were already wet. The affected finishes and concealed areas still need to be evaluated.", "Separating source repair, drying, removal, and reconstruction makes the scope easier for the property owner to understand."),
        ("Document Conditions During Removal", "Demolition can reveal wet insulation, damaged backing, staining, or additional affected materials that were not visible before. Photographing and measuring those findings creates a useful record before the area is closed.", "That documentation can also help explain why the reconstruction scope changed from the initial visible assessment."),
    ],
}

GENERAL_TOPICS = [
    ("Planning a Remodel Around Existing Conditions", "Every property has a different combination of age, previous repairs, materials, access, and hidden construction. A useful estimate starts with what is actually present rather than assuming the building matches a standard plan.", "Reviewing visible conditions and the trades that may interact with the work helps create a more realistic sequence before demolition begins."),
    ("Why a Written Scope Matters", "A remodeling project is easier to manage when the work is described clearly before crews begin. Separating demolition, repairs, installation, finishes, and owner selections helps show what is included and where decisions are still needed.", "The same scope can then be used to discuss changes if hidden conditions are discovered during construction."),
    ("Coordinate Decisions Before Ordering Materials", "Cabinets, flooring, tile, fixtures, doors, countertops, and paint can depend on dimensions or choices made by other trades. Ordering too early can lock the project into a detail that no longer fits the field conditions.", "Confirming measurements and major selections first can reduce returns, delays, and last-minute modifications."),
    ("Existing Homes Often Reveal Surprises", "Previous remodeling, concealed damage, or nonstandard construction may not be visible until an area is opened. Those discoveries are normal reasons to verify conditions before covering the work again.", "Documenting the finding and its effect on the scope gives the owner a clearer basis for approving the next step."),
    ("The Best Sequence Protects Finished Work", "Construction has a natural order. Rough work, inspections, wall repairs, cabinets, flooring, trim, fixtures, and paint should be planned so later trades do not damage work that was completed too early.", "A coordinated sequence also makes cleanup and material staging easier in an occupied property."),
    ("Local Service Means Field-Based Planning", "Online price ranges can be useful for early budgeting, but the actual property determines the labor, access, preparation, material quantities, and coordination required. Field measurements provide the information needed for a written project scope.", "That approach helps compare options based on the real building rather than a generic example."),
]

CITY_LEADS = [
    "For a project in {city}, the useful starting point is the condition of the actual property and the way the space is used.",
    "In {city}, we approach remodeling by connecting the requested finish work to the existing building conditions behind it.",
    "A {city} project is easier to plan when measurements, access, existing materials, and trade dependencies are reviewed together.",
    "For homeowners and property managers in {city}, a clear field-based scope can make remodeling decisions easier to compare.",
    "Before work begins at a property in {city}, it helps to identify the decisions that affect more than one trade or finish.",
    "Projects in {city} can vary widely even when the requested service sounds the same, so the scope should follow the property rather than a generic template.",
    "At a {city} property, early planning can reduce avoidable changes once demolition or installation is underway.",
    "For construction work in {city}, practical sequencing and documented field conditions are often as important as the final material selections.",
]

CLOSERS = [
    "The goal is a repair or remodel that is easier to understand before work starts and easier to inspect when it is finished.",
    "That planning gives the owner clearer expectations and gives each trade better information before its part of the work begins.",
    "A few minutes spent coordinating these details early can prevent much larger corrections after finish materials are installed.",
    "Keeping these items in the written scope also makes later changes easier to document and price separately.",
    "This approach keeps the work focused on durable results instead of solving only the most visible symptom.",
    "The final scope should reflect what the property actually needs while keeping optional upgrades clearly separated from required repairs.",
    "Clear decisions at this stage help protect the schedule and reduce unnecessary rework in completed areas.",
    "The result is a more organized project with fewer assumptions between the owner, contractor, and individual trades.",
]


def stable_index(key: str, salt: str, length: int) -> int:
    digest = hashlib.sha256(f"{salt}|{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % length


def extract_city(page_html: str, filename: str) -> str:
    match = re.search(r'<p class="eyebrow gold">(?:Serving\s+)?([^<]+?),\s*Texas</p>', page_html, re.I)
    if match:
        return re.sub(r"^Serving\s+", "", html.unescape(match.group(1)), flags=re.I).strip()

    stem = Path(filename).stem
    for suffix in sorted(SERVICE_SUFFIXES, key=len, reverse=True):
        marker = f"-{suffix}"
        if stem.endswith(marker):
            stem = stem[: -len(marker)]
            break
    return stem.replace("-", " ").title()


def extract_service(filename: str, page_html: str) -> str | None:
    stem = Path(filename).stem
    for suffix, label in sorted(SERVICE_SUFFIXES.items(), key=lambda item: len(item[0]), reverse=True):
        if stem.endswith(f"-{suffix}"):
            return label

    h1 = re.search(r"<h1>(.*?)</h1>", page_html, re.S | re.I)
    if h1 and " in " in re.sub(r"<[^>]+>", "", h1.group(1)):
        visible = re.sub(r"<[^>]+>", "", h1.group(1)).strip()
        candidate = visible.split(" in ", 1)[0].strip()
        if candidate:
            return candidate
    return None


def build_blog(filename: str, city: str, service: str | None) -> str:
    key = filename.lower()
    lead = CITY_LEADS[stable_index(key, "lead", len(CITY_LEADS))].format(city=city)
    closer = CLOSERS[stable_index(key, "closer", len(CLOSERS))]

    if service and service in SERVICE_TOPICS:
        options = SERVICE_TOPICS[service]
        title, p1, p2 = options[stable_index(key, "topic", len(options))]
        heading = f"{title} in {city}"
    else:
        title, p1, p2 = GENERAL_TOPICS[stable_index(key, "general", len(GENERAL_TOPICS))]
        heading = f"{title} in {city}"

    # Extra filename-based sentence selection makes the copy combination unique even
    # when the same service topic is used in different cities.
    paragraph_one = f"{lead} {p1}"
    paragraph_two = f"{p2} {closer}"

    return (
        '<section class="seo-section seo-mini-blog"><div class="container">'
        '<article><p class="eyebrow gold">Local Project Notes</p>'
        f'<h2>{html.escape(heading)}</h2>'
        f'<p>{html.escape(paragraph_one)}</p>'
        f'<p>{html.escape(paragraph_two)}</p>'
        '</article></div></section>'
    )


def replace_or_insert_blog(page_html: str, block: str) -> tuple[str, bool]:
    pattern = re.compile(
        r'<section class="seo-section seo-mini-blog">.*?</section>',
        re.S | re.I,
    )
    if pattern.search(page_html):
        new_html = pattern.sub(block, page_html, count=1)
        return new_html, new_html != page_html
    if FAQ_ANCHOR not in page_html:
        return page_html, False
    return page_html.replace(FAQ_ANCHOR, block + FAQ_ANCHOR, 1), True


def main() -> None:
    if not MANIFEST.exists():
        raise SystemExit("Missing seo-generated-manifest.txt")

    manifest_files = [
        line.strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip().endswith(".html")
    ]

    targets: list[str] = []
    updated: list[str] = []
    missing_anchor: list[str] = []
    blog_fingerprints: dict[str, str] = {}

    for filename in manifest_files:
        if filename in EXCLUDED:
            continue
        path = Path(filename)
        if not path.exists():
            continue
        page_html = path.read_text(encoding="utf-8")

        # Local city/service pages generated by this site include the local FAQ section.
        if FAQ_ANCHOR not in page_html and BLOG_CLASS not in page_html:
            continue

        city = extract_city(page_html, filename)
        service = extract_service(filename, page_html)
        block = build_blog(filename, city, service)
        targets.append(filename)

        fingerprint = hashlib.sha256(block.encode("utf-8")).hexdigest()
        if fingerprint in blog_fingerprints:
            other = blog_fingerprints[fingerprint]
            raise SystemExit(f"Duplicate mini-blog generated for {other} and {filename}")
        blog_fingerprints[fingerprint] = filename

        new_html, changed = replace_or_insert_blog(page_html, block)
        if BLOG_CLASS not in new_html:
            missing_anchor.append(filename)
            continue
        if changed:
            path.write_text(new_html, encoding="utf-8")
            updated.append(filename)

    if missing_anchor:
        raise SystemExit("Mini-blog insertion failed for: " + ", ".join(missing_anchor[:20]))

    # Validate every selected local page now contains exactly one mini-blog block.
    invalid: list[str] = []
    for filename in targets:
        text = Path(filename).read_text(encoding="utf-8")
        if text.count(BLOG_CLASS) != 1:
            invalid.append(filename)
    if invalid:
        raise SystemExit("Mini-blog validation failed for: " + ", ".join(invalid[:20]))

    print(f"Local pages checked: {len(targets)}")
    print(f"Local pages updated: {len(updated)}")
    print(f"Unique mini-blog blocks validated: {len(blog_fingerprints)}")


if __name__ == "__main__":
    main()
