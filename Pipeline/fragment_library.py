"""
Fragment library for synthetic review generation.

Each fragment is (aspect_code, sentiment_tier, text). Tiers, where
present for an aspect, are: strong_positive, mild_positive, neutral,
mild_negative, strong_negative. Not every aspect uses all five tiers,
some naturally skew (e.g. HIDDEN_COSTS rarely gets a "strong_positive"
review, the absence of hidden costs is more often neutral relief than
delight).

Fragments deliberately vary in:
  - polarity (the tier itself)
  - subjectivity (some fragments are flatly descriptive, others are
    heavily opinionated, even within the same tier)
  - emotional tone (anger vs sadness on the negative side, joy vs
    trust/reassurance on the positive side), so NRC has genuine
    differentiation to detect, not just polarity-flipped synonyms

Each fragment naturally uses vocabulary relevant to its aspect, which
doubles as the source material for the aspect keyword dictionary built
later in the ETL/aspect-extraction step.

Built in batches by category. This file: Location (5 aspects).
"""

FRAGMENTS = []

# ---- LOCATION ----
FRAGMENTS += [
    ("LOCATION", "strong_positive", "The location could not have been better, right in the heart of everything we wanted to see."),
    ("LOCATION", "mild_positive", "It was in a fairly convenient location, close enough to most of the main attractions."),
    ("LOCATION", "neutral", "The location is about ten minutes from the city centre by taxi."),
    ("LOCATION", "mild_negative", "The location was a bit out of the way, so we ended up relying on taxis more than expected."),
    ("LOCATION", "strong_negative", "The location was genuinely inconvenient, far from anything worth walking to and poorly served by public transport."),
]

# ---- VIEW ----
FRAGMENTS += [
    ("VIEW", "strong_positive", "We were blown away by the view, it alone made the whole visit worth it."),
    ("VIEW", "mild_positive", "The view from the terrace was quite pleasant, especially in the early morning."),
    ("VIEW", "neutral", "The view looked out toward an inner courtyard rather than the street."),
    ("VIEW", "mild_negative", "The view was a little disappointing, mostly overlooking the car park."),
    ("VIEW", "strong_negative", "There was barely any view to speak of, just a brick wall a few metres from the window."),
]

# ---- ACCESSIBILITY ----
FRAGMENTS += [
    ("ACCESSIBILITY", "strong_positive", "Accessibility was excellent, with ramps and a lift that made things effortless for my mother, who uses a wheelchair."),
    ("ACCESSIBILITY", "mild_positive", "Getting around was reasonably easy, even with a stroller."),
    ("ACCESSIBILITY", "neutral", "There is a lift available, though it is fairly small."),
    ("ACCESSIBILITY", "mild_negative", "Accessibility could be improved, there were a few steps with no alternative route."),
    ("ACCESSIBILITY", "strong_negative", "Accessibility was a real problem, no lift at all and several flights of stairs throughout."),
]

# ---- PARKING ----
FRAGMENTS += [
    ("PARKING", "strong_positive", "Free parking right outside made arriving with the car completely stress-free."),
    ("PARKING", "mild_positive", "Parking was easy enough to find nearby, and reasonably priced."),
    ("PARKING", "neutral", "There is a paid car park about five minutes' walk away."),
    ("PARKING", "mild_negative", "Parking was a bit of a hassle, we circled the block twice before finding a spot."),
    ("PARKING", "strong_negative", "There was nowhere reasonable to park, we ended up paying far more than expected just to leave the car somewhere safe."),
]

# ---- SAFETY ----
FRAGMENTS += [
    ("SAFETY", "strong_positive", "We felt completely safe the entire time, even walking back late at night."),
    ("SAFETY", "mild_positive", "The area felt reasonably safe, well lit and fairly quiet in the evenings."),
    ("SAFETY", "neutral", "The street has a police station a couple of blocks away."),
    ("SAFETY", "mild_negative", "We felt slightly uneasy walking back after dark, the street was poorly lit."),
    ("SAFETY", "strong_negative", "We genuinely did not feel safe in the area, especially after sunset."),
]

# ---- CLEANLINESS ----
FRAGMENTS += [
    ("CLEANLINESS", "strong_positive", "Everything was spotless from the moment we arrived, every surface looked freshly cleaned."),
    ("CLEANLINESS", "mild_positive", "It was clean and well kept throughout, nothing to complain about."),
    ("CLEANLINESS", "neutral", "Cleaning takes place on a regular schedule."),
    ("CLEANLINESS", "mild_negative", "The bathroom wasn't as clean as I would have expected, there was some grime around the taps."),
    ("CLEANLINESS", "strong_negative", "Cleanliness was a real problem, dust and grime were noticeable in several places."),
]

# ---- ROOM_QUALITY ----
FRAGMENTS += [
    ("ROOM_QUALITY", "strong_positive", "The room itself was beautifully furnished, comfortable bed, plenty of space, everything felt high quality."),
    ("ROOM_QUALITY", "mild_positive", "The room was fairly comfortable and well kept, though nothing extraordinary."),
    ("ROOM_QUALITY", "neutral", "The room has a queen bed, a small desk and a wardrobe."),
    ("ROOM_QUALITY", "mild_negative", "The room felt a bit tired, the furniture could use an update."),
    ("ROOM_QUALITY", "strong_negative", "The room was cramped and the mattress was so worn it was uncomfortable to sleep on."),
]

# ---- NOISE_LEVEL ----
FRAGMENTS += [
    ("NOISE_LEVEL", "strong_positive", "It was wonderfully quiet, a welcome change from how noisy these places can often be."),
    ("NOISE_LEVEL", "mild_positive", "Noise wasn't really an issue, just the occasional street sound in the evening."),
    ("NOISE_LEVEL", "neutral", "The space faces an internal courtyard rather than the main road."),
    ("NOISE_LEVEL", "mild_negative", "There was a fair amount of noise from the street, which made it hard to relax at times."),
    ("NOISE_LEVEL", "strong_negative", "The noise was unbearable, far too loud to relax or hold a conversation comfortably."),
]

# ---- PRESERVATION_STATE ----
FRAGMENTS += [
    ("PRESERVATION_STATE", "strong_positive", "The site has been beautifully preserved, it genuinely feels like stepping back in time."),
    ("PRESERVATION_STATE", "mild_positive", "The structure is in fairly good condition for its age."),
    ("PRESERVATION_STATE", "neutral", "Parts of the site date back to the medieval period."),
    ("PRESERVATION_STATE", "mild_negative", "Some areas showed visible wear and could use restoration work."),
    ("PRESERVATION_STATE", "strong_negative", "Much of the site is in disrepair, it was sad to see such an important place so neglected."),
]

# ---- FACILITIES_CONDITION ----
FRAGMENTS += [
    ("FACILITIES_CONDITION", "strong_positive", "The pool and gym were immaculate and clearly very well maintained."),
    ("FACILITIES_CONDITION", "mild_positive", "The shared facilities were in decent shape, nothing fancy but functional."),
    ("FACILITIES_CONDITION", "neutral", "There is a small pool on the ground floor."),
    ("FACILITIES_CONDITION", "mild_negative", "A couple of the facilities, like the lift, felt a bit outdated."),
    ("FACILITIES_CONDITION", "strong_negative", "Several facilities were simply out of order during our visit, which was a real letdown."),
]

# ---- TEMPERATURE_CONTROL ----
FRAGMENTS += [
    ("TEMPERATURE_CONTROL", "strong_positive", "The air conditioning worked perfectly, the room stayed pleasantly cool the entire stay."),
    ("TEMPERATURE_CONTROL", "mild_positive", "Temperature control was fine, easy to adjust to a comfortable level."),
    ("TEMPERATURE_CONTROL", "neutral", "The room has individual air conditioning controls."),
    ("TEMPERATURE_CONTROL", "mild_negative", "The heating was a little inconsistent, sometimes too warm, sometimes too cold."),
    ("TEMPERATURE_CONTROL", "strong_negative", "The air conditioning barely worked, the room was uncomfortably hot for most of the stay."),
]

# ---- STAFF_QUALITY ----
FRAGMENTS += [
    ("STAFF_QUALITY", "strong_positive", "The staff went above and beyond, genuinely warm, helpful and attentive throughout our time there."),
    ("STAFF_QUALITY", "mild_positive", "The staff were friendly and helpful whenever we needed something."),
    ("STAFF_QUALITY", "neutral", "Staff are available to assist throughout opening hours."),
    ("STAFF_QUALITY", "mild_negative", "A couple of the staff seemed a bit indifferent, not unfriendly exactly, just not very engaged."),
    ("STAFF_QUALITY", "strong_negative", "The staff were rude and dismissive on more than one occasion, it really soured the experience."),
]

# ---- SERVICE_EFFICIENCY ----
FRAGMENTS += [
    ("SERVICE_EFFICIENCY", "strong_positive", "Service was remarkably fast, our orders and requests were handled almost immediately."),
    ("SERVICE_EFFICIENCY", "mild_positive", "Service was reasonably prompt, no real complaints there."),
    ("SERVICE_EFFICIENCY", "neutral", "Orders are taken at the table by waiting staff."),
    ("SERVICE_EFFICIENCY", "mild_negative", "Service was a little slow, we waited longer than expected for our order."),
    ("SERVICE_EFFICIENCY", "strong_negative", "Service was painfully slow, we waited nearly an hour and had to ask twice."),
]

# ---- CHECK_IN_EXPERIENCE ----
FRAGMENTS += [
    ("CHECK_IN_EXPERIENCE", "strong_positive", "Check-in was effortless, we were in our room within minutes of arriving."),
    ("CHECK_IN_EXPERIENCE", "mild_positive", "Check-in went smoothly, only a short wait."),
    ("CHECK_IN_EXPERIENCE", "neutral", "Check-in is available from 3pm onwards."),
    ("CHECK_IN_EXPERIENCE", "mild_negative", "Check-in took a bit longer than expected, there was a short queue."),
    ("CHECK_IN_EXPERIENCE", "strong_negative", "Check-in was a frustrating ordeal, we waited nearly forty minutes with no explanation."),
]

# ---- COMMUNICATION ----
FRAGMENTS += [
    ("COMMUNICATION", "strong_positive", "Communication before our arrival was excellent, every question was answered quickly and clearly."),
    ("COMMUNICATION", "mild_positive", "Communication was fine, they responded to our messages within a reasonable time."),
    ("COMMUNICATION", "neutral", "Guests are sent a confirmation email after booking."),
    ("COMMUNICATION", "mild_negative", "Communication could have been clearer, a couple of our messages went unanswered for a while."),
    ("COMMUNICATION", "strong_negative", "Communication was a real problem, our messages were ignored and nothing was confirmed in advance."),
]

# ---- FOOD_QUALITY ----
FRAGMENTS += [
    ("FOOD_QUALITY", "strong_positive", "The food was outstanding, easily some of the best we've had in the region."),
    ("FOOD_QUALITY", "mild_positive", "The food was tasty and well prepared overall."),
    ("FOOD_QUALITY", "neutral", "The menu includes several traditional regional dishes."),
    ("FOOD_QUALITY", "mild_negative", "The food was a bit bland, nothing particularly memorable."),
    ("FOOD_QUALITY", "strong_negative", "The food was disappointing, overcooked and clearly not fresh."),
]

# ---- BREAKFAST_QUALITY ----
FRAGMENTS += [
    ("BREAKFAST_QUALITY", "strong_positive", "Breakfast was a real highlight, a huge spread of fresh, high quality options every morning."),
    ("BREAKFAST_QUALITY", "mild_positive", "Breakfast was decent, a reasonable variety to choose from."),
    ("BREAKFAST_QUALITY", "neutral", "Breakfast is served between 7am and 10am."),
    ("BREAKFAST_QUALITY", "mild_negative", "Breakfast was fairly limited, the same few options repeated each day."),
    ("BREAKFAST_QUALITY", "strong_negative", "Breakfast was poor, cold food and very little choice."),
]

# ---- MENU_VARIETY ----
FRAGMENTS += [
    ("MENU_VARIETY", "strong_positive", "The menu had an impressive range, something for every taste and several creative options."),
    ("MENU_VARIETY", "mild_positive", "There was a reasonable variety on the menu."),
    ("MENU_VARIETY", "neutral", "The menu changes seasonally."),
    ("MENU_VARIETY", "mild_negative", "The menu was a bit limited, not much choice beyond the usual standards."),
    ("MENU_VARIETY", "strong_negative", "The menu was extremely limited, barely any options for those with dietary restrictions."),
]

# ---- INFORMATIONAL_VALUE ----
FRAGMENTS += [
    ("INFORMATIONAL_VALUE", "strong_positive", "The signage and guided information were excellent, we learned so much about the site's history."),
    ("INFORMATIONAL_VALUE", "mild_positive", "There was enough information provided to understand what we were looking at."),
    ("INFORMATIONAL_VALUE", "neutral", "Information panels are available in Portuguese and English."),
    ("INFORMATIONAL_VALUE", "mild_negative", "The information provided was a bit sparse, we had to look things up ourselves afterward."),
    ("INFORMATIONAL_VALUE", "strong_negative", "There was almost no information available on site, quite a missed opportunity given the history involved."),
]

# ---- WIFI_CONNECTIVITY ----
FRAGMENTS += [
    ("WIFI_CONNECTIVITY", "strong_positive", "The wifi was fast and reliable throughout, no complaints at all."),
    ("WIFI_CONNECTIVITY", "mild_positive", "Wifi worked fine for everyday browsing."),
    ("WIFI_CONNECTIVITY", "neutral", "Free wifi is available throughout the property."),
    ("WIFI_CONNECTIVITY", "mild_negative", "The wifi connection was a bit patchy in some parts of the building."),
    ("WIFI_CONNECTIVITY", "strong_negative", "The wifi barely worked, it was practically unusable for video calls."),
]

# ---- AMENITIES_VARIETY ----
FRAGMENTS += [
    ("AMENITIES_VARIETY", "strong_positive", "The range of amenities was fantastic, pool, gym and spa all included and well kept."),
    ("AMENITIES_VARIETY", "mild_positive", "There were a decent number of amenities on offer."),
    ("AMENITIES_VARIETY", "neutral", "Amenities include a small gym and an outdoor pool."),
    ("AMENITIES_VARIETY", "mild_negative", "The amenities were fairly limited compared to what was advertised."),
    ("AMENITIES_VARIETY", "strong_negative", "Several advertised amenities simply weren't available during our stay."),
]

# ---- VALUE_FOR_MONEY ----
FRAGMENTS += [
    ("VALUE_FOR_MONEY", "strong_positive", "Excellent value for money, we honestly expected to pay much more for what we got."),
    ("VALUE_FOR_MONEY", "mild_positive", "Reasonably good value overall, fair for what was included."),
    ("VALUE_FOR_MONEY", "neutral", "Prices are in line with similar places in the area."),
    ("VALUE_FOR_MONEY", "mild_negative", "It felt a bit overpriced for what was actually offered."),
    ("VALUE_FOR_MONEY", "strong_negative", "Poor value for money, far too expensive given the quality we received."),
]

# ---- HIDDEN_COSTS ----
FRAGMENTS += [
    ("HIDDEN_COSTS", "mild_positive", "Pricing was transparent, no unexpected charges showed up at checkout."),
    ("HIDDEN_COSTS", "neutral", "A city tax is added at checkout, as is standard locally."),
    ("HIDDEN_COSTS", "mild_negative", "There were a few extra charges we hadn't anticipated, mostly small but still a bit annoying."),
    ("HIDDEN_COSTS", "strong_negative", "We were hit with several hidden fees that were never mentioned during booking, quite frustrating."),
]

# ---- BOOKING_PROCESS ----
FRAGMENTS += [
    ("BOOKING_PROCESS", "strong_positive", "Booking was incredibly easy, the whole process took less than two minutes online."),
    ("BOOKING_PROCESS", "mild_positive", "The booking process was straightforward enough."),
    ("BOOKING_PROCESS", "neutral", "Bookings can be made directly through the website or by phone."),
    ("BOOKING_PROCESS", "mild_negative", "The booking process was a bit clunky, the website kept timing out."),
    ("BOOKING_PROCESS", "strong_negative", "Booking was a nightmare, our reservation wasn't properly confirmed and we had to sort it out on arrival."),
]

# ---- OVERALL_EXPERIENCE ----
FRAGMENTS += [
    ("OVERALL_EXPERIENCE", "strong_positive", "Overall this was one of the best trips we've had in years, everything came together perfectly."),
    ("OVERALL_EXPERIENCE", "mild_positive", "Overall it was a pleasant experience, we'd happily come back."),
    ("OVERALL_EXPERIENCE", "neutral", "We visited for two nights during a longer trip around the region."),
    ("OVERALL_EXPERIENCE", "mild_negative", "Overall the experience was a bit underwhelming given what we'd expected."),
    ("OVERALL_EXPERIENCE", "strong_negative", "Overall we were genuinely disappointed, it fell far short of what we'd hoped for."),
]

# ---- ATMOSPHERE ----
FRAGMENTS += [
    ("ATMOSPHERE", "strong_positive", "The atmosphere was wonderful, warm and inviting from the moment we arrived."),
    ("ATMOSPHERE", "mild_positive", "There was a nice, relaxed atmosphere throughout."),
    ("ATMOSPHERE", "neutral", "The space has a fairly modern, minimalist design."),
    ("ATMOSPHERE", "mild_negative", "The atmosphere felt a little cold and impersonal."),
    ("ATMOSPHERE", "strong_negative", "The atmosphere was unpleasant, loud and chaotic rather than relaxing."),
]

# ---- CROWDING ----
FRAGMENTS += [
    ("CROWDING", "strong_positive", "We visited early and practically had the place to ourselves, it was lovely and peaceful."),
    ("CROWDING", "mild_positive", "It wasn't too crowded during our visit, easy to move around comfortably."),
    ("CROWDING", "neutral", "Visitor numbers tend to be highest around midday."),
    ("CROWDING", "mild_negative", "It got fairly crowded by mid-afternoon, harder to enjoy at that point."),
    ("CROWDING", "strong_negative", "It was unbearably crowded, we could barely move and it ruined the experience somewhat."),
]

# ---- ENTERTAINMENT_OPTIONS ----
FRAGMENTS += [
    ("ENTERTAINMENT_OPTIONS", "strong_positive", "There was live music most evenings and it really added to the experience."),
    ("ENTERTAINMENT_OPTIONS", "mild_positive", "There were a few entertainment options on offer, nothing major but a nice touch."),
    ("ENTERTAINMENT_OPTIONS", "neutral", "Live performances are scheduled on weekends."),
    ("ENTERTAINMENT_OPTIONS", "mild_negative", "There wasn't much in the way of entertainment during our visit."),
    ("ENTERTAINMENT_OPTIONS", "strong_negative", "Despite what was advertised, there was essentially no entertainment offered at all."),
]

# ---- FAMILY_FRIENDLINESS ----
FRAGMENTS += [
    ("FAMILY_FRIENDLINESS", "strong_positive", "Wonderfully family friendly, our kids had a great time and the staff went out of their way to accommodate them."),
    ("FAMILY_FRIENDLINESS", "mild_positive", "It worked well enough for our family, the kids didn't get bored."),
    ("FAMILY_FRIENDLINESS", "neutral", "A children's menu is available on request."),
    ("FAMILY_FRIENDLINESS", "mild_negative", "It wasn't especially geared toward families, our kids were a bit restless."),
    ("FAMILY_FRIENDLINESS", "strong_negative", "Not at all family friendly, there was nothing for the children to do and the staff seemed annoyed by their presence."),
]

# ---- DECOR_AND_DESIGN ----
FRAGMENTS += [
    ("DECOR_AND_DESIGN", "strong_positive", "The decor was stunning, every detail felt carefully thought through."),
    ("DECOR_AND_DESIGN", "mild_positive", "The design was tasteful and pleasant overall."),
    ("DECOR_AND_DESIGN", "neutral", "The interior follows a fairly traditional Portuguese style."),
    ("DECOR_AND_DESIGN", "mild_negative", "The decor felt a bit dated and could use refreshing."),
    ("DECOR_AND_DESIGN", "strong_negative", "The decor was tired and mismatched, it really detracted from the overall feel."),
]


# ---- LOCATION ----
FRAGMENTS += [
    ("LOCATION", "strong_positive", "Everything we wanted to visit was within easy walking distance, which made planning each day effortless."),
    ("LOCATION", "mild_positive", "Getting to the main sights from here took very little effort."),
    ("LOCATION", "neutral", "Public transport connections are available within a short walk."),
    ("LOCATION", "mild_negative", "A few of the places we wanted to see required a longer trip than we expected."),
    ("LOCATION", "strong_negative", "Almost nothing of interest was nearby, every outing meant a long journey first."),
]

# ---- VIEW ----
FRAGMENTS += [
    ("VIEW", "strong_positive", "The outlook stopped us in our tracks the first morning, we didn't expect anything so striking."),
    ("VIEW", "mild_positive", "There was a nice outlook to enjoy during meals."),
    ("VIEW", "neutral", "The main outlook faces east, catching the morning light."),
    ("VIEW", "mild_negative", "The outlook left something to be desired, mostly facing a neighbouring building."),
    ("VIEW", "strong_negative", "There was essentially nothing worth looking at from where we were."),
]

# ---- ACCESSIBILITY ----
FRAGMENTS += [
    ("ACCESSIBILITY", "strong_positive", "Every entrance had a ramp and the paths were wide enough for a wheelchair without any trouble."),
    ("ACCESSIBILITY", "mild_positive", "Ramps were available at most of the entrances we needed."),
    ("ACCESSIBILITY", "neutral", "An accessible entrance is available on the north side."),
    ("ACCESSIBILITY", "mild_negative", "A few narrow doorways made getting around slightly awkward."),
    ("ACCESSIBILITY", "strong_negative", "There was no accommodation at all for anyone with limited mobility, several areas were simply unreachable."),
]

# ---- PARKING ----
FRAGMENTS += [
    ("PARKING", "strong_positive", "We never once struggled to find a spot, and it didn't cost us anything extra."),
    ("PARKING", "mild_positive", "Finding somewhere to leave the car wasn't difficult."),
    ("PARKING", "neutral", "Paid parking is available a short distance away."),
    ("PARKING", "mild_negative", "Finding parking took longer than we would have liked."),
    ("PARKING", "strong_negative", "Parking turned into a genuine ordeal, we lost almost an hour just trying to find somewhere legal to leave the car."),
]

# ---- SAFETY ----
FRAGMENTS += [
    ("SAFETY", "strong_positive", "Not once did we feel uneasy, even walking back well after dark."),
    ("SAFETY", "mild_positive", "The surroundings felt secure enough for an evening stroll."),
    ("SAFETY", "neutral", "CCTV coverage is present throughout the surrounding streets."),
    ("SAFETY", "mild_negative", "A couple of areas nearby felt a little uneasy after dark."),
    ("SAFETY", "strong_negative", "There was a real sense of unease walking around after sunset."),
]

# ---- CLEANLINESS ----
FRAGMENTS += [
    ("CLEANLINESS", "strong_positive", "Every surface gleamed, it was clear a great deal of care went into keeping things spotless."),
    ("CLEANLINESS", "mild_positive", "Things were kept tidy and presentable throughout."),
    ("CLEANLINESS", "neutral", "Upkeep is handled on a fixed weekly schedule."),
    ("CLEANLINESS", "mild_negative", "A few corners could have used more attention when it came to tidiness."),
    ("CLEANLINESS", "strong_negative", "Cleanliness fell well short of what we expected, several areas looked neglected."),
]

# ---- ROOM_QUALITY ----
FRAGMENTS += [
    ("ROOM_QUALITY", "strong_positive", "The room exceeded what we expected for the price, spacious and beautifully finished."),
    ("ROOM_QUALITY", "mild_positive", "The room was perfectly adequate, comfortable enough for what we needed."),
    ("ROOM_QUALITY", "neutral", "Rooms are furnished with a work desk and a seating area."),
    ("ROOM_QUALITY", "mild_negative", "The room's furnishings looked like they hadn't been updated in some time."),
    ("ROOM_QUALITY", "strong_negative", "The room was in poor shape, stained carpet and a bed that dipped noticeably in the middle."),
]

# ---- NOISE_LEVEL ----
FRAGMENTS += [
    ("NOISE_LEVEL", "strong_positive", "It stayed remarkably peaceful throughout, a genuine surprise given the location."),
    ("NOISE_LEVEL", "mild_positive", "Noise levels were manageable, nothing that got in the way of conversation."),
    ("NOISE_LEVEL", "neutral", "Sound insulation varies depending on which side faces the street."),
    ("NOISE_LEVEL", "mild_negative", "Sound carried more than expected whenever it got busy."),
    ("NOISE_LEVEL", "strong_negative", "The noise levels were genuinely disruptive, impossible to hold a conversation without raising your voice."),
]

# ---- PRESERVATION_STATE ----
FRAGMENTS += [
    ("PRESERVATION_STATE", "strong_positive", "The restoration work has been done with real care, you can tell how much effort went into keeping it authentic."),
    ("PRESERVATION_STATE", "mild_positive", "The structure has held up reasonably well considering its age."),
    ("PRESERVATION_STATE", "neutral", "Restoration work was last completed several decades ago."),
    ("PRESERVATION_STATE", "mild_negative", "Weathering was visible on several of the outer walls."),
    ("PRESERVATION_STATE", "strong_negative", "Large sections looked abandoned and crumbling, which felt like a real shame given the history."),
]

# ---- FACILITIES_CONDITION ----
FRAGMENTS += [
    ("FACILITIES_CONDITION", "strong_positive", "Every facility we used was in excellent working order, clearly well looked after."),
    ("FACILITIES_CONDITION", "mild_positive", "The facilities on offer were in reasonable working condition."),
    ("FACILITIES_CONDITION", "neutral", "Facilities are inspected on a routine maintenance schedule."),
    ("FACILITIES_CONDITION", "mild_negative", "Some of the equipment on offer looked past its best."),
    ("FACILITIES_CONDITION", "strong_negative", "Multiple facilities were simply unusable when we visited, which was disappointing."),
]

# ---- TEMPERATURE_CONTROL ----
FRAGMENTS += [
    ("TEMPERATURE_CONTROL", "strong_positive", "The climate control in the room worked flawlessly the entire time we were there."),
    ("TEMPERATURE_CONTROL", "mild_positive", "Keeping the room at a comfortable temperature was never an issue."),
    ("TEMPERATURE_CONTROL", "neutral", "Each room is fitted with its own thermostat."),
    ("TEMPERATURE_CONTROL", "mild_negative", "The room ran a little warmer than we would have liked most nights."),
    ("TEMPERATURE_CONTROL", "strong_negative", "The heating system was unreliable, we spent much of the stay too cold to relax."),
]

# ---- STAFF_QUALITY ----
FRAGMENTS += [
    ("STAFF_QUALITY", "strong_positive", "Every single interaction with the team left a good impression, genuinely attentive and kind."),
    ("STAFF_QUALITY", "mild_positive", "The people working there were pleasant and easy to deal with."),
    ("STAFF_QUALITY", "neutral", "Staff wear identifiable uniforms during working hours."),
    ("STAFF_QUALITY", "mild_negative", "Not every interaction with the team felt particularly warm."),
    ("STAFF_QUALITY", "strong_negative", "Several interactions with staff were unpleasant, curt responses and little willingness to help."),
]

# ---- SERVICE_EFFICIENCY ----
FRAGMENTS += [
    ("SERVICE_EFFICIENCY", "strong_positive", "Requests were handled almost before we finished asking, genuinely impressive turnaround."),
    ("SERVICE_EFFICIENCY", "mild_positive", "Things generally moved along at a reasonable pace."),
    ("SERVICE_EFFICIENCY", "neutral", "Service requests are logged and handled in the order received."),
    ("SERVICE_EFFICIENCY", "mild_negative", "There were a few delays getting things sorted that felt avoidable."),
    ("SERVICE_EFFICIENCY", "strong_negative", "Everything took far longer than it should have, repeated requests before anything happened."),
]

# ---- CHECK_IN_EXPERIENCE ----
FRAGMENTS += [
    ("CHECK_IN_EXPERIENCE", "strong_positive", "The whole arrival process took barely any time at all."),
    ("CHECK_IN_EXPERIENCE", "mild_positive", "Getting checked in was a fairly painless process."),
    ("CHECK_IN_EXPERIENCE", "neutral", "Late check-in can be arranged in advance by request."),
    ("CHECK_IN_EXPERIENCE", "mild_negative", "The check-in process dragged on longer than it needed to."),
    ("CHECK_IN_EXPERIENCE", "strong_negative", "Checking in was chaotic, nobody seemed to know what was going on and we waited far too long."),
]

# ---- COMMUNICATION ----
FRAGMENTS += [
    ("COMMUNICATION", "strong_positive", "Every message we sent got a fast, helpful reply, made the whole planning process easy."),
    ("COMMUNICATION", "mild_positive", "Getting a response when we needed one wasn't difficult."),
    ("COMMUNICATION", "neutral", "A dedicated contact number is provided for enquiries."),
    ("COMMUNICATION", "mild_negative", "A couple of our questions took a while to get answered."),
    ("COMMUNICATION", "strong_negative", "Reaching anyone was a struggle, messages went unanswered for days at a time."),
]

# ---- FOOD_QUALITY ----
FRAGMENTS += [
    ("FOOD_QUALITY", "strong_positive", "Every dish that came out was cooked with real skill, nothing felt like an afterthought."),
    ("FOOD_QUALITY", "mild_positive", "The food was solid, nothing to complain about."),
    ("FOOD_QUALITY", "neutral", "Dishes are prepared fresh to order."),
    ("FOOD_QUALITY", "mild_negative", "A couple of dishes came out less flavourful than expected."),
    ("FOOD_QUALITY", "strong_negative", "The food was genuinely poor, undercooked in places and lacking any real seasoning."),
]

# ---- BREAKFAST_QUALITY ----
FRAGMENTS += [
    ("BREAKFAST_QUALITY", "strong_positive", "Breakfast alone was worth getting up early for, fresh pastries and a genuinely impressive spread."),
    ("BREAKFAST_QUALITY", "mild_positive", "Breakfast covered the basics well enough."),
    ("BREAKFAST_QUALITY", "neutral", "A continental breakfast is included with every booking."),
    ("BREAKFAST_QUALITY", "mild_negative", "Breakfast options were fairly repetitive after the first couple of days."),
    ("BREAKFAST_QUALITY", "strong_negative", "Breakfast was a letdown, stale options and nothing replenished when it ran out."),
]

# ---- MENU_VARIETY ----
FRAGMENTS += [
    ("MENU_VARIETY", "strong_positive", "The menu offered something genuinely different at every course, clearly a lot of thought went into it."),
    ("MENU_VARIETY", "mild_positive", "A handful of dishes stood out as genuinely creative choices."),
    ("MENU_VARIETY", "neutral", "The menu is printed fresh each week."),
    ("MENU_VARIETY", "mild_negative", "Options felt fairly repetitive across the menu."),
    ("MENU_VARIETY", "strong_negative", "The menu offered almost nothing beyond the most basic standards."),
]

# ---- INFORMATIONAL_VALUE ----
FRAGMENTS += [
    ("INFORMATIONAL_VALUE", "strong_positive", "The information provided throughout gave real depth to the visit, we left knowing far more than we expected."),
    ("INFORMATIONAL_VALUE", "mild_positive", "The context on offer made it easy to appreciate what was in front of us."),
    ("INFORMATIONAL_VALUE", "neutral", "Audio guides are available for an additional fee."),
    ("INFORMATIONAL_VALUE", "mild_negative", "More context would have helped make sense of some of the exhibits."),
    ("INFORMATIONAL_VALUE", "strong_negative", "Almost nothing was explained on site, we had no real sense of what we were looking at."),
]

# ---- WIFI_CONNECTIVITY ----
FRAGMENTS += [
    ("WIFI_CONNECTIVITY", "strong_positive", "The internet connection was fast and never dropped once during our visit."),
    ("WIFI_CONNECTIVITY", "mild_positive", "Getting online wasn't a problem when we needed to."),
    ("WIFI_CONNECTIVITY", "neutral", "A network password is provided at the time of arrival."),
    ("WIFI_CONNECTIVITY", "mild_negative", "The internet connection struggled at busier times."),
    ("WIFI_CONNECTIVITY", "strong_negative", "Getting online was practically impossible, the connection dropped constantly."),
]

# ---- AMENITIES_VARIETY ----
FRAGMENTS += [
    ("AMENITIES_VARIETY", "strong_positive", "The range of extras on offer was genuinely impressive, more than we expected for the price."),
    ("AMENITIES_VARIETY", "mild_positive", "There was a decent range of extras to make use of."),
    ("AMENITIES_VARIETY", "neutral", "A fitness room is available to guests at no extra charge."),
    ("AMENITIES_VARIETY", "mild_negative", "The extras on offer felt fairly basic."),
    ("AMENITIES_VARIETY", "strong_negative", "Almost none of the advertised extras were actually usable during our visit."),
]

# ---- VALUE_FOR_MONEY ----
FRAGMENTS += [
    ("VALUE_FOR_MONEY", "strong_positive", "What we paid felt like a genuine bargain for everything included."),
    ("VALUE_FOR_MONEY", "mild_positive", "The price felt fair for what we received."),
    ("VALUE_FOR_MONEY", "neutral", "Pricing is comparable to similar options in the area."),
    ("VALUE_FOR_MONEY", "mild_negative", "The price felt a little steep given what was actually included."),
    ("VALUE_FOR_MONEY", "strong_negative", "What we paid did not come close to matching what we actually got."),
]

# ---- HIDDEN_COSTS ----
FRAGMENTS += [
    ("HIDDEN_COSTS", "mild_positive", "Every cost was laid out clearly from the start, no surprises at the end."),
    ("HIDDEN_COSTS", "neutral", "A service charge is applied automatically to the final bill."),
    ("HIDDEN_COSTS", "mild_negative", "One or two minor fees came as a surprise on the final bill."),
    ("HIDDEN_COSTS", "strong_negative", "Multiple charges appeared that were never disclosed upfront, which felt deceptive."),
]

# ---- BOOKING_PROCESS ----
FRAGMENTS += [
    ("BOOKING_PROCESS", "strong_positive", "Reserving a spot took less than a minute and everything was confirmed instantly."),
    ("BOOKING_PROCESS", "mild_positive", "Securing a reservation only took a couple of steps."),
    ("BOOKING_PROCESS", "neutral", "Bookings can be modified free of charge up to 48 hours in advance."),
    ("BOOKING_PROCESS", "mild_negative", "The booking system was a little confusing to navigate at first."),
    ("BOOKING_PROCESS", "strong_negative", "The booking process failed repeatedly, we had to try several times before it actually went through."),
]

# ---- OVERALL_EXPERIENCE ----
FRAGMENTS += [
    ("OVERALL_EXPERIENCE", "strong_positive", "This ended up being one of the highlights of the whole trip, everything just worked."),
    ("OVERALL_EXPERIENCE", "mild_positive", "On the whole it was a solid, enjoyable time."),
    ("OVERALL_EXPERIENCE", "neutral", "This was our first time visiting this particular spot."),
    ("OVERALL_EXPERIENCE", "mild_negative", "On the whole it fell a little short of what we were hoping for."),
    ("OVERALL_EXPERIENCE", "strong_negative", "This was a genuinely frustrating experience from start to finish."),
]

# ---- ATMOSPHERE ----
FRAGMENTS += [
    ("ATMOSPHERE", "strong_positive", "The atmosphere hit exactly the right note, warm without trying too hard."),
    ("ATMOSPHERE", "mild_positive", "The mood throughout felt unforced and easy to settle into."),
    ("ATMOSPHERE", "neutral", "Lighting is kept low during the evening hours."),
    ("ATMOSPHERE", "mild_negative", "The atmosphere felt a bit flat compared to what we expected."),
    ("ATMOSPHERE", "strong_negative", "There was a distinctly cold, unwelcoming feel to the whole place."),
]

# ---- CROWDING ----
FRAGMENTS += [
    ("CROWDING", "strong_positive", "We had plenty of space to ourselves the whole time, never once felt crowded."),
    ("CROWDING", "mild_positive", "It never got uncomfortably busy during our visit."),
    ("CROWDING", "neutral", "Visitor numbers are typically higher on weekends."),
    ("CROWDING", "mild_negative", "Things got a bit tight once more people arrived."),
    ("CROWDING", "strong_negative", "The sheer number of people made it hard to enjoy properly."),
]

# ---- ENTERTAINMENT_OPTIONS ----
FRAGMENTS += [
    ("ENTERTAINMENT_OPTIONS", "strong_positive", "There was genuinely engaging entertainment throughout, far more than we expected."),
    ("ENTERTAINMENT_OPTIONS", "mild_positive", "There was a reasonable amount to keep us entertained."),
    ("ENTERTAINMENT_OPTIONS", "neutral", "Scheduled activities run on weekday afternoons."),
    ("ENTERTAINMENT_OPTIONS", "mild_negative", "There wasn't a great deal to keep us occupied beyond the basics."),
    ("ENTERTAINMENT_OPTIONS", "strong_negative", "Despite the promises, there was essentially nothing in the way of entertainment on offer."),
]

# ---- FAMILY_FRIENDLINESS ----
FRAGMENTS += [
    ("FAMILY_FRIENDLINESS", "strong_positive", "This was fantastic with children in tow, genuinely thought through for families."),
    ("FAMILY_FRIENDLINESS", "mild_positive", "It worked out fine for our family, no major complaints."),
    ("FAMILY_FRIENDLINESS", "neutral", "A play area is available for younger visitors."),
    ("FAMILY_FRIENDLINESS", "mild_negative", "This wasn't particularly geared toward children."),
    ("FAMILY_FRIENDLINESS", "strong_negative", "Bringing children along was clearly not something they'd planned for, nothing suitable at all."),
]

# ---- DECOR_AND_DESIGN ----
FRAGMENTS += [
    ("DECOR_AND_DESIGN", "strong_positive", "The design choices throughout were genuinely striking, every detail felt deliberate."),
    ("DECOR_AND_DESIGN", "mild_positive", "Everything about the visual presentation felt well considered."),
    ("DECOR_AND_DESIGN", "neutral", "The colour scheme follows a consistent theme throughout."),
    ("DECOR_AND_DESIGN", "mild_negative", "The design felt a little tired in places."),
    ("DECOR_AND_DESIGN", "strong_negative", "The overall look was mismatched and poorly maintained, dragging down the whole experience."),
]
