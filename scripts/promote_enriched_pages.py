#!/usr/bin/env python3
"""Promote evidence-backed local pages into the public sitemap.

The site generators can rebuild these pages. This idempotent post-processing
step restores verified-work context, complete social metadata and sitemap
coverage without claiming that a portfolio image came from a specific city
unless the related project record supports that attribution.
"""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"
LASTMOD = "2026-09-06"
START = "<!-- READY_PAGE_ENRICHMENT_START -->"
END = "<!-- READY_PAGE_ENRICHMENT_END -->"

CITY_PAGES = {
    "addison.html": {
        "city": "Addison",
        "title": "Addison, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Addison, TX, with written scopes and coordinated trades. Call Luna at (817) 784-5998 for a free estimate.",
        "planning": "Addison projects may combine occupied homes, townhomes and commercial spaces. Before pricing the work, we separate access requirements, protection, trade sequencing and any urgent weather-exposure items from the planned improvements.",
        "checks": [
            "Confirm residential or commercial access and allowable working areas.",
            "Inspect roof penetrations, flashing, transitions and drainage before selecting a repair.",
            "Identify interior protection when exterior damage has reached ceilings or walls.",
            "Write exclusions and concealed-condition allowances into the scope.",
        ],
    },
    "aledo.html": {
        "city": "Aledo",
        "title": "Aledo, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Aledo, TX, with site-specific scopes and coordinated trades. Call (817) 784-5998 for a free estimate.",
        "planning": "Aledo estimates should account for the actual lot, building access and connections between roofing, drainage and exterior finishes. Material matching and delivery planning are confirmed before the scope is finalized.",
        "checks": [
            "Confirm delivery access, work-area protection and material staging.",
            "Review roof slopes, penetrations, flashing and runoff at the property.",
            "Compare existing exterior materials before promising a visual match.",
            "Sequence roofing, carpentry, siding, drywall and paint where scopes overlap.",
        ],
    },
    "benbrook.html": {
        "city": "Benbrook",
        "title": "Benbrook, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Benbrook, TX, based on the property's visible conditions. Call Luna at (817) 784-5998 for a free estimate.",
        "planning": "For Benbrook repairs, the first visible stain or damaged shingle may not define the full scope. We trace likely entry points, examine roof-to-wall details and document connected interior finishes before recommending work.",
        "checks": [
            "Examine roof edges, wall transitions, chimneys, vents and drainage paths.",
            "Photograph visible wind or hail conditions before temporary or permanent repairs.",
            "Trace interior staining to the likely exterior source instead of patching only the finish.",
            "Confirm cleanup, access and protection requirements in writing.",
        ],
    },
    "denton.html": {
        "city": "Denton",
        "title": "Denton, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Denton, TX, with clear scopes for homes, rentals and businesses. Call (817) 784-5998 for an estimate.",
        "planning": "Denton work can involve established buildings, newer additions, rentals and occupied commercial areas. A useful inspection separates existing repairs from new damage and confirms which trades must be completed first.",
        "checks": [
            "Document previous repairs and the condition of adjoining materials.",
            "Review ventilation, roof penetrations, flashing and drainage together.",
            "Plan access and working hours around occupants or business operations.",
            "Verify finish matching before drywall, flooring or paint work begins.",
        ],
    },
    "flower-mound.html": {
        "city": "Flower Mound",
        "title": "Flower Mound, TX General Contractor | Luna",
        "description": "Roofing, remodeling, restoration and commercial construction in Flower Mound, TX. Call Luna at (817) 784-5998 for a free project estimate.",
        "planning": "Flower Mound projects often connect exterior protection with interior finish work. We document roof and wall tie-ins, confirm material lead times and organize the trade sequence around the occupied property.",
        "checks": [
            "Review roofing, drainage and exterior-envelope details as one system.",
            "Confirm how new materials will connect to existing finishes.",
            "Identify owner, property-management or association requirements before scheduling.",
            "Plan protection and daily access for occupied spaces.",
        ],
    },
    "highland-village.html": {
        "city": "Highland Village",
        "title": "Highland Village, TX General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Highland Village, TX, with coordinated trades and written scopes. Call (817) 784-5998 for an estimate.",
        "planning": "Highland Village scopes should connect roof protection, exterior details and any affected interior finishes. We document existing materials and access needs before recommending repair, replacement or coordinated remodeling.",
        "checks": [
            "Inspect roof edges, penetrations, ventilation, flashing and visible drainage conditions.",
            "Protect landscaping, entries and interior traffic paths during the work.",
            "Record material and finish selections before ordering.",
            "Sequence roofing, carpentry, drywall and painting when more than one trade is involved.",
        ],
    },
}

ARTICLE_PAGES = {
    "best-flooring-for-pets-grand-prairie.html": {
        "title": "Pet-Friendly Flooring in Grand Prairie, TX | Luna",
        "description": "Compare pet-friendly flooring for Grand Prairie homes by scratch resistance, moisture, traction, cleanup and subfloor needs. Request a free estimate.",
        "image": "dfw-gray-plank-flooring-installation-2018.jpg", "width": 669, "height": 891,
        "alt": "Finished gray wood-look plank flooring installed by Luna General Contractors in DFW",
        "caption": "Completed plank-flooring work from Luna's documented DFW project portfolio.",
        "heading": "Pet-friendly flooring inspection checklist",
        "checks": ["Pet size, activity level and traction needs", "Likely water-bowl and accident exposure", "Direct sunlight and room temperature changes", "Subfloor flatness, moisture and damaged areas", "Transitions, stairs, doors and adjoining floor heights"],
        "proof": "The portfolio photo shows completed Luna flooring work. It demonstrates installation quality but is not presented as the exact Grand Prairie home discussed in this guide.",
        "proof_link": "flooring.html", "proof_label": "View verified flooring photos",
    },
    "commercial-tenant-improvement-planning-irving.html": {
        "title": "Commercial Tenant Improvements in Irving, TX | Luna",
        "description": "Plan an Irving tenant improvement around permits, existing systems, access, trade sequencing, inspections and turnover. Request a written project scope.",
        "image": "dfw-commercial-deli-finish-out-2019.jpg", "width": 669, "height": 891,
        "alt": "Completed commercial deli finish-out with service counter, cabinets, flooring and lighting",
        "caption": "Completed commercial finish-out from Luna's documented DFW project portfolio.",
        "heading": "Tenant-improvement preconstruction checklist",
        "checks": ["Lease and landlord construction requirements", "Permit, plan-review and inspection responsibilities", "Existing electrical, plumbing and HVAC capacity", "Occupied-hours, deliveries, dust control and public access", "Long-lead finishes, final cleaning and turnover documentation"],
        "proof": "This completed DFW finish-out demonstrates coordinated cabinets, counter, flooring and lighting. It is included as workmanship evidence and is not represented as the specific Irving property.",
        "proof_link": "commercial.html", "proof_label": "View commercial project photos",
    },
    "drywall-texture-matching-desoto.html": {
        "title": "Drywall Texture Matching in DeSoto, TX | Luna",
        "description": "Learn how DeSoto drywall patches are blended by identifying texture, widening the repair, priming and matching paint sheen. Request a free estimate.",
        "image": "drywall-commercial-project.jpg", "width": 1600, "height": 900,
        "alt": "Commercial drywall construction in progress by Luna General Contractors",
        "caption": "Documented drywall construction in progress from Luna's DFW portfolio.",
        "heading": "What to record before matching texture",
        "checks": ["Texture pattern under direct and side lighting", "Patch dimensions and nearby joints or corners", "Whether the leak or movement that caused damage is corrected", "Existing primer, paint color and sheen", "A dry sample area before coating the full repair"],
        "proof": "The project image verifies Luna's drywall experience. Texture matching still requires an on-site sample because lighting, previous paint and application technique change the final appearance.",
        "proof_link": "drywall.html", "proof_label": "View drywall project photos",
    },
    "exterior-paint-preparation-cedar-hill.html": {
        "title": "Exterior Paint Preparation in Cedar Hill, TX | Luna",
        "description": "Prepare a Cedar Hill exterior with cleaning, scraping, repairs, caulk and spot primer before paint. See the checklist and request an estimate.",
        "image": "siding-after.jpg", "width": 1600, "height": 1200,
        "alt": "Completed residential siding and exterior finish project by Luna General Contractors",
        "caption": "Completed siding and exterior-finish work from Luna's documented DFW portfolio.",
        "heading": "Exterior preparation walk-through checklist",
        "checks": ["Loose coating, chalking, mildew and surface contamination", "Rot, open joints and damaged siding or trim", "Failed caulk around openings and penetrations", "Bare areas that require the correct primer", "Weather window, masking, landscaping protection and cure time"],
        "proof": "The photograph documents completed Luna exterior work. Paint cannot correct rot, movement or failed weather details, so those conditions belong in the repair scope before coating.",
        "proof_link": "painting.html", "proof_label": "Review Luna's painting process",
    },
    "kitchen-remodel-planning-mansfield.html": {
        "title": "Mansfield Kitchen Remodel Planning | Luna",
        "description": "Plan a Mansfield kitchen remodel around layout, cabinets, countertops, appliances, lighting, plumbing and construction sequence. Request an estimate.",
        "image": "dfw-kitchen-remodel-quartz-island-2018.jpg", "width": 669, "height": 891,
        "alt": "Completed white and gray kitchen remodel with quartz island by Luna General Contractors",
        "caption": "Completed kitchen remodeling work from Luna's documented DFW project portfolio.",
        "heading": "Decisions to confirm before demolition",
        "checks": ["Final cabinet plan and appliance specifications", "Countertop overhangs, sink, faucet and backsplash dimensions", "Electrical, lighting, ventilation and plumbing changes", "Flooring transitions and finished floor height", "Material lead times and the order of inspections and trades"],
        "proof": "For a Mansfield-specific example, Luna's documented gray subway-tile backsplash case records the materials, detailed cuts and approximately two-day installation without adding undocumented claims.",
        "proof_link": "gray-subway-kitchen-backsplash-mansfield.html", "proof_label": "See the verified Mansfield kitchen case",
    },
    "roof-repair-vs-replacement-arlington.html": {
        "title": "Roof Repair or Replacement in Arlington, TX | Luna",
        "description": "Compare roof repair and replacement in Arlington using age, damage extent, flashing, decking and leak history. Request a documented inspection.",
        "image": "dfw-roof-replacement-brick-home-2019.jpg", "width": 1188, "height": 891,
        "alt": "Completed architectural shingle roof on a brick home by Luna General Contractors",
        "caption": "Completed shingle-roof work from Luna's documented DFW project portfolio.",
        "heading": "Information needed for a repair-or-replace decision",
        "checks": ["Roof age, material and available matching products", "Number and location of leaks or impact areas", "Flashing, penetrations, valleys, edges and ventilation", "Decking condition visible from accessible areas", "Prior repairs, warranties and the owner's expected time in the property"],
        "proof": "The image documents completed Luna roofing work in DFW. A photograph alone cannot determine the correct Arlington scope; the decision requires inspection of the actual roof.",
        "proof_link": "roofing.html", "proof_label": "View verified roofing photos",
    },
    "storm-damage-documentation-fort-worth.html": {
        "title": "Documenting Storm Damage in Fort Worth, TX | Luna",
        "description": "Document Fort Worth storm damage safely with dated photos, affected rooms, temporary repairs, estimates and receipts. Request a construction scope.",
        "image": "dfw-commercial-ceiling-damage-documentation-2024.jpg", "width": 669, "height": 891,
        "alt": "Commercial ceiling damage documented for a construction repair scope in DFW",
        "caption": "Visible ceiling damage documented during development of a DFW construction repair scope.",
        "heading": "Storm file checklist",
        "checks": ["Storm date and when each condition was first observed", "Wide and close photos taken from safe accessible locations", "Room-by-room list of stains, openings and damaged finishes", "Temporary protection invoices, receipts and photographs", "Contractor scopes, carrier correspondence and revision dates"],
        "proof": "Luna can document visible construction conditions and prepare a repair scope. The insurance carrier and policy determine coverage; documentation should describe observed damage without promising a claim outcome.",
        "proof_link": "insurance-claims.html", "proof_label": "Review claim-documentation services",
    },
    "walk-in-shower-cost-midlothian.html": {
        "title": "Midlothian Walk-In Shower Cost Factors | Luna",
        "description": "Understand Midlothian walk-in shower cost factors: demolition, plumbing, waterproofing, tile, glass and hidden conditions. Request an estimate.",
        "image": "dfw-bathroom-remodel-glass-shower-2020.jpg", "width": 1188, "height": 891,
        "alt": "Finished bathroom remodel with glass shower by Luna General Contractors",
        "caption": "Completed glass-shower remodel from Luna's documented DFW project portfolio.",
        "heading": "Measurements and selections that affect the scope",
        "checks": ["Existing shower or tub dimensions and demolition limits", "Drain location, plumbing changes and subfloor condition", "Waterproofing system, niches, benches and curb design", "Tile size, pattern, edge details and grout selection", "Glass configuration, fixtures, ventilation and accessories"],
        "proof": "Luna's Midlothian master-bathroom case provides location-specific project evidence. Every new shower still needs its own measurements and concealed-condition allowance.",
        "proof_link": "luxury-master-bathroom-remodel-midlothian.html", "proof_label": "See the verified Midlothian bathroom case",
    },
    "water-damage-rebuild-process-dallas.html": {
        "title": "Dallas Water-Damage Rebuild Process | Luna",
        "description": "Follow the Dallas water-damage rebuild sequence from source correction and drying through framing, drywall, paint, flooring and final inspection.",
        "image": "dfw-interior-rebuild-framing-2018.jpg", "width": 1188, "height": 891,
        "alt": "Interior framing exposed during reconstruction work by Luna General Contractors",
        "caption": "Documented interior reconstruction work from Luna's DFW project portfolio.",
        "heading": "Rebuild readiness checklist",
        "checks": ["Water source corrected and affected areas released for reconstruction", "Damaged materials and repair boundaries documented", "Framing, insulation and mechanical conditions reviewed", "Cabinet, drywall, texture, paint and flooring matches confirmed", "Trade sequence, inspections and final cleaning included in the scope"],
        "proof": "The photograph documents Luna reconstruction work with framing exposed. It is evidence of field experience, not a claim that every Dallas loss needs the same demolition or repair sequence.",
        "proof_link": "mitigation.html", "proof_label": "Review restoration and rebuild services",
    },
    "wood-fence-repair-vs-replacement-waxahachie.html": {
        "title": "Fence Repair or Replacement in Waxahachie, TX | Luna",
        "description": "Compare wood fence repair and replacement in Waxahachie by post condition, alignment, damaged sections, gates and finish. Request an estimate.",
        "image": "fencing-project-two.jpg", "width": 1600, "height": 1200,
        "alt": "Completed stained wood privacy fence by Luna General Contractors",
        "caption": "Completed stained privacy-fence work from Luna's documented DFW project portfolio.",
        "heading": "Fence condition checklist",
        "checks": ["Loose, leaning or rotted posts and their spacing", "Rail condition and the number of damaged pickets", "Gate frame, hinges, latch and ground clearance", "Property access, utilities and drainage near the fence line", "Desired stain or sealer and replacement-material match"],
        "proof": "The image verifies completed Luna fence work. The repair-or-replacement recommendation for a Waxahachie property depends on the percentage of reusable posts, rails and sections observed on site.",
        "proof_link": "fencing.html", "proof_label": "View verified fencing photos",
    },
    "bathroom-ventilation-bedford.html": {
        "title": "Bathroom Ventilation in Bedford, TX | Luna",
        "description": "Plan bathroom ventilation in Bedford by checking fan capacity, duct route, outdoor termination, controls and moisture damage. Request a site estimate.",
        "image": "dfw-bathroom-remodel-glass-shower-2020.jpg", "width": 1188, "height": 891,
        "alt": "Finished bathroom remodel with glass shower by Luna General Contractors",
        "caption": "Completed bathroom remodeling work from Luna's documented DFW project portfolio.",
        "heading": "Bathroom ventilation site checklist",
        "checks": ["Room dimensions, ceiling height and shower enclosure", "Fan label, condition, controls and observed airflow", "Duct diameter, length, bends and insulation where accessible", "Outdoor termination and working backdraft damper", "Peeling paint, staining, soft drywall or recurring condensation"],
        "sections": [
            ("Start with the moisture pattern", "A replacement fan should be selected after documenting the room and how moisture behaves. Persistent condensation may reflect low airflow, a restricted duct, short run time or another moisture source, so the inspection should not assume the fan is the only problem."),
            ("Check the complete air path", "The grille, fan housing, duct connections and exterior hood work as one system. Accessible sections should be checked for crushed duct, excessive bends and disconnections. The room also needs a path for replacement air when the door is closed."),
            ("Sequence finish repairs correctly", "Roof or plumbing leaks must be corrected separately. Damaged areas should be evaluated and ready for reconstruction before new drywall, primer or bathroom paint is installed, reducing the chance that a fresh finish hides an unresolved condition."),
        ],
        "proof": "The photograph verifies completed Luna bathroom work in DFW. It is not presented as the Bedford bathroom described in this planning guide.",
        "proof_link": "bathrooms.html", "proof_label": "View bathroom remodeling services",
    },
    "bathroom-waterproofing-frisco.html": {
        "title": "Bathroom Waterproofing in Frisco, TX | Luna",
        "description": "Plan a Frisco shower waterproofing scope around substrate, drainage, seams, penetrations, niches and tile assembly. Request an on-site estimate.",
        "image": "dfw-bathroom-remodel-glass-shower-2020.jpg", "width": 1188, "height": 891,
        "alt": "Finished bathroom remodel with glass shower by Luna General Contractors",
        "caption": "Completed glass-shower remodel from Luna's documented DFW project portfolio.",
        "heading": "Waterproofing scope checklist",
        "checks": ["Demolition limits and condition of framing or subfloor", "Drain location and finished slope to the drain", "Compatible pan, wall-board and membrane components", "Seams, corners, curbs, niches and plumbing penetrations", "Inspection or water-test requirements for the selected assembly"],
        "sections": [
            ("Treat waterproofing as a complete assembly", "Tile and grout are finish surfaces, not the entire water-management system. The drain, sloped base, wall substrate, membrane, seams and penetrations must be planned together using components approved for the selected installation method."),
            ("Inspect what demolition reveals", "Previous leaks, movement, swollen subfloor or out-of-square framing can change the scope. Those conditions should be documented before covering the walls so repair decisions and any concealed-condition changes remain clear."),
            ("Verify before tile conceals the work", "Required inspections and testing depend on the assembly and local authority. The scope should identify who coordinates them and when tile may begin, while photographs preserve a record of corners, penetrations and other details that will no longer be visible."),
        ],
        "proof": "Luna's documented Midlothian bathroom case shows completed shower workmanship. The waterproofing design for a Frisco property must still be based on that bathroom's actual conditions.",
        "proof_link": "luxury-master-bathroom-remodel-midlothian.html", "proof_label": "See a verified bathroom case",
    },
    "ceiling-drywall-repair-garland.html": {
        "title": "Ceiling Drywall Repair in Garland, TX | Luna",
        "description": "Plan a Garland ceiling drywall repair after correcting the leak and checking gypsum, insulation, framing, texture and paint. Request an estimate.",
        "image": "drywall-commercial-project.jpg", "width": 1600, "height": 900,
        "alt": "Commercial drywall construction in progress by Luna General Contractors",
        "caption": "Documented drywall construction in progress from Luna's DFW portfolio.",
        "heading": "Ceiling repair inspection checklist",
        "checks": ["Confirmed source of roof, plumbing or HVAC moisture", "Dryness and condition of gypsum, insulation and accessible framing", "Ceiling thickness and any required assembly rating", "Patch boundaries, nearby joints and texture pattern", "Primer, ceiling paint and protection for occupied rooms"],
        "sections": [
            ("Correct the source before closing", "A ceiling stain does not identify the full path of water. The roof, plumbing or mechanical source should be corrected and the affected assembly evaluated before new drywall closes the cavity."),
            ("Match the existing ceiling assembly", "The repair scope should identify board thickness and any special assembly requirements instead of selecting material by appearance alone. Loose, sagging or deteriorated material may require a wider repair than the visible stain."),
            ("Blend the finish in stages", "A durable repair includes fastening, tape, joint compound, sanding, compatible texture, primer and paint. Side lighting often reveals patches, so the estimator should discuss how far texture and paint must extend for a reasonable blend."),
        ],
        "proof": "The image verifies Luna drywall experience in DFW and is not represented as the exact Garland ceiling in this guide.",
        "proof_link": "drywall.html", "proof_label": "View drywall repair services",
    },
    "commercial-office-remodel-richardson.html": {
        "title": "Office Remodeling in Richardson, TX | Luna",
        "description": "Plan a Richardson office remodel around operations, approvals, life-safety items, MEP trades, finishes and turnover. Request a written construction scope.",
        "image": "dfw-commercial-deli-finish-out-2019.jpg", "width": 669, "height": 891,
        "alt": "Completed commercial finish-out with cabinets, counter, flooring and lighting",
        "caption": "Completed commercial finish-out from Luna's documented DFW project portfolio.",
        "heading": "Office preconstruction checklist",
        "checks": ["Owner, tenant and landlord approval responsibilities", "Plans, permits, inspections and design-team requirements", "Occupancy, egress, accessibility and life-safety impacts", "Electrical, data, plumbing, HVAC and ceiling coordination", "Working hours, dust control, deliveries, cleaning and turnover"],
        "sections": [
            ("Define how the office must operate", "The scope should identify occupied areas, shutdown limits, public access and acceptable work hours. Phasing and temporary protection can affect both price and duration, especially when staff or customers remain in the building."),
            ("Coordinate systems before finishes", "Walls, ceilings and millwork depend on electrical, data, plumbing, mechanical and fire-protection decisions. Reflected ceiling plans, device locations and finish schedules should be coordinated before ordering materials or closing walls."),
            ("Plan procurement and turnover", "Long-lead fixtures and owner-furnished items need responsible parties and required-on-site dates. The closeout scope should also address final cleaning, inspections, punch work and delivery of available product or warranty information. Record who owns each closeout item and its target date."),
        ],
        "proof": "The photograph documents a Luna commercial finish-out in DFW. It demonstrates coordinated trades but is not claimed as the Richardson office discussed here.",
        "proof_link": "commercial.html", "proof_label": "View commercial construction services",
    },
    "contractor-estimate-comparison-carrollton.html": {
        "title": "Comparing Contractor Estimates in Carrollton, TX | Luna",
        "description": "Compare Carrollton contractor estimates by scope, quantities, materials, allowances, exclusions, schedule and change-order terms—not price alone.",
        "image": "dfw-kitchen-remodel-quartz-island-2018.jpg", "width": 669, "height": 891,
        "alt": "Completed kitchen remodel with quartz island by Luna General Contractors",
        "caption": "Completed remodeling work from Luna's documented DFW project portfolio.",
        "heading": "Estimate comparison checklist",
        "checks": ["Same rooms, measurements and demolition limits", "Named materials, finish level and installation method", "Allowances, exclusions and concealed-condition assumptions", "Permits, protection, cleanup, disposal and trade coordination", "Schedule, payment milestones, change orders and warranty terms"],
        "sections": [
            ("Normalize the scope first", "Two totals are not comparable when one includes demolition, disposal, preparation and finish repairs while another does not. Mark every included task and ask each contractor to clarify missing quantities or vague phrases."),
            ("Separate selections from unknown conditions", "An allowance should state what it covers and how an overage or credit will be calculated. Concealed damage is different: the estimate should explain the assumption and the approval process if opening the work reveals something unexpected."),
            ("Compare project controls", "Review start conditions, estimated duration, payment milestones and who coordinates each trade. A written change-order process protects both parties by recording added work, price and schedule effects before the extra work proceeds."),
        ],
        "proof": "The portfolio image verifies completed Luna remodeling work. A Carrollton proposal should still be evaluated against its own drawings, selections and site conditions.",
        "proof_link": "projects.html", "proof_label": "Compare documented project work",
    },
    "exterior-paint-southlake.html": {
        "title": "Exterior Painting in Southlake, TX | Luna",
        "description": "Plan Southlake exterior painting with cleaning, scraping, repairs, caulk, primer, product selection and weather conditions. Request a site estimate.",
        "image": "siding-after.jpg", "width": 1600, "height": 1200,
        "alt": "Completed residential siding and exterior finish project by Luna General Contractors",
        "caption": "Completed siding and exterior-finish work from Luna's documented DFW portfolio.",
        "heading": "Exterior coating inspection checklist",
        "checks": ["Siding, stucco, masonry, trim and previously coated surfaces", "Peeling, chalking, mildew, open joints and failed sealant", "Rot or movement that paint cannot correct", "Bare areas and the primer required for each substrate", "Weather window, masking, landscaping protection and cure time"],
        "sections": [
            ("Identify why the coating failed", "Peeling can result from moisture, poor adhesion, incompatible coatings or movement. The estimator should inspect the substrate and nearby joints instead of assuming a new coat will solve the original cause."),
            ("Put repairs before finish work", "Cleaning and dry time come before scraping, sanding and spot repairs. Failed caulk, loose trim and deteriorated material should be addressed before primer and paint so the proposal distinguishes repair work from coating work."),
            ("Match the product to conditions", "Product, sheen, application method and number of coats should be written into the scope. Temperature, surface moisture, direct sun and forecast conditions affect scheduling and cure time, so the work plan should follow the selected manufacturer's instructions."),
        ],
        "proof": "The image documents completed Luna exterior work in DFW and is not represented as the exact Southlake property discussed in this guide.",
        "proof_link": "painting.html", "proof_label": "Review exterior painting services",
    },
    "exterior-trim-carpentry-keller.html": {
        "title": "Exterior Trim Repair in Keller, TX | Luna",
        "description": "Plan Keller exterior trim repair by finding moisture entry, checking substrate, selecting compatible material and restoring flashing, sealant and paint.",
        "image": "siding-after.jpg", "width": 1600, "height": 1200,
        "alt": "Completed residential siding and exterior trim finish by Luna General Contractors",
        "caption": "Completed exterior-finish work from Luna's documented DFW portfolio.",
        "heading": "Exterior trim repair checklist",
        "checks": ["Soft, split or loose trim and the condition behind it", "Roof edge, window, door and wall details that direct water", "Existing dimensions, profile and adjacent finish materials", "Replacement material, fasteners, joints and end-grain treatment", "Flashing, sealant, primer and finish-paint sequence"],
        "sections": [
            ("Find the water path", "Rotten trim is often the visible result rather than the source. Roof runoff, failed joints, missing flashing or open transitions should be reviewed before replacing the damaged board."),
            ("Rebuild the detail, not only the face", "Removal may reveal damaged sheathing, framing or an incomplete weather detail. The estimate should define what is visible now, what is assumed and how concealed conditions will be documented if the scope changes."),
            ("Protect every cut and joint", "Material selection should fit the location and existing profile. Compatible fasteners, supported joints, treated cuts, primer, sealant and finish paint work together; relying on a bead of caulk alone does not rebuild a failed exterior trim assembly."),
        ],
        "proof": "The photograph verifies Luna exterior-finish workmanship in DFW. It is not claimed as a Keller trim project.",
        "proof_link": "carpentry.html", "proof_label": "View carpentry services",
    },
    "fence-post-replacement-mesquite.html": {
        "title": "Fence Post Replacement in Mesquite, TX | Luna",
        "description": "Plan a Mesquite fence-post replacement by checking alignment, soil, drainage, utilities, rails, gates and reusable sections. Request an estimate.",
        "image": "fencing-project-two.jpg", "width": 1600, "height": 1200,
        "alt": "Completed stained wood privacy fence by Luna General Contractors",
        "caption": "Completed stained privacy-fence work from Luna's documented DFW portfolio.",
        "heading": "Fence-post inspection checklist",
        "checks": ["Number and location of loose, leaning or rotted posts", "Rail, picket and fastener condition around each post", "Gate weight, hinge alignment and latch operation", "Slope, drainage, roots and access along the fence line", "Utility-location and property-line responsibilities before digging"],
        "sections": [
            ("Determine whether the post is the only failure", "A leaning section can involve a deteriorated post, loose rails, gate loading, soil movement or drainage. Inspecting the connected bays prevents a one-post estimate from overlooking work needed to realign the section."),
            ("Confirm the work area before excavation", "The owner and contractor should establish access and known property constraints, and utilities must be located before digging. Roots, irrigation and limited equipment access can change the method and labor."),
            ("Brace and reconnect in sequence", "Reusable panels need support while the old post is removed. The replacement location, depth, footing and cure time should follow site conditions and applicable requirements before rails, pickets and gates are fully loaded."),
        ],
        "proof": "The photograph verifies completed Luna fencing work in DFW and is not represented as the Mesquite fence in this guide.",
        "proof_link": "fencing.html", "proof_label": "View fencing project photos",
    },
    "flooring-subfloor-preparation-allen.html": {
        "title": "Subfloor Preparation in Allen, TX | Luna",
        "description": "Plan Allen flooring preparation by checking flatness, moisture, movement, damaged areas, underlayment, transitions and manufacturer requirements.",
        "image": "dfw-gray-plank-flooring-installation-2018.jpg", "width": 669, "height": 891,
        "alt": "Finished gray wood-look plank flooring installed by Luna General Contractors",
        "caption": "Completed plank-flooring work from Luna's documented DFW portfolio.",
        "heading": "Subfloor readiness checklist",
        "checks": ["Existing floor removal and adhesive or fastener residue", "Flatness measured against the selected flooring requirements", "Moisture conditions and any active source that needs correction", "Loose, damaged or moving areas and accessible framing concerns", "Underlayment, transitions, door clearances and finished floor height"],
        "sections": [
            ("Start with the flooring specification", "Flatness, moisture and underlayment limits vary by product and installation method. The selected manufacturer's instructions should guide testing and preparation instead of using one rule for every vinyl, laminate or wood floor."),
            ("Correct movement and height changes", "Squeaks, loose panels, damaged areas and abrupt transitions should be addressed before finish flooring. Patch or leveling work also needs compatible materials and cure time before adhesive or floating-floor installation."),
            ("Coordinate the room edges", "Preparation affects baseboards, cabinets, appliances, door clearance and adjacent floors. Recording finished heights and transition locations early reduces last-minute cuts and helps the new flooring continue cleanly through connected spaces."),
        ],
        "proof": "The portfolio image documents completed Luna flooring work in DFW. The Allen subfloor must be evaluated independently before choosing a preparation method.",
        "proof_link": "flooring.html", "proof_label": "View flooring project photos",
    },
    "insurance-scope-review-rockwall.html": {
        "title": "Insurance Scope Review in Rockwall, TX | Luna",
        "description": "Compare a Rockwall construction scope with visible damage, quantities, trades and repair sequence. Coverage decisions remain with the insurer and policy.",
        "image": "dfw-commercial-ceiling-damage-documentation-2024.jpg", "width": 669, "height": 891,
        "alt": "Commercial ceiling damage documented for a construction repair scope in DFW",
        "caption": "Visible property damage documented during development of a DFW construction repair scope.",
        "heading": "Construction-scope review checklist",
        "checks": ["Rooms, elevations and visible damage included in each document", "Measurements, quantities, material descriptions and finish continuity", "Demolition, access, protection, disposal and trade sequence", "Photographs, estimates, receipts and dates supporting construction facts", "Questions about coverage, depreciation or payment directed to the insurer"],
        "sections": [
            ("Keep construction facts separate from coverage", "A contractor can inspect visible conditions, prepare a repair estimate and explain construction sequencing. The insurance company and policy determine coverage and payment; Luna does not act as a public adjuster or promise a claim result."),
            ("Compare line items to the repair path", "Review whether each affected room, material and connected trade appears in the documents. A useful comparison also considers access, removal, surface preparation, finish continuity and the order required to complete the physical repairs."),
            ("Build a dated documentation file", "Keep photographs, measurements, proposals, invoices, temporary-repair receipts and written carrier communications together. If damage or required work becomes visible later, document it before covering the area and ask the insurer how it wants additional information submitted."),
        ],
        "proof": "The image shows documented DFW property damage used to develop a construction scope. It is not represented as a Rockwall claim or as evidence of insurance coverage.",
        "proof_link": "insurance-claims.html", "proof_label": "Review construction documentation services",
        "reference_link": "https://www.tdi.texas.gov/consumer/storms/roofing-and-insurance-know-the-law.html",
        "reference_label": "Texas Department of Insurance: roofing and insurance law",
    },
    "kitchen-island-layout-mckinney.html": {
        "title": "Kitchen Island Layout in McKinney, TX | Luna",
        "description": "Plan a McKinney kitchen island around work paths, appliance doors, seating, countertop support, utilities and flooring. Request a measured estimate.",
        "image": "dfw-kitchen-remodel-quartz-island-2018.jpg", "width": 669, "height": 891,
        "alt": "Completed kitchen remodel with quartz island by Luna General Contractors",
        "caption": "Completed kitchen remodeling work from Luna's documented DFW portfolio.",
        "heading": "Kitchen island field-measure checklist",
        "checks": ["Wall-to-wall dimensions and existing cabinet layout", "Appliance, dishwasher and door swing clearances", "Primary work paths and seating positions", "Sink, plumbing, electrical and ventilation requirements", "Cabinet anchorage, countertop overhang and support details"],
        "sections": [
            ("Test the island at full operating size", "Layout should be checked with appliance and cabinet doors open, not only as an empty rectangle on a plan. Exact clearances depend on the room, appliances, seating and applicable requirements, so field measurements come before cabinet ordering."),
            ("Plan utilities before finish surfaces", "A sink, dishwasher, outlets or specialty appliance can affect plumbing, electrical, ventilation and the floor below. Those routes and inspection steps should be settled before anchoring cabinets or templating countertops."),
            ("Coordinate structure and finishes", "Countertop material, overhang, seating and cabinet construction determine support needs. Flooring height, end panels, fillers, trim and adjacent walkway finishes should also be part of the scope so the island looks integrated rather than added later."),
        ],
        "proof": "The image documents completed Luna kitchen work in DFW. It provides workmanship evidence but is not presented as the specific McKinney kitchen.",
        "proof_link": "kitchens.html", "proof_label": "View kitchen remodeling services",
    },
    "roof-flashing-grapevine.html": {
        "title": "Roof Flashing Repair in Grapevine, TX | Luna",
        "description": "Plan Grapevine roof-flashing repair by inspecting walls, chimneys, valleys, penetrations, adjacent materials and the actual water path. Request an inspection.",
        "image": "dfw-roof-replacement-brick-home-2019.jpg", "width": 1188, "height": 891,
        "alt": "Completed architectural shingle roof on a brick home by Luna General Contractors",
        "caption": "Completed shingle-roof work from Luna's documented DFW portfolio.",
        "heading": "Roof-flashing inspection checklist",
        "checks": ["Roof-to-wall transitions and step or counterflashing", "Chimneys, vents, skylights and other penetrations", "Valleys, edges, kickout details and drainage paths", "Adjacent shingles, underlayment, decking, siding or masonry", "Previous sealant patches and interior leak history"],
        "sections": [
            ("Trace water beyond the visible stain", "Water can travel along decking, framing or a penetration before appearing indoors. Inspection should connect the interior pattern to roof transitions and drainage rather than assuming the nearest surface crack is the source."),
            ("Repair the surrounding assembly", "Flashing works with shingles, underlayment, siding, masonry and sealant details. A lasting scope may require carefully opening adjacent materials to restore laps and drainage; surface caulk alone is not a substitute for missing or incorrectly integrated flashing."),
            ("Match materials and sequence", "Metal type, coating and connection details should be compatible with the surrounding roof system. The scope should also identify which materials are removed, replaced or reused and how exposed areas will be protected during the repair."),
        ],
        "proof": "The photograph verifies completed Luna roofing work in DFW and is not claimed as a Grapevine flashing repair.",
        "proof_link": "roofing.html", "proof_label": "View verified roofing photos",
    },
    "roof-ventilation-plano.html": {
        "title": "Roof Ventilation in Plano, TX | Luna",
        "description": "Evaluate Plano attic ventilation by calculating intake and exhaust, checking blocked paths, insulation, air leaks and roof-system compatibility.",
        "image": "dfw-roof-replacement-brick-home-2019.jpg", "width": 1188, "height": 891,
        "alt": "Completed architectural shingle roof on a brick home by Luna General Contractors",
        "caption": "Completed shingle-roof work from Luna's documented DFW portfolio.",
        "heading": "Attic ventilation inspection checklist",
        "checks": ["Attic area and ventilation requirements for the actual assembly", "Available low intake and high exhaust openings", "Blocked soffits, insulation baffles and accessible airflow paths", "Existing exhaust types and whether they work together", "Bathroom ducts, attic air leakage, moisture signs and insulation condition"],
        "sections": [
            ("Calculate before adding vents", "More openings do not automatically create better airflow. Intake and exhaust should be sized and balanced for the actual attic, roof design and applicable requirements, with product net-free-area information used instead of vent dimensions alone."),
            ("Keep the airflow path open", "Soffit vents can be present but ineffective when insulation blocks the path. Accessible intake, baffles and upper exhaust should be reviewed together, along with signs of moisture or heat concentration that may point to another building-envelope issue."),
            ("Coordinate the attic as a system", "Air sealing and insulation affect attic performance, and bathroom exhaust should terminate outdoors rather than add moisture to the attic. Existing powered and passive exhaust methods should be evaluated for compatibility before combining systems."),
        ],
        "proof": "The image documents completed Luna roofing work in DFW. It is not represented as the Plano ventilation system described here.",
        "proof_link": "roofing.html", "proof_label": "Request a roof-system inspection",
    },
    "siding-repair-rowlett.html": {
        "title": "Siding Repair in Rowlett, TX | Luna",
        "description": "Plan a Rowlett siding repair by identifying damage, checking the wall behind it, matching profiles and restoring flashing, drainage and finish details.",
        "image": "siding-after.jpg", "width": 1600, "height": 1200,
        "alt": "Completed residential siding and exterior finish project by Luna General Contractors",
        "caption": "Completed siding and exterior-finish work from Luna's documented DFW portfolio.",
        "heading": "Siding repair inspection checklist",
        "checks": ["Impact, moisture, movement or installation cause", "Condition of sheathing and weather-resistive layers where accessible", "Existing material, profile, thickness, texture and color availability", "Window, door, roof and wall flashing transitions", "Clearances, fasteners, sealant, primer and finish requirements"],
        "sections": [
            ("Identify the cause before choosing patch size", "Cracked, loose or swollen siding can reflect impact, water entry, movement or fastening problems. The estimator should inspect the nearby joints and transitions so the repair addresses more than the visible panel."),
            ("Check what the siding protects", "Selective removal may reveal damaged sheathing or incomplete drainage details. The scope should state visible conditions, expected removal boundaries and how concealed findings will be photographed and approved before additional work."),
            ("Plan a realistic material match", "Profiles, textures and colors change over time. A small repair may be structurally practical but visually noticeable, while a larger section can provide a cleaner transition. The owner should understand that choice before materials are ordered."),
        ],
        "proof": "The photograph documents completed Luna siding work in DFW and is not claimed as the exact Rowlett repair.",
        "proof_link": "siding.html", "proof_label": "View siding project photos",
    },
    "water-damage-cabinet-repair-lewisville.html": {
        "title": "Water-Damaged Cabinet Repair in Lewisville, TX | Luna",
        "description": "Plan Lewisville cabinet repairs after stopping the water source and evaluating drying, swelling, finish match, countertops, plumbing and flooring.",
        "image": "dfw-interior-rebuild-framing-2018.jpg", "width": 1188, "height": 891,
        "alt": "Interior framing exposed during reconstruction work by Luna General Contractors",
        "caption": "Documented interior reconstruction work from Luna's DFW project portfolio.",
        "heading": "Cabinet rebuild assessment checklist",
        "checks": ["Water source corrected and affected area ready for reconstruction", "Swelling, delamination, staining and cabinet-box stability", "Toe kicks, backs, end panels and concealed wall or floor areas", "Door style, finish and replacement-component availability", "Countertop, sink, plumbing, electrical and flooring sequence"],
        "sections": [
            ("Wait until the loss is ready for rebuild", "Cabinet work should begin after the source is corrected and the affected area has been evaluated for reconstruction. New finishes installed too early can conceal continuing moisture or create another round of removal."),
            ("Separate cosmetic damage from material failure", "Doors or trim may be refinishable while swollen composite cabinet boxes are not. The assessment should examine structural stability, delamination, odors and finish availability instead of deciding from the front face alone."),
            ("Plan connected removals carefully", "Countertops, sinks, plumbing, backsplashes and flooring can limit access to the damaged cabinet. The scope should identify removal risks, reusable items, finish matching and trade sequence before promising a partial repair."),
        ],
        "proof": "The image verifies Luna reconstruction experience in DFW. It is not represented as the Lewisville cabinet loss described in this guide.",
        "proof_link": "mitigation.html", "proof_label": "Review restoration and rebuild services",
    },
}

LOCAL_SERVICE_PAGES = {
    "arlington-backsplash-installation.html": {
        "city": "Arlington",
        "title": "Backsplash Installation in Arlington, TX | Luna",
        "description": "Plan an Arlington backsplash installation with verified project evidence, layout checks, material options and a written scope. Request a free estimate.",
        "image": "20180530-181936.webp", "width": 720, "height": 405,
        "alt": "Representative gray tile backsplash installation by Luna General Contractors",
        "caption": "Representative DFW portfolio photograph shown with Luna's documented Arlington backsplash case; it is not identified as the exact Arlington installation.",
        "intro": [
            "An Arlington backsplash estimate should begin with the actual wall dimensions, cabinet clearances, countertop condition and every outlet or appliance interruption. Those details determine the layout, cut count, edge treatment and whether wall preparation belongs in the scope.",
            "Luna's project record for Arlington provides a concrete reference for material selection and installation sequence while the estimate for a new property remains based on its own measurements and conditions.",
        ],
        "case_title": "Gray Glass Mosaic Kitchen Backsplash in Arlington",
        "case_link": "gray-glass-mosaic-kitchen-backsplash-arlington.html",
        "project_date": "June 4, 2018",
        "duration": "Approximately two days",
        "material": "Gray glass mosaic tile, grout, setting and edge-finishing materials",
        "evidence": "The documented scope coordinated a reflective gray glass mosaic with existing cabinets, countertops and stainless-steel appliances. Installation included careful layout, cuts and grout joints throughout the backsplash area.",
        "heading": "Plan reflective mosaic around the existing kitchen",
        "planning": "Glass mosaic can emphasize uneven walls, irregular counter lines and inconsistent outlet placement. Before installation, we establish the most visible reference lines, confirm the finished height beneath cabinets and decide how exposed edges will terminate. That planning reduces narrow cuts and helps the pattern remain balanced across the working wall.",
        "checks": ["Measured wall area and cabinet-to-counter height", "Outlet, switch, window and appliance locations", "Flatness and readiness of the existing wall", "Starting point, focal areas and planned cut distribution", "Grout color, edge profile, protection and cleanup"],
        "planning_summary": "The Arlington scope should identify the selected mosaic, wall preparation, layout reference, edge trim, grout, electrical plate handling, protection and cleanup before installation begins.",
    },
    "mansfield-backsplash-installation.html": {
        "city": "Mansfield",
        "title": "Backsplash Installation in Mansfield, TX | Luna",
        "description": "See a verified Mansfield gray subway-tile backsplash and plan wall preparation, layout, cuts, grout and edge trim. Request a free estimate.",
        "image": "20180530-181936.webp", "width": 720, "height": 405,
        "alt": "Gray subway tile kitchen backsplash installation in Mansfield, Texas",
        "caption": "Photograph from Luna's documented gray subway-tile backsplash project in Mansfield.",
        "intro": [
            "A Mansfield backsplash scope should connect the tile layout to the cabinets, countertop, range area and decorative hood rather than treat the wall as one uninterrupted rectangle. Exact measurements show where full tiles, cut pieces and finished edges will appear.",
            "Luna's documented Mansfield project gives homeowners a city-specific example with recorded material, scope, completion date and duration. A new estimate still depends on the conditions at the property being priced.",
        ],
        "case_title": "Gray Subway Tile Kitchen Backsplash in Mansfield",
        "case_link": "gray-subway-kitchen-backsplash-mansfield.html",
        "project_date": "May 30, 2018",
        "duration": "Approximately two days",
        "material": "Gray subway tile, grout, setting materials, edge trim and electrical finish plates",
        "evidence": "The project protected the working wall and coordinated gray subway tile with white cabinetry, darker countertops and a decorative range hood. Detailed cuts were completed around cabinets, outlets and the range area.",
        "heading": "Use the range and hood as a visual reference",
        "planning": "Subway tile looks simple, but the result depends on where courses start and finish. At the Mansfield project, the range wall and hood created an important focal area. A current scope should define the bond pattern, grout-joint size, termination points and how the layout responds to any change in cabinet height.",
        "checks": ["Countertop length and distance to upper cabinets", "Range, hood and appliance-center reference lines", "Outlet-cover removal and safe electrical coordination", "Tile pattern, joint width, grout and edge trim", "Wall repair, protection, cure time and final cleanup"],
        "planning_summary": "The Mansfield estimate should record the tile and pattern, wall repairs, range-area layout, cut details, grout, edge trim, protection and realistic working sequence.",
    },
    "midlothian-backsplash-installation.html": {
        "city": "Midlothian",
        "title": "Backsplash Installation in Midlothian, TX | Luna",
        "description": "Plan a Midlothian backsplash using verified gray subway and metallic-accent project evidence, layout checks and a written installation scope.",
        "image": "20180429-113604.webp", "width": 523, "height": 720,
        "alt": "Representative completed kitchen backsplash by Luna General Contractors",
        "caption": "Representative DFW portfolio photograph shown with Luna's documented Midlothian backsplash case; it is not identified as the exact Midlothian installation.",
        "intro": [
            "A Midlothian backsplash with an accent band needs more layout decisions than a single-field tile. The estimator must confirm band height, interruptions at outlets, transitions near the range and how the accent meets corners or exposed edges.",
            "Luna's documented Midlothian case records a gray subway installation with metallic mosaic accents, providing a useful local example without assuming that another kitchen needs the same pattern or materials.",
        ],
        "case_title": "Gray Subway Backsplash with Metallic Accents in Midlothian",
        "case_link": "gray-subway-metallic-accent-backsplash-midlothian.html",
        "project_date": "August 17, 2018",
        "duration": "Approximately two days",
        "material": "Gray subway tile, metallic mosaic accent, grout, setting materials and edge trim",
        "evidence": "The recorded project added horizontal metallic accent bands within a gray subway-tile field. The layout was completed around cabinets, countertops and electrical components to add contrast without overwhelming the existing finishes.",
        "heading": "Lay out decorative bands before setting field tile",
        "planning": "Accent material can be thinner or thicker than the field tile and may arrive on flexible sheets. The scope should address surface alignment, band height, sheet seams and transitions before setting begins. A dry layout helps reveal awkward fragments at corners and keeps the feature line continuous across visible sections.",
        "checks": ["Field-tile and accent-sheet thickness", "Accent height through outlets and focal areas", "Corner, cabinet and exposed-edge terminations", "Wall flatness and preparation requirements", "Grout compatibility, protection and cure schedule"],
        "planning_summary": "The Midlothian estimate should distinguish field tile from accent material and specify alignment, transitions, edge treatment, grout, wall preparation and protection.",
    },
    "grand-prairie-backsplash-installation.html": {
        "city": "Grand Prairie",
        "title": "Backsplash Installation in Grand Prairie, TX | Luna",
        "description": "Review a documented Grand Prairie patterned-tile backsplash and plan alignment, focal areas, cuts, grout and wall preparation. Get an estimate.",
        "image": "20180429-113627.webp", "width": 523, "height": 720,
        "alt": "Representative decorative kitchen backsplash detail by Luna General Contractors",
        "caption": "Representative DFW portfolio photograph shown with Luna's documented Grand Prairie backsplash case; it is not identified as the exact Grand Prairie installation.",
        "intro": [
            "Patterned tile makes layout errors more visible, so a Grand Prairie estimate should document focal walls, centerlines, corner transitions and where the pattern will be interrupted by cabinets, outlets or appliances.",
            "Luna's Grand Prairie project record supplies a city-specific example with a documented material choice, installation scope, date and approximate duration. New work is measured and priced from the current kitchen rather than copied from that earlier project.",
        ],
        "case_title": "Black and White Patterned Kitchen Backsplash in Grand Prairie",
        "case_link": "black-white-patterned-kitchen-backsplash-grand-prairie.html",
        "project_date": "February 4, 2019",
        "duration": "Approximately two days",
        "material": "Black-and-white patterned tile, grout, setting and edge-finishing materials",
        "evidence": "The documented installation used patterned tile to create a focal surface while coordinating with the existing countertops, cabinets and appliances. Work included consistent alignment, detailed cuts and finished grout joints.",
        "heading": "Center the pattern where the kitchen is seen first",
        "planning": "A repeating design should be reviewed across the complete elevation before tile is set. We identify the main viewing angle, test how the motif meets corners and verify that cuts around electrical boxes do not break the pattern unnecessarily. Extra tile should be considered for pattern alignment and future repairs.",
        "checks": ["Pattern repeat and recommended material overage", "Primary focal point and elevation centerline", "Corner transitions and cabinet-end visibility", "Outlet, switch and appliance interruptions", "Wall preparation, grout choice and edge finish"],
        "planning_summary": "The Grand Prairie scope should show the pattern reference, starting point, anticipated cuts, material allowance, grout, edge finish and wall-preparation responsibilities.",
    },
    "waxahachie-backsplash-installation.html": {
        "city": "Waxahachie",
        "title": "Backsplash Installation in Waxahachie, TX | Luna",
        "description": "See a verified Waxahachie white-hexagon backsplash and plan range-wall layout, cuts, edge finishing, grout and wall preparation.",
        "image": "20180429-113604.webp", "width": 523, "height": 720,
        "alt": "Completed white hexagon backsplash behind a range and microwave in Waxahachie, Texas",
        "caption": "Completed range-wall photograph from Luna's documented white-hexagon backsplash project in Waxahachie.",
        "intro": [
            "A Waxahachie range-wall backsplash needs a layout that stays balanced beneath the microwave and reads cleanly beside cabinet edges. Hexagon tile adds diagonal cuts and small perimeter pieces that should be planned before installation.",
            "Luna's documented Waxahachie project includes exact progress and completed photographs plus the material, work scope, completion date and approximate duration. Those records provide direct local proof while each new kitchen receives its own measurements.",
        ],
        "case_title": "White Hexagon Kitchen Backsplash in Waxahachie",
        "case_link": "white-hexagon-kitchen-backsplash-waxahachie.html",
        "project_date": "April 29, 2018",
        "duration": "Approximately two days",
        "material": "White hexagon tile, grout, setting and edge-finishing materials",
        "evidence": "The project installed white hexagon tile behind the range and microwave, coordinating the bright neutral finish with white cabinets, stainless appliances and existing granite countertops. Layout and cuts were completed around cabinets, counter edges and electrical components.",
        "heading": "Plan small perimeter cuts before installing hexagon tile",
        "planning": "Hexagon sheets can drift at seams if the pattern is not checked continuously. A dry layout helps balance the range wall and shows whether the top, bottom or side boundaries would create fragile pieces. The estimate should also identify exposed edges and any wall correction needed behind the tile.",
        "checks": ["Range and microwave centerline", "Sheet orientation and seam alignment", "Perimeter cuts at cabinets and countertops", "Outlet placement and electrical finish plates", "Wall flatness, grout, edge finish and cleanup"],
        "planning_summary": "The Waxahachie estimate should document sheet orientation, range-wall centerline, perimeter cuts, wall preparation, grout, edge finish, protection and cleanup.",
    },
}


REVIEWS = {
    "reviews.html": {
        "title": "Customer Reviews | Luna General Contractors",
        "description": "Read sourced Google, Yelp and Nextdoor feedback for Luna General Contractors, then compare documented DFW projects and request a free estimate.",
        "image": "dfw-bathroom-remodel-glass-shower-2020.jpg", "width": 1188, "height": 891,
        "alt": "Finished bathroom remodel with glass shower by Luna General Contractors",
    }
}

PROMOTED = set(CITY_PAGES) | set(ARTICLE_PAGES) | set(LOCAL_SERVICE_PAGES) | set(REVIEWS)
HUB_PAGES = {"service-areas.html", "articles.html", "kitchens.html"}


def replace_tag_value(source: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.I | re.S)
    if count != 1:
        raise SystemExit(f"Unable to update {label}")
    return updated


def social_metadata(config: dict[str, object], canonical: str, og_type: str) -> str:
    title = html.escape(str(config["title"]), quote=True)
    description = html.escape(str(config["description"]), quote=True)
    image_url = f'{DOMAIN}/{config["image"]}'
    alt = html.escape(str(config["alt"]), quote=True)
    return (
        f'<meta property="og:type" content="{html.escape(og_type, quote=True)}">'
        f'<meta property="og:title" content="{title}">'
        f'<meta property="og:description" content="{description}">'
        f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">'
        f'<meta property="og:image" content="{image_url}">'
        f'<meta property="og:image:width" content="{config["width"]}">'
        f'<meta property="og:image:height" content="{config["height"]}">'
        f'<meta property="og:image:alt" content="{alt}">'
        '<meta property="og:site_name" content="Luna General Contractors">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{title}">'
        f'<meta name="twitter:description" content="{description}">'
        f'<meta name="twitter:image" content="{image_url}">'
        f'<meta name="twitter:image:alt" content="{alt}">'
    )


def update_head(source: str, config: dict[str, object]) -> str:
    title = html.escape(str(config["title"]), quote=False)
    description = html.escape(str(config["description"]), quote=True)
    source = replace_tag_value(source, r"<title>[\s\S]*?</title>", f"<title>{title}</title>", "title")
    source = replace_tag_value(source, r'<meta\b[^>]*\bname=["\']description["\'][^>]*>', f'<meta name="description" content="{description}">', "description")
    robots = '<meta name="robots" content="index, follow, max-image-preview:large">'
    if re.search(r'<meta\b[^>]*\bname=["\']robots["\'][^>]*>', source, re.I):
        source = re.sub(r'<meta\b[^>]*\bname=["\']robots["\'][^>]*>', robots, source, count=1, flags=re.I)
    else:
        description_tag = re.search(r'<meta\b[^>]*\bname=["\']description["\'][^>]*>', source, re.I)
        if not description_tag:
            raise SystemExit("Missing description insertion point")
        source = source[: description_tag.end()] + robots + source[description_tag.end() :]
    canonical_match = re.search(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)', source, re.I)
    if not canonical_match:
        raise SystemExit("Missing canonical insertion point")
    canonical = html.unescape(canonical_match.group(1))
    type_match = re.search(r'<meta\b[^>]*\bproperty=["\']og:type["\'][^>]*\bcontent=["\']([^"\']+)', source, re.I)
    og_type = html.unescape(type_match.group(1)) if type_match else "website"
    for key in ("og:type", "og:title", "og:description", "og:url", "og:image", "og:image:width", "og:image:height", "og:image:alt", "og:site_name"):
        source = re.sub(rf'<meta\b[^>]*\bproperty=["\']{re.escape(key)}["\'][^>]*>\s*', "", source, flags=re.I)
    for key in ("twitter:card", "twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"):
        source = re.sub(rf'<meta\b[^>]*\bname=["\']{re.escape(key)}["\'][^>]*>\s*', "", source, flags=re.I)
    marker = re.search(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>', source, re.I)
    if not marker:
        raise SystemExit("Missing canonical insertion point")
    return source[: marker.end()] + social_metadata(config, canonical, og_type) + source[marker.end() :]


def update_schema(source: str, config: dict[str, object], page_kind: str) -> str:
    image_url = f'{DOMAIN}/{config["image"]}'

    def transform(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        schema_type = data.get("@type")
        types = set(schema_type if isinstance(schema_type, list) else [schema_type])
        target = page_kind == "article" and "Article" in types
        target = target or page_kind == "city" and bool(types & {"LocalBusiness", "GeneralContractor", "RoofingContractor"})
        target = target or page_kind == "local_service" and bool(types & {"Service", "WebPage"})
        target = target or page_kind == "reviews" and "GeneralContractor" in types
        if not target:
            return match.group(0)
        data["image"] = image_url
        if page_kind == "article":
            data["headline"] = str(config["title"]).split(" | Luna")[0]
            data["description"] = str(config["description"])
            data["dateModified"] = LASTMOD
        elif page_kind == "local_service":
            data["description"] = str(config["description"])
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    pattern = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)', re.I)
    updated, count = pattern.subn(transform, source)
    if count == 0:
        raise SystemExit("No JSON-LD blocks found")
    return updated


def clear_block(source: str) -> str:
    return re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END), "", source)


def city_block(config: dict[str, object]) -> str:
    city = html.escape(str(config["city"]))
    checks = "".join(f"<li>{html.escape(item)}</li>" for item in config["checks"])
    return (
        f'{START}<section data-ready-page-enrichment><div class="local-grid" style="margin:48px 0">'
        '<div><p class="eyebrow gold">Site-Specific Planning</p>'
        f'<h2>What We Verify Before an Estimate in {city}</h2><p>{html.escape(str(config["planning"]))}</p>'
        f'<ul>{checks}</ul><p><a href="projects.html"><strong>View documented DFW projects →</strong></a> '
        '<a href="reviews.html"><strong>Read sourced customer reviews →</strong></a></p></div>'
        '<figure class="local-card" style="margin:0"><img src="dfw-roof-replacement-brick-home-2019.jpg" '
        'alt="Completed shingle roof on a brick home by Luna General Contractors in DFW" width="1188" height="891" '
        'loading="lazy" decoding="async" style="display:block;width:100%;height:auto">'
        f'<figcaption style="margin-top:12px">Verified Luna roofing work from the DFW portfolio. This photograph is not represented as a project completed in {city}.</figcaption>'
        f'</figure></div></section>{END}'
    )


def article_block(config: dict[str, object]) -> str:
    checks = "".join(f"<li>{html.escape(item)}</li>" for item in config["checks"])
    sections = "".join(
        f'<h3>{html.escape(str(heading))}</h3><p>{html.escape(str(body))}</p>'
        for heading, body in config.get("sections", [])
    )
    reference = ""
    if config.get("reference_link"):
        reference = (
            f'<p><a class="seo-text-link" href="{html.escape(str(config["reference_link"]), quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">{html.escape(str(config["reference_label"]))} →</a></p>'
        )
    return (
        f'{START}<figure class="seo-article-photo">'
        f'<img src="{config["image"]}" alt="{html.escape(str(config["alt"]), quote=True)}" width="{config["width"]}" height="{config["height"]}" loading="lazy" decoding="async">'
        f'<figcaption>{html.escape(str(config["caption"]))}</figcaption></figure>'
        f'<section data-ready-page-enrichment><h2>{html.escape(str(config["heading"]))}</h2><ul class="seo-checklist">{checks}</ul>'
        f'{sections}<p>{html.escape(str(config["proof"]))}</p><p><a class="seo-text-link" href="{config["proof_link"]}">{html.escape(str(config["proof_label"]))} →</a></p>'
        f'{reference}</section>{END}'
    )


def local_service_block(config: dict[str, object]) -> str:
    intro = "".join(f"<p>{html.escape(str(paragraph))}</p>" for paragraph in config["intro"])
    checks = "".join(f"<li>{html.escape(str(item))}</li>" for item in config["checks"])
    return (
        f'{START}{intro}<div class="local-grid" data-evidence-backed-service style="margin:32px 0 40px">'
        '<div><p class="eyebrow gold">Verified Local Project</p>'
        f'<h2>{html.escape(str(config["case_title"]))}</h2>'
        f'<p>{html.escape(str(config["evidence"]))}</p>'
        '<ul class="seo-checklist">'
        f'<li><strong>Completed:</strong> {html.escape(str(config["project_date"]))}</li>'
        f'<li><strong>Recorded duration:</strong> {html.escape(str(config["duration"]))}</li>'
        f'<li><strong>Materials:</strong> {html.escape(str(config["material"]))}</li></ul>'
        f'<p><a class="seo-text-link" href="{html.escape(str(config["case_link"]), quote=True)}">View the documented {html.escape(str(config["city"]))} project →</a></p></div>'
        '<figure class="seo-article-photo" style="margin:0">'
        f'<img src="{html.escape(str(config["image"]), quote=True)}" alt="{html.escape(str(config["alt"]), quote=True)}" '
        f'width="{config["width"]}" height="{config["height"]}" loading="lazy" decoding="async">'
        f'<figcaption>{html.escape(str(config["caption"]))}</figcaption></figure></div>'
        f'<section><h2>Backsplash estimate checklist for {html.escape(str(config["city"]))}</h2>'
        f'<ul class="seo-checklist">{checks}</ul>'
        f'<h3>{html.escape(str(config["heading"]))}</h3><p>{html.escape(str(config["planning"]))}</p>'
        '<p><a class="seo-text-link" href="kitchens.html">Explore kitchen remodeling services →</a> '
        '<a class="seo-text-link" href="#estimate-form">Request a property-specific estimate →</a></p></section>'
        f'{END}'
    )


def reviews_block() -> str:
    config = REVIEWS["reviews.html"]
    return (
        f'{START}<section class="source-box" data-ready-page-enrichment><h2>Compare Reviews With Documented Work</h2>'
        '<p>The review summaries identify their public sources. The project pages separately document photographs, city, scope, materials and dates when those facts are available.</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;align-items:center">'
        f'<img src="{config["image"]}" alt="{html.escape(str(config["alt"]), quote=True)}" width="{config["width"]}" height="{config["height"]}" loading="lazy" decoding="async" style="display:block;width:100%;height:auto;border-radius:12px">'
        '<div><p><strong>Check both forms of evidence:</strong> read the original review source, then compare Luna\'s documented project records and photographs.</p>'
        '<p><a class="source-link gold" href="projects.html">View documented projects →</a> '
        '<a class="source-link" href="proyecto-backsplash-cocina-mansfield.html">Caso en español →</a></p></div></div></section>'
        f'{END}'
    )


def service_area_links_block() -> str:
    cards = "".join(
        f'<article class="seo-city-card"><h2><a href="{name}">{html.escape(str(config["city"]))}</a></h2>'
        f'<p>{html.escape(str(config["planning"]))}</p>'
        f'<a class="seo-text-link" href="{name}">View {html.escape(str(config["city"]))} services →</a></article>'
        for name, config in CITY_PAGES.items()
    )
    return (
        f'{START}<section class="seo-section" data-ready-page-enrichment><div class="container">'
        '<div class="section-heading"><p class="eyebrow gold">Additional Service Areas</p>'
        '<h2>Property-Specific Planning Across DFW</h2>'
        '<p>These city pages explain what Luna reviews before preparing a roofing, remodeling or restoration scope.</p></div>'
        f'<div class="seo-city-grid">{cards}</div></div></section>{END}'
    )


def article_links_block() -> str:
    cards = "".join(
        f'<article class="seo-city-card"><p class="eyebrow gold">Local Planning Guide</p>'
        f'<h2><a href="{name}">{html.escape(str(config["title"]).split(" | Luna")[0])}</a></h2>'
        f'<p>{html.escape(str(config["description"]))}</p>'
        f'<a class="seo-text-link" href="{name}">Read guide →</a></article>'
        for name, config in ARTICLE_PAGES.items()
    )
    return (
        f'{START}<section class="seo-section" data-ready-page-enrichment><div class="container">'
        '<div class="section-heading"><p class="eyebrow gold">More Local Resources</p>'
        '<h2>Inspection and Project-Planning Guides</h2>'
        '<p>Use these checklists to prepare for a site visit and compare options before requesting a written scope.</p></div>'
        f'<div class="seo-city-grid">{cards}</div></div></section>{END}'
    )


def kitchen_local_links_block() -> str:
    cards = "".join(
        f'<article class="seo-city-card"><p class="eyebrow gold">Verified Local Example</p>'
        f'<h2><a href="{name}">{html.escape(str(config["city"]))} Backsplash Installation</a></h2>'
        f'<p>{html.escape(str(config["description"]))}</p>'
        f'<a class="seo-text-link" href="{name}">View local service and project evidence →</a></article>'
        for name, config in LOCAL_SERVICE_PAGES.items()
    )
    return (
        f'{START}<section class="seo-section" data-ready-page-enrichment><div class="container">'
        '<div class="section-heading"><p class="eyebrow gold">Backsplash Work by City</p>'
        '<h2>Plan With Real DFW Project Evidence</h2>'
        '<p>These five service pages connect estimating guidance to a documented Luna backsplash project in the same city.</p></div>'
        f'<div class="seo-city-grid">{cards}</div></div></section>{END}'
    )


def enrich_city(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    image_config = {**config, "image": "dfw-roof-replacement-brick-home-2019.jpg", "width": 1188, "height": 891, "alt": "Completed shingle roof on a brick home by Luna General Contractors in DFW"}
    source = update_head(source, image_config)
    source = update_schema(source, image_config, "city")
    anchor = f'<h2>Services Available in {config["city"]}</h2>'
    if anchor not in source:
        raise SystemExit(f"{path.name}: city insertion point not found")
    source = source.replace(anchor, city_block(config) + anchor, 1)
    path.write_text(source, encoding="utf-8")


def enrich_article(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    source = update_head(source, config)
    source = update_schema(source, config, "article")
    stylesheet_tags = re.findall(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', source, re.I)
    style_hrefs = [re.search(r'href=["\']([^"\']+)', tag, re.I).group(1) for tag in stylesheet_tags if re.search(r'href=["\']([^"\']+)', tag, re.I)]
    if "/styles.css" in style_hrefs and "styles.css" in style_hrefs:
        source = re.sub(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*href=["\']/styles\.css["\'][^>]*>\s*', "", source, count=1, flags=re.I)
    if not any("local-seo.css" in href for href in style_hrefs):
        source = source.replace("</head>", '<link rel="stylesheet" href="local-seo.css?v=20260906">\n</head>', 1)
    lead = re.search(r'<p class="seo-lead">[\s\S]*?</p>', source, re.I)
    block = article_block(config)
    if lead:
        source = source[: lead.end()] + block + source[lead.end() :]
    else:
        container = re.search(r'<article\b[^>]*class=["\'][^"\']*local-content[^"\']*["\'][^>]*>\s*<div\b[^>]*class=["\'][^"\']*container[^"\']*["\'][^>]*>', source, re.I)
        if not container:
            raise SystemExit(f"{path.name}: article insertion point not found")
        source = source[: container.end()] + block + source[container.end() :]
    path.write_text(source, encoding="utf-8")


def enrich_local_service(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    source = update_head(source, config)
    source = update_schema(source, config, "local_service")
    stylesheet_tags = re.findall(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', source, re.I)
    style_hrefs = [re.search(r'href=["\']([^"\']+)', tag, re.I).group(1) for tag in stylesheet_tags if re.search(r'href=["\']([^"\']+)', tag, re.I)]
    if not any("local-seo.css" in href for href in style_hrefs):
        source = source.replace("</head>", '<link rel="stylesheet" href="local-seo.css?v=20260906">\n</head>', 1)
    intro_pattern = re.compile(r'(<h2>Local Backsplash Installation Services</h2>)[\s\S]*?(<div class="local-grid">)', re.I)
    source, count = intro_pattern.subn(lambda match: match.group(1) + local_service_block(config) + match.group(2), source, count=1)
    if count != 1:
        raise SystemExit(f"{path.name}: local-service insertion point not found")
    planning_pattern = re.compile(r'(<h2>Planning the Project</h2>)[\s\S]*?(</article>)', re.I)
    planning = f'<p>{html.escape(str(config["planning_summary"]))}</p>'
    source, count = planning_pattern.subn(lambda match: match.group(1) + planning + match.group(2), source, count=1)
    if count != 1:
        raise SystemExit(f"{path.name}: planning section not found")
    path.write_text(source, encoding="utf-8")


def enrich_reviews(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    source = update_head(source, config)
    source = update_schema(source, config, "reviews")
    anchor = '<div class="review-list">'
    if anchor not in source:
        raise SystemExit("reviews.html: review-list insertion point not found")
    source = source.replace(anchor, reviews_block() + anchor, 1)
    path.write_text(source, encoding="utf-8")


def enrich_hub(path: Path, block: str) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    anchor = "</main>"
    if anchor not in source:
        raise SystemExit(f"{path.name}: main insertion point not found")
    source = source.replace(anchor, block + anchor, 1)
    path.write_text(source, encoding="utf-8")


def remove_promoted_classifications() -> None:
    inventory = ROOT / "seo" / "sitemap-exclusions.csv"
    with inventory.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader if row["path"].strip() not in PROMOTED]
        fields = reader.fieldnames
    if not fields:
        raise SystemExit("Classification inventory has no header")
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        handle.write(",".join(fields) + "\n")
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(rows)


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    priorities = {name: "0.9" for name in CITY_PAGES}
    priorities.update({name: "0.7" for name in ARTICLE_PAGES})
    priorities.update({name: "0.8" for name in LOCAL_SERVICE_PAGES})
    priorities["reviews.html"] = "0.8"
    additions = []
    for name in sorted(PROMOTED):
        url = f"{DOMAIN}/{name}"
        block_re = re.compile(rf'<url><loc>{re.escape(url)}</loc>[\s\S]*?</url>')
        match = block_re.search(source)
        entry = f'<url><loc>{url}</loc><lastmod>{LASTMOD}</lastmod><changefreq>monthly</changefreq><priority>{priorities[name]}</priority></url>'
        if match:
            source = source[: match.start()] + entry + source[match.end() :]
        else:
            additions.append("  " + entry + "\n")
    if additions:
        source = source.replace("</urlset>", "".join(additions) + "</urlset>", 1)
    for name in sorted(HUB_PAGES):
        url = f"{DOMAIN}/{name}"
        block_re = re.compile(rf'(<url><loc>{re.escape(url)}</loc>)([\s\S]*?)(</url>)')
        match = block_re.search(source)
        if not match:
            raise SystemExit(f"{name}: existing sitemap entry not found")
        middle = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{LASTMOD}</lastmod>', match.group(2), count=1)
        source = source[: match.start()] + match.group(1) + middle + match.group(3) + source[match.end() :]
    path.write_text(source, encoding="utf-8")


def validate() -> None:
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    inventory = (ROOT / "seo" / "sitemap-exclusions.csv").read_text(encoding="utf-8")
    for name in sorted(PROMOTED):
        source = (ROOT / name).read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
        description = re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', source, re.I)
        if not title or len(html.unescape(title.group(1))) > 60:
            raise SystemExit(f"{name}: title missing or exceeds 60 characters")
        if not description or len(html.unescape(description.group(1))) > 160:
            raise SystemExit(f"{name}: description missing or exceeds 160 characters")
        for token in (START, 'property="og:image"', 'name="twitter:image"', 'width="', 'height="'):
            if token not in source:
                raise SystemExit(f"{name}: missing {token}")
        if source.count("<h1") != 1:
            raise SystemExit(f"{name}: expected one H1")
        for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', source, re.I):
            json.loads(raw)
        if f"{DOMAIN}/{name}" not in sitemap:
            raise SystemExit(f"{name}: missing from sitemap")
        if re.search(rf'^"?{re.escape(name)}"?,', inventory, re.M):
            raise SystemExit(f"{name}: stale sitemap-exclusion row")
    service_areas = (ROOT / "service-areas.html").read_text(encoding="utf-8")
    articles = (ROOT / "articles.html").read_text(encoding="utf-8")
    kitchens = (ROOT / "kitchens.html").read_text(encoding="utf-8")
    if any(f'href="{name}"' not in service_areas for name in CITY_PAGES):
        raise SystemExit("service-areas.html: missing promoted city link")
    if any(f'href="{name}"' not in articles for name in ARTICLE_PAGES):
        raise SystemExit("articles.html: missing promoted article link")
    if any(f'href="{name}"' not in kitchens for name in LOCAL_SERVICE_PAGES):
        raise SystemExit("kitchens.html: missing promoted backsplash link")
    for name, source in (("service-areas.html", service_areas), ("articles.html", articles), ("kitchens.html", kitchens)):
        if source.count(START) != 1 or source.count(END) != 1:
            raise SystemExit(f"{name}: expected one enrichment block")


def main() -> None:
    for name, config in CITY_PAGES.items():
        enrich_city(ROOT / name, config)
    for name, config in ARTICLE_PAGES.items():
        enrich_article(ROOT / name, config)
    for name, config in LOCAL_SERVICE_PAGES.items():
        enrich_local_service(ROOT / name, config)
    for name, config in REVIEWS.items():
        enrich_reviews(ROOT / name, config)
    enrich_hub(ROOT / "service-areas.html", service_area_links_block())
    enrich_hub(ROOT / "articles.html", article_links_block())
    enrich_hub(ROOT / "kitchens.html", kitchen_local_links_block())
    remove_promoted_classifications()
    update_sitemap()
    validate()
    print(f"Promoted {len(PROMOTED)} enriched pages into sitemap.xml.")


if __name__ == "__main__":
    main()
