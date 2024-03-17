"""Test filenames with human parsed correct results."""

from types import MappingProxyType

TEST_COMIC_FIELDS = {
    "series": "Long Series Name",
    "issue": "001",
    "year": "2000",
    "original_format": "TPB",
    "scan_info": "Releaser",
    "title": "Title",
    "ext": "cbz",
}
TEST_COMIC_FIELDS_VOL = {
    "series": "Long Series Name",
    "volume": "1",
    "issue": "001",
    "year": "2000",
    "title": "Title",
    "original_format": "TPB",
    "scan_info": "Releaser",
    "ext": "cbz",
}
TEST_COMIC_VOL_ONLY = {
    "series": "Long Series Name",
    "volume": "1",
    "issue": "1",
    "title": "Title",
    "original_format": "TPB",
    "year": "2000",
    "scan_info": "Releaser & Releaser-Releaser",
    "ext": "cbr",
}

# Tests for 0.1.0
FNS = {
    "Night of 1000 Wolves 001 (2013).cbz": {
        "series": "Night of 1000 Wolves",
        "issue": "001",
        "year": "2013",
        "ext": "cbz",
    },
    "19687 Sandman 53.cbz": {
        "series": "19687 Sandman",
        "issue": "53",
        "ext": "cbz",
    },
    "33475 OMAC v3 2.cbr": {
        "series": "33475 OMAC",
        "volume": "3",
        "issue": "2",
        "ext": "cbr",
    },
    "Long Series Name 001 (2000) Title (TPB) (Releaser).cbz": TEST_COMIC_FIELDS,
    "Long Series Name #001 (2000) Title (TPB) (Releaser).cbz": TEST_COMIC_FIELDS,
    "Long Series Name (2000) 001 Title (TPB) (Releaser).cbz": TEST_COMIC_FIELDS,
    "Long Series Name (2000) #001 Title (TPB) (Releaser).cbz": TEST_COMIC_FIELDS,
    "Ultimate Craziness (2019) (Digital) (Friends-of-Bill).cbr": {
        "series": "Ultimate Craziness",
        "year": "2019",
        "ext": "cbr",
        "original_format": "Digital",
        "scan_info": "Friends-of-Bill",
    },
    "Jimmy Stocks Love Chain (2005) (digital) (The Magicians-Empire).cbr": {
        "series": "Jimmy Stocks Love Chain",
        "year": "2005",
        "ext": "cbr",
        "original_format": "digital",
        "scan_info": "The Magicians-Empire",
    },
    "Arkenstone Vol. 01 - The Smell of Burnt Toast (2020) (digital) (My-brother).cbr": {
        "series": "Arkenstone",
        "volume": "01",
        "issue": "01",
        "year": "2020",
        "ext": "cbr",
        "scan_info": "My-brother",
        "title": "The Smell of Burnt Toast",
        "original_format": "digital",
    },
    "The_Arkenstone_v03_(2002)_(Digital)_(DR_&amp;_Quenya-Elves).cbr": {
        "series": "The Arkenstone",
        "volume": "03",
        "issue": "03",
        "year": "2002",
        "ext": "cbr",
        "scan_info": "DR &amp; Quenya-Elves",
        "original_format": "Digital",
    },
    "Kartalk v01 001 - Fear the Brakes (2004) (digital) (Son of Ultron-EMpire).cbr": {
        "series": "Kartalk",
        "volume": "01",
        "issue": "001",
        "year": "2004",
        "ext": "cbr",
        "original_format": "digital",
        "scan_info": "Son of Ultron-EMpire",
        "title": "Fear the Brakes",
    },
    "Kartalk Library Edition v01 (1992) (digital) (Son of Ultron-Empire).cbr": {
        "series": "Kartalk Library Edition",
        "volume": "01",
        "issue": "01",
        "year": "1992",
        "ext": "cbr",
        "original_format": "digital",
        "scan_info": "Son of Ultron-Empire",
    },
    "Kind of Deadly v02 - Last Bullet (2006) (Digital) (Zone-Empire).cbr": {
        "series": "Kind of Deadly",
        "volume": "02",
        "issue": "02",
        "year": "2006",
        "ext": "cbr",
        "original_format": "Digital",
        "scan_info": "Zone-Empire",
        "title": "Last Bullet",
    },
    "Jeremy John - Not A Title (2017) (digital-Minutement).cbz": {
        "series": "Jeremy John - Not A Title",
        "year": "2017",
        "ext": "cbz",
        "original_format": "digital",
        "scan_info": "Minutement",
    },
    "Jeremy John 001 (2006) (digital (Minutemen-Faessla).cbz": {
        "series": "Jeremy John",
        "issue": "001",
        "year": "2006",
        "ext": "cbz",
        "scan_info": "Minutemen-Faessla",
        "original_format": "digital",
    },
    "Jeremy John 003 (2007) (4 covers) (digital) (Minutemen-Faessla).cbz": {
        "series": "Jeremy John",
        "issue": "003",
        "year": "2007",
        "ext": "cbz",
        "scan_info": "Minutemen-Faessla",
        "original_format": "digital",
        "remainders": ("(4 covers)",),
    },
    "Jeremy John v01 - Uninterested! (2007) (Digital) (Asgard-Empire).cbr": {
        "series": "Jeremy John",
        "volume": "01",
        "issue": "01",
        "year": "2007",
        "ext": "cbr",
        "original_format": "Digital",
        "scan_info": "Asgard-Empire",
        "title": "Uninterested!",
    },
    "King of Skittles 01 (of 05) (2020) (digital) (Son of Ultron-Empire).cbr": {
        "series": "King of Skittles",
        "issue": "01",
        "issue_count": "05",
        "year": "2020",
        "ext": "cbr",
        "original_format": "digital",
        "scan_info": "Son of Ultron-Empire",
    },
    "Darkwad 011 (2019) (Digital) (Zone-Empire).cbr": {
        "series": "Darkwad",
        "issue": "011",
        "year": "2019",
        "ext": "cbr",
        "original_format": "Digital",
        "scan_info": "Zone-Empire",
    },
    "Darkwad by Carlos Zemo v01 - Knuckle Fight (2009) (Digital) (Zone-Empire).cbr": {
        "series": "Darkwad by Carlos Zemo",
        "volume": "01",
        "issue": "01",
        "year": "2009",
        "ext": "cbr",
        "title": "Knuckle Fight",
        "original_format": "Digital",
        "scan_info": "Zone-Empire",
    },
    "The Walking Dead #002 (2003).cbz": {
        "series": "The Walking Dead",
        "issue": "002",
        "year": "2003",
        "ext": "cbz",
    },
    "The Walking Dead #3.cbz": {
        "series": "The Walking Dead",
        "issue": "3",
        "ext": "cbz",
    },
    "The Walking Dead 4.cbz": {
        "series": "The Walking Dead",
        "issue": "4",
        "ext": "cbz",
    },
    "A Fractional Comic 1.1.cbz": {
        "series": "A Fractional Comic",
        "issue": "1.1",
        "ext": "cbz",
    },
    "A Fractional Comic 8.54.cbz": {
        "series": "A Fractional Comic",
        "issue": "8.54",
        "ext": "cbz",
    },
    "Earth X #½.cbz": {
        "series": "Earth X",
        "issue": "½",
        "ext": "cbz",
    },
    "Avengers #001½.cbz": {
        "series": "Avengers",
        "issue": "001½",
        "ext": "cbz",
    },
    "The Amazing Spider-Man #78.BEY.cbz": {
        "series": "The Amazing Spider-Man",
        "issue": "78.BEY",
        "ext": "cbz",
    },
    "The Amazing Spider-Man #54.LR.cbz": {
        "series": "The Amazing Spider-Man",
        "issue": "54.LR",
        "ext": "cbz",
    },
    "Wolverine & the X-Men #27AU.cbz": {
        "series": "Wolverine & the X-Men",
        "issue": "27AU",
        "ext": "cbz",
    },
    "Fantastic Four #5AU.cbz": {
        "series": "Fantastic Four",
        "issue": "5AU",
        "ext": "cbz",
    },
}

# Tests for 0.2.0
FNS.update(
    {
        # Philosopy change regarding dashes.
        "Bardude - The Last Thing I Remember.cbz": {
            "series": "Bardude - The Last Thing I Remember",
            "ext": "cbz",
        },
        "Drunkguy - The Man Without Fear - 01.cbz": {
            "series": "Drunkguy - The Man Without Fear",
            "issue": "01",
            "ext": "cbz",
        },
        # BIG Change. title after token. more stripping.
        "'Batman - Superman - World's Finest 022 (2024) (Webrip) (The Last Kryptonian-DCP).cbz": {
            "ext": "cbz",
            "issue": "022",
            "original_format": "Webrip",
            "series": "Batman - Superman - World's Finest",
            "scan_info": "The Last Kryptonian-DCP",
            "year": "2024",
        },
        # Issue number starting with a letter requested in https://github.com/comictagger/comictagger/issues/543
        #   word characters now allowed to lead issue numbers only if preceded by a # marker
        "batman #B01 title.cbz": {
            "ext": "cbz",
            "issue": "B01",
            "series": "batman",
            "title": "title",
        },
        "Monster_Island_v1_#2__repaired__c2c.cbz": {
            "ext": "cbz",
            "issue": "2",
            "series": "Monster Island",
            "volume": "1",
            "scan_info": "c2c",
            "remainders": ("(repaired)",),
        },
        # Extra - in the series
        " X-Men-V1-#067.cbr": {
            "ext": "cbr",
            "issue": "067",
            "series": "X-Men",
            "volume": "1",
            "remainders": ("-",),
        },
        "Aquaman - Green Arrow - Deep Target #01 (of 07) (2021).cbr": {
            "ext": "cbr",
            "issue": "01",
            "series": "Aquaman - Green Arrow - Deep Target",
            "year": "2021",
            "issue_count": "07",
        },
        # CT only separates this into a title if the '-' is attached to the previous word eg 'aquaman- Green Arrow'. @bpepple opened a ticket for this https://github.com/ajslater/comicfn2dict/issues/1 already
        "Batman_-_Superman_#020_(2021).cbr": {
            "ext": "cbr",
            "issue": "020",
            "series": "Batman - Superman",
            "year": "2021",
        },
        # Publishers like to re-print some of their annuals using this format for the year
        "Batman '89 (2021) .cbr": {
            "ext": "cbr",
            "series": "Batman '89",
            "year": "2021",
        },
        # This made the parser in CT much more complicated. It's understandable that this isn't parsed on the first few iterations of this project
        "Star Wars - War of the Bounty Hunters - IG-88 (2021).cbz": {
            "ext": "cbz",
            "series": "Star Wars - War of the Bounty Hunters - IG-88",
            "year": "2021",
        },  # The addition of the '#1' turns this into the same as 'Aquaman - Green Arrow - Deep Target' above
        "Star Wars - War of the Bounty Hunters - IG-88 #1 (2021).cbz": {
            "ext": "cbz",
            "issue": "1",
            "series": "Star Wars - War of the Bounty Hunters - IG-88",
            "year": "2021",
        },
        "Free Comic Book Day - Avengers.Hulk (2021).cbz": {
            "ext": "cbz",
            "series": "Free Comic Book Day - Avengers Hulk",
            "year": "2021",
        },
        # CT assumes the volume is also the issue number if it can't find an issue number
        "Avengers By Brian Michael Bendis volume 03 (2013).cbz": {
            "ext": "cbz",
            "issue": "03",
            "series": "Avengers By Brian Michael Bendis",
            "volume": "03",
            "year": "2013",
        },
        # CT catches the year
        "Marvel Previews #002 (January 2022).cbr": {
            "ext": "cbr",
            "issue": "002",
            "series": "Marvel Previews",
            "publisher": "Marvel",
            "month": "01",
            "year": "2022",
        },
        "Test Numeric Year #2 2001-02-24.cbz": {
            "ext": "cbz",
            "issue": "2",
            "series": "Test Numeric Year",
            "year": "2001",
            "month": "02",
            "day": "24",
        },
        "Test Month First Date 02-24-2001.cbz": {
            "ext": "cbz",
            "series": "Test Month First Date",
            "year": "2001",
            "month": "02",
            "day": "24",
        },
        # CT notices that this is a full date, CT doesn't actually return the month or day though just removes it
        "X-Men, 2021-08-04 (#02).cbz": {
            "ext": "cbz",
            "issue": "02",
            "series": "X-Men",
            "year": "2021",
            "month": "08",
            "day": "04",
        },
        # 4 digit issue number
        #   should this be an issue number if year DONE?.
        "action comics 1024.cbz": {
            "ext": "cbz",
            "issue": "1024",
            "series": "action comics",
        },
        # This is a contrived test case. I've never seen this I just wanted to handle it with my parser
        "Cory Doctorow's Futuristic Tales of the Here and Now #0.0.1 (2007).cbz": {
            "ext": "cbz",
            "issue": "0.0.1",
            "series": "Cory Doctorow's Futuristic Tales of the Here and Now",
            "year": "2007",
        },
        # CT treats ':' the same as '-' but here the ':' is attached to 'Now' which CT sees as a title separation
        "Cory Doctorow's Futuristic Tales of the Here and Now: Anda's Game #001 (2007).cbz": {
            "ext": "cbz",
            "issue": "001",
            "series": "Cory Doctorow's Futuristic Tales of the Here and Now",
            "title": "Anda's Game",
            "year": "2007",
        },
        # If a title ends in a year, it's not an issue (and is a year if no year)
        "Blade Runner Free Comic Book Day 2021 (2021).cbr": {
            "ext": "cbr",
            "series": "Blade Runner Free Comic Book Day 2021",
            "year": "2021",
        },
        # If a year occurs after another year,  and no volume, do volume / year
        "Super Strange Yarns (1957) #92 (1969).cbz": {
            "ext": "cbz",
            "issue": "92",
            "series": "Super Strange Yarns",
            "volume": "1957",
            "year": "1969",
        },
        # CT checks for the following '(of 06)' after the '03' and marks it as the volume
        "Elephantmen 2259 #008 - Simple Truth 03 (of 06) (2021).cbr": {
            "ext": "cbr",
            "issue": "008",
            "series": "Elephantmen 2259",
            "title": "Simple Truth",
            "volume": "03",
            "year": "2021",
            "volume_count": "06",
        },
        # CT treats book like 'v' but also adds it as the title (matches ComicVine for this particular series)
        "Bloodshot Book 03 (2020).cbr": {
            "ext": "cbr",
            "issue": "03",
            "series": "Bloodshot",
            "title": "Book 03",
            "volume": "03",
            "year": "2020",
        },
        # c2c aka "cover to cover" is fairly common and CT moves it to scan_info/remainder
        "Marvel Two In One V1 #090  c2c.cbr": {
            "ext": "cbr",
            "issue": "090",
            "series": "Marvel Two In One",
            "publisher": "Marvel",
            "volume": "1",
            "scan_info": "c2c",
        },
        # CT treats '[]' as equivalent to '()', catches DC as a publisher and 'Sep-Oct 1951' as dates and removes them. CT doesn't catch the digital though so that could be better but I blame whoever made this atrocious filename
        "Wonder Woman #49 DC Sep-Oct 1951 digital [downsized, lightened, 4 missing story pages restored] (Shadowcat-Empire).cbz": {
            "ext": "cbz",
            "issue": "49",
            "series": "Wonder Woman",
            "original_format": "digital",
            "publisher": "DC",
            "year": "1951",
            "month": "09",
            "remainders": (
                "(downsized, lightened, 4 missing story pages "
                "restored) (Shadowcat-Empire)",
            ),
        },
        "Captain Science #001 (1950) The Beginning - nothing.cbz": {
            "ext": "cbz",
            "issue": "001",
            "title": "The Beginning - nothing",
            "series": "Captain Science",
            "year": "1950",
        },
        "Captain Science #001-cix-cbi.cbr": {
            "ext": "cbr",
            "issue": "001",
            "series": "Captain Science",
            "title": "cix-cbi",
        },
        "Long Series Name v1 (2000) #001 "
        "Title (TPB) (Releaser).cbz": TEST_COMIC_FIELDS_VOL,
        "Long Series Name 001 (2000) (TPB-Releaser) Title.cbz": {
            "series": "Long Series Name",
            "issue": "001",
            "year": "2000",
            "original_format": "TPB",
            "scan_info": "Releaser",
            "remainders": ("Title",),
            "ext": "cbz",
        },
        "Long Series Name Vol 1 "
        "(2000) (TPB) (Releaser & Releaser-Releaser) Title.cbr": {
            "series": "Long Series Name",
            "volume": "1",
            "issue": "1",
            "remainders": ("Title",),
            "original_format": "TPB",
            "year": "2000",
            "scan_info": "Releaser & Releaser-Releaser",
            "ext": "cbr",
        },
        "Ex Machina 050 (2 Covers) (2010) (Digital) (Zone-Empire).cbz": {
            "ext": "cbz",
            "issue": "050",
            "original_format": "Digital",
            "scan_info": "Zone-Empire",
            "series": "Ex Machina",
            "year": "2010",
            "remainders": ("(2 Covers)",),
        },
    }
)

# first_key, first_val = NEW.popitem()
# FNS[first_key] = first_val
PARSE_FNS = MappingProxyType(FNS)

SERIALIZE_FNS = MappingProxyType(
    {
        "Long Series Name #001 (2000) Title (TPB) (Releaser).cbz": TEST_COMIC_FIELDS,
        "Long Series Name v1 #001 "
        "(2000) Title (TPB) (Releaser & Releaser-Releaser).cbr": TEST_COMIC_VOL_ONLY,
        "Series Name (2000-12-31).cbz": {
            "series": "Series Name",
            "year": "2000",
            "month": "12",
            "day": "31",
            "ext": "cbz",
        },
        "Series Name (2000-12).cbz": {
            "series": "Series Name",
            "year": "2000",
            "month": "12",
            "ext": "cbz",
        },
        "Series Name (Dec-31).cbz": {
            "series": "Series Name",
            "month": "12",
            "day": "31",
            "ext": "cbz",
        },
    }
)
