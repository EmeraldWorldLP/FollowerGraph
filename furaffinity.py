import requests
import json
import signal
import sys
from collections import deque
import csv
import concurrent.futures

# Global variables to store results
results_by = {}
results_to = {}

def save_to_json(data, filename):
    """
    Saves the given data to a JSON file.
    
    Args:
    data (dict): The data to be saved.
    filename (str): The name of the file to save the data in.
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def signal_handler(sig, frame):
    """
    Signal handler to catch interrupt signal and save current results.
    """
    print("\nInterrupt received, saving current results...")
    save_to_json(results_by, 'watchlist_by_results.json')
    save_to_json(results_to, 'watchlist_to_results.json')
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def get_watchlist_to(username, cookies, bfs=False, start_page=1):
    watchlist_to = []
    page_num = start_page
    while True:
        try:
            url = f"https://furaffinity-api.herokuapp.com/user/{username}/watchlist/to/{page_num}/"
            headers = {'Content-Type': 'application/json'}
            data = {"cookies": cookies, "bbcode": False}
            print(f"Fetching URL: {url}")
            response = None
            
            while response is None:
                try:
                    response = requests.post(url, headers=headers, json=data)
                except requests.exceptions.ConnectionError:
                    print("Connection error occurred. Retrying...")
            
            if response.status_code == 200:
                print(f"Successfully fetched watchlist for {username} - Page {page_num}")
                page_data = response.json()
                if not page_data or 'results' not in page_data or not page_data['results']:
                    break
                watchlist_to.extend([{"name": user["name"]} for user in page_data['results']])
                page_num += 1
            else:
                print(f"Failed to fetch watchlist for {username}, status code: {response.status_code}")
                break
        except requests.exceptions.ConnectionError:
            print("Connection error occurred. Retrying...")
            continue

    return watchlist_to, page_num

def fetch_watchlists(usernames, cookies, bfs=False, pages_per_user=10):
    global results_to
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_watchlist_to, username, cookies, bfs, start_page=1): username for username in usernames}
        
        for future in concurrent.futures.as_completed(futures):
            username = futures[future]
            watchlist_to, _ = future.result()
            print(f"Watchlist to {username}: {watchlist_to}")
            results_to[username] = watchlist_to
            
            # Save the results for the current user after fetching all pages
            save_to_json(results_to, 'watchlist_to_results.json')

def main(usernames, cookies, bfs=False):
    global results_to

    # Fetch watchlists for existing usernames
    fetch_watchlists(usernames, cookies, bfs)

    # Create a dictionary to store the count of shared followers between each pair of users
    shared_followers = {}

    # Iterate through each pair of usernames in the main function
    for i in range(len(usernames)):
        for j in range(i + 1, len(usernames)):
            user1 = usernames[i]
            user2 = usernames[j]
            
            # Get the watchlist data for each user
            watchlist_user1 = [user['name'] for user in results_to.get(user1, [])]
            watchlist_user2 = [user['name'] for user in results_to.get(user2, [])]
            
            # Calculate the number of shared followers
            shared_followers[(user1, user2)] = len(set(watchlist_user1).intersection(set(watchlist_user2)))

    # Write the shared followers data to edges.csv
    with open('edges.csv', 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for (user1, user2), count in shared_followers.items():
            csv_writer.writerow([user1, user2, count])

    # Calculate the total watchlist count for each user and write to labels.csv
    with open('watchlist_to_results.json') as f:
        watchlist_to_data = json.load(f)
        
        user_watchlist_count = {user: len(watchlist) for user, watchlist in watchlist_to_data.items()}
        
        with open('labels.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Id', 'Total Watchlist Count'])
            for user, count in user_watchlist_count.items():
                csv_writer.writerow([user, count])

if __name__ == "__main__":
    usernames = ['asloosh', 'catboyzz', 'eliotak', 'pewbutt', 'huffywhuffers', 'thundra~', 'jigglypuffer', 'onehandsomefox', 'midsummernightsdream', 'gluttonousguzzlord', '-xero', 'honeytoxant', 'saffronmilkcap', 'bignlarge', 'fayse', 'home-made', 'crestdraggy', 'pumppumppop', 'fauvfox', 'unfunnyjeyai', 'blushysnoots', 'daddyzagur', 'themadcatter', 'mountaindewdrawer', 'plat', 'ltoo', 'catsikune', 'electricfire', 'bucklerparry', 'chubberdy', 'jacalope', 'birdo', 'pakaproductions', 'sketchygenet', 'nyil', 'fattybread', 'miromax-inc.', 'mistymistmi', 'minedoo', 'shibadoodles', 'kygen', 'theboldcharr', 'skaifox', 'loquaciousjango', 'tuzzleton', 'mazhthegrey', 'anuvia', 'boltheeye', 'valerayu', 'djfatshepherd', 'fatglaz', 'syc', 'smokeygraypaws', 'shadowthehedhehogsimp', 'guyfuy', 'gamingmarko', 'lugiaberry', 'castdraws', 'coldquarantine', 'fattoid', 'weegeethedoggo', 'naughtybutt', 'angryantlers', 'quesomancer', 'cro-iba', 'retrowave', 'camuushamuu', 'kikatsu', 'shineyfox123', 'carnalcervidae', 'roundwombo', 'greenendorf', 'hungrybehemoth', 'chocolateandmilk', 'lizardsoup', 'widewobblyproductions', '-kronexfire-', 'rumash', 'howlfykofu', 'tcw', 'careforsomemore', 'kinnghyena', 'chich121', 'azurewolfx', 'chunkaz0id', 'flamboyantone', 'scaliecrocs', 'borisgrim', 'spottedtigress', 'koolish', 'wouhlven', 'squibbleart', 'kouhicoffee', 'mistko', 'anonymousman69nice', 'kyxrra', 'patacon', 'crediblemyth', 'yoshixeros', 'velkno', 'archy101', 'jangleforks', 'misterfaceless', 'robirobi', 'rabid', 'wolkewolf', 'randomgayfox', 'mitzix', 'vorchitect', 'shysho', 'fat', 'professorxii', 'jelliroll', 'milk-knight', 'aurelina', 'nkil', 'daebelly', 'thatbluewhale', 'yina', 'pillowbun', 'wingnutxlv', 'agnilla', 'captainelderly', 'maddeku', 'faithdoe', 'floofymeister', 'scheibutts', 'travister', 'pierrotthevagabond', 'dogburger', 'mcpossum', 'cowcollar', 'roundanimal', 'awolf', 'dandydays', 'darkcresentskymin', 'tehsquishyray', 'deerbelly', 'hishipy', 'almeric', 'sxfpantera', 'toxictoby', 'swatchfodder', 'charchu', 'lionalliance', 'logtut', 'atlaspost', 'aimbot-jones', 'tubacat', 'draconder', 'vdisco', 'liquid-savage', 'fawxen', 'lcshian', 'slatly', 'shepherd0821', 'chunkymoth', 'eon54', 'juicybubble', 'pearybear', 'trinitystrike', 'fatxolotl', 'chirpsalot', 'erichtofen', 'brennanhalls', 'afrothicc720', 'softfoxxo', 'boxmingle', 'fathips', 'trinityfate62', 'reyriders', 'pearypanda', 'silver-stag', 'nekobaron', 'pengs', 'n4t4s-angel', 'mairari', 'beanbagbellycafe', 'preney', 'huwon', 'mazaku', 'dragontzin', 'sugarboy', 'jeffpat', 'cowdypie', 'nastyboys', 'dulynoted', 'nekomata.', 'chunkychips', 'coffeequasar', 'sethmanthedragon', 'newtonthedog', 'krocomaw', 'aikoarts', 'gritzoz', 'araidian', 'cn57', 'lotharkushala', 'arkveveen', 'rahiros', 'massiveguild', 'holidaysoftfox', 'chocowerehound', 'butterflux', 'aokmaidu', 'jirobas', 'volkenfox', 'nolovehugepleb', 'thesammon', 'nennsen', 'smokeygraypaws', 'frozedfrenchdragon', 'robthehoopedchipmunk', 'kazecat', 'lotsofmoon', 'superix', 'squishypsycho', 'azsola', 'gluttonous.cake', 'saonimorro', 'k9wolf', 'croccarnal', 'satoshikumada', 'theguynooneremembers', 'biglovealicia', 'rushrabbit', 'omeome', 'demolitionman', 'grosbald', 'tawnyscrawnyleo', 'gravitysecretagent', 'thefoxbro', 'gillpanda', 'thunderkid92', 'brashotter', 'boot', 'possywossy', 'redpixie', '0-3-5-4', 'syntaxaero', 'seachomps', 'immoralwacha', 'saonimorro', 'pawberry', 'aquamix', 'qweave', 'tach0012', 'curritos', 'wamnugget', 'chonky-shark', 'miluoxie', 'unixcat', 'area-break', 'veryfilthything', 'alek.s', 'kinkaxa', 'otterpupps', 'fabiantheprotogen', 'elektr0', 'cracker.', 'indigo2', 'aucherr', 'snotdrips', 'vulpgulps', 'eddybelly', 'saintdraconis', 'kuronekocoffee', 'jouigidragon', 'xxedge', 'pusinie', 'cantielabs', 'crestdraggy', 'catarsi', 'cuchuflehest', 'palenque', 'roppu', 'redphlannel', 'cchilab', 'plushpuff', 'callmems', 'takarachan', 'weighty-kyte', 'borisbearr', 'derfisch', 'abthegreat', 'wamnugget', 'okaeri', 'chubby-shark', 'wideshark', 'darrkemperor', 'pillowopossum', 'artisipancake', 'kelpu', 'kkoart', 'blueberryroti', 'doxxylbox', 'silverfang725', 'beverage', 'homemosaco', 'huhunya', 'sumisune', 'gummyfruitcup', 'sleepyheadspoosha', 'javcavk541', 'thatoneaceguy', 'zaphod-', 'cirronaja', 'haloopdy', 'decafbat', 'maxine-dragon-787', 'ahjerchubbywolf', 'calorie', 'milkmeats', 'garudasix', 'adansin', 'vomits', 'hitodama', 'carcupholder', 'feyfoxen', 'mochi-squish', 'pillowpatche', 'puffwuffballoon', 'incidental', 'shweetmagnet', 'awesomnater', 'saintsucrose', 'or-fi-s', 'museuk', 'gnarly-gnasties', 'dondedun', 'orcalx', 'randomguy645', 'inuzu', 'xnonax', 'javcavk541', 'slimecatt', 'heavydoodles', 'cavios', 'batspid2', 'the-netwayman', 'hosinokedama', 'okaeri', 'smokeydraws', 'doncogneetoe', 'chubbypuppies', 'mexifurfoof', 'wenisberry', 'evkem', 'astrozone', 'pastelgeneticist', 'orbyssey', 'haradoshin', 'inksplot', 'porcine', 'grimbler', 'trubbol', 'reshirii', 'aquatin', 'chimeracauldron', 'biowhat', 'nyuufruit', 'cynicalfluff', 'yellowhellion', 'mk-artichoke', 'gil~', 'smolsnuff', 'saltypantz', 'heftyhorsehostler', 'bluebrush', 'fattydragonite']
    cookies = [
        {"name": "b", "value": ""},
        {"name": "a", "value": ""},
        {"name": "sz", "value": ""}
    ]
    main(usernames, cookies, bfs=False)