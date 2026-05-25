import io
import csv
from datetime import datetime
from app import db
from app.models import Movie
from app.services import TMDBService

DATA = """Count	YearCount	Year	Movie Title	Provider	Date Watched	Year of Release	Director	Leading Actors	Rewatch
1	1	2022	Encanto	Disney+	1/15/22	2021	Jared Bush, Byron Howard	Stephanie Beatriz	
2	2	2022	Miss Peregrine's House for Peculiar Children	Disney+	1/23/22	2016	Tim Burton	Eva Green	
3	3	2022	Black Widow	Disney+	2/4/22	2021	Cate Shortland	Scarlet Johannsen	
4	4	2022	Turning Red	Disney+	3/15/22	2022	Domee Shi	Rosalie Chiang	
5	5	2022	Uncharted	Theater	4/9/22	2022	Ruben Fleischer	Tom Holland	
6	6	2022	Sonic the Hedgehog 2	Theater	4/11/22	2022	Jeff Fowler	Ben Schwarz	
7	7	2022	Chip & Dale: Rescue Rangers	Disney+	5/25/22	2022	Akiva Schaffer	Andy Samberg	
8	8	2022	Evil Dead	Tubi	6/8/22	1981	Sam Raimi	Bruce Campbell	
9	9	2022	Scream	HBO Max	6/17/22	2022	Matt Bettinelli-Olpin, Tyler Gillett	Neve Campbell	
10	10	2022	Beavis and Butt-head Do The Universe	Paramount+	6/24/22	2022	John Rice, Albert Calleros	Mike Judge	
11	11	2022	Everything Everywhere All At Once	VOD	7/17/22	2022	Daniel Kwan, Daniel Scheinert	Michelle Yeoh	
12	12	2022	The Bob's Burgers Movie	HBO Max	7/21/22	2022	Loren Bouchard, Bernard Derriman	Jon Benjamin	
13	13	2022	Joker	HBO Max	8/28/22	2019	Todd Phillips	Joaquin Phoenix	
14	14	2022	Spider-man No Way Home	VOD	9/18/22	2021	Jon Watts	Tom Holland	
15	15	2022	Evil Dead 2	Blu-Ray	10/1/22	1987	Sam Raimi	Bruce Campbell	
16	16	2022	A Quiet Place	Paramount+	11/5/22	2018	John Krasinski	Emily Blunt	
17	17	2022	The Girl With All The Gifts	YouTube	11/7/22	2017	Colm McCarthy	Gemma Arterton	
18	18	2022	Weird: The Al Yankovic Story	Roku Channel	11/11/22	2022	Eric Appel	Daniel Radcliffe	
19	19	2022	Glass Onion: A Knives Out Mystery	Theater	11/23/22	2022	Rian Johnson	Daniel Craig	
20	20	2022	Black Panther: Wakanda Forever 	Theater	12/4/22	2022	Ryan Coogler	Letitia Wright 	
21	21	2022	Matilda: The Musical	Netflix	12/27/22	2022	Matthew Warchus	Alisha Weir	
22	1	2023	The Batman	HBO Max	1/29/23	2022	Matt Reeves	Robert Pattinson	
23	2	2023	Creed III	Theater	3/4/23	2023	Michael B. Jordan	Michael B. Jordan	
24	3	2023	Onward 	Disney+	3/26/23	2020	Dan Scanlon	Tom Holland 	
25	4	2023	Tetris	Apple TV+	4/2/23	2023	Jon S. Baird	Taron Egerton	
26	5	2023	The Founder	Netflix	4/3/23	2017	Robert Siegel	Michael Keaton	
27	6	2023	Dungeons and Dragons: Honor Among Thieves	Theater	4/4/23	2023	John Francis Daley	Chris Pine	
28	7	2023	The Super Mario Bros. Movie	Theater	4/5/23	2023	Aaron Horvath	Chris Pratt	
29	8	2023	Gerald's Game	Netflix	4/13/23	2017	Mike Flanagan	Carla Gugino	
30	9	2023	Guardians of the Galaxy Vol 3	Theater	5/6/23	2023	James Gun	Chris Pratt	
31	10	2023	Three Identical Strangers 	Hulu	5/21/23	2018	Tim Wardle	N/A	
32	11	2023	Air	Prime Video	6/10/23	2023	Ben Affleck	Matt Damon	
33	12	2023	Spider-Man: Across the Spider-Verse	Theater	6/11/23	2023	Joaquim Dos Santos	Shameik Moore	
34	13	2023	Asteroid City	Theater	6/27/23	2023	Wes Anderson	Jason Schwartzman	
35	14	2023	The Lego Batman Movie	Max	7/3/23	2017	Chris McKay	Will Arnett	
36	15	2023	Reality	Max	7/16/23	2023	Tina Satter	Sydney Sweeney	
37	16	2023	Barbie	Theater	7/20/23	2023	Greta Gerwig	Margot Robbie	
38	17	2023	Crazy Rich Asians 	Hulu	8/5/23	2018	Jon Chu	Constance Wu	
39	18	2023	We're All Gonna Die	Patreon	8/13/23	2023	Freddie Wong & Matt Arnold	Ashly Burch	
40	19	2023	Teenage Mutant Ninja Turtles: Mutant Mayhem	Theater	8/20/23	2023	Jeff Rowe	Nicolas Cantu	
41	20	2023	BS High	Max	9/4/23	2023	Travon Free	Roy Johnson	
42	21	2023	Glitch: The Rise & Fall of HQ Trivia	Max	9/4/23	2023	Salima Koroma	Scott Rogowsky	
43	22	2023	You Are So Not Invited To My Bat Mizvah	Netflix	9/17/23	2023	Sammi Cohen	Sadie Sandler	
44	23	2023	Taylor Swift: The Eras Tour	Theater	10/13/23	2023	Sam Wrench	Taylor Swift	
45	24	2023	A Nightmare On Elm Street	Max	10/22/23	1984	Wes Craven	Robert Englund	
46	25	2023	Halloween	Crackle	10/22/23	1978	John Carpenter 	Jamie Lee Curtis	
47	26	2023	Totally Killer	Prime Video	10/28/23	2023	Nahnatchka Khan	Kiernan Shipka	
48	27	2023	Friday the 13th	Max	10/29/23	1980	Sean S. Cunningham 	Adrienne King	
49	28	2023	I Am Mother	Netflix	12/3/23	2019	Grant Sputore	Clara Rugaard-Larsen	
50	29	2023	8-Bit Christmas	Max	12/16/23	2021	Michael Dowse	Neil Patrick Harris	
51	1	2024	Mean Girls The Musical	Theater	1/10/24	2024	Samantha Jayne	Angourie Rice	
52	2	2024	Self-Reliance	Hulu	1/13/24	2023	Jake Johnson	Jake Johnson	
53	3	2024	The Holdovers	Peacock	1/20/24	2023	Alexander Payne 	Paul Giamatti	
54	4	2024	Charlie and the Chocolate Factory	Max	1/23/24	2005	Tim Burton	Johnny Depp	
55	5	2024	Grounded II: The Making of The Last Of Us Part II	Youtube	2/2/24	2024	Neil Druckmann	Neil Druckmann	
56	6	2024	Poor Things	Theater	2/2/24	2023	Yorgos Lanthimos	Emma Stone	
57	7	2024	Dumb Money	Netflix	2/10/24	2023	Craig Gillespie	Paul Dano	
58	8	2024	Lover, Stalker, Killer	Netflix	2/14/24	2024	Sam Hobkinson	Chris Maher	
59	9	2024	Batman vs Superman: Dawn of Justice	Max	3/4/24	2016	Zack Snyder	Ben Affleck	
60	10	2024	Dune Part One	Max	3/9/24	2021	Denis Villeneuve	Timothée Chalamet	
61	11	2024	The Truth vs Alex Jones	Max	3/28/24	2024	Dan Reed	Alex Jones	
62	12	2024	This Is 40	Netflix	3/30/24	2012	Judd Apatow	Paul Rudd	X
63	13	2024	Juliet, Naked	Max	4/13/24	2018	Jesse Peretz	Rose Byrne	
64	14	2024	Madame Web	Prime Video	4/26/24	2024	SJ Clarkson	Dakota Johnson	
65	15	2024	BlackBerry	Hulu	5/3/24	2024	Matthew Johnson	Jay Baruchel	
66	16	2024	Joyride	Prime Video	5/10/24	2023	Adele Lim	Ashley Park	
67	17	2024	Turtles All The Way Down	Max	5/18/24	2024	Hannah Marks	Isabela Merced	
68	18	2024	Ghostbusters Afterlife	Google TV	6/15/24	2021	Jason Reitman	Finn Wolfhard	
69	19	2024	Inside Out 2	Theater	6/22/24	2024	Kelsey Mann	Amy Poehler	
70	20	2024	Queenpins	Netflix	7/6/24	2021	Gita Pullapilly	Kristen Bell	
71	21	2024	Me, Earl, and the Dying Girl	Max	7/7/24	2015	Alfonso Gomez-Rejon	Thomas Mann	
72	22	2024	Quiz Lady	Hulu	7/13/24	2023	Jessica Yu	Awkwafina	
73	23	2024	Don't Look Up	Netflix	8/3/24	2021	Adam McKay	Leonardo DiCaprio	
74	24	2024	The Hunger Games	Plex	8/4/24	2012	Gary Ross	Jennifer Lawrence	X
75	25	2024	The Hunger Games: Catching Fire	Plex	8/4/24	2013	Francis Lawrence	Jennifer Lawrence	X
76	26	2024	The Hunger Games: Mockingjay Part 1	Plex	8/4/24	2014	Francis Lawrence	Jennifer Lawrence	X
77	27	2024	The Hunger Games: Mockingjay Part 2	Plex	8/5/24	2015	Francis Lawrence	Jennifer Lawrence	X
78	28	2024	The Hunger Games: The Ballad of Songbirds and Snakes	Google TV	8/8/24	2023	Francis Lawrence	Tom Blyth	
79	29	2024	Alien	Disney+	8/9/24	1979	Ridley Scott	Sigourney Weaver	X
80	30	2024	RoboCop	Max	8/9/24	1987	Paul Verhoeven	Peter Weller	
81	31	2024	Aliens	Google TV	8/15/24	1986	James Cameron	Sigourney Weaver	X
82	32	2024	Prometheus	Disney+	8/21/24	2012	Ridley Scott	Noomi Rapace	
83	33	2024	Alien: Romulus	Theater	8/24/24	2024	Fede Álvarez	Cailee Spaeny	
84	34	2024	The Shining	Max	9/2/24	1980	Stanley Kubrick	Jack Nicholson	
85	35	2024	Beetlejuice Beetlejuice	Theater	9/4/24	2024	Tim Burton	Winona Ryder	
86	36	2024	Pan's Labyrinth	Theater	9/28/24	2006	Guillermo Del Toro	Ivana Baquero	
87	37	2024	The Thing	Peacock	10/7/24	1982	John Carpenter 	Kurt Russell	
88	38	2024	Doctor Sleep	Max	10/10/24	2019	Mike Flanagan	Ewan McGregor	
89	39	2024	Saturday Night	Theater	10/12/24	2024	Jason Reitman	Gabriel LaBelle	
90	40	2024	Barbarian	Hulu	10/13/24	2022	Zach Cregger	Georgina Campbell	
91	41	2024	Late Night with the Devil	Shudder	10/14/24	2023	Colin and Cameron Cairnes	David Dastmalchian	
92	42	2024	Talk To me	Netflix	10/14/24	2022	Danny and Michael Philippou	 Sophie Wilde	
93	43	2024	Saw	Peacock	10/18/24	2004	James Wan	Cary Elwas	X
94	44	2024	Saw II	Peacock	10/21/24	2005	Darren Lynn Bousman	Donnie Wahlberg	
95	45	2024	Tucker and Dale vs. Evil	Peacock	10/25/24	2010	Eli Craig	Alan Tudyk	
96	46	2024	Annhilation	Paramount+	10/27/24	2018	Alex Garland	Natalie Portman	X
97	47	2024	The Conjuring	Max	10/27/24	2013	James Wan	Ron Livingston	
98	48	2024	Saw III	Max	11/2/24	2006	Darren Lynn Bousman	Tobin Bell	
99	49	2024	X	Max	11/3/24	2022	Ti West	Mia Goth	
100	50	2024	Four Hours at the Capitol	Max	11/4/24	2021	Jamie Roberts	N/A	
101	51	2024	Heretic	Theater	11/11/24	2024	Scott Beck, Bryan Woods	Hugh Grant	
102	52	2024	Creep	Netflix	11/11/24	2014	 Patrick Brice	Mark Duplass	
103	53	2024	The Babadook	Netflix	11/18/24	2014	Jennifer Kent	Essie Davis	
104	54	2024	Wicked: Part 1	Theater	11/20/24	2024	Jon M. Chu	Ariana Grande	
105	55	2024	Drive Away Dolls	Prime Video	12/2/24	2024	Ethan Coen	Margaret Qualley	
106	56	2024	Woman of the Hour	Netflix	12/15/24	2024	Anna Kendrick	Anna Kendrick	
107	57	2024	My Old Ass	Prime Video	12/30/24	2024	Megan Park	Maisy Stella	
108	1	2025	Hot Rod	Theater	1/15/25	2007	Akiva Schaffer	Andy Samberg	X
109	2	2025	Am I Ok?	Max	1/16/25	2022	Tig Notaro, Stephanie Allynne	Dakota Johnson	
110	3	2025	Vinyl Nation	Prime Video	1/26/25	2022			
111	4	2025	MacGruber	Theater	1/28/25	2010	Jorma Taccone	Will Forte	
112	5	2025	Popstar: Never Stop Never Stopping	Theater	2/4/25	2016	Jorma Taccone, Akiva Schaffer	Andy Samberg	X
113	6	2025	The Menu	Netflix	3/27/25	2022	Mark Mylod	Anya Taylor-Joy	
114	7	2025	The Room	Theater	3/30/25	2003	Tommy Wisseau	Tommy Wisseau	X
115	8	2025	The Disaster Artist	HBO Max	3/31/25	2017	James Franco	James Franco	X
116	9	2025	Waynes World	Paramount+	3/31/25	1992	Penelope Spheeris	Mike Meyers	X
117	10	2025	A Minecraft Movie	Theater	4/11/25	2025	Jared Hess	Jack Black	
118	11	2025	Mission Impossible	Paramount+	5/12/25	1996	Brian De Palma	Tom Cruise	
119	12	2025	Companion	HBO Max	5/21/25	2025	Drew Hancock	Sophie Thatcher	
120	13	2025	Friendship	Theater	5/24/25	2025	Andrew DeYoung	Tim Robinson	
121	14	2025	Pearl	Max	5/25/25	2022	Ti West	Mia Goth	
122	15	2025	Ant Man & The Wasp Quantumania	Disney+	5/29/25	2023	Peyton Reed	Paul Rudd	
123	16	2025	Y2K	Max	6/5/25	2024	Kyle Mooney	Jaeden Martell	
124	17	2025	Mountainhead	Max	6/16/25	2025	Jesse Armstrong	Steve Carrell	
125	18	2025	Mid90s	Netflix	6/20/25	2025	Jonah Hill	Sunny Suljic	
126	19	2025	Love & Mercy	VOD	6/25/25	2015	Bill Pohlad	John Cusack	
127	20	2025	Challengers	Prime Video	6/26/25	2024	Luca Guadagnino	Zendaya	
128	21	2025	The Phoenician Scheme	Theater	7/5/25	2025	Wes Anderson	Benicio Del Toro	
129	22	2025	The Royal Tanenbaums	Disney+	7/23/25	2001	Wes Anderson 	Gene Hackman	X
130	23	2025	Superman	Theater	7/27/25	2025	James Gunn	David Corenswet	
131	24	2025	Fantastic 4: First Steps	Theater	7/27/25	2025	Matt Shakman	Pedro Pascal	
132	25	2025	Final Destination	HBO Max	8/1/25	2000	James Wong	Devon Sawa	
133	26	2025	Bring It On	Theater	9/23/25	2000	Peyton Reed	Kirsten Dunst	X
134	27	2025	Unknown Number: The High School Catfish	Netflix	9/29/25	2025	Skye Borgman		
135	28	2025	Creep 2	Netflix	9/29/25	2017	Patrick Brice	Mark Duplass	
136	29	2025	The Princess Bride	Disney+	10/1/25	1987	Rob Reiner	Cary Elwes	X
137	30	2025	The Naked Gun	Paramount+	10/2/25	2025	Akiva Schaffer	Liam Neeson	
138	31	2025	Hereditary	HBO Max	10/4/25	2018	Ari Aster	Toni Collette	
139	32	2025	Kiki's Delivery Service	HBO Max	10/5/25	1989	Hayao Miyazaki	Kirsten Dunst	
140	33	2025	KPop Demon Hunters	Netflix	10/9/25	2025	Maggie Kang	Arden Cho	
141	34	2025	Adventureland	Plex	10/13/25	2009	Greg Motolla	Jesse Eisenberg	X
142	35	2025	The Substance	HBO Max	10/14/25	2024	Coralie Fargeat	Demi Moore	
143	36	2025	Midsommar	HBO Max	10/16/25	2019	Ari Aster	Florence Pugh	
144	37	2025	The Perfect Neighbor	Netflix	11/14/25	2025			
145	38	2025	Weapons	HBO Max	11/15/25	2025	Zach Creeger		
146	39	2025	Wicked: For Good	Theater	11/23/25	2025	John Cho	Ariana Grande	
147	40	2025	Predator: Badlands	Theater	11/26/25	2025			
148	41	2025	Happy Christmas	Hulu	12/24/25	2014	Joe Swanberg	Anna Kendrick	
149	42	2025	Have You Seen Me Lately	HBO Max	12/28/25	2025	Amy Scott Elizabeth	Adam Duritz	
150	43	2025	What If (The F-Word)	VOD	12/30/25	2013	Michael Dowse	Daniel Radcliffe	
151	1	2026	Knives Out: Wake up Dead Men	Peacock	1/15/26	2025	Rian Johnson	Daniel Craig	
152	2	2026	Sinners	HBO Max	1/22/26	2025	Ryan Coogler	Michael B. Jordan	
153	3	2026	28 Years Later	Theater	2/4/26	2025	Danny Boyle	Alfie Williams	
154	4	2026	Drop	Prime Video	2/14/26	2025	Christopher Landon	Meghann Fahy	
155	5	2026	Anora	Hulu	2/14/26	2024	Sean Baker	Mikey Madison	
156	6	2026	Fear Of Flying	VOD	2/16/26	2025	Mark Phinney	Mike Mitchell	
157	7	2026	I Saw The TV Glow	HBO Max	2/20/26	2024	Jane Schoenbrun	Justice Smith	
158	8	2026	Nebraska	VOD	3/2/26	2013	Alexander Payne	Bruce Dern	
159	9	2026	They Will Kill You	Theater	3/23/26	2026	Kirill Sokolov	Zazie Beetz	
160	10	2026	Project Hail Mary	Theater	3/29/26	2026	Phil Lord and Christopher Miller	Ryan Gosling	
161	11	2026	The Super Mario Galaxy Movie	Theater	4/1/26	2026	Aaron Horvath and Michael Jelenic	Chris Pratt	
162	12	2026	Smile	Hulu	4/2/26	2022	Parker Finn	Sosie Bacon	
163	13	2026	Ready Or Not	HBO Max	4/10/26	2019	Tyler Gillett, Matt Bettinelli-Olpin	Samara Weaving	
164	14	2026	Ready or Not 2	Theater	4/15/26	2026	Tyler Gillett, Matt Bettinelli-Olpin	Samara Weaving	
165	15	2026	Mortal Kombat	HBO Max	4/25/26	2021	Simon McQuoid	Lewis Tan	
166	16	2026	Smile 2	Paramount+	4/27/26	2024	Parker Finn	Naomi Scott	
167	17	2026	D(e)ad	VOD	5/1/26	2025	Izzy Roland	Izzy Roland	
168	18	2026	Obsession 	Theater	5/16/26	2026	Curry Barker	Inde Navarrette	
169	19	2026	Mortal Kombat II	Theater	5/17/26	2026	Simon McQuoid	Karl Urban	
170	20	2026	Star Wars: A New Hope	Disney+	5/25/26	1977	George Lucas	Mark Hamill	X"""

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Check if year is 2-digit or 4-digit
        parts = date_str.split('/')
        if len(parts[-1]) == 2:
            return datetime.strptime(date_str, '%m/%d/%y').date()
        else:
            return datetime.strptime(date_str, '%m/%d/%Y').date()
    except ValueError:
        return None

def run_backfill():
    # Clear existing movies to ensure a clean start and no duplicates from partial runs
    Movie.query.delete()
    db.session.commit()
    
    f = io.StringIO(DATA)
    reader = csv.DictReader(f, delimiter='\t')
    
    count = 0
    for row in reader:
        title = row['Movie Title']
        year_of_release = row['Year of Release']
        date_watched = parse_date(row['Date Watched'])
        provider = row['Provider']
        # Normalize providers
        if provider == 'Disney+':
            provider = 'Disney Plus'
        elif provider == 'HBO Max': # Some older entries might be Max
            provider = 'HBO Max' 
        
        is_rewatch = True if row['Rewatch'] == 'X' else False

        print(f"Processing: {title} ({year_of_release})...")

        # Attempt TMDB Enrichment

        tmdb_id = None
        search_results = TMDBService.search_movies(title)
        
        # Find exact year match if possible
        for res in search_results:
            res_year = res.get('release_date', '')[:4]
            if res_year == year_of_release:
                tmdb_id = res.get('id')
                break
        
        if not tmdb_id and search_results:
            tmdb_id = search_results[0].get('id')
        
        if tmdb_id:
            details = TMDBService.get_movie_details(tmdb_id)
            if details:
                # Extract details
                credits = details.get('credits', {})
                cast = ", ".join([member.get('name') for member in credits.get('cast', [])[:5]])
                directors = ", ".join([member.get('name') for member in credits.get('crew', []) if member.get('job') == 'Director'])
                writers = ", ".join([member.get('name') for member in credits.get('crew', []) if member.get('department') == 'Writing'])
                
                # Certification
                certification = "N/A"
                release_dates = details.get('release_dates', {}).get('results', [])
                for rd in release_dates:
                    if rd.get('iso_3166_1') == 'US':
                        for release in rd.get('release_dates', []):
                            cert = release.get('certification')
                            if cert:
                                certification = cert
                                break
                        break
                
                # Trailer
                trailer_url = None
                videos = details.get('videos', {}).get('results', [])
                for video in videos:
                    if video.get('site') == 'YouTube' and video.get('type') == 'Trailer':
                        trailer_url = f"https://www.youtube.com/embed/{video.get('key')}"
                        break
                
                # Wiki
                external_ids = details.get('external_ids', {})
                wiki_id = external_ids.get('wikidata_id')
                wiki_url = f"https://www.wikidata.org/wiki/{wiki_id}" if wiki_id else None
                
                new_movie = Movie(
                    title=details.get('title'),
                    release_year=int(year_of_release) if year_of_release.isdigit() else None,
                    external_id=str(tmdb_id),
                    imdb_id=details.get('imdb_id'),
                    director=directors or row['Director'],
                    writer=writers or row.get('Writer', ''),
                    leading_actors=cast or row['Leading Actors'],
                    plot=details.get('overview'),
                    poster_path=details.get('poster_path'),
                    user_score=details.get('vote_average'),
                    runtime=details.get('runtime'),
                    certification=certification,
                    budget=details.get('budget'),
                    revenue=details.get('revenue'),
                    trailer_url=trailer_url,
                    wikipedia_url=wiki_url,
                    provider=provider,
                    is_revisit=is_rewatch,
                    date_watched=date_watched
                )
                db.session.add(new_movie)
                count += 1
            else:
                tmdb_id = None # Fallback
        
        if not tmdb_id:
            new_movie = Movie(
                title=title,
                release_year=int(year_of_release) if year_of_release.isdigit() else None,
                director=row['Director'],
                leading_actors=row['Leading Actors'],
                provider=provider,
                is_revisit=is_rewatch,
                date_watched=date_watched
            )
            db.session.add(new_movie)
            count += 1
        
        # Commit every 10 movies to avoid timeouts
        if count % 10 == 0:
            db.session.commit()

    db.session.commit()
    return count
