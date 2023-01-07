def extract_with_css(response, query):
    string = response.css(query).extract_first()
    if string is not None:
        return string.strip()


thunderpick_country = {
                4: "Afghanistan",
                248: "Aland Islands",
                8: "Albania",
                12: "Algeria",
                16: "American Samoa",
                20: "Andorra",
                24: "Angola",
                660: "Anguilla",
                10: "Antarctica",
                28: "Antigua And Barbuda",
                32: "Argentina",
                51: "Armenia",
                533: "Aruba",
                36: "Australia",
                40: "Austria",
                31: "Azerbaijan",
                44: "Bahamas",
                48: "Bahrain",
                50: "Bangladesh",
                52: "Barbados",
                112: "Belarus",
                56: "Belgium",
                84: "Belize",
                204: "Benin",
                60: "Bermuda",
                64: "Bhutan",
                68: "Bolivia",
                70: "Bosnia And Herzegovina",
                72: "Botswana",
                74: "Bouvet Island",
                76: "Brazil",
                86: "British Indian Ocean Territory",
                96: "Brunei Darussalam",
                100: "Bulgaria",
                854: "Burkina Faso",
                108: "Burundi",
                132: "Cabo Verde",
                116: "Cambodia",
                120: "Cameroon",
                124: "Canada",
                136: "Cayman Islands",
                140: "Central African Republic",
                148: "Chad",
                152: "Chile",
                156: "China",
                162: "Christmas Island",
                166: "Cocos Islands",
                170: "Colombia",
                174: "Comoros",
                178: "Congo",
                180: "Congo Democratic Republic Of The",
                184: "Cook Islands",
                188: "Costa Rica",
                191: "Croatia",
                192: "Cuba",
                531: "Curacao",
                196: "Cyprus",
                203: "Czech Republic",
                384: "Cote D Ivoire",
                208: "Denmark",
                262: "Djibouti",
                212: "Dominica",
                214: "Dominican Republic",
                218: "Ecuador",
                818: "Egypt",
                222: "ElSalvador",
                226: "Equatorial Guinea",
                82601: "England",
                232: "Eritrea",
                233: "Estonia",
                748: "Eswatini",
                231: "Ethiopia",
                238: "Falkland Islands",
                234: "Faroe Islands",
                242: "Fiji",
                246: "Finland",
                250: "France",
                254: "French Guiana",
                258: "French Polynesia",
                260: "French Southern Territories",
                266: "Gabon",
                270: "Gambia",
                268: "Georgia",
                276: "Germany",
                288: "Ghana",
                292: "Gibraltar",
                300: "Greece",
                304: "Greenland",
                308: "Grenada",
                312: "Guadeloupe",
                316: "Guam",
                320: "Guatemala",
                831: "Guernsey",
                324: "Guinea",
                624: "Guinea Bissau",
                328: "Guyana",
                332: "Haiti",
                334: "Heard Island And Mc Donald Islands",
                336: "Holy See",
                340: "Honduras",
                344: "Hong Kong",
                348: "Hungary",
                352: "Iceland",
                356: "India",
                360: "Indonesia",
                364: "Iran",
                368: "Iraq",
                372: "Ireland",
                833: "Isle Of Man",
                376: "Israel",
                380: "Italy",
                388: "Jamaica",
                392: "Japan",
                832: "Jersey",
                400: "Jordan",
                398: "Kazakhstan",
                404: "Kenya",
                296: "Kiribati",
                408: "Korea Democratic People Republic Of",
                410: "Korea Republic Of",
                414: "Kuwait",
                417: "Kyrgyzstan",
                418: "Lao Peoples Democratic Republic",
                428: "Latvia",
                422: "Lebanon",
                426: "Lesotho",
                430: "Liberia",
                434: "Libya",
                438: "Liechtenstein",
                440: "Lithuania",
                442: "Luxembourg",
                446: "Macao",
                807: "Macedonia",
                450: "Madagascar",
                454: "Malawi",
                458: "Malaysia",
                462: "Maldives",
                466: "Mali",
                470: "Malta",
                584: "Marshall Islands",
                474: "Martinique",
                478: "Mauritania",
                480: "Mauritius",
                175: "Mayotte",
                484: "Mexico",
                583: "Micronesia Federated States Of",
                498: "Moldova Republic Of",
                492: "Monaco",
                496: "Mongolia",
                499: "Montenegro",
                500: "Montserrat",
                504: "Morocco",
                508: "Mozambique",
                104: "Myanmar",
                516: "Namibia",
                520: "Nauru",
                524: "Nepal",
                528: "Netherlands",
                540: "New Caledonia",
                554: "New Zealand",
                558: "Nicaragua",
                562: "Niger",
                566: "Nigeria",
                570: "Niue",
                574: "Norfolk Island",
                82602: "Northern Ireland",
                580: "Northern Mariana Islands",
                578: "Norway",
                512: "Oman",
                586: "Pakistan",
                585: "Palau",
                275: "Palestine State Of",
                591: "Panama",
                598: "Papua New Guinea",
                600: "Paraguay",
                604: "Peru",
                608: "Philippines",
                612: "Pitcairn",
                616: "Poland",
                620: "Portugal",
                630: "Puerto Rico",
                634: "Qatar",
                638: "Reunion",
                642: "Romania",
                643: "Russian Federation",
                646: "Rwanda",
                652: "Saint Barthelemy",
                654: "Saint Helena Ascension And Tristan Da Cunha",
                659: "Saint Kitts And Nevis",
                662: "Saint Lucia",
                663: "Saint Martin French Part",
                666: "Saint Pierre And Miquelon",
                670: "Saint Vincent And The Grenadines",
                882: "Samoa",
                674: "San Marino",
                678: "Sao Tome And Principe",
                682: "Saudi Arabia",
                82603: "Scotland",
                686: "Senegal",
                688: "Serbia",
                690: "Seychelles",
                694: "SierraLeone",
                702: "Singapore",
                534: "Sint Maarten",
                703: "Slovakia",
                705: "Slovenia",
                90: "Solomon Islands",
                706: "Somalia",
                710: "South Africa",
                239: "South Georgia And The South Sandwich Islands",
                728: "South Sudan",
                724: "Spain",
                144: "Sri Lanka",
                729: "Sudan",
                740: "Suriname",
                744: "Svalbard And Jan Mayen",
                752: "Sweden",
                756: "Switzerland",
                760: "Syrian Arab Republic",
                158: "Taiwan Province Of China",
                762: "Tajikistan",
                834: "Tanzania United Republic Of",
                764: "Thailand",
                626: "Timor Leste",
                768: "Togo",
                772: "Tokelau",
                776: "Tonga",
                780: "Trinidad And Tobago",
                788: "Tunisia",
                792: "Turkey",
                795: "Turkmenistan",
                796: "Turks And Caicos Islands",
                798: "Tuvalu",
                800: "Uganda",
                804: "Ukraine",
                784: "United Arab Emirates",
                826: "Great Britain",
                581: "United States Minor Outlying Islands",
                840: "United States Of America",
                858: "Uruguay",
                860: "Uzbekistan",
                548: "Vanuatu",
                862: "Venezuela Bolivarian Republic Of",
                704: "VietNam",
                92: "Virgin Islands British",
                850: "Virgin Islands US",
                82604: "Wales",
                876: "Wallis And Futuna",
                732: "Western Sahara",
                887: "Yemen",
                894: "Zambia",
                716: "Zimbabwe"
}




#{
   #"Afghanistan":"af",
   #"AlandIslands":"ax",
   #"Albania":"al",
   #"Algeria":"dz",
   #"AmericanSamoa":"as",
   #"Andorra":"ad",
   #"Angola":"ao",
   #"Anguilla":"ai",
   #"Antarctica":"aq",
   #"AntiguaAndBarbuda":"ag",
   #"Argentina":"ar",
   #"Armenia":"am",
   #"Aruba":"aw",
   #"Australia":"au",
   #"Austria":"at",
   #"Azerbaijan":"az",
   #"Bahamas":"bs",
   #"Bahrain":"bh",
   #"Bangladesh":"bd",
   #"Barbados":"bb",
   #"Belarus":"by",
   #"Belgium":"be",
   #"Belize":"bz",
   #"Benin":"bj",
   #"Bermuda":"bm",
   #"Bhutan":"bt",
   #"Bolivia":"bo",
   #"BosniaAndHerzegovina":"ba",
   #"Botswana":"bw",
   #"BouvetIsland":"bv",
   #"Brazil":"br",
   #"BritishIndianOceanTerritory":"io",
   #"BruneiDarussalam":"bn",
   #"Bulgaria":"bg",
   #"BurkinaFaso":"bf",
   #"Burundi":"bi",
   #"CaboVerde":"cv",
   #"Cambodia":"kh",
   #"Cameroon":"cm",
   #"Canada":"ca",
   #"CaymanIslands":"ky",
   #"CentralAfricanRepublic":"cf",
   #"Chad":"td",
   #"Chile":"cl",
   #"China":"cn",
   #"ChristmasIsland":"cx",
   #"CocosIslands":"cc",
   #"Colombia":"co",
   #"Comoros":"km",
   #"Congo":"cg",
   #"CongoDemocraticRepublicOfThe":"cd",
   #"CookIslands":"ck",
   #"CostaRica":"cr",
   #"Croatia":"hr",
   #"Cuba":"cu",
   #"Curacao":"cw",
   #"Cyprus":"cy",
   #"CzechRepublic":"cz",
   #"CoteDIvoire":"ci",
   #"Denmark":"dk",
   #"Djibouti":"dj",
   #"Dominica":"dm",
   #"DominicanRepublic":"do",
   #"Ecuador":"ec",
   #"England":"eng",
   #"Egypt":"eg",
   #"ElSalvador":"sv",
   #"EquatorialGuinea":"gq",
   #"Eritrea":"er",
   #"Estonia":"ee",
   #"Eswatini":"sz",
   #"Ethiopia":"et",
   #"FalklandIslands":"fk",
   #"FaroeIslands":"fo",
   #"Fiji":"fj",
   #"Finland":"fi",
   #"France":"fr",
   #"FrenchGuiana":"gf",
   #"FrenchPolynesia":"pf",
   #"FrenchSouthernTerritories":"tf",
   #"Gabon":"ga",
   #"Gambia":"gm",
   #"Georgia":"ge",
   #"Germany":"de",
   #"Ghana":"gh",
   #"Gibraltar":"gi",
   #"Greece":"gr",
   #"Greenland":"gl",
   #"Grenada":"gd",
   #"Guadeloupe":"gp",
   #"Guam":"gu",
   #"Guatemala":"gt",
   #"Guernsey":"gg",
   #"Guinea":"gn",
   #"GuineaBissau":"gw",
   #"Guyana":"gy",
   #"Haiti":"ht",
   #"HeardIslandAndMcDonaldIslands":"hm",
   #"HolySee":"va",
   #"Honduras":"hn",
   #"HongKong":"hk",
   #"Hungary":"hu",
   #"Iceland":"is",
   #"India":"in",
   #"Indonesia":"id",
   #"Iran":"ir",
   #"Iraq":"iq",
   #"Ireland":"ie",
   #"IsleOfMan":"im",
   #"Israel":"il",
   #"Italy":"it",
   #"Jamaica":"jm",
   #"Japan":"jp",
   #"Jersey":"je",
   #"Jordan":"jo",
   #"Kazakhstan":"kz",
   #"Kenya":"ke",
   #"Kiribati":"ki",
   #"KoreaDemocraticPeopleRepublicOf":"kp",
   #"KoreaRepublicOf":"kr",
   #"Kuwait":"kw",
   #"Kyrgyzstan":"kg",
   #"LaoPeoplesDemocraticRepublic":"la",
   #"Latvia":"lv",
   #"Lebanon":"lb",
   #"Lesotho":"ls",
   #"Liberia":"lr",
   #"Libya":"ly",
   #"Liechtenstein":"li",
   #"Lithuania":"lt",
   #"Luxembourg":"lu",
   #"Macao":"mo",
   #"Macedonia":"mk",
   #"Madagascar":"mg",
   #"Malawi":"mw",
   #"Malaysia":"my",
   #"Maldives":"mv",
   #"Mali":"ml",
   #"Malta":"mt",
   #"MarshallIslands":"mh",
   #"Martinique":"mq",
   #"Mauritania":"mr",
   #"Mauritius":"mu",
   #"Mayotte":"yt",
   #"Mexico":"mx",
   #"MicronesiaFederatedStatesOf":"fm",
   #"MoldovaRepublicOf":"md",
   #"Monaco":"mc",
   #"Mongolia":"mn",
   #"Montenegro":"me",
   #"Montserrat":"ms",
   #"Morocco":"ma",
   #"Mozambique":"mz",
   #"Myanmar":"mm",
   #"Namibia":"na",
   #"Nauru":"nr",
   #"Nepal":"np",
   #"Netherlands":"nl",
   #"NewCaledonia":"nc",
   #"NewZealand":"nz",
   #"Nicaragua":"ni",
   #"Niger":"ne",
   #"Nigeria":"ng",
   #"Niue":"nu",
   #"NorfolkIsland":"nf",
   #"NorthernIreland":"nir",
   #"NorthernMarianaIslands":"mp",
   #"Norway":"no",
   #"Oman":"om",
   #"Pakistan":"pk",
   #"Palau":"pw",
   #"PalestineStateOf":"ps",
   #"Panama":"pa",
   #"PapuaNewGuinea":"pg",
   #"Paraguay":"py",
   #"Peru":"pe",
   #"Philippines":"ph",
   #"Pitcairn":"pn",
   #"Poland":"pl",
   #"Portugal":"pt",
   #"PuertoRico":"pr",
   #"Qatar":"qa",
   #"Reunion":"re",
   #"Romania":"ro",
   #"RussianFederation":"ru",
   #"Rwanda":"rw",
   #"SaintBarthelemy":"bl",
   #"SaintHelenaAscensionAndTristanDaCunha":"sh",
   #"SaintKittsAndNevis":"kn",
   #"SaintLucia":"lc",
   #"SaintMartinFrenchPart":"mf",
   #"SaintPierreAndMiquelon":"pm",
   #"SaintVincentAndTheGrenadines":"vc",
   #"Samoa":"ws",
   #"SanMarino":"sm",
   #"SaoTomeAndPrincipe":"st",
   #"SaudiArabia":"sa",
   #"Scotland":"sct",
   #"Senegal":"sn",
   #"Serbia":"rs",
   #"Seychelles":"sc",
   #"SierraLeone":"sl",
   #"Singapore":"sg",
   #"SintMaarten":"sx",
   #"Slovakia":"sk",
   #"Slovenia":"si",
   #"SolomonIslands":"sb",
   #"Somalia":"so",
   #"SouthAfrica":"za",
   #"SouthGeorgiaAndTheSouthSandwichIslands":"gs",
   #"SouthSudan":"ss",
   #"Spain":"es",
   #"SriLanka":"lk",
   #"Sudan":"sd",
   #"Suriname":"sr",
   #"SvalbardAndJanMayen":"sj",
   #"Sweden":"se",
   #"Switzerland":"ch",
   #"SyrianArabRepublic":"sy",
   #"TaiwanProvinceOfChina":"tw",
   #"Tajikistan":"tj",
   #"TanzaniaUnitedRepublicOf":"tz",
   #"Thailand":"th",
   #"TimorLeste":"tl",
   #"Togo":"tg",
   #"Tokelau":"tk",
   #"Tonga":"to",
   #"TrinidadAndTobago":"tt",
   #"Tunisia":"tn",
   #"Turkey":"tr",
   #"Turkmenistan":"tm",
   #"TurksAndCaicosIslands":"tc",
   #"Tuvalu":"tv",
   #"Uganda":"ug",
   #"Ukraine":"ua",
   #"UnitedArabEmirates":"ae",
   #"GreatBritain":"gb",
   #"UnitedStatesMinorOutlyingIslands":"um",
   #"UnitedStatesOfAmerica":"us",
   #"Uruguay":"uy",
   #"Uzbekistan":"uz",
   #"Vanuatu":"vu",
   #"VenezuelaBolivarianRepublicOf":"ve",
   #"VietNam":"vn",
   #"VirginIslandsBritish":"vg",
   #"VirginIslandsUS":"vi",
   #"WallisAndFutuna":"wf",
   #"Wales":"wls",
   #"WesternSahara":"eh",
   #"Yemen":"ye",
   #"Zambia":"zm",
   #"Zimbabwe":"zw"}