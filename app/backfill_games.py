import io
import csv
from datetime import datetime
from app import db
from app.models import Game
from app.services import IGDBService

DATA = """Count,YearCount,Year,Title,Publisher,Platform Played,Original Platform,Franchise,Date Finished,Year Published,Replay?,,,,,
1,1,2022,Guardians of the Galaxy,Square Enix,Playstation 5,Playstation 5,,1/22/22,2021,,,,,,
2,2,2022,Goragoa,Annapurna Interactive,PC / Steam Deck,PC / Steam Deck,,1/29/22,2017,,,,,,
3,3,2022,Life is Strange 2,Square Enix,PC / Steam Deck,PC / Steam Deck,Life is Strange,2/6/22,2018,,,,,,
4,4,2022,Demon's Souls,Sony ,Playstation 5,Playstation 5,Dark Souls,2/15/22,2020,,,,,,
5,5,2022,Mother 3 ,Nintendo,Retro Handheld,Game Boy Advance,Mother,3/13/22,2006,,,,,,
6,6,2022,King of Dragons (Capcom Beat Em Up Bundle),Capcom,Nintendo Switch,Arcade,,4/10/22,1991,,,,,,
7,7,2022,Horizon Forbidden West,Sony ,Playstation 5,Playstation 5,Horizon,5/5/22,2022,,,,,,
8,8,2022,Kirby and the Forgotten Land,Nintendo,Nintendo Switch,Nintendo Switch,Kirby,5/28/22,2022,,,,,,
9,9,2022,Elden Ring,Namco Bandai,Playstation 5,Playstation 5,,6/6/22,2022,,,,,,
10,10,2022,TMNT: Shredder's Revenge,DotEmu,Nintendo Switch,Nintendo Switch,TMNT,6/20/22,2022,,,,,,
11,11,2022,Bloodstained: Curse of the Moon 2,Inti Creates,Nintendo Switch,Nintendo Switch,Bloodstained,6/24/22,2020,,,,,,
12,12,2022,Infernax,DotEmu,Nintendo Switch,Nintendo Switch,,8/13/22,2022,,,,,,
13,13,2022,Final Fantasy VII Remake,Square Enix,Playstation 5,Playstation 5,Final Fantasy,9/6/22,2020,,,,,,
14,14,2022,Metroid Dread (Hard),Nintendo,Nintendo Switch,Nintendo Switch,Metroid,9/16/22,2021,X,,,,,count 
15,15,2022,Battle Circuit (Capcom Beat Em Up Bundle),Capcom,Nintendo Switch,Arcade,,10/13/22,1997,,,,,PC / Steam Deck,36
16,16,2022,The Last Of Us Part II,Sony ,Playstation 5,Playstation 5,TLOU,10/15/22,2020,X,,,,Playstation 5,17
17,17,2022,Resident Evil Village: Shadows of Rose,Capcom,PC / Steam Deck,PC / Steam Deck,Resident Evil,10/30/22,2022,,,,,Nintendo Switch,13
18,18,2022,Resident Evil Village (3rd Person Mode),Capcom,PC / Steam Deck,PC / Steam Deck,Resident Evil,11/11/22,2021,X,,,,Switch 2,11
19,19,2022,Resident Evil VII: End of Zoe,Capcom,PC / Steam Deck,PC / Steam Deck,Resident Evil,11/12/22,2017,,,,,Analogue Pocket,5
20,20,2022,TMNT: Turtles in Time,Konami,Nintendo Switch,Arcade,TMNT,11/21/22,1991,,,,,Retro Handheld,4
21,21,2022,Dark Souls 2: Scholar of the First Sin,Namco Bandai,PC / Steam Deck,PC / Steam Deck,Dark Souls,12/10/22,2014,,,,,SNES,3
22,22,2022,Immortality,Half Mermaid Productions,PC / Steam Deck,PC / Steam Deck,,12/12/22,2022,,,,,Arcade,2
23,1,2023,God of War Ragnarok ,Sony ,Playstation 5,Playstation 5,God of War,1/8/23,2022,,,,,NES,2
24,2,2023,Bowser's Fury,Nintendo,Nintendo Switch,Nintendo Switch,Mario,1/9/23,2021,,,,,Playstation 3,2
25,3,2023,It Takes Two,EA,Playstation 5,Playstation 5,,1/18/23,2021,,,,,,0
26,4,2023,Metal Gear Solid,Konami,Playstation 3,Playstation,Metal Gear Solid,1/18/23,1998,,,,,,
27,5,2023,Z1M1,Nintendo,PC / Steam Deck,NES,Randomizer,2/5/23,2019,X,,,,,
28,6,2023,Metroid Prime Remastered,Nintendo,Nintendo Switch,Nintendo Switch,Metroid ,2/17/23,2023,X,,,,,
29,7,2023,Powerwash Simulator,Square Enix,PC / Steam Deck,PC / Steam Deck,,2/24/23,2021,,,,,,
30,8,2023,Metal Gear Solid 2: Sons of Liberty HD,Konami,Playstation 3,Playstation 2,Metal Gear Solid,3/5/23,2001,,,,,,
31,9,2023,Pikmin,Nintendo,PC / Steam Deck,GameCube,Pikmin,3/8/23,2001,X,,,,,
32,10,2023,Stray,Annapurna ,Playstation 5,Playstation 5,,3/25/23,2022,,,,,,
33,11,2023,Resident Evil 4,Capcom,Playstation 5,Playstation 5,Resident Evil,4/15/23,2023,,,,,,
34,12,2023,A Way Out,EA,Playstation 5,Playstation 4,,4/19/23,2018,,,,,,
35,13,2023,Super Mario World,Nintendo,SNES,SNES,Mario,4/30/23,1991,X,,,,,
36,14,2023,The Legend of Zelda (Redux - Romhack),Nintendo,NES,NES,Zelda,5/6/23,1986,,,,,,
37,15,2023,Sons of the Forest,Newnight,PC / Steam Deck,PC / Steam Deck,Forest,6/5/23,2023,,,,,,
38,16,2023,The Legend of Zelda: Tears of the Kingdom,Nintendo,Nintendo Switch,Nintendo Switch,Zelda,6/12/23,2023,,,,,,
39,17,2023,Little Samson ,Taito,Retro Handheld,NES,,7/1/23,1992,,,,,,
40,18,2023,Pikmin 2 HD (Debt Only Run),Nintendo,Nintendo Switch,Nintendo Switch,Pikmin,7/9/23,2023,X,,,,,
41,19,2023,Telling Lies,Annapurna,PC / Steam Deck,PC / Steam Deck,,7/12/23,2019,,,,,,
42,20,2023,Pikmin 4,Nintendo,Nintendo Switch,Nintendo Switch,Pikmin,8/20/23,2023,,,,,,
43,21,2023,Super Mario Advance,Nintendo,Nintendo Switch,Game Boy Advance,Mario,8/25/23,2001,,,,,,
44,22,2023,The Last Of Us Part I (Hard),Sony ,Playstation 5,Playstation 5,The Last of Us,9/3/23,2022,,,,,,
45,23,2023,Dark Souls 3 (w/ DLC),Namco Bandai,PC / Steam Deck,PC / Steam Deck,Dark Souls,10/7/23,2016,X,,,,,
46,24,2023,Sea of Stars,Sabotage,Nintendo Switch,Nintendo Switch,Messenger,10/15/23,2023,,,,,,
47,25,2023,Batman,Sunsoft,Analogue Pocket,Game Boy,Batman,10/18/23,1990,,,,,,
48,26,2023,The Last of Us Part 1 Left Behind (Hard),Sony,Playstation 5,Playstation 5,The Last Of Us,11/1/23,2022,,,,,,
49,27,2023,Castlevania: Rondo of Blood,Konami,Analogue Pocket,PC Engine CD,Castlevania ,11/4/23,1993,,,,,,
50,28,2023,Resident Evil 4: Separate Ways,Capcom,Playstation 5,Playstation 5,Resident Evil,11/10/23,2023,,,,,,
51,1,2024,The Witcher 3: Wild Hunt,CD Projekt Red,PC / Steam Deck,PC / Steam Deck,The Witcher,1/5/24,2015,,,,,,
52,2,2024,BS Zelda Third Quest,Nintendo,SNES,SNES,Zelda,1/9/24,1995,,,,,,
53,3,2024,Metroid II: Return of Samus,Nintendo ,Analogue Pocket,Game Boy,Metroid,1/13/24,1991,,,,,,
54,4,2024,Lies of P,Neowiz,PC / Steam Deck,PC / Steam Deck,,2/3/24,2023,,,,,,
55,5,2024,Silent Hill: The Short Message,Konami,Playstation 5,Playstation 5,Silent Hill,2/4/24,2024,,,,,,
56,6,2024,Uncharted: The Lost Legacy (Legacy of Thieves Collection),Sony,PC / Steam Deck,Playstation 4,Uncharted,3/3/24,2022,X,,,,,
57,7,2024,X-Men,Konami,Arcade,Arcade,X-Men,4/27/24,1992,,,,,,
58,8,2024,Captain America and the Avengers,Data East,Arcade,Arcade,Marvel,4/27/24,1991,,,,,,
59,9,2024,SMZ3,Nintendo,SNES,SNES,Zelda / Metroid,5/1/24,2022,,,,,,
60,10,2024,Spider-Man 2,Sony,Playstation 5,Playstation 5,Spider-Man,5/6/24,2023,,,,,,
61,11,2024,Indika,11 bit Studios,PC / Steam Deck,PC / Steam Deck,,5/12/24,2024,,,,,,
62,12,2024,Hades,Supergiant Games,Nintendo Switch,Nintendo Switch,,5/22/24,2020,,,,,,
63,13,2024,Super Mario RPG,Nintendo ,Nintendo Switch,Nintendo Switch,Mario,6/14/24,2023,,,,,,
64,14,2024,Life Is Strange: True Colors,Square Enix,PC / Steam Deck,PC / Steam Deck,Life Is Strange,7/1/24,2021,,,,,,
65,15,2024,Divinity: Original Sin II,Larian Studios,PC / Steam Deck,PC / Steam Deck,Divinity,7/16/24,2017,,,,,,
66,16,2024,Nintendo World Championships: NES Edition,Nintendo,Nintendo Switch,Nintendo Switch,,7/26/24,2024,,,,,,
67,17,2024,The Legend of Zelda,Nintendo,Analogue Pocket,NES,Zelda,8/3/24,1986,X,,,,,
68,18,2024,Baldur's Gate 3,Larian Studios,Playstation 5,Playstation 5,,9/1/24,2023,,,,,,
69,19,2024,Xenoblade Chronicles 3,Nintendo,Nintendo Switch,Nintendo Switch,Xenoblade,9/19/24,2022,,,,,,
70,20,2024,Alien: Isolation,Sega,PC / Steam Deck,PC / Steam Deck,Alien,10/4/24,2014,,,,,,
71,21,2024,Elden Ring (Seamless Co-Op),Namco Bandai,PC / Steam Deck,PC / Steam Deck,,10/5/24,2022,X,,,,,
72,22,2024,Remnant 2,Gearbox,PC / Steam Deck,PC / Steam Deck,,10/14/24,2023,,,,,,
73,23,2024,Torchlight II,Runic Games,Nintendo Switch,Nintendo Switch,Torchlight,10/26/24,2012,,,,,,
74,24,2024,The Goonies II,Konami,NES,NES,,11/1/24,1987,,,,,,
75,25,2024,Silent Hill 2,Konami,Playstation 5,Playstation 5,Silent Hill,11/28/24,2024,,,,,,
76,26,2024,Diablo IV,Blizzard,PC / Steam Deck,PC / Steam Deck,Diablo,11/30/24,2023,,,,,,
77,1,2025,Elden Ring: Shadow of the Erdtree (Seamless Co-Op),Namco Bandai,PC / Steam Deck,PC / Steam Deck,,1/4/25,2023,,,,,,
78,2,2025,Metroid: Zero Mission (100% Complete),Nintendo,Retro Handheld,Game Boy Advance,Metroid,1/20/25,2004,X,,,,,
79,3,2025,Metaphor Refantazio,Atlus,Playstation 5,Playstation 5,,2/13/25,2024,,,,,,
80,4,2025,Diablo IV: Vessel of Hatred,Blizzard,PC / Steam Deck,PC / Steam Deck,Diablo,2/13/25,2024,,,,,,
81,5,2025,Control,Remedy,PC / Steam Deck,PC / Steam Deck,,2/23/25,2018,,,,,,
82,6,2025,Control: AWE DLC,Remedy,PC / Steam Deck,PC / Steam Deck,,3/1/25,2020,,,,,,
83,7,2025,Monster Hunter Wilds,Capcom,PC / Steam Deck,PC / Steam Deck,Monster Hunter,3/11/25,2025,,,,,,
84,8,2025,Doom Eternal,Bethesda,PC / Steam Deck,PC / Steam Deck,Doom,4/6/25,2019,,,,,,
85,9,2025,Super Metroid (Best Ending),Nintendo,Retro Handheld,SNES,Metroid,4/14/25,1994,X,,,,,
86,10,2025,Dark Souls (Seamless Co-Op),Namco Bandai,PC / Steam Deck,PC / Steam Deck,Dark Souls,4/27/25,2011,X,,,,,
87,11,2025,Tunic,Finji,PC / Steam Deck,PC / Steam Deck,,4/27/25,2022,,,,,,
88,12,2025,Dark Souls 3 (Seamless Co-Op),Namco Bandai,PC / Steam Deck,PC / Steam Deck,Dark Souls,5/19/25,2016,X,,,,,
89,13,2025,Dark Souls (NG+),Namco Bandai,Nintendo Switch,Nintendo Switch,Dark Souls,5/19/25,2011,X,,,,,
90,14,2025,Bloodborne (Bad Ending),Sony,Playstation 5,Playstation 4,,5/31/25,2016,X,,,,,
91,15,2025,Mario Kart World (All GP),Nintendo,Switch 2,Switch 2,Mario Kart,6/5/25,2025,,,,,,
92,16,2025,Fantasy Life i: The Girl Who Steals Time,Level-5,Switch 2,Switch 2,,6/15/25,2025,,,,,,
93,17,2025,Dying Light,Techland,Switch 2,Nintendo Switch,,7/14/25,2015,,,,,,
94,18,2025,Portal,Valve,Switch 2,PC / Steam Deck,Portal,8/8/25,2007,X,,,,,
95,19,2025,Injustice: Gods Among Us,Warner Bros.,PC / Steam Deck,PC / Steam Deck,Injustice,8/16/25,2013,,,,,,
96,20,2025,Portal 2,Valve,Switch 2,PC / Steam Deck,Portal,8/25/25,2011,X,,,,,
97,21,2025,Dark Souls 3 Platinum Trophy,Namco Bandai,PC / Steam Deck,PC / Steam Deck,Dark Souls,8/30/25,2016,X,,,,,
98,22,2025,Donkey Kong Bananza,Nintendo,Switch 2,Switch 2,Donkey Kong,8/30/25,2025,,,,,,
99,23,2025,Mortal Kombat,Warner Bros.,PC / Steam Deck,PC / Steam Deck,Mortal Kombat,9/1/25,2011,,,,,,
100,24,2025,Donkey Kong 94,Nintendo,Analogue Pocket,Game Boy,Donkey Kong,10/4/25,1994,,,,,,
101,25,2025,Astro Bot,Sony,Playstation 5,Playstation 5,,10/27/25,2024,,,,,,
102,26,2025,Elden Ring Nightreign,Namco Bandai,PC / Steam Deck,PC / Steam Deck,Elden Ring,11/2/25,2024,,,,,,
103,27,2025,Elden Ring,Namco Bandai,PC / Steam Deck,PC / Steam Deck,Elden Ring,11/9/25,2022,X,,,,,
104,28,2025,Elden Ring: Shadow of the Erdtree,Namco Bandai,PC / Steam Deck,PC / Steam Deck,Elden Ring,11/10/25,2023,X,,,,,
105,29,2025,Shining Force: Ressurection of the Dark Dragon,Sega,Retro Handheld,Game Boy Advance,Shining Force,11/15/25,2004,,,,,,
106,30,2025,Hollow Knight Silksong,Team Cherry,Switch 2,Switch 2,Hollow Knight,11/22/25,2025,,,,,,
107,31,2025,Metroid Prime 4: Beyond,Nintendo,Switch 2,Switch 2,Metroid,12/19/25,2025,,,,,,
108,32,2025,Five Dates,,PC / Steam Deck,PC / Steam Deck,,,,,,,,,
109,1,2026,Ghost of Yotei,Sony,Playstation 5,Playstation 5,,1/30/26,2025,,,,,,
110,2,2026,Resident Evil: Requiem,Capcom,PC / Steam Deck,PC / Steam Deck,Resident Evil,3/2/26,2026,,,,,,
111,3,2026,Resident Evil Remake HD Remaster,Capcom,Switch 2,GameCube,Resident Evil,3/9/26,2002,X,,,,,
112,4,2026,Resident Evil 2,Capcom,PC / Steam Deck,PC / Steam Deck,Resident Evil,3/16/26,2019,X,,,,,
113,5,2026,The Exit 8,Playism,PC / Steam Deck,PC / Steam Deck,,4/19/26,2023,,,,,,
114,6,2026,Dungeons & Dragons: Demeo Battlemarked ,,PC / Steam Deck,PC / Steam Deck,,,,,,,,,
115,7,2026,Death Stranding 2: On The Beach,Sony,Playstation 5,Playstation 5,Death Stranding,5/2/26,2025,,,,,,
116,8,2026,The Legend of Zelda: Echoes of Wisdom,Nintendo,Switch 2,Nintendo Switch,Zelda,5/16/26,2024,,,,,,
117,9,2026,Ninja Gaiden Ragebound,Dotemu,Switch 2,Nintendo Switch,Ninja Gaiden,5/18/26,2025,,,,,,
"""

def parse_date(date_str):
    if not date_str: return None
    try:
        parts = date_str.split('/')
        if len(parts[-1]) == 2:
            return datetime.strptime(date_str, '%m/%d/%y').date()
        return datetime.strptime(date_str, '%m/%d/%Y').date()
    except ValueError: return None

def run_backfill_games():
    Game.query.delete()
    db.session.commit()
    
    f = io.StringIO(DATA)
    reader = csv.DictReader(f)
    
    count = 0
    for row in reader:
        title = row['Title'].strip()
        year_published = row['Year Published']
        date_finished = parse_date(row['Date Finished'])
        is_rewatch = True if row['Replay?'] == 'X' else False
        
        # Clean title for searching (remove variant info in parens)
        search_title = title.split(' (')[0]
        variant = ""
        if '(' in title:
            variant = title.split('(')[1].replace(')', '')

        print(f"Processing Game: {title}...")

        tmdb_id = None
        search_results = IGDBService.search_games(search_title)
        
        igdb_id = None
        if search_results:
            # Find best year match
            for res in search_results:
                res_year = datetime.fromtimestamp(res['first_release_date']).year if res.get('first_release_date') else None
                if str(res_year) == year_published:
                    igdb_id = res['id']
                    break
            if not igdb_id:
                igdb_id = search_results[0]['id']
        
        if igdb_id:
            details = IGDBService.get_game_details(igdb_id)
            if details:
                # Companies
                involved = details.get('involved_companies', [])
                developers = ", ".join([ic['company']['name'] for ic in involved if ic.get('developer')])
                publishers = ", ".join([ic['company']['name'] for ic in involved if ic.get('publisher')])
                
                # Release year
                release_date_ts = details.get('first_release_date')
                release_year = datetime.fromtimestamp(release_date_ts).year if release_date_ts else None

                # Cover
                cover_filename = None
                if details.get('cover'):
                    cover_filename = IGDBService.download_cover(details['cover']['url'])

                new_game = Game(
                    title=details.get('name'),
                    release_year=release_year or (int(year_published) if year_published.isdigit() else None),
                    external_id=str(igdb_id),
                    developer=developers or row['Publisher'],
                    publisher=publishers or row['Publisher'],
                    franchise=", ".join([f['name'] for f in details.get('franchises', [])]) or row['Franchise'],
                    summary=details.get('summary'),
                    genres=", ".join([g['name'] for g in details.get('genres', [])]),
                    user_score=details.get('rating'),
                    critic_score=details.get('aggregated_rating'),
                    poster_path=cover_filename,
                    platform_played=row['Platform Played'],
                    original_platform=row['Original Platform'] or ", ".join([p['name'] for p in details.get('platforms', [])[:3]]),
                    is_revisit=is_rewatch,
                    variant=variant,
                    date_finished=date_finished,
                    status='Finished'
                )
                db.session.add(new_game)
                count += 1
            else:
                igdb_id = None

        if not igdb_id:
            new_game = Game(
                title=title,
                release_year=int(year_published) if year_published.isdigit() else None,
                publisher=row['Publisher'],
                platform_played=row['Platform Played'],
                original_platform=row['Original Platform'],
                franchise=row['Franchise'],
                is_revisit=is_rewatch,
                variant=variant,
                date_finished=date_finished,
                status='Finished'
            )
            db.session.add(new_game)
            count += 1
        
        if count % 10 == 0:
            db.session.commit()

    db.session.commit()
    return count
