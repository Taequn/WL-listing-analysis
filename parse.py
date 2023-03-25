import requests
from bs4 import BeautifulSoup
import json
import datetime
import pandas as pd
from urllib.request import Request, urlopen
import re
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class Listings:
    def __init__(self):
        self.df = pd.DataFrame(columns=['Date', 'Link', 'Collection', 'Discord', 'Twitter', 'Supply', 'Platform', 'Price'])


    def coinmarketcap(self):
        def convert_date_format(date_str):
            date_str = date_str.replace("GMT+8", "").replace("UTC", "").replace("AM", "").replace("PM", "").strip()
            date_formats = ["%B %d, %Y %H:%M", "%Y-%m-%d %H:%M:%S",
                            "%B %d, %Y"]
            
            for fmt in date_formats:
                try:
                    dt = datetime.datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            raise ValueError("No matching date format found")


        df = pd.DataFrame()
        print("Checking CoinMarketCap")
        for i in range(1, 3):
            print("Page: {}".format(i))
            request = requests.get("https://coinmarketcap.com/nft/upcoming/?page={}".format(i))

            body = request.text
            soup = BeautifulSoup(body, 'html.parser')

            #Working with data
            script = soup.find("script", id="__NEXT_DATA__")
            json_data = json.loads(script.text)
            upcoming_nfts = json_data["props"]["pageProps"]["upcomingNFTs"]["upcomings"]

            for upcoming_nft in upcoming_nfts:
                date = upcoming_nft["dateTime"]
                try:
                    date = convert_date_format(date)
                except ValueError:
                    continue
                price = upcoming_nft["mintPrice"][:-4]
                df = df.append({"Date": date, "Link": upcoming_nft["website"], "Collection": upcoming_nft["name"],
                                "Discord": upcoming_nft["discord"], "Twitter": upcoming_nft["twitter"], "Supply": upcoming_nft["volume"],
                                "Platform": upcoming_nft["platform"], "Price": price}, ignore_index=True)
        df['Listing'] = 'CoinMarketCap'
        #iterate through the column Date and print the value
        self.df = self.df.append(df, ignore_index=True)

    def nftreminder(self):
        df=pd.DataFrame()
        print("Checking NFTReminder")

        #results = response.json()['results'][0]
        request = requests.get("https://nftreminder.io/listing/?today=on&tomorrow=on&next=on")
        
        #body =  results['content']
        body = request.text
        soup = BeautifulSoup(body, 'html.parser')

        #Working with data
        collection_blocks = soup.find_all("div", class_="collection-block")

        for collection_block in collection_blocks:
            date = collection_block.find("div", class_="date").text.strip()
            date = datetime.datetime.strptime(date, '%d %B, %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                date = "2023" + date[4:]
                date = datetime.datetime.strptime(date, '%d %B, %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

            link = collection_block.find("a")["href"]
            collection = collection_block.find("div", class_="title").a.text.strip()
            discord = collection_block.find_next("div", class_="item item-discord").a["href"]
            twitter = collection_block.find_next("div", class_="item item-twitter").a["href"]
            supply = collection_block.find_next("div", class_="item item-count").text.strip()
            platform = collection_block.find_next("div", class_="item item-platforms").img["alt"]
            
            if(platform == "ETH"):
                platform = "Ethereum"
            elif(platform == "BSC"):
                platform = "Binance Smart Chain"
            elif(platform == "MATIC"):
                platform = "Polygon"
            elif(platform == 'SOL'):
                platform = "Solana"
            
            
            price = collection_block.find_next("div", class_="item item-price").text.strip()
            price = re.findall(r'\d+\.\d+|\d+', price)[0]
            

            df = df.append({"Date": date, "Link": link, "Collection": collection, "Discord": discord, "Twitter": twitter, "Supply": supply, "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'NFTReminder'
        self.df = self.df.append(df, ignore_index=True)

    def raritysniper(self):
        df = pd.DataFrame()
        print("Checking Rarity Sniper")

        request = requests.get("https://raritysniper.com/nft-drops-calendar")
        body =  request.text
        soup = BeautifulSoup(body, 'html.parser')


        scripts = soup.find_all("script", type="application/json", attrs={"data-ttl": "30"})

        script = scripts[0]
        json_data = json.loads(script.text)['body']
        json_data = json.loads(json_data)['hits']

        for data in json_data:
            collection = data['document']
            timestamp = collection['saleDate']/1000
            date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            #{'blockchain': 'ethereum', 'collectionName': 'SPACE GIRL PASS', 'discordMemberCount': 0, 'discordUrl': '', 'id': '77835', 'image': 'https://media.raritysniper.com/upcoming/space-girl-pass.webp', 'presaleDate': 1675897866050, 'published': True, 'saleDate': 1676178000000, 'salePrice': 0.001, 'supply': 1000, 'twitterHandle': 'spacegirl_nft', 'websiteUrl': 'https://japannftmuseum.one/spacegirl'}
            df = df.append({"Date": date, "Link": collection["websiteUrl"], "Collection": collection["collectionName"],
                            "Discord": collection["discordUrl"], "Twitter": collection["twitterHandle"], "Supply": collection["supply"],
                            "Platform": collection["blockchain"].capitalize(), "Price": collection["salePrice"]}, ignore_index=True)

        df['Listing'] = 'Rarity Sniper'
        self.df = self.df.append(df, ignore_index=True)

    def upcomingnft(self):
        df = pd.DataFrame()
        print("Checking UpcomingNFT.net")

        url = 'https://upcomingnft.net/wp-json/wp/v2/event/calender'
        r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(r).read()
        json_data = json.loads(response)
        for data in json_data:
            try:
                data["public_date"] = datetime.datetime.strptime(data["public_date"], '%d %b %Y-%I:%M %p (UTC)').strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                data['public_date'] = "TBA"

            df = df.append({"Date": data["public_date"], "Link": data["thundergamestudio_url"], "Collection": data["title"],
                            "Discord": data["discord_url"], "Twitter": data["twitter_url"], "Supply": data["wpcf-event-supply"],
                            "Platform": "Ethereum", "Price": data["wpcf-price"]}, ignore_index=True)
        df['Listing'] = 'UpcomingNFT.net'
        self.df = self.df.append(df, ignore_index=True)

    def nearingnft(self):
        df = pd.DataFrame()
        print("Checking NearingNFT.net")

        url = 'https://www.nearingnft.net/api/v1/filter-data/?path=%2F&filter=upcoming'
        r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(r).read()
        json_data = json.loads(response)
        html_body = json_data['data']
        soup = BeautifulSoup(html_body, 'html.parser')
        divs = soup.find_all("div", class_="row")
        for div in divs:
            name = div.find("h3", class_='d-inline').text.strip()
            date = div.find('div', class_=re.compile('card-date')).text.strip() + " 2023"
            date = datetime.datetime.strptime(date, '%b %d %Y').strftime("%Y-%m-%d")


            try:
                twitter = div.find('a', title=name+"'s twitter").get('href')
            except AttributeError:
                twitter = ''

            try:
                website = div.find('a', title=name+"'s website").get('href')
            except AttributeError:
                website = ''

            try:
                discord = div.find('a', title=name+"'s discord").get('href')
            except AttributeError:
                discord = ''


            socials = div.find('ul', class_='card-socials')
            socials = socials.find_all('li')
            price = socials[0].text.strip()

            platform = socials[0].find('img').get('alt').split(" ")[0]
            platform = platform[0].upper() + platform[1:]

            df = df.append({"Date": date, "Link": website, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": 'N/A',
                            "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'NearingNFT.net'
        self.df = self.df.append(df, ignore_index=True)


    def luckytrader(self):
        df = pd.DataFrame()
        print("Checking NearingNFT.net")

        url = 'https://luckytrader.com/nft/schedule?category=1'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        script = soup.find("script", id="__NEXT_DATA__")
        json_data = json.loads(script.text)
        nfts = json_data['props']['pageProps']['events']
        for nft in nfts:
            name = nft['title']
            try:
                date = nft['date']
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")
            except KeyError: date = 'TBA'

            try: twitter = nft['twitterHandle']
            except KeyError: twitter = ''

            try: discord = nft['discordLink']
            except KeyError: discord = ''

            try: platform = nft['project']['blockchain']['name']
            except KeyError: platform = ''

            try:
                supply = nft['summary']
                supply = re.findall(r'\d+', supply)
                supply = ''.join(supply)
            except KeyError: supply = ''

            description = nft['description']
            #pull out the first url from the description
            try:
                link = re.findall(r'(https?://[^\s]+)', description)[0][:-1]
            except:
                link = ''


            try:
                price = re.findall(r'\d+\.?\d*', description)[0]
                price = float(price)
            except:
                price = ''

            df = df.append({"Date": date, "Link": link, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'LuckyTrader.com'
        self.df = self.df.append(df, ignore_index=True)

    def crypto(self):
        df = pd.DataFrame()
        print("Checking Crypto.com")

        iteration = True
        page_number = 1
        while iteration:
            url = 'https://price-api.crypto.com/nft/v1/calendar/upcoming?page={}&type=1&limit=20'.format(page_number)
            request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(request).read()
            json_data = json.loads(response)
            nfts = json_data['data']['data']
            if(len(nfts) <= 20):
                iteration = False
            else:
                page_number += 1


            for nft in nfts:
                name = nft['collection']
                try:
                    date = nft['release_date']
                    date = datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date = nft['release_date']

                twitter = nft['twitter_url']
                discord = nft['discord_url']
                platform = nft['blockchain']
                supply = nft['assets']
                price = nft['mint_price']
                link = nft['website_url']

                df = df.append({"Date": date, "Link": link, "Collection": name,
                                "Discord": discord, "Twitter": twitter, "Supply": supply,
                                "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'Crypto.com'
        self.df = self.df.append(df, ignore_index=True)

    ####################
    #Gottaa FIX it.
    ####################
    def magic_eden(self):
        df = pd.DataFrame()
        print("Checking Magic Eden")

        with open('data/me.json') as f:
            json_data = json.load(f)

        for nft in json_data:
            try:
                date = nft['launchDate']
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

            name = nft['name']
            price = ''

            try: twitter = nft['links']['twitter']
            except KeyError: twitter = ''

            try: discord = nft['links']['discord']
            except KeyError: discord = ''

            try: link = nft['links']['website']
            except KeyError: link = ''

            try: platform = nft['blockchain']
            except KeyError: platform = ''

            description = nft['description']
            try:
                supply = re.findall(r'\d+', supply)
                supply = ''.join(supply)
            except: supply = ''

            df = df.append({"Date": date, "Link": link, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'Magic Eden'
        self.df = self.df.append(df, ignore_index=True)


    def mintyscore(self):
        df = pd.DataFrame()
        print("Checking mintyscore.com")

        url = 'https://api.mintyscore.com/api/v1/nfts/projects?desc=true&chain=all&status=upcoming&sort_by=like_count&include_hidden=false'
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(request).read()
        json_data = json.loads(response)
        nfts = json_data['result']

        for nft in nfts:
            try:
                date = nft['sale_date']
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00').strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

            name = nft['name']
            price = nft['price_info']
            if(price == '' or price=='TBA'):
                price = 'TBA'
            else:
                price = re.findall(r'\d+\.\d+', price)
                price = ''.join(price)

            discord = nft['discord_link']
            twitter = nft['twitter_link']
            link = nft['website_link']
            platform = nft['chain'].capitalize()

            try:
                supply = nft['supply_info']
                supply = re.findall(r'\d+', supply)
                supply = ''.join(supply)
            except: supply = ''

            df = df.append({"Date": date, "Link": link, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'MintyScore'
        self.df = self.df.append(df, ignore_index=True)


    def raritytools(self):
        df = pd.DataFrame()
        print("Checking rarity.tools")

        url = 'https://collections.rarity.tools/upcoming2'
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage)
        nfts = data[2:]

        for nft in nfts:
            name = nft['Project']
            try:
                date = nft['Sale Date']
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

            try: twitter = nft['TwitterId']
            except KeyError: twitter = ''

            try: discord = nft['Discord']
            except KeyError: discord = ''

            try: link = nft['Website']
            except KeyError: link = ''

            try: supply = nft['Max Items']
            except KeyError: supply = ''

            try:price = nft['Price']
            except KeyError: price = ''
            
            try:
                platform = nft['Price Text']

                if 'SOL' in platform:
                    platform = 'Solana'
                elif 'ETH' in platform:
                    platform = 'Ethereum'
                elif 'ADA' in platform:
                    platform = 'Cardano'
                elif 'TBA' in platform:
                    price = 'TBA'
                    platform = ''
                else:
                    platform = ''
            except: platform = 'Ethereum'
            



            df = df.append({"Date": date, "Link": link, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)
        df['Listing'] = 'RarityTools'
        self.df = self.df.append(df, ignore_index=True)


    def seafloor(self):
        df = pd.DataFrame()
        print("Checking seafloor.io")

        url = 'https://seafloor.io/assets/js/collection_test.php'
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        nfts = json.loads(webpage)

        for nft in nfts:
            name = nft['name']
            try:
                date = nft['dateTime']
                date = datetime.datetime.strptime(date, '%B %d, %Y %I:%M %p GMT+8').strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

            try: twitter = nft['twitter']
            except KeyError: twitter = ''

            try: discord = nft['discord']
            except KeyError: discord = ''

            try: link = nft['website']
            except KeyError: link = ''

            try: supply = nft['volume']
            except KeyError: supply = ''

            try:price = nft['mintPrice']
            except KeyError: price = ''

            try: platform = nft['platform']
            except KeyError: platform = ''

            df = df.append({"Date": date, "Link": link, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price[:-3]}, ignore_index=True)

        df['Listing'] = 'Seafloor'
        self.df = self.df.append(df, ignore_index=True)

    def nfteller(self):
        df = pd.DataFrame()
        print("Checking nfteller.io")

        url = 'https://nfteller.io/nft-calendar-drops/?_page=1&num=100&sort=post_published'

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')

        nfts = soup.find_all('div', class_='drts-col-12 drts-view-entity-container')
        for nft in nfts:
            name = nft.find("a", {"data-content-name": "nft_calander_dir_ltg"}).text
            platform = nft.find('div', class_='list_chain').text.strip()
            try:
                date = nft.find('time', class_='drts-datetime').text.strip() + ' 2023'
                date = datetime.datetime.strptime(date, '%d %b %Y').strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

            links = nft.find_all('div', class_='drts-entity-field-value')
            discord = ''
            twitter = ''
            supply = ''
            price = ''
            for url in links:
                link = url.find('a')
                if link:
                    link = link.get('href')
                    if 'discord' in link:
                        discord = link
                    elif 'twitter' in link:
                        twitter = link
                    elif 'Link' in url.text:
                        link = link
                else:
                    time_test = url.find('time')
                    if time_test:
                        continue
                    else:
                        text = url.text
                        numbers = re.findall(r'\d+', text)
                        numbers = ''.join(numbers)
                        if numbers:
                            if(int(numbers) > 200):
                                supply = numbers
                            else:
                                price = numbers


        df = df.append({"Date": date, "Link": link, "Collection": name,
                        "Discord": discord, "Twitter": twitter, "Supply": supply,
                        "Platform": platform, "Price": price}, ignore_index=True)

        df['Listing'] = 'NFTeller'
        self.df = self.df.append(df, ignore_index=True)

    def nftevening(self):
        df = pd.DataFrame()
        print("Checking nftevening.com")

        url = 'https://calendar.nftevening.com/calendar/page/1'

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html.parser')

        nfts = soup.find_all('div', class_='details')
        for nft in nfts:
            name = nft.find('h2', class_='title').text.strip()
            table = nft.find('table', class_='metas')
            rows = table.find_all("tr")

            try: blockchain = rows[0].find_all("td")[1].text.strip()
            except IndexError: blockchain = ''

            try: supply = rows[1].find_all("td")[1].text.strip()
            except IndexError: supply = ''

            try: price = rows[2].find_all("td")[1].text.strip()
            except IndexError: price = ''

            date = nft.find('div', class_='counter').get('drop_date')
            date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S")

            socials = nft.find('ul', class_='social')
            links = socials.find_all('a')
            for url in links:
                if 'discord' in url.get('href'):
                    discord = url.get('href')
                elif 'twitter' in url.get('href'):
                    twitter = url.get('href')
                else:
                    link = url.get('href')

            df = df.append({"Date": date, "Link": link, "Collection": name,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": blockchain, "Price": price}, ignore_index=True)

        df['Listing'] = 'NFT Evening'
        self.df = self.df.append(df, ignore_index=True)

    def icytools(self):
        df = pd.DataFrame()
        print("Checking icy.tools")

        url = 'https://icy.tools/calendar'

        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')

        json_data = soup.find('script', type='application/json').text
        json_data = json.loads(json_data)['apolloState']['ROOT_QUERY']['calendarEvents({"filter":{"isPublished":true},"skip":0,"take":50})']

        for entry in json_data:
            date = entry['startDatetime']
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")
            link = entry['websiteUrl']
            collection = entry['title']
            discord = entry['discordUrl']
            twitter = entry['twitterUsername']
            supply = entry['totalSupply']
            platform = entry['blockchain']
            platform = platform[0].upper() + platform[1:].lower()
            price = entry['price']

            df = df.append({"Date": date, "Link": link, "Collection": collection,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)

        df['Listing'] = 'Icy Tools'
        self.df = self.df.append(df, ignore_index=True)


    def nftsolana(self):
        df = pd.DataFrame()
        print('Checking nftsolana.io')

        url = 'https://nftsolana.io/'
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')

        try:
            json_data = soup.find_all('script', type='application/ld+json')[1]
        except IndexError:
            return
        entries = json.loads(json_data.text)

        for entry in entries:
            date = entry['startDate']
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00').strftime("%Y-%m-%d %H:%M:%S")
            link = entry['url']
            collection = entry['name']

            description = entry['description']
            description = description.split('&lt;br /&gt;\\n')
            discord = ''
            twitter = ''
            supply = ''
            price = ''
            website = ''


            for line in description:
                if 'discord' in line:
                    try:
                        discord = line.split('&quot;')[1]
                    except IndexError:
                        sentences = line.split('.')
                        for sentence in sentences:
                            if 'discord.gg' in sentence:
                                discord = sentence.strip()

                if 'twitter' in line:
                    twitter = line.split('&quot;')[1]
                if 'Supply' in line:
                    supply = line.split('&lt;/b&gt;')[1]
                if 'Mint' in line:
                    price = line.split('&lt;/b&gt;')[1]
                if 'Website' in line:
                    website = line.split('&quot;')[1]
            platform = 'Solana'

            df = df.append({"Date": date, "Link": link, "Collection": collection,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)

        df['Listing'] = 'NFTSolana.io'
        self.df = self.df.append(df, ignore_index=True)

    def nextdrop(self):
        df = pd.DataFrame()
        print("Checking nextdrop.is")

        url = 'https://nextdrop.is/upcoming-nft-drops'
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')

        # find all <tr> tags
        entries = soup.find_all('tr')

        for entry in entries:
            columns = entry.find_all('td')
            date = ''
            link = ''
            collection = ''
            discord = ''
            twitter = ''
            supply = ''
            platform = ''
            price = ''

            for x in range(len(columns)):
                if x == 0:
                    date = columns[x].text.split('Z')[0] + 'Z'
                    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d %H:%M:%S")
                if x == 2:
                    collection = columns[x].find('strong').text.strip()
                if x == 3:
                    supply = columns[x].text.strip()
                if x == 4:
                    price = columns[x].text.strip()
                    if "ETH" in price:
                        platform = 'Ethereum'
                    elif "SOL" in price:
                        platform = 'Solana'
                    elif "ADA" in price:
                        platform = 'Cardano'
                    price = price.split(' ')[0]
                if x == 5:
                    link = columns[x].find('a')['href']
                if x == 6:
                    try:
                        discord = columns[x].find('a')['href']
                    except TypeError:
                        pass
                if x == 7:
                    twitter = columns[x].find('a')['href']

            df = df.append({"Date": date, "Link": link, "Collection": collection,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)

        df['Listing'] = 'NextDrop.is'
        self.df = self.df.append(df, ignore_index=True)

    def nextdrop_com(self):
        df = pd.DataFrame()
        print('Checking nextdrop.com')

        url = 'https://nextdrop.com/collections/'
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')

        projects = soup.find_all('div', class_='nft-project-info')

        for project in projects:
            collection = project.find('h2').text.strip()
            rows = project.find_all('li')
            date = ''
            link = ''
            discord = ''
            twitter = ''
            supply = ''
            platform = ''
            price = ''

            for x in range(len(rows)):
                if x == 0:
                    platform = rows[x].find('span').text.strip()

                if x == 3:
                    date = rows[x].find('span').text.strip()
                    date = datetime.datetime.strptime(date, '%B %d, %Y').strftime("%Y-%m-%d %H:%M:%S")

                if x == 5:
                    price = rows[x].find('span').text.strip()

                if x == 6:
                    supply = rows[x].find('span').text.strip()

            df = df.append({"Date": date, "Link": link, "Collection": collection,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)

        df['Listing'] = 'NextDrop.com'
        self.df = self.df.append(df, ignore_index=True)

    def oxalus(self):
        df = pd.DataFrame()
        print('Checking oxalus.io')

        
        today = int(datetime.datetime.today().timestamp() * 1000)
        url = 'https://analytics-api.oxalus.io/collection-events?from=' + str(today) + '&limit=200&offset=0&name=&append_zero_from_date=true'
        request = requests.get(url)
        json_data = json.loads(request.content)
        projects = json_data['data']['records']
        
        for project in projects:
            if project['date'] == 0:
                date = 'TBA'
            else:
                date = datetime.datetime.fromtimestamp(project['date']/1000).strftime("%Y-%m-%d %H:%M:%S")
            link = project['home_link']
            collection = project['name']
            discord = ''
            twitter = ''
            supply = ''
            platform = project['chain_slug'].capitalize()
            price = str(project['price_value'])
            
            for channel in project['media_channels']:
                if channel['key'] == 'twitter':
                    twitter = channel['link']
                if channel['key'] == 'discord':
                    discord = channel['link']
            
            df = df.append({"Date": date, "Link": link, "Collection": collection,
                            "Discord": discord, "Twitter": twitter, "Supply": supply,
                            "Platform": platform, "Price": price}, ignore_index=True)
            
        df['Listing'] = 'Oxalus.io'
        self.df = self.df.append(df, ignore_index=True)

    def cleaning_df(self):
        df = self.df
        df = df.replace(r'^\s*$', 'TBA', regex=True)
        df = df[df['Platform'] != '']
        
        
    
    
    def run(self, save=True):
        # run all the functions
        self.coinmarketcap()
        self.nftreminder()
        self.raritysniper()
        self.upcomingnft()
        #self.nearingnft()
        self.luckytrader()
        self.crypto()
        self.mintyscore()
        self.raritytools()
        self.seafloor()
        self.nfteller()
        #self.nftevening() FIX THIS
        self.icytools()
        self.nftsolana()
        self.nextdrop()
        self.nextdrop_com()
        self.oxalus()
        

        if save:
            self.df.to_csv('nft_calendar.csv', index=False)
            
    def fetch_data(self):
        self.run(save=False)
        return self.df





if __name__ == "__main__":
    listings = Listings()
    listings.run()   
    

