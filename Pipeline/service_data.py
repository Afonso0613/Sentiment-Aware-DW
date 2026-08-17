"""
The 80 synthetic services used by the Chapter 7 prototype (second
implemented instance, superseding the original 40-service dataset).

Distribution: 40 accommodation, 24 restaurant/bar, 16 tourist site,
maintaining the same 5:3:2 category ratio as the first instance.
Spread across 22 municipalities covering all 7 Portuguese regions,
including the Autonomous Region of the Azores, which had no
representation in the first instance.

SCD2_CHANGES marks three services (SVC_002, SVC_015, SVC_033) that
carry a genuine attribute change partway through the review period,
each represented as an original/changed attribute pair with an
explicit change_date. This is what allows UC7 (sentiment change
following a service change) to be empirically demonstrated rather
than architecturally supported but untested, as it was in the first
instance.

Fields remain RAW / pre-standardisation, matching RAW_REVIEW's service
block, consistent with the first instance's design.
"""

# (service_source_id, service_name, service_type, municipality_name,
#  star_rating, price_tier_raw, overall_ranking, photo_count)
SERVICES = [
    # ---- Accommodation (40) ----
    ("SVC_001", "Hotel Avenida Liberdade", "Hotel", "Lisboa", 4, "premium", 12, 184),
    ("SVC_002", "Lisbon Riverside Suites", "Boutique Hotel", "Lisboa", 5, "luxury", 4, 312),
    ("SVC_003", "Alfama Guesthouse", "Guesthouse", "Lisboa", 3, "mid-range", 87, 56),
    ("SVC_004", "Hotel Douro Ribeira", "Hotel", "Porto", 4, "premium", 18, 201),
    ("SVC_005", "Porto Old Town Hostel", "Hostel", "Porto", 2, "budget", 145, 39),
    ("SVC_006", "Vila Nova Boutique Stay", "Boutique Hotel", "Porto", 4, "premium", 33, 167),
    ("SVC_007", "Braga Cathedral Inn", "Inn", "Braga", 3, "mid-range", 56, 71),
    ("SVC_008", "Hotel Bom Jesus", "Hotel", "Braga", 4, "premium", 21, 142),
    ("SVC_009", "Sintra Palace View Hotel", "Hotel", "Sintra", 5, "luxury", 6, 298),
    ("SVC_010", "Pena Hill Guesthouse", "Guesthouse", "Sintra", 3, "mid-range", 64, 48),
    ("SVC_011", "Cascais Marina Resort", "Resort", "Cascais", 5, "luxury", 9, 276),
    ("SVC_012", "Hotel Costa do Estoril", "Hotel", "Cascais", 4, "premium", 27, 159),
    ("SVC_013", "Faro Old Town Hotel", "Hotel", "Faro", 3, "mid-range", 71, 63),
    ("SVC_014", "Ria Formosa Lodge", "Guesthouse", "Faro", 4, "premium", 38, 121),
    ("SVC_015", "Albufeira Beach Resort", "Resort", "Albufeira", 5, "luxury", 11, 341),
    ("SVC_016", "Hotel Praia Dourada", "Hotel", "Albufeira", 4, "premium", 29, 188),
    ("SVC_017", "Hostel Coimbra Centro", "Hostel", "Coimbra", 2, "budget", 132, 44),
    ("SVC_018", "Hotel Mondego", "Hotel", "Coimbra", 3, "mid-range", 68, 79),
    ("SVC_019", "Évora Heritage Hotel", "Hotel", "Évora", 4, "premium", 24, 153),
    ("SVC_020", "Funchal Bay Hotel", "Hotel", "Funchal", 4, "premium", 17, 211),
    ("SVC_041", "Setúbal Bay Hotel", "Hotel", "Setúbal", 3, "mid-range", 74, 68),
    ("SVC_042", "Guimarães Historic Inn", "Inn", "Guimarães", 4, "premium", 31, 132),
    ("SVC_043", "Douro Valley Vila Real Lodge", "Guesthouse", "Vila Real", 3, "mid-range", 79, 51),
    ("SVC_044", "Aveiro Canal Hotel", "Hotel", "Aveiro", 4, "premium", 26, 147),
    ("SVC_045", "Viseu City Hostel", "Hostel", "Viseu", 2, "budget", 149, 33),
    ("SVC_046", "Leiria Castle View Hotel", "Hotel", "Leiria", 3, "mid-range", 82, 58),
    ("SVC_047", "Elvas Fortress Guesthouse", "Guesthouse", "Elvas", 3, "mid-range", 91, 42),
    ("SVC_048", "Beja Plains Hotel", "Hotel", "Beja", 3, "mid-range", 96, 47),
    ("SVC_049", "Lagos Cliffside Resort", "Resort", "Lagos", 5, "luxury", 8, 289),
    ("SVC_050", "Tavira Riverside Inn", "Inn", "Tavira", 4, "premium", 44, 118),
    ("SVC_051", "Ponta Delgada Harbour Hotel", "Hotel", "Ponta Delgada", 4, "premium", 22, 156),
    ("SVC_052", "Azores Volcanic Lodge", "Guesthouse", "Ponta Delgada", 4, "premium", 35, 124),
    ("SVC_053", "Angra Heritage Hotel", "Hotel", "Angra do Heroísmo", 4, "premium", 28, 138),
    ("SVC_054", "Sintra Forest Boutique Hotel", "Boutique Hotel", "Sintra", 5, "luxury", 7, 267),
    ("SVC_055", "Cascais Cliffs Guesthouse", "Guesthouse", "Cascais", 3, "mid-range", 77, 61),
    ("SVC_056", "Porto Riverside Hostel", "Hostel", "Porto", 2, "budget", 141, 37),
    ("SVC_057", "Braga Business Hotel", "Hotel", "Braga", 3, "mid-range", 69, 66),
    ("SVC_058", "Faro Marina Resort", "Resort", "Faro", 5, "luxury", 13, 251),
    ("SVC_059", "Coimbra University Inn", "Inn", "Coimbra", 3, "mid-range", 88, 49),
    ("SVC_060", "Funchal Garden Hotel", "Hotel", "Funchal", 4, "premium", 19, 178),

    # ---- Restaurant/Bar (24) ----
    ("SVC_021", "Taberna do Chiado", "Restaurant", "Lisboa", None, "mid-range", 142, 92),
    ("SVC_022", "Bairro Alto Rooftop Bar", "Bar", "Lisboa", None, "premium", 88, 134),
    ("SVC_023", "Cervejaria Ribeira", "Restaurant", "Porto", None, "mid-range", 119, 87),
    ("SVC_024", "Porto Wine Lounge", "Bar", "Porto", None, "premium", 95, 108),
    ("SVC_025", "Restaurante Minho Antigo", "Restaurant", "Braga", None, "mid-range", 156, 61),
    ("SVC_026", "Quintal Sintra Bistro", "Restaurant", "Sintra", None, "mid-range", 134, 73),
    ("SVC_027", "Cascais Seafood House", "Restaurant", "Cascais", None, "premium", 102, 96),
    ("SVC_028", "Marisqueira do Algarve", "Restaurant", "Faro", None, "mid-range", 148, 68),
    ("SVC_029", "Albufeira Sunset Bar", "Bar", "Albufeira", None, "mid-range", 167, 84),
    ("SVC_030", "Tasca do Estudante", "Restaurant", "Coimbra", None, "budget", 189, 47),
    ("SVC_031", "Adega Alentejana", "Restaurant", "Évora", None, "mid-range", 121, 59),
    ("SVC_032", "Funchal Madeira Wine Bar", "Bar", "Funchal", None, "premium", 99, 113),
    ("SVC_061", "Setúbal Fish Market Grill", "Restaurant", "Setúbal", None, "mid-range", 128, 72),
    ("SVC_062", "Guimarães Founders Tavern", "Restaurant", "Guimarães", None, "mid-range", 137, 64),
    ("SVC_063", "Vila Real Vineyard Bar", "Bar", "Vila Real", None, "premium", 108, 91),
    ("SVC_064", "Aveiro Lagoon Restaurant", "Restaurant", "Aveiro", None, "mid-range", 145, 58),
    ("SVC_065", "Viseu Central Tasca", "Restaurant", "Viseu", None, "budget", 178, 41),
    ("SVC_066", "Leiria Castle Bistro", "Restaurant", "Leiria", None, "mid-range", 152, 55),
    ("SVC_067", "Elvas Fortress Cafe Bar", "Bar", "Elvas", None, "budget", 184, 38),
    ("SVC_068", "Beja Plains Grill House", "Restaurant", "Beja", None, "mid-range", 163, 52),
    ("SVC_069", "Lagos Sunset Seafood Bar", "Bar", "Lagos", None, "premium", 94, 121),
    ("SVC_070", "Tavira Riverside Restaurant", "Restaurant", "Tavira", None, "mid-range", 139, 67),
    ("SVC_071", "Ponta Delgada Ocean Grill", "Restaurant", "Ponta Delgada", None, "mid-range", 131, 76),
    ("SVC_072", "Angra Heritage Wine Bar", "Bar", "Angra do Heroísmo", None, "premium", 116, 89),

    # ---- Tourist Site (16) ----
    ("SVC_033", "Castelo de São Jorge", "Historical Monument", "Lisboa", None, None, 8, 421),
    ("SVC_034", "Livraria Lello", "Cultural Attraction", "Porto", None, None, 5, 389),
    ("SVC_035", "Santuário do Bom Jesus", "Religious Site", "Braga", None, None, 14, 267),
    ("SVC_036", "Palácio da Pena", "Historical Monument", "Sintra", None, None, 3, 512),
    ("SVC_037", "Ria Formosa Natural Park", "Nature Reserve", "Faro", None, None, 22, 178),
    ("SVC_038", "Mosteiro de Santa Cruz", "Religious Site", "Coimbra", None, None, 31, 142),
    ("SVC_039", "Templo Romano de Évora", "Historical Monument", "Évora", None, None, 19, 196),
    ("SVC_040", "Jardim Botânico da Madeira", "Nature Reserve", "Funchal", None, None, 16, 223),
    ("SVC_073", "Forte de Elvas", "Historical Monument", "Elvas", None, None, 41, 132),
    ("SVC_074", "Paço dos Duques de Guimarães", "Historical Monument", "Guimarães", None, None, 27, 168),
    ("SVC_075", "Museu de Aveiro", "Cultural Attraction", "Aveiro", None, None, 46, 108),
    ("SVC_076", "Sé de Viseu", "Religious Site", "Viseu", None, None, 53, 91),
    ("SVC_077", "Fortaleza de Lagos", "Historical Monument", "Lagos", None, None, 24, 187),
    ("SVC_078", "Ilha de Tavira Nature Reserve", "Nature Reserve", "Tavira", None, None, 37, 149),
    ("SVC_079", "Lagoa do Fogo", "Nature Reserve", "Ponta Delgada", None, None, 29, 174),
    ("SVC_080", "Sé Catedral de Angra do Heroísmo", "Religious Site", "Angra do Heroísmo", None, None, 44, 121),
]

# ---------------------------------------------------------------------
# SCD2 test data: three services carry a genuine attribute change at a
# fixed point during the review period, so UC7 can be demonstrated
# empirically. change_date splits each service's raw reviews: reviews
# captured before change_date use the ORIGINAL attributes below;
# reviews captured on or after change_date use the CHANGED attributes.
# This is applied deterministically in generate_raw_reviews.py, not
# left to the random generator, so the fixed seed's other output is
# undisturbed.
# ---------------------------------------------------------------------

SCD2_CHANGES = {
    "SVC_002": {
        # Lisbon Riverside Suites: renovation completed, official star
        # rating upgraded from 4 to 5.
        "change_date": "2024-06-01",
        "original": {"star_rating": 4, "price_tier_raw": "premium"},
        "changed":  {"star_rating": 5, "price_tier_raw": "luxury"},
    },
    "SVC_015": {
        # Albufeira Beach Resort: downgraded following a change in
        # management, official star rating reduced from 5 to 4.
        "change_date": "2023-09-01",
        "original": {"star_rating": 5, "price_tier_raw": "luxury"},
        "changed":  {"star_rating": 4, "price_tier_raw": "premium"},
    },
    "SVC_033": {
        # Castelo de São Jorge: price tier reclassified following a
        # change in ticketing structure (a tourist site attribute
        # change not involving star_rating, which does not apply to
        # this category).
        "change_date": "2024-01-15",
        "original": {"price_tier_raw": None},
        "changed":  {"price_tier_raw": "mid-range"},
    },
}
