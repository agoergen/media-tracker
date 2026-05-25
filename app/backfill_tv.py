import io
import csv
from datetime import datetime
from app import db
from app.models import TVSeason
from app.services import TMDBService

DATA = """Count,YearCount,Year,Season,Series Title,Network,Date Finished,Year of Release,# of Episodes,Rewatch,,,
1,1,2022,4,Cobra Kai,Netflix,1/3/22,2022,10,,,,"Cobra Kai, Season 4"
2,2,2022,1,Yellowjackets,Showtime,1/25/22,2021,10,,,,"Yellowjackets, Season 1"
3,3,2022,1,Only Murders in the Building,Hulu,2/22/22,2021,10,,,,"Only Murders in the Building, Season 1"
4,4,2022,33,The Amazing Race,CBS,3/2/22,2022,10,,,,"The Amazing Race, Season 33"
5,5,2022,1,Inventing Anna,Netflix,3/24/22,2022,8,,,,"Inventing Anna, Season 1"
6,6,2022,1,Dicktown,Hulu,4/23/22,2020,10,,,,"Dicktown, Season 1"
7,7,2022,2,Star Trek: Picard,Paramount Plus,5/16/22,2022,10,,,,"Star Trek: Picard, Season 2"
8,8,2022,1,Severance,Apple TV+,5/17/22,2022,9,,,,"Severance, Season 1"
9,9,2022,1,The Righteous Gemstones,HBO Max,5/23/22,2019,10,,,,"The Righteous Gemstones, Season 1"
10,10,2022,1,The Afterparty,Apple TV+,6/1/22,2022,8,,,,"The Afterparty, Season 1"
11,11,2022,2,The Righteous Gemstones,HBO Max,6/21/22,2022,10,,,,"The Righteous Gemstones, Season 2"
12,12,2022,4,Stranger Things,Netflix,7/14/22,2022,9,,,,"Stranger Things, Season 4"
13,13,2022,1,Players,Paramount Plus,7/27/22,2022,10,,,,"Players, Season 1"
14,14,2022,1,Keep Breathing,Netflix,8/14/22,2022,6,,,,"Keep Breathing, Season 1"
15,15,2022,6,Better Call Saul,AMC,8/15/22,2022,13,,,,"Better Call Saul, Season 6"
16,16,2022,1,Trainwreck: Woodstock 99,Netflix,9/4/22,2022,3,,,,"Trainwreck: Woodstock 99, Season 1"
17,17,2022,5,Cobra Kai,Netflix,9/13/22,2022,10,,,,"Cobra Kai, Season 5"
18,18,2022,5,The Handmaid's Tale,Hulu,11/9/22,2022,10,,,,"The Handmaid's Tale, Season 5"
19,19,2022,1,Last Chance U,Netflix,11/10/22,2016,6,,,,"Last Chance U, Season 1"
20,20,2022,4,The Marvelous Mrs. Maisel,Prime Video,11/13/22,2022,8,,,,"The Marvelous Mrs. Maisel, Season 4"
21,21,2022,2,Last Chance U,Netflix,11/14/22,2017,9,,,,"Last Chance U, Season 2"
22,22,2022,1,Vice Principals,HBO Max,11/20/22,2016,9,,,,"Vice Principals, Season 1"
23,23,2022,2,Vice Principals,HBO Max,11/25/22,2017,9,,,,"Vice Principals, Season 2"
24,24,2022,1,The Big Brunch,HBO Max,11/30/22,2022,8,,,,"The Big Brunch, Season 1"
25,25,2022,3,Dead To Me,Netflix,12/4/22,2022,10,,,,"Dead To Me, Season 3"
26,26,2022,1,"Pepsi, Where's My Jet",Netflix,12/17/22,2022,4,,,,"Pepsi, Where's My Jet, Season 1"
27,27,2022,34,The Amazing Race,CBS,12/26/22,2022,12,,,,"The Amazing Race, Season 34"
28,1,2023,1,Succession,HBO Max,1/19/23,2018,10,,,,"Succession, Season 1"
29,2,2023,1,The Haunting of Hill House,Netflix,1/28/23,2018,10,,,,"The Haunting of Hill House, Season 1"
30,3,2023,1,The Haunting of Bly Manor,Netflix,3/2/23,2020,9,,,,"The Haunting of Bly Manor, Season 1"
31,4,2023,1,Murdaugh Murders: A Southern Scandal,Netflix,3/8/23,2023,3,,,,"Murdaugh Murders: A Southern Scandal, Season 1"
32,5,2023,1,The Last Of Us ,HBO Max,3/13/2023,2023,9,,,,"The Last Of Us , Season 1"
33,6,2023,2,Succession,HBO Max,4/2/2023,2019,10,,,,"Succession, Season 2"
34,7,2023,1,Mythic Quest,Apple TV+,4/2/2023,2020,9,,,,"Mythic Quest, Season 1"
35,8,2023,1,Eastbound & Down,HBO Max,4/10/2023,2009,6,,,,"Eastbound & Down, Season 1"
36,9,2023,2,Eastbound & Down,HBO Max,4/16/2023,2010,7,,,,"Eastbound & Down, Season 2"
37,10,2023,3,Succession ,HBO Max,4/28/2023,2021,9,,,,"Succession , Season 3"
38,11,2023,4,Succession,HBO Max,5/28/2023,2023,10,,,,"Succession, Season 4"
39,12,2023,1,Jury Duty,Prime Video,6/17/2023,2023,8,,,,"Jury Duty, Season 1"
40,13,2023,1,The Bear,Hulu,6/28/2023,2022,8,,,,"The Bear, Season 1"
41,14,2023,1,Silo,Apple TV+,6/30/2023,2023,10,,,,"Silo, Season 1"
42,15,2023,1,Secret Chef,Hulu,7/2/2023,2023,10,,,,"Secret Chef, Season 1"
43,16,2023,2,Mythic Quest,Apple TV+,7/8/2023,2021,9,,,,"Mythic Quest, Season 2"
44,17,2023,3,Star Trek: Picard,Paramount Plus,7/17/2023,2023,10,,,,"Star Trek: Picard, Season 3"
45,18,2023,3,Eastbound & Down,HBO Max,8/2/2023,2012,8,,,,"Eastbound & Down, Season 3"
46,19,2023,4,Eastbound & Down,HBO Max,8/4/2023,2013,8,,,,"Eastbound & Down, Season 4"
47,20,2023,1,Telemarketers,HBO Max,8/30/2023,2023,3,,,,"Telemarketers, Season 1"
48,21,2023,1,Twisted Metal ,Peacock,9/1/2023,2023,10,,,,"Twisted Metal , Season 1"
49,22,2023,2,Killing It,Peacock,10/1/2023,2023,8,,,,"Killing It, Season 2"
50,23,2023,2,Only Murders in the Building,Hulu,10/1/2023,2022,10,,,,"Only Murders in the Building, Season 2"
51,23,2023,1,Breaking Bad,Netflix,10/3/2023,2008,7,X,,,"Breaking Bad, Season 1"
52,25,2023,3,The Righteous Gemstones,HBO Max,10/22/2023,2023,9,,,,"The Righteous Gemstones, Season 3"
53,26,2023,1,The Dropout,Hulu,10/25/2023,2022,8,,,,"The Dropout, Season 1"
54,26,2023,2,Breaking Bad,Netflix,11/14/2024,2009,13,X,,,"Breaking Bad, Season 2"
55,28,2023,5,The Marvelous Mrs. Maisel,Prime Video,12/2/2023,2023,9,,,,"The Marvelous Mrs. Maisel, Season 5"
56,29,2023,35,The Amazing Race,Paramount Plus,12/14/2023,2023,10,,,,"The Amazing Race, Season 35"
57,30,2023,1,Big Little Lies,HBO Max,12/22/2023,2017,7,,,,"Big Little Lies, Season 1"
58,31,2023,1,Daisy Jones and the Six,Prime Video,12/22/2023,2023,10,,,,"Daisy Jones and the Six, Season 1"
59,32,2023,1,Scavenger's Reign,HBO Max,12/31/2023,2023,12,,,,"Scavenger's Reign, Season 1"
60,1,2024,1,The White Lotus,HBO Max,1/6/2024,2021,6,,,,"The White Lotus, Season 1"
61,2,2024,3,Breaking Bad,Netflix,1/23/2024,2010,13,X,,,"Breaking Bad, Season 3"
62,3,2024,1,The Witcher,Netflix,2/21/2024,2019,8,,,,"The Witcher, Season 1"
63,4,2024,2,Big Little Lies,HBO Max,3/1/2024,2019,7,,,,"Big Little Lies, Season 2"
64,5,2024,3,American Nightmare,Netflix,3/28/2024,2024,3,,,,"American Nightmare, Season 3"
65,6,2024,4,Breaking Bad,Netflix,4/9/2024,2011,13,X,,,"Breaking Bad, Season 4"
66,7,2024,1,The Unbreakable Kimmy Schmidt,Netflix,5/5/2024,2015,13,,,,"The Unbreakable Kimmy Schmidt, Season 1"
67,8,2024,36,The Amazing Race,Paramount Plus,5/16/2024,2024,10,,,,"The Amazing Race, Season 36"
68,9,2024,1,Midnight Mass,Netflix,6/3/2024,2021,7,,,,"Midnight Mass, Season 1"
69,10,2024,1,Joe Pera Talks With You,HBO Max,6/16/2024,2018,10,,,,"Joe Pera Talks With You, Season 1"
70,11,2024,2,The Bear,Hulu,6/19/2024,2023,10,,,,"The Bear, Season 2"
71,12,2024,1,The Big Door Prize,Apple TV+,6/25/2024,2023,10,,,,"The Big Door Prize, Season 1"
72,13,2024,5,Breaking Bad,Netflix,6/25/2024,2013,16,X,,,"Breaking Bad, Season 5"
73,14,2024,1,Maid,Netflix,7/6/2024,2021,10,,,,"Maid, Season 1"
74,15,2024,1,Better Call Saul,Netflix,8/27/2024,2015,10,X,,,"Better Call Saul, Season 1"
75,16,2024,1,Terminator Zero,Netflix,9/21/2024,2024,8,,,,"Terminator Zero, Season 1"
76,17,2024,1,Mr. McMahon,Netflix,10/17/2024,2024,6,,,,"Mr. McMahon, Season 1"
77,18,2024,2,Better Call Saul,Netflix,10/22/2024,2016,10,X,,,"Better Call Saul, Season 2"
78,19,2024,1,Beef,Netflix,10/31/2024,2023,10,,,,"Beef, Season 1"
79,20,2024,1,The Haunting of Hill House,Netflix,11/27/2024,2018,10,X,,,"The Haunting of Hill House, Season 1"
80,21,2024,3,Better Call Saul,Netflix,12/31/2024,2017,10,X,,,"Better Call Saul, Season 3"
81,1,2025,1,Nobody Wants This,Netflix,2/1/2025,2024,10,,,,"Nobody Wants This, Season 1"
82,2,2025,1,House of the Dragon,HBO Max,2/5/2025,2022,10,,,,"House of the Dragon, Season 1"
83,3,2025,6,Cobra Kai,Netflix,2/15/2025,2025,15,,,,"Cobra Kai, Season 6"
84,4,2025,1,Halt and Catch Fire,VOD,2/17/2025,2014,10,X,,,"Halt and Catch Fire, Season 1"
85,5,2025,2,Halt and Catch Fire,VOD,2/21/2025,2015,10,X,,,"Halt and Catch Fire, Season 2"
86,6,2025,3,Halt and Catch Fire,VOD,3/8/2025,2016,10,X,,,"Halt and Catch Fire, Season 3"
87,7,2025,4,Better Call Saul,Netflix,3/11/2025,2018,10,X,,,"Better Call Saul, Season 4"
88,8,2025,2,Severance,Apple TV+,3/23/2025,2025,10,,,,"Severance, Season 2"
89,9,2025,4,Halt and Catch Fire,VOD,3/31/2025,2017,10,X,,,"Halt and Catch Fire, Season 4"
90,10,2025,1,Severance,Apple TV+,4/8/2025,2022,9,X,,,"Severance, Season 1"
91,11,2025,2,White Lotus,HBO Max,4/12/2025,2022,7,,,,"White Lotus, Season 2"
92,12,2025,1,Love,Netflix,4/18/2025,2016,10,X,,,"Love, Season 1"
93,13,2025,1,Dying for Sex,Hulu,4/27/2025,2025,8,,,,"Dying for Sex, Season 1"
94,14,2025,2,Love,Netflix,4/27/2025,2017,12,X,,,"Love, Season 2"
95,15,2025,5,Better Call Saul,Netflix,5/13/2025,2020,10,X,,,"Better Call Saul, Season 5"
96,16,2025,3,Love,Netflix,5/19/2025,2018,12,X,,,"Love, Season 3"
97,17,2025,1,Loki,Disney+,5/25/2025,2021,6,,,,"Loki, Season 1"
98,18,2025,2,The Last Of Us ,HBO Max,5/26/2025,2025,7,,,,"The Last Of Us , Season 2"
99,19,2025,2,The Rehearsal,HBO Max,5/26/2025,2025,6,,,,"The Rehearsal, Season 2"
100,20,2025,6,The Handmaid's Tale,Hulu,6/3/2025,2025,10,,,,"The Handmaid's Tale, Season 6"
101,21,2025,1,Casual,Hulu,6/8/2025,2015,10,X,,,"Casual, Season 1"
102,22,2025,2,Casual,Hulu,6/9/2025,2016,13,,,,"Casual, Season 2"
103,23,2025,1,Pee-Wee As Himself,HBO Max,6/15/2025,2025,2,,,,"Pee-Wee As Himself, Season 1"
104,24,2025,3,Casual,Hulu,6/17/2025,2025,13,,,,"Casual, Season 3"
105,25,2025,1,Scott Pilgrim Takes Off,Netflix,6/17/2025,2023,8,,,,"Scott Pilgrim Takes Off, Season 1"
106,26,2025,4,Casual,Hulu,6/20/2025,2018,8,,,,"Casual, Season 4"
107,27,2025,1,Wet Hot American Summer: First Day of Camp,Netflix,6/29/2025,2015,8,X,,,
108,28,2025,2,Severance,Apple TV+,6/26/2025,2025,10,X,,,
109,29,2025,1,Shrinking,Apple TV+,7/12/2025,2023,10,,,,
110,30,2025,1,Home Movies,Max,7/22/2025,1999,13,X,,,
111,31,2025,2,Shrinking,Apple TV+,7/21/2025,2024,12,,,,
112,32,2025,6,Better Call Saul,Netflix,7/30/2025,2023,13,X,,,
113,33,2025,4,The Righteous Gemstones,HBO Max,8/6/2025,2025,9,,,,
114,34,2025,1,The Hunting Wives,Netflix,8/7/2025,2025,8,,,,
115,35,2025,1,Haunting of Hill House,Netflix,10/26/2025,2018,10,X,,,
116,36,2025,1,Crazy Ex-Girlfriend,VOD,11/8/2025,2015,18,X,,,
117,37,2025,2,Crazy Ex-Girlfriend,VOD,11/19/2025,2016,13,X,,,
118,38,2025,1,Stranger Things,Netflix,11/28/2025,2016,8,X,,,
119,39,2025,2,Stranger Things,Netflix,12/1/2025,2017,9,X,,,
120,40,2025,1,The Chair Company,HBO Max,12/7/2025,2025,8,,,,
121,41,2025,3,Crazy Ex-Girlfriend,VOD,12/5/2025,2017,13,X,,,
122,42,2025,1,Pluribus,Apple TV+,12/24/2025,2025,9,,,,
123,43,2025,5,Stranger Things,Netflix,12/31/2026,2025,9,,,,
124,1,2026,4,Crazy Ex-Girlfriend,VOD,1/4/2026,2018,18,X,,,
125,2,2026,2,Nobody Wants This,Netflix,1/15/2026,2025,10,,,,
126,3,2026,1,Schitt's Creek,Hulu,2/1/2026,2015,13,X,,,
127,4,2026,2,Schitt's Creek,Hulu,2/4/2026,2016,13,,,,
128,5,2026,3,Schitt's Creek,Hulu,2/8/2026,2017,13,,,,
129,6,2026,3,Stranger Things,Netflix,2/8/2026,2019,8,X,,,
130,7,2026,4,Schitt's Creek,Hulu,2/14/2026,2018,10,X,,,
131,8,2026,4,Mythic Quest,Apple TV+,2/20/2026,2025,10,,,,
132,9,2026,37,The Amazing Race,Paramount Plus,2/25/2026,2024,12,,,,
133,10,2026,5,Schitt's Creek,Netflix,3/5/2026,2019,14,X,,,
134,11,2026,4,The Traitors,Peacock,2/19/2026,2026,12,,,,
135,12,2026,6,Schitt's Creek,Netflix,3/14/2026,2020,15,X,,,
136,13,2026,2,The Traitors UK,Peacock,3/28/2026,2024,12,,,,
137,14,2026,1,Scrubs 2026,Disney+,4/20/2026,2026,9,,,,
138,15,2026,4,Stranger Things,Netflix,4/17/2026,2022,9,,,,
139,16,2026,3,Shrinking,Apple TV+,5/3/2026,2026,11,,,,
140,17,2026,1,The Orville,Disney+,5/24/2026,2017,12,,,,"""

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Check for 2-digit or 4-digit year
        parts = date_str.split('/')
        if len(parts[-1]) == 2:
            return datetime.strptime(date_str, '%m/%d/%y').date()
        else:
            return datetime.strptime(date_str, '%m/%d/%Y').date()
    except ValueError:
        return None

def run_backfill_tv():
    # Clear existing TV seasons for a clean start
    TVSeason.query.delete()
    db.session.commit()
    
    f = io.StringIO(DATA)
    reader = csv.DictReader(f)
    
    count = 0
    for row in reader:
        title = row['Series Title'].strip()
        season_number = int(row['Season'])
        date_watched = parse_date(row['Date Finished'])
        provider = row['Network']
        is_rewatch = True if row['Rewatch'] == 'X' else False
        
        # Normalize providers
        if provider == 'Disney+': provider = 'Disney Plus'
        if provider == 'Paramount Plus': provider = 'Paramount+'

        print(f"Processing TV: {title} Season {season_number}...")

        # Search for TV series
        tmdb_id = None
        search_results = TMDBService.search_tv(title)
        if search_results:
            tmdb_id = search_results[0].get('id')
        
        if tmdb_id:
            show_details = TMDBService.get_tv_show_details(tmdb_id)
            season_details = TMDBService.get_tv_season_details(tmdb_id, season_number)
            
            if show_details and season_details:
                # Trailer (from series level)
                trailer_url = None
                videos = show_details.get('videos', {}).get('results', [])
                for video in videos:
                    if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                        trailer_url = f"https://www.youtube.com/embed/{video.get('key')}"
                        break

                new_season = TVSeason(
                    series_title=show_details.get('name'),
                    season_number=season_number,
                    date_watched=date_watched,
                    release_year=int(season_details.get('air_date', '')[:4]) if season_details.get('air_date') else None,
                    is_revisit=is_rewatch,
                    external_id=str(tmdb_id),
                    network=provider or show_details.get('networks', [{}])[0].get('name'),
                    episode_count=len(season_details.get('episodes', [])),
                    poster_path=season_details.get('poster_path') or show_details.get('poster_path'),
                    user_score=season_details.get('vote_average'),
                    plot=season_details.get('overview') or show_details.get('overview'),
                    trailer_url=trailer_url,
                    imdb_id=show_details.get('external_ids', {}).get('imdb_id')
                )
                db.session.add(new_season)
                count += 1
            else:
                tmdb_id = None # Fallback

        if not tmdb_id:
            # Basic fallback
            new_season = TVSeason(
                series_title=title,
                season_number=season_number,
                date_watched=date_watched,
                is_revisit=is_rewatch,
                network=provider,
                episode_count=int(row.get('# of Episodes', 0)) if row.get('# of Episodes') else 0
            )
            db.session.add(new_season)
            count += 1
        
        if count % 10 == 0:
            db.session.commit()

    db.session.commit()
    return count
