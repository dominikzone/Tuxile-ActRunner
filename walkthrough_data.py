import os

ICON_MAPPING = {
    "WAYPOINT": "assets/icons/waypoint.png",
    "QUEST_ITEM": "assets/icons/quest_item.png",
    "SKILL_POINT": "assets/icons/skill_point.png",
    "TRIAL": "assets/icons/trial.png",
    "KILL_BOSS": "assets/icons/kill_boss.png",
    "ENTER_TOWN": "assets/icons/town.png",
    "ENTER_ZONE": "assets/icons/zone.png",
    "TAKE_REWARD": "assets/icons/reward.png",
    "OPEN_PASSAGE": "assets/icons/passage.png",
    "COLLECT_ITEM": "assets/icons/collect.png",
}

WALKTHROUGH = [
  # ── ACT 1 ──────────────────────────────────────────────────────────────────
  {"zone": "Twilight Strand",
   "text": "ACT 1\n[ICON:KILL_BOSS]Kill Hillock. 💡 Dodge his swings — spam potions freely, town is right after. [ICON:ENTER_TOWN]Enter Lioneye's Watch."},

  {"zone": "Lioneye's Watch",
   "text": "⚠️ Grab skill gem from Tarkleigh before leaving! Shop vendors. [ICON:ENTER_ZONE]Exit north to The Coast."},

  {"zone": "The Coast",
   "text": "[ICON:WAYPOINT]Grab Waypoint. 💡 Skip Tidal Island for now — return via WP later. [ICON:ENTER_ZONE]Head to The Mud Flats."},

  {"zone": "The Mud Flats",
   "text": "[ICON:COLLECT_ITEM]Collect 3x Rhoa Eggs. [ICON:OPEN_PASSAGE]Place eggs in wall → opens Submerged Passage.\n💡 Rhoas charge straight — strafe sideways to dodge the stun."},

  {"zone": "The Submerged Passage",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Go to The Coast WP → Tidal Island. Return here after.\n💡 Leave a Town Portal at Flooded Depths entrance, continue to Ledge, return later."},

  {"zone": "Tidal Island",
   "text": "[ICON:KILL_BOSS]Kill Hailrake (chill effects — keep moving). [ICON:TAKE_REWARD]Reward: Quicksilver Flask + Gem.\n💡 Exit to char select after kill to return to town instantly. Collect rewards, WP back."},

  {"zone": "The Flooded Depths",
   "text": "[ICON:KILL_BOSS]Kill Dweller of the Deep. [ICON:TAKE_REWARD]Reward: Passive Skill Point. [ICON:ENTER_ZONE]Back to Submerged Passage → The Ledge."},

  {"zone": "The Ledge",
   "text": "[ICON:WAYPOINT]Grab Waypoint (middle of zone). 💡 Just after WP, three stones in triangle point toward exit. [ICON:ENTER_ZONE]Head to The Climb."},

  {"zone": "The Climb",
   "text": "[ICON:WAYPOINT]Grab Waypoint (near start). [ICON:ENTER_ZONE]Find wall door at far end → The Lower Prison."},

  {"zone": "The Lower Prison",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:TRIAL]Do Trial of Ascendancy (1/6). [ICON:TAKE_REWARD]Reward: Level 8 Gems (return to town to shop). [ICON:ENTER_ZONE]Proceed to The Upper Prison."},

  {"zone": "The Upper Prison",
   "text": "💡 Strongbox hidden behind wall — find SWITCH on nearby pillar to open it. [ICON:ENTER_ZONE]Find entrance to The Warden's Quarters."},

  {"zone": "The Warden's Quarters",
   "text": "[ICON:KILL_BOSS]Kill Brutus (sustain with potions — he doesn't fully respawn on death). [ICON:TAKE_REWARD]Reward: Level 10 Gems. [ICON:ENTER_ZONE]Go to Prisoner's Gate."},

  {"zone": "Prisoner's Gate",
   "text": "[ICON:WAYPOINT]Grab Waypoint (zone start). 💡 Main path is blocked by Piety — hug the opposite wall toward the 'deeper' path to find Ship Graveyard. [ICON:ENTER_ZONE]Find The Ship Graveyard."},

  {"zone": "The Ship Graveyard",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Find Ship Graveyard Cave near a sunken ship in center of zone."},

  {"zone": "The Ship Graveyard Cave",
   "text": "[ICON:KILL_BOSS]Kill Stranglecharm. [ICON:COLLECT_ITEM]Grab Allflame quest item. [ICON:ENTER_ZONE]Exit through wall behind boss → back to Ship Graveyard."},

  {"zone": "The Cavern of Wrath",
   "text": "[ICON:WAYPOINT]Grab Waypoint (zone start). [ICON:KILL_BOSS]Kill Fairgraves. [ICON:TAKE_REWARD]Skill Point (collect in town). [ICON:ENTER_ZONE]Find wall entrance to Cavern of Anger."},

  {"zone": "The Cavern of Anger",
   "text": "[ICON:ENTER_ZONE]Follow path to wall entrance → Merveil's Lair."},

  {"zone": "Merveil's Lair",
   "text": "[ICON:KILL_BOSS]Kill Merveil — heavy cold damage. ⚠️ Avoid large cyclones, kill minions immediately, stay mobile — multiple phases. [ICON:ENTER_ZONE]Exit north → Act 2."},

  # ── ACT 2 ──────────────────────────────────────────────────────────────────
  {"zone": "The Southern Forest",
   "text": "ACT 2\n[ICON:ENTER_TOWN]Head straight north to Forest Encampment."},

  {"zone": "The Forest Encampment",
   "text": "[ICON:TAKE_REWARD]Buy Level 16 gems from Yeena. [ICON:ENTER_ZONE]Exit north to The Old Fields."},

  {"zone": "The Old Fields",
   "text": "[ICON:ENTER_ZONE]Follow path to The Crossroads. Skip The Den."},

  {"zone": "The Crossroads",
   "text": "[ICON:WAYPOINT]Grab Waypoint — bookmark, you'll return many times.\nOrder: 1. NORTHWEST → Chamber of Sins. 2. NORTHEAST → Broken Bridge. 3. SOUTHEAST → Fellshrine Ruins."},

  {"zone": "The Chamber of Sins Level 1",
   "text": "[ICON:WAYPOINT]Grab Waypoint (center). [ICON:ENTER_ZONE]Find staircase to Level 2."},

  {"zone": "The Chamber of Sins Level 2",
   "text": "[ICON:TRIAL]Do Trial of Ascendancy (2/6) — opposite side from boss. [ICON:KILL_BOSS]Kill Fidelitas. [ICON:COLLECT_ITEM]Pick up Baleful Gem. [ICON:ENTER_TOWN]Return to town. [ICON:ENTER_ZONE]Crossroads NORTHEAST → Broken Bridge."},

  {"zone": "The Broken Bridge",
   "text": "[ICON:KILL_BOSS]Kill/Help Kraityn. ⚠️ Pick up Kraityn's Amulet! [ICON:ENTER_ZONE]Return to Crossroads → SOUTHEAST → Fellshrine Ruins."},

  {"zone": "The Fellshrine Ruins",
   "text": "[ICON:ENTER_ZONE]Stay on path, ignore distractions. Follow to graveyard archway → angle north → The Crypt."},

  {"zone": "The Crypt Level 1",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:TRIAL]Do Trial of Ascendancy (3/6). [ICON:ENTER_ZONE]Proceed to Level 2."},

  {"zone": "The Crypt Level 2",
   "text": "[ICON:KILL_BOSS]Kill Archbishop Geofri. [ICON:COLLECT_ITEM]Grab Golden Hand from altar behind him. [ICON:TAKE_REWARD]Skill Point (turn in at town). [ICON:ENTER_ZONE]Head to Riverways."},

  {"zone": "The Riverways",
   "text": "[ICON:WAYPOINT]Grab Waypoint (middle). Note side path to Wetlands — return here later. [ICON:ENTER_ZONE]Continue main path to The Western Forest."},

  {"zone": "The Western Forest",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:KILL_BOSS]Kill Captain Ateri → socket Thaumetic Emblem in wall behind camp. [ICON:TAKE_REWARD]Skill Point (redeem at Act 1 Lioneye's Watch!). [ICON:KILL_BOSS]Kill/Help Alira (follow torches off main path). ⚠️ Grab Alira's Amulet! [ICON:ENTER_ZONE]Find Weaver's Chambers on opposite wall."},

  {"zone": "The Weaver's Chambers",
   "text": "[ICON:ENTER_ZONE]Find The Weaver's Nest inside."},

  {"zone": "The Weaver's Nest",
   "text": "[ICON:KILL_BOSS]Kill The Weaver. [ICON:COLLECT_ITEM]Grab Maligaro's Spike. [ICON:ENTER_TOWN]Return to town. [ICON:ENTER_ZONE]Riverways → north → The Wetlands."},

  {"zone": "The Wetlands",
   "text": "[ICON:WAYPOINT]Grab Waypoint (north, near Oak's Camp). [ICON:KILL_BOSS]Kill/Help Oak. ⚠️ Grab Oak's Amulet! [ICON:ENTER_ZONE]Find Vaal Ruins wall entrance near Waypoint."},

  {"zone": "The Vaal Ruins",
   "text": "[ICON:COLLECT_ITEM]Find Ancient Seal (large purple orb) — click it. [ICON:ENTER_ZONE]Proceed to Northern Forest."},

  {"zone": "The Northern Forest",
   "text": "[ICON:WAYPOINT]Grab Waypoint (near entrance). [ICON:ENTER_ZONE]Head north to The Caverns."},

  {"zone": "The Caverns",
   "text": "[ICON:WAYPOINT]Grab Waypoint. ⚠️ Locked Door needs Apex item — turn in all 3 bandit amulets at town first! [ICON:ENTER_ZONE]Head to Ancient Pyramid."},

  {"zone": "The Ancient Pyramid",
   "text": "[ICON:KILL_BOSS]Kill Vaal Oversoul — click altar to spawn (multiple phases, OST is great 😄). [ICON:ENTER_ZONE]Exit north → Act 3."},

  # ── ACT 3 ──────────────────────────────────────────────────────────────────
  {"zone": "The City of Sarn",
   "text": "ACT 3\n⚠️ Not a walk-through — skipping Clarissa BRICKS Act 3 progression! [ICON:KILL_BOSS]Kill Guard Captain. [ICON:COLLECT_ITEM]Talk to Clarissa NPC. [ICON:ENTER_TOWN]Head north to Sarn Encampment."},

  {"zone": "The Sarn Encampment",
   "text": "⚠️ DO NOT enter Sarn Arena (north) — PvP only, no campaign value. [ICON:ENTER_ZONE]Exit northeast to The Slums."},

  {"zone": "The Slums",
   "text": "[ICON:WAYPOINT]Grab Waypoint if visible. Note locked Sewers gate. [ICON:ENTER_ZONE]Find The Crematorium."},

  {"zone": "The Crematorium",
   "text": "[ICON:TRIAL]Do Trial of Ascendancy (4/6). [ICON:KILL_BOSS]Kill Piety. [ICON:COLLECT_ITEM]Pick up Tolman's Bracelet. [ICON:ENTER_TOWN]Return to town → get Sewer Keys from Clarissa. [ICON:OPEN_PASSAGE]Use keys to unlock Sewers gate in The Slums."},

  {"zone": "The Sewers",
   "text": "[ICON:COLLECT_ITEM]Find 3x Bust stashes — Victario's Secrets. [ICON:TAKE_REWARD]Skill Point. [ICON:WAYPOINT]Grab Waypoint near Undying Blockage (remember location). Skip Sister Cassia. [ICON:ENTER_ZONE]Find Marketplace wall entrance at back of zone."},

  {"zone": "The Marketplace",
   "text": "[ICON:WAYPOINT]Grab Waypoint (near large statues). [ICON:TRIAL]Enter Catacombs nearby for Trial (5/6). ⚠️ Ignore the Ornate Chest. [ICON:ENTER_ZONE]Head north, hug top wall west → The Battlefront."},

  {"zone": "The Catacombs",
   "text": "[ICON:TRIAL]Do Trial of Ascendancy (5/6). Grab Recipe Altar. [ICON:ENTER_ZONE]Return to Marketplace."},

  {"zone": "The Battlefront",
   "text": "[ICON:WAYPOINT]Grab Waypoint (north). [ICON:COLLECT_ITEM]Find Blackguard Chest near WP (usually SW) — grab Ribbon Spool. [ICON:ENTER_ZONE]Head west then north → The Docks."},

  {"zone": "The Docks",
   "text": "[ICON:COLLECT_ITEM]Find Supply Container on a dock — grab Thaumetic Sulphite. [ICON:ENTER_ZONE]Return to Battlefront → northeast → The Solaris Temple."},

  {"zone": "The Solaris Temple Level 1",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Proceed to Level 2."},

  {"zone": "The Solaris Temple Level 2",
   "text": "⚠️ Need Ribbon Spool AND Thaumetic Sulphite! [ICON:COLLECT_ITEM]Talk to Lady Dialla → get Infernal Talc. [ICON:ENTER_ZONE]Go to Sewers WP → burn Undying Blockage → The Ebony Barracks."},

  {"zone": "The Ebony Barracks",
   "text": "[ICON:WAYPOINT]Grab Waypoint (north, near entrance). [ICON:KILL_BOSS]Kill General Gravicius. [ICON:ENTER_ZONE]Head NORTHWEST → The Lunaris Temple."},

  {"zone": "The Lunaris Temple Level 1",
   "text": "[ICON:ENTER_ZONE]Follow carpets to Waypoint and staircase → Level 2."},

  {"zone": "The Lunaris Temple Level 2",
   "text": "💡 Carts: 1 cart = correct path. 2 carts = wrong. Use blink in cage labyrinth. [ICON:KILL_BOSS]Kill Piety. [ICON:COLLECT_ITEM]Get Tower Key. [ICON:TAKE_REWARD]Skill Point from Grigor in town. [ICON:ENTER_ZONE]Return to Ebony Barracks → EAST → Imperial Gardens."},

  {"zone": "The Imperial Gardens",
   "text": "[ICON:WAYPOINT]Grab Waypoint. Order: 1. NORTHWEST → The Library. 2. NORTHEAST → Trial (6/6) then Ascend! 3. EAST → Sceptre of God."},

  {"zone": "The Library",
   "text": "[ICON:COLLECT_ITEM]Find Siosa. [ICON:OPEN_PASSAGE]Find Loose Candle → opens The Archives."},

  {"zone": "The Archives",
   "text": "[ICON:COLLECT_ITEM]Collect 4x Golden Pages from Book Stands (❗ on minimap). [ICON:TAKE_REWARD]Give to Siosa → Reward: Level 31 Gems (massive unlock!). [ICON:ENTER_ZONE]Return → Imperial Gardens → Trial → Ascend!"},

  {"zone": "The Sceptre of God",
   "text": "[ICON:ENTER_ZONE]Climb stairs at each of three levels → Upper Sceptre of God."},

  {"zone": "The Upper Sceptre of God",
   "text": "[ICON:KILL_BOSS]Kill Dominus. ⚠️ 'A Touch of God' thunderfist → GET BACK immediately. Phase 2: stand NEXT TO him during shield (avoids Corrupted Blood). [ICON:ENTER_ZONE]Speak to Dialla. Exit right → Act 4."},

  # ── ACT 4 ──────────────────────────────────────────────────────────────────
  {"zone": "The Aqueduct",
   "text": "ACT 4\n⚠️ Very long bridge — death sends you back to start! When one side closes, cross to the other. [ICON:ENTER_ZONE]Find Highgate entrance at far left end."},

  {"zone": "Highgate",
   "text": "[ICON:ENTER_ZONE]Exit SOUTHWEST to The Dried Lake."},

  {"zone": "The Dried Lake",
   "text": "[ICON:KILL_BOSS]Kill Voll (head south and west to his camp). [ICON:COLLECT_ITEM]Grab Deshret's Banner. [ICON:ENTER_TOWN]Return to town → click Deshret's Seal north of town → opens The Mines."},

  {"zone": "The Mines Level 1",
   "text": "[ICON:COLLECT_ITEM]Grab Recipe Altar along main path. Ignore Sulphite/Niko (league content). [ICON:ENTER_ZONE]Proceed to Level 2."},

  {"zone": "The Mines Level 2",
   "text": "[ICON:COLLECT_ITEM]Follow cart tracks to Deshret's Spirit ❗. [ICON:KILL_BOSS]Kill Hammerstorm. [ICON:TAKE_REWARD]Click Spirit — Skill Point. [ICON:ENTER_ZONE]Continue to Crystal Veins."},

  {"zone": "The Crystal Veins",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:COLLECT_ITEM]Talk to Lady Dialla. [ICON:ENTER_ZONE]Complete Kaom's Dream AND Daresso's Dream (either order)."},

  {"zone": "Kaom's Dream",
   "text": "[ICON:ENTER_ZONE]Go ALL WAY RIGHT from start → up stairs → ALL WAY LEFT → north to Kaom's Stronghold."},

  {"zone": "Kaom's Stronghold",
   "text": "[ICON:WAYPOINT]Grab Waypoint + Crafting Altar at start. Hug left wall north. [ICON:KILL_BOSS]Kill Kaom (dodge telegraphed moves — easy fight). [ICON:COLLECT_ITEM]Grab Eye of Fury. [ICON:ENTER_ZONE]Return to Crystal Veins."},

  {"zone": "Daresso's Dream",
   "text": "[ICON:ENTER_ZONE]Follow narrow alleyways. Some rooms gate you until all enemies dead. [ICON:KILL_BOSS]Kill Barkhul in arena. [ICON:ENTER_ZONE]Proceed to The Grand Arena."},

  {"zone": "The Grand Arena",
   "text": "[ICON:WAYPOINT]Grab Waypoint + Crafting Altar. Exit always at NORTH end — alternate Passageways and Arenas. [ICON:KILL_BOSS]Kill Daresso (4 phases — hardest is last). [ICON:COLLECT_ITEM]Grab Eye of Desire. [ICON:ENTER_ZONE]Return to Dialla → she opens Belly of the Beast."},

  {"zone": "The Belly of the Beast Level 1",
   "text": "⚠️ Stock up — long zone chain begins here! [ICON:ENTER_ZONE]Head north-center to Level 2."},

  {"zone": "The Belly of the Beast Level 2",
   "text": "[ICON:KILL_BOSS]Kill Piety (dodge rotating beam — it varies speed). [ICON:COLLECT_ITEM]Grab Recipe Altar. [ICON:ENTER_ZONE]Proceed up to The Harvest."},

  {"zone": "The Harvest",
   "text": "[ICON:WAYPOINT]Grab Waypoint. Loop entire zone for 3 bosses: [ICON:KILL_BOSS]Kill Shavronne → Malachai's Entrails. [ICON:KILL_BOSS]Kill Doedre → Malachai's Lungs. [ICON:KILL_BOSS]Kill Maligaro → Malachai's Heart. [ICON:TAKE_REWARD]Return all 3 to Piety at WP → opens Black Core."},

  {"zone": "The Black Core",
   "text": "[ICON:KILL_BOSS]Kill Malachai. 💡 Big AoE: move BEHIND him. Phase 2: kill Hearts in arena corners at each 25% threshold. [ICON:ENTER_ZONE]Use red portal → Highgate. Collect gem reward from Dialla → top-right wall exit → Act 5."},

  # ── ACT 5 ──────────────────────────────────────────────────────────────────
  {"zone": "The Ascent",
   "text": "ACT 5\n[ICON:ENTER_ZONE]1. Head NORTH+WEST across long bridge. 2. Follow icy path to Wall Face + Crafting Altar. 3. Head WEST to Resonator ❗ → click → enter Oriath Portal → Slave Pens."},

  {"zone": "The Slave Pens",
   "text": "[ICON:ENTER_ZONE]Stay FAR RIGHT → bottom-right corner → then SOUTHWEST. [ICON:KILL_BOSS]Kill Overseer Krow. [ICON:ENTER_TOWN]Take ladder to Overseer's Tower."},

  {"zone": "The Overseer's Tower",
   "text": "[ICON:ENTER_ZONE]Exit NORTHWEST to The Control Blocks."},

  {"zone": "The Control Blocks",
   "text": "💡 Use blink skill through fence gaps — saves major navigation time. [ICON:COLLECT_ITEM]Find Miasmeter near ❗ symbol — blink through. [ICON:TAKE_REWARD]Skill Point. [ICON:KILL_BOSS]Kill Justicar Casticus → get Eyes of Zeal. [ICON:ENTER_ZONE]Proceed to Oriath Square."},

  {"zone": "Oriath Square",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Cross bridge east → find The Templar Courts."},

  {"zone": "The Templar Courts",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]After WP: EAST to wall → SOUTH to bottom-right → WEST → NORTH → The Chamber of Innocence."},

  {"zone": "The Chamber of Innocence",
   "text": "[ICON:KILL_BOSS]Kill Innocence. ⚠️ 'I am the end' = large AoE → RUN AWAY. 'I' beam = circle around him. [ICON:COLLECT_ITEM]Speak to Sin. Exit RIGHT side, pass WP, talk to Bannon. [ICON:ENTER_ZONE]Enter The Torched Courts."},

  {"zone": "The Torched Courts",
   "text": "[ICON:ENTER_ZONE]Navigate counter-clockwise to The Ruined Square."},

  {"zone": "The Ruined Square",
   "text": "[ICON:WAYPOINT]Grab Waypoint. Four objectives: [ICON:ENTER_ZONE]NORTH → Ossuary. [ICON:ENTER_ZONE]Find The Reliquary (opposite end from WP). [ICON:KILL_BOSS]Kill Utula (side area near center). [ICON:ENTER_ZONE]Find Cathedral Rooftop (opposite corner from WP side)."},

  {"zone": "The Ossuary",
   "text": "[ICON:COLLECT_ITEM]Clockwise loop — find Sign of Purity from Tomb of First Templar. Grab Crafting Altar. [ICON:ENTER_ZONE]Return to Ruined Square."},

  {"zone": "The Reliquary",
   "text": "[ICON:COLLECT_ITEM]Explore all corners — find 3x Torments: Hinekora's Hair, Tukohama's Tooth, Valako's Jaw. [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Return to town to collect Skill Books."},

  {"zone": "The Cathedral Rooftop",
   "text": "[ICON:ENTER_ZONE]Turn LEFT, head north all the way to NORTHWEST corner → Cathedral Apex. [ICON:KILL_BOSS]Kill Kitava — (-30% All Resistances!). 💡 Death respawns you at entrance — just keep going. [ICON:ENTER_ZONE]Speak to Lilly Roth → Sail to Wraeclast → Act 6."},

  # ── ACT 6 ──────────────────────────────────────────────────────────────────
  {"zone": "The Twilight Strand",
   "text": "ACT 6\n⚠️ Kill EVERY monster — counter appears when 5 remain. [ICON:TAKE_REWARD]Reward: Respec Points + ALL Skill Gems. [ICON:ENTER_TOWN]Return to Lioneye's Watch → talk to Lilly (bottom-right)."},

  {"zone": "The Coast",
   "text": "[ICON:WAYPOINT]Grab Waypoint (NORTHEAST corner). Skip Tidal Island entirely. [ICON:ENTER_ZONE]Head straight to The Mud Flats."},

  {"zone": "The Mud Flats",
   "text": "[ICON:ENTER_ZONE]Head EAST to north wall shack at end of zone. [ICON:KILL_BOSS]Kill Dishonored Queen. [ICON:COLLECT_ITEM]Grab Eye of Conquest. [ICON:ENTER_ZONE]Head NORTHWEST → The Karui Fortress."},

  {"zone": "The Karui Fortress",
   "text": "[ICON:ENTER_ZONE]Find interior door on inner side of the circle. [ICON:KILL_BOSS]Kill Tukohama. ⚠️ At 50%: destroy 3 totems to resume damaging him, then avoid circling beam! [ICON:TAKE_REWARD]Skill Point. [ICON:COLLECT_ITEM]Speak to Sin. [ICON:ENTER_ZONE]Exit northeast → The Ridge."},

  {"zone": "The Ridge",
   "text": "[ICON:ENTER_ZONE]Follow linear path to The Lower Prison."},

  {"zone": "The Lower Prison",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:TRIAL]Do Trial (1/6 Cruel) — usually SOUTHERNMOST part. [ICON:ENTER_ZONE]Find Shavronne's Tower in opposite corner."},

  {"zone": "Shavronne's Tower",
   "text": "[ICON:KILL_BOSS]Kill Brutus + Shavronne (both have telegraphed 1-shot moves). 💡 Shavronne phases mid-fight — dodge lightning. [ICON:COLLECT_ITEM]Speak to Sin. [ICON:ENTER_ZONE]Head left → downstairs → Warden's Chambers → Prisoner's Gate."},

  {"zone": "Prisoner's Gate",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:COLLECT_ITEM]Talk to Nessa (east corner). [ICON:ENTER_ZONE]Find Valley of Fire Drinker (north). After: head opposite direction → The Western Forest."},

  {"zone": "The Valley of the Fire Drinker",
   "text": "[ICON:KILL_BOSS]Kill Abberath — 2 arenas, dodge telegraphed 1-shots, avoid ground effects. [ICON:TAKE_REWARD]Skill Point. [ICON:COLLECT_ITEM]Speak to Sin → Pantheon. [ICON:ENTER_ZONE]Return to Prisoner's Gate → Western Forest."},

  {"zone": "The Western Forest",
   "text": "[ICON:ENTER_ZONE]Follow road to Riverways. 💡 Crafting Altar at old Alira Camp — follow torches off main path."},

  {"zone": "The Riverways",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Side path (two rod blocks) → The Wetlands. After Wetlands: return WP → NORTH then EAST → The Southern Forest."},

  {"zone": "The Wetlands",
   "text": "[ICON:ENTER_ZONE]Find The Spawning Ground (usually north wall). [ICON:KILL_BOSS]Kill Ryslatha — slay 3 eggs (L/C/R), she respawns upper center. Watch for Chaos damage! [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Return to Riverways."},

  {"zone": "The Southern Forest",
   "text": "[ICON:ENTER_ZONE]Navigate wood bridges between islands. [ICON:WAYPOINT]Grab Waypoint (east corner). [ICON:ENTER_ZONE]Find Cavern of Anger entrance."},

  {"zone": "The Cavern of Anger",
   "text": "[ICON:COLLECT_ITEM]Grab Black Flag in middle passage. [ICON:ENTER_ZONE]Find wall entrance to The Beacon."},

  {"zone": "The Beacon",
   "text": "[ICON:ENTER_ZONE]Follow shoreline as it wraps up the map. [ICON:OPEN_PASSAGE]Activate 2 circular platforms — stand inside each until column fully retracts. [ICON:TAKE_REWARD]Find final ❗ → light the Beacon. [ICON:COLLECT_ITEM]Talk to Weylam Roth → sail to Brine King's Reef."},

  {"zone": "The Brine King's Reef",
   "text": "[ICON:ENTER_ZONE]Stay on border/wall — find The Brine King's Throne entrance. [ICON:KILL_BOSS]Kill The Brine King. 💡 Stay BEHIND him. ⚠️ Don't enter ocean walls, dodge small white whirlpools (hard to see)! [ICON:COLLECT_ITEM]Speak to Sin. Sail to Bridge Encampment → Act 7."},

  # ── ACT 7 ──────────────────────────────────────────────────────────────────
  {"zone": "The Bridge Encampment",
   "text": "ACT 7\n[ICON:ENTER_ZONE]Head north to The Broken Bridge."},

  {"zone": "The Broken Bridge",
   "text": "[ICON:ENTER_ZONE]Walk linear path to The Crossroads. Optional: search corners for Dirty Lockbox (Silver Locket — flask reward)."},

  {"zone": "The Crossroads",
   "text": "[ICON:WAYPOINT]Grab Waypoint (center). [ICON:ENTER_ZONE]EAST+SOUTH → Fellshrine Ruins first. NORTH+WEST → Chamber of Sins after."},

  {"zone": "The Fellshrine Ruins",
   "text": "[ICON:ENTER_ZONE]Stay on path. Under archway → slightly north through cemetery → The Crypt."},

  {"zone": "The Crypt",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:TRIAL]Do Trial (2/6 Cruel) + Crafting Altar. [ICON:COLLECT_ITEM]Find Container of Sins (near Sarcophagus door ❗) → grab Maligaro's Map. [ICON:ENTER_ZONE]Return to Crossroads → Chamber of Sins L1."},

  {"zone": "The Chamber of Sins Level 1",
   "text": "[ICON:OPEN_PASSAGE]Find Silk in center → use Maligaro's Map in map device → enter Maligaro's Sanctum."},

  {"zone": "Maligaro's Sanctum",
   "text": "⚠️ 6 portals only — dying uses one. If all used, get new map from Crypt. [ICON:ENTER_ZONE]Left at entrance → narrow bridge → NORTH → top wall left → NORTH → Maligaro's Workshop. [ICON:KILL_BOSS]Kill Maligaro + Black Death + Fidelitas. [ICON:COLLECT_ITEM]Grab Black Venom → get Obsidian Key from Silk. [ICON:OPEN_PASSAGE]Use key at stairway → Chamber L2."},

  {"zone": "The Chamber of Sins Level 2",
   "text": "[ICON:TRIAL]Do Trial (3/6 Cruel). [ICON:ENTER_ZONE]Find Secret Passage ❗ → The Den."},

  {"zone": "The Den",
   "text": "[ICON:ENTER_ZONE]Stay left — find wall entrance to The Ashen Fields."},

  {"zone": "The Ashen Fields",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Head SOUTHWEST toward Fortress Encampment area. [ICON:KILL_BOSS]Kill Greust. [ICON:TAKE_REWARD]Skill Point + Pantheon. [ICON:ENTER_ZONE]Head north to Northern Forest."},

  {"zone": "The Northern Forest",
   "text": "[ICON:ENTER_ZONE]Head NORTH+WEST to The Dread Thicket. Skip optional Azmeri Shrine sidequest."},

  {"zone": "The Dread Thicket",
   "text": "[ICON:COLLECT_ITEM]Collect 7x Fireflies scattered across zone. [ICON:KILL_BOSS]Find Den of Despair → Kill Gruthkul. [ICON:TAKE_REWARD]Skill Point + Pantheon. [ICON:ENTER_ZONE]Return to Northern Forest → The Causeway."},

  {"zone": "The Causeway",
   "text": "[ICON:WAYPOINT]Grab Waypoint + Crafting Altar (NORTH+slightly WEST). [ICON:COLLECT_ITEM]Find Kishara's Star in Lockbox near zone exit. [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Head to The Vaal City."},

  {"zone": "The Vaal City",
   "text": "[ICON:WAYPOINT]Grab Waypoint (north-middle area — find Yeena). ⚠️ Need all 7 Fireflies to open Temple of Decay door! [ICON:COLLECT_ITEM]Talk to Yeena. [ICON:ENTER_ZONE]Enter Temple of Decay."},

  {"zone": "The Temple of Decay Level 1",
   "text": "[ICON:ENTER_ZONE]Multiple floors — find next path in OPPOSITE corner from where you entered at each floor."},

  {"zone": "The Temple of Decay Level 2",
   "text": "Crafting Altar on 4th floor. [ICON:KILL_BOSS]Kill Arakaali. ⚠️ 50%: she eats Silk — dodge PURPLE FLYING DISCS (very dangerous!). [ICON:COLLECT_ITEM]Speak to Sin + Yeena. [ICON:ENTER_ZONE]Head north → Act 8."},

  # ── ACT 8 ──────────────────────────────────────────────────────────────────
  {"zone": "The Sarn Ramparts",
   "text": "ACT 8\n[ICON:ENTER_ZONE]Head EAST along wall → up staircase → double back WEST along top → down staircase → Sarn Encampment."},

  {"zone": "The Sarn Encampment",
   "text": "[ICON:ENTER_ZONE]Exit WEST past Clarissa → The Toxic Conduits."},

  {"zone": "The Toxic Conduits",
   "text": "⚠️ Chaos Damage starts appearing here — check resistances! [ICON:ENTER_ZONE]Follow path to Doedre's Cesspool."},

  {"zone": "Doedre's Cesspool",
   "text": "[ICON:OPEN_PASSAGE]Follow conduits to gate → open it → descend → click Valve. [ICON:KILL_BOSS]Kill Doedre. [ICON:COLLECT_ITEM]Speak to Sin. [ICON:ENTER_ZONE]Exit via Sewer Outlet: NORTHEAST → The Quay (first). SOUTHWEST → Grand Promenade (after Quay)."},

  {"zone": "The Quay",
   "text": "⚠️ Order matters! [ICON:COLLECT_ITEM]1. Find Sealed Casket (short narrow bridge) → grab Ankh of Eternity. [ICON:KILL_BOSS]2. Find Resurrection Site → defeat army, talk to Clarissa. [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]3. Find The Grain Gate."},

  {"zone": "The Grain Gate",
   "text": "[ICON:WAYPOINT]Grab Waypoint (zone start). Alternate indoor rooms + outdoor courtyards. [ICON:KILL_BOSS]Kill Gemling Legionnaires (2nd outdoor courtyard, slightly NW). [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Continue to Imperial Fields."},

  {"zone": "The Imperial Fields",
   "text": "[ICON:WAYPOINT]Grab Waypoint (middle). Follow main path to dead end → continue same direction to find Solaris Temple (courtyard flooring with statues)."},

  {"zone": "The Solaris Temple Level 1",
   "text": "⚠️ Ignore The Solaris Concourse — large distraction, nothing required. [ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Descend to Level 2."},

  {"zone": "The Solaris Temple Level 2",
   "text": "[ICON:KILL_BOSS]Kill Dawn (4 telegraphed moves — easy to dodge). [ICON:COLLECT_ITEM]Grab Sun Orb. [ICON:ENTER_ZONE]Return to Doedre's Cesspool → take other direction → The Grand Promenade."},

  {"zone": "The Grand Promenade",
   "text": "[ICON:ENTER_ZONE]Follow semi-circle counter-clockwise → The Bath House."},

  {"zone": "The Bath House",
   "text": "[ICON:TRIAL]Do Trial (4/6 Cruel) — pull all levers in area first. [ICON:ENTER_ZONE]Head SOUTHWEST → High Gardens (kill Yugul). Return here → The Lunaris Concourse."},

  {"zone": "The High Gardens",
   "text": "⚠️ Dying resets the entire path — move quickly and carefully! [ICON:KILL_BOSS]Kill Yugul. 💡 Phases twice — defeat his reflections during each phase. [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Return to Bath House → take Lunaris Concourse."},

  {"zone": "The Lunaris Concourse",
   "text": "[ICON:WAYPOINT]Grab Waypoint (slightly north of center). [ICON:ENTER_ZONE]NORTH+EAST → Lunaris Temple. After temple: return WP → EAST → The Harbour Bridge."},

  {"zone": "The Lunaris Temple Level 1",
   "text": "[ICON:ENTER_ZONE]Follow blue carpet. At cathedral room: NORTH+EAST through forking rooms → find WP and stairs to Level 2."},

  {"zone": "The Lunaris Temple Level 2",
   "text": "💡 Very confusing — many dead ends. Use blink in cage sections liberally. [ICON:KILL_BOSS]Kill Dusk (easy — similar to Dawn). [ICON:COLLECT_ITEM]Grab Moon Orb. [ICON:ENTER_ZONE]Return to Lunaris Concourse → EAST+SOUTH → Harbour Bridge."},

  {"zone": "The Harbour Bridge",
   "text": "⚠️ Need Sun Orb + Moon Orb! [ICON:OPEN_PASSAGE]Head to center — click Statue of the Sisters to begin fight. [ICON:KILL_BOSS]Kill Solaris + Lunaris — attack only the currently ACTIVE one. 💡 Good time for Cruel Lab! [ICON:COLLECT_ITEM]Speak to Sin (Lunaris Pantheon — very useful). [ICON:ENTER_ZONE]Take exit → Act 9."},

  # ── ACT 9 ──────────────────────────────────────────────────────────────────
  {"zone": "The Blood Aqueduct",
   "text": "ACT 9\n[ICON:ENTER_ZONE]Two long parallel paths — cross bridge when one side closes. Find Highgate at very end."},

  {"zone": "Highgate",
   "text": "[ICON:ENTER_ZONE]Exit northeast → The Descent."},

  {"zone": "The Descent",
   "text": "[ICON:ENTER_ZONE]Three zones: head EAST+slightly NORTH to Supply Hoist each time. Ignore Jun's doorways (league content). 3rd zone has entrance to Vastiri Desert."},

  {"zone": "The Vastiri Desert",
   "text": "[ICON:COLLECT_ITEM]Find Storm-Weathered Chest ❗ (central) → defeat mummies → grab Storm Blade. [ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_TOWN]Town Portal → talk to Petarus+Vanja → get Bottled Storm. Return → [ICON:OPEN_PASSAGE]open blocked entrance EAST → The Oasis. Find Foothills entrance after Oasis."},

  {"zone": "The Oasis",
   "text": "[ICON:KILL_BOSS]Kill Shakari. 💡 At ~60%: she burrows — follow SLOWLY and incrementally, don't run ahead or she won't follow. Final arena at end of path. [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Return to Vastiri Desert → find The Foothills."},

  {"zone": "The Foothills",
   "text": "[ICON:WAYPOINT]Grab Waypoint (north). [ICON:ENTER_ZONE]Continue NORTH → Boiling Lake. Return WP → search opposite walls → The Tunnel."},

  {"zone": "The Boiling Lake",
   "text": "[ICON:KILL_BOSS]Kill The Basilisk (head NORTH+slightly EAST — stand behind him, very easy). [ICON:COLLECT_ITEM]Grab Basilisk Acid. [ICON:ENTER_ZONE]Return to Foothills → find The Tunnel."},

  {"zone": "The Tunnel",
   "text": "[ICON:TRIAL]Do Trial (5/6 Cruel) — usually near entrance. [ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Proceed to The Quarry."},

  {"zone": "The Quarry",
   "text": "[ICON:WAYPOINT]Grab Waypoint + Crafting Altar + talk to Sin. [ICON:ENTER_ZONE]Search borders: 1. The Refinery. 2. The Shrine of the Winds. When done → return to WP, talk to Sin → opens Belly of the Beast."},

  {"zone": "The Refinery",
   "text": "[ICON:ENTER_ZONE]Follow cart railway WEST then NORTH+WEST to ❗. [ICON:KILL_BOSS]Kill General Adus (dodge lightning bolts — highly telegraphed, very high damage). [ICON:COLLECT_ITEM]Grab Trarthan Powder. Grab secret crafting recipe. [ICON:ENTER_ZONE]Return to Quarry."},

  {"zone": "The Shrine of the Winds",
   "text": "[ICON:KILL_BOSS]Kill Garukhan+Kira. 💡 Many tornadoes — small ones dangerous! Bait Garukhan into safe spaces between twisters. [ICON:COLLECT_ITEM]Speak to Sin, grab Sekhema Feather. [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Return to Quarry → talk to Sin at WP."},

  {"zone": "The Belly of the Beast",
   "text": "[ICON:ENTER_ZONE]Head toward UPPER-MIDDLE TOP of zone. ⚠️ Watch for random Corrupted Blood stacks! [ICON:ENTER_ZONE]Find entrance to The Rotting Core."},

  {"zone": "The Rotting Core",
   "text": "[ICON:KILL_BOSS]Kill The Trinity — Doedre+Maligaro+Shavronne across 3 domains, then all three together. [ICON:COLLECT_ITEM]Speak to Lilly Roth → travel to Oriath Docks → Act 10."},

  # ── ACT 10 ─────────────────────────────────────────────────────────────────
  {"zone": "Oriath Docks",
   "text": "ACT 10\n[ICON:ENTER_ZONE]Head NORTH → take stairs → The Cathedral Rooftop."},

  {"zone": "The Cathedral Rooftop",
   "text": "[ICON:ENTER_ZONE]Just WEST of entrance → Cathedral Apex. [ICON:KILL_BOSS]Kill Plaguewing. [ICON:COLLECT_ITEM]Speak to Bannon. [ICON:TAKE_REWARD]Flask reward. [ICON:ENTER_ZONE]Run SOUTHEAST to bottom of zone → The Ravaged Square."},

  {"zone": "The Ravaged Square",
   "text": "[ICON:WAYPOINT]Grab Waypoint. Objectives: [ICON:ENTER_ZONE]SOUTH → Control Blocks → bridge → NORTH → Ossuary. [ICON:ENTER_ZONE]EAST+SOUTH → Torched Courts. When done: return WP → speak to Innocence → opens The Canals."},

  {"zone": "The Control Blocks",
   "text": "💡 Use blink through fence gaps. [ICON:KILL_BOSS]Kill Vilenta (loop around back → wall entrance to arena). [ICON:TAKE_REWARD]Skill Point. [ICON:ENTER_ZONE]Return → cross bridge → The Ossuary."},

  {"zone": "The Ossuary",
   "text": "[ICON:COLLECT_ITEM]Find Elixir of Allure (random corner). [ICON:TRIAL]Do Trial (6/6 Cruel) — head NORTH+WEST. 💡 Good time for Merciless Lab now! [ICON:ENTER_ZONE]Return to Ravaged Square."},

  {"zone": "The Torched Courts",
   "text": "[ICON:ENTER_ZONE]Giant clockwise circle from ~12 o'clock: EAST → SOUTH → WEST → slightly NORTH → exit to Desecrated Chambers."},

  {"zone": "The Desecrated Chambers",
   "text": "[ICON:WAYPOINT]Grab Waypoint. [ICON:ENTER_ZONE]Counter-clockwise: WEST → SOUTH → EAST → slightly NORTH → Sanctum. [ICON:KILL_BOSS]Kill Avarius (dodge red charging beam + large melee swing). [ICON:COLLECT_ITEM]Grab Staff of Purity → town → talk to Bannon → Innocence appears. [ICON:ENTER_ZONE]Return to Ravaged Square → SE of WP → The Canals."},

  {"zone": "The Canals",
   "text": "[ICON:ENTER_ZONE]Head WEST+NORTH to zone tip → The Feeding Trough."},

  {"zone": "The Feeding Trough",
   "text": "⚠️ DO MERCILESS LAB BEFORE THIS BOSS! [ICON:ENTER_ZONE]Head WEST+NORTH to tip. Grab Crafting Altar. Talk to Sin. [ICON:KILL_BOSS]Kill Kitava. [ICON:COLLECT_ITEM]Speak to Sin → portal to Oriath Docks → sail to Karui Shores."},

  # ── EPILOGUE ────────────────────────────────────────────────────────────────
  {"zone": "Karui Shores",
   "text": "EPILOGUE\n[ICON:COLLECT_ITEM]Grab Crafting Altar. [ICON:TAKE_REWARD]Talk to Lani → 2x Skill Points. [ICON:COLLECT_ITEM]Talk to Kirac → get a Map. [ICON:KILL_BOSS]Open Map Device → enter → kill boss. ✅ Campaign complete — welcome to the endgame, Exile!"},
]

TOWNS = {
    "Lioneye's Watch",
    "Forest Encampment",
    "The Forest Encampment",
    "Sarn Encampment",
    "The Sarn Encampment",
    "Highgate",
    "Overseer's Tower",
    "The Overseer's Tower",
    "The Bridge Encampment",
    "Oriath Docks",
    "Karui Shores"
}
