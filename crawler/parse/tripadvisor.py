import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from crawler.models import Attraction, Restaurant
from crawler.parse.abstractions import WebsiteParserBase

traveler_types = {
    '3': 'Families',
    '2': 'Couples',
    '5': 'Solo',
    '1': 'Business',
    '4': 'Friends'
}


class TripAdvisorParser(WebsiteParserBase):
    def parse(self, node, url):
        if re.search('www.tripadvisor.com/TravelersChoice-Destinations', url) is not None:
            pass
        return None

    def extract_targets(self, node, article, current_url):
        return [urljoin(current_url, tag['href']) for tag in node.findAll(href=re.compile('Attractions'))]


class AttractionParser(WebsiteParserBase):
    def _get_all_reviews_pages(self, url, base_page):
        comments_number = 1
        try:
            comments_number = base_page.find('div', {'class': 'pagination-details'}).find_all('b')[-1].text
            comments_number = int(comments_number.replace(',', ''))
            if comments_number > 1000:
                comments_number = 1000
        except Exception as e:
            print(e)
        all_pages = []
        for i in range(0, comments_number, 10):
            all_pages.append(url.replace('Reviews-', f'Reviews-or{i}-'))
        return all_pages

    def _get_page_content(self, url, params=None):
        result = requests.get(url, params=params)
        content = result.content
        return BeautifulSoup(content, 'html.parser')

    def _get_rate_catagories_by_traveler_type(self, url, traveler_type):
        params = {
            'preferFriendReviews': 'FALSE',
            't': '',
            'q': '',
            'filterSeasons': '',
            'filterLang': 'ALL',
            'filterSegment': traveler_type,
            'trating': '',
            'reqNum': 1,
            'changeSet': 'REVIEW_LIST',
            'puid': 'XDB8IQokMm4ABLndbbcAAACr'
        }
        page = self._get_page_content(url, params)
        return page.find('div', {'class': 'choices'}).find_all('div', {'class': ['ui_checkbox', 'item']})

    def _get_all_comments_by_traveler_type_and_rate(self, attraction_url, traveler_type, rate):
        params = {
            'preferFriendReviews': 'FALSE',
            't': '',
            'q': '',
            'filterSeasons': '',
            'filterLang': 'ALL',
            'filterSegment': traveler_type,
            'trating': rate,
            'reqNum': 1,
            'changeSet': 'REVIEW_LIST',
            'puid': 'XDB8IQokMm4ABLndbbcAAACr'
        }
        page = self._get_page_content(attraction_url, params)
        all_comments_pages = self._get_all_reviews_pages(attraction_url, page)
        all_comments = []
        for page_url in all_comments_pages:
            page_content = self._get_page_content(page_url)
            comments = page_content.find_all('div', {'class': 'review-container'})
            for comment in comments:
                try:
                    user = comment.find_all('div', {'class': 'info_text'})[0].find('div').text
                    user_address = comment.find_all('div', {'class': 'info_text'})[0].find('div', {'class': 'userLoc'}).strong.text
                    rate = rate
                    content = comment.find_all('p', {'class': 'partial_entry'})[0].text
                    date = comment.find_all('div', {'class': ['prw_rup', 'prw_reviews_stay_date_hsx']})[0].text
                    traveler_type = traveler_type
                    all_comments.append(
                        {
                            'username': user,
                            'user_address': user_address,
                            'content': content,
                            'comment_date': date,
                            'user_type': traveler_types[traveler_type]
                        }
                    )
                except:
                    pass
        return all_comments

    def _get_reviews_statistics(self, url):
        rates = []
        for traveler_type in traveler_types:
            rate_catagories = self._get_rate_catagories_by_traveler_type(url, traveler_type)
            rates.append({
                'category': traveler_types[traveler_type],
                'rate': {
                    'Excellent': {
                        'count': rate_catagories[0].find('span', {'class': 'row_num'}).text,
                        'reviews': self._get_all_comments_by_traveler_type_and_rate(url, traveler_type, 5)

                    },
                    'Very good': {
                        'count': rate_catagories[1].find('span', {'class': 'row_num'}).text,
                        'reviews': self._get_all_comments_by_traveler_type_and_rate(url, traveler_type, 4)
                    },
                    'Average': {
                        'count': rate_catagories[2].find('span', {'class': 'row_num'}).text,
                        'reviews': self._get_all_comments_by_traveler_type_and_rate(url, traveler_type, 3)
                    },
                    'Poor': {
                        'count': rate_catagories[3].find('span', {'class': 'row_num'}).text,
                        'reviews': self._get_all_comments_by_traveler_type_and_rate(url, traveler_type, 2)
                    },
                    'Terrible': {
                        'count': rate_catagories[4].find('span', {'class': 'row_num'}).text,
                        'reviews': self._get_all_comments_by_traveler_type_and_rate(url, traveler_type, 1)
                    }
                }

            })
        return rates

    def _parse_reviews(self, url):
        reviews_list = []
        page = self._get_page_content(url)
        all_reviews_pages = self._get_all_reviews_pages(url, page)
        for page_url in all_reviews_pages:
            page_content = self._get_page_content(page_url)
            reviews = page_content.find_all('div', {'class': 'review-container'})
            for review in reviews:
                url = review.find('div', {'class': 'quote'}).a['href']
                title = review.find('div', {'class': 'quote'}).a.span.text
                content = review.find('p', {'class': 'partial_entry'}).text
                rate = ''
                reviewer = review.find('div', {'class': 'info_text'}).div.text
                try:
                    rate = review.find('span', {'class': 'ui_bubble_rating'})['class'][1]
                    rate = re.findall('\d+', rate)[0]
                except Exception as ex:
                    pass
                reviews_list.append({
                    'url': url,
                    'title': title,
                    'content': content,
                    'rate': float(rate)/10,
                    'reviewer': reviewer
                })
        return reviews_list

    def parse(self, node, url):
        if re.search('www.tripadvisor.com/Attraction_Review', url) is not None:
            try:
                name = node.find('h1', {"id": "HEADING"}).text
                rate = node.find('span', {'class': 'ui_bubble_rating'})['alt'].split(' ')[0]
                ta_place = node.find('span', {'class': 'header_popularity'}).b.span.text.replace('#', '')
                location = node.find('span', {'class': 'locality'}).text.replace(', ', '')
                reviews = {
                    'number': node.find('a', {'class': 'seeAllReviews'}).text,
                    'reviews': self._parse_reviews(url)
                }
                tags = [link.text for link in node.find('div', {'class': 'detail'}).find_all('a')]

                # Not implemented in this stage #
                photos = None
                contact = None

                about = ''
                try:
                    about = node.find('div', {'class': re.compile('attractions-attraction-detail-about')}).text
                except:
                    pass
                attraction = Attraction(
                    name=name,
                    rate=rate,
                    ta_place=ta_place,
                    location=location,
                    reviews=reviews,
                    tags=tags,
                    url=url
                )
                return attraction
            except Exception:
                return None
        return None

    def extract_targets(self, node, article, current_url):  # Turn attr off for only restaurants
        targets = [urljoin(current_url, tag['href']) for tag in node.findAll(href=re.compile('Attraction_Review'))]
        targets.extend([urljoin(current_url, tag['href']) for tag in node.findAll(href=re.compile('Attractions'))])
        targets.extend([urljoin(current_url, tag['href']) for tag in node.findAll(href=re.compile('Restaurants'))])
        return targets


class RestaurantParser(WebsiteParserBase):
    def _get_details(self, node):
        details = {}
        details_table = node.find('div', {'class': 'restaurants-details-card-DetailsCard__innerDiv--1Imq5'})
        details_table = details_table.findAll('div')[1].find('div').findAll('div', {'class': 'ui_column'})
        about_section = details_table[0]
        details['about'] = ''
        try:
            details['about'] = about_section.find('div', {'class': 'restaurants-details-card-DesktopView__desktopAboutText--1VvQH'}).text
        except:
            pass
        for i in range(1, len(details_table)):
            catagories = details_table[i].findAll('div')
            for catagory in catagories:
                try:
                    catagory_name = catagory.find('div', {'class': 'restaurants-details-card-TagCategories__categoryTitle--28rB6'}).text.lower()
                    catagory_value = catagory.find('div', {'class': 'restaurants-details-card-TagCategories__tagText--Yt3iG'}).text.split(',')
                    details[catagory_name] = catagory_value
                except:
                    pass
        return details

    def parse(self, node, url):
        if re.search('www.tripadvisor.com/Restaurant_Review', url) is not None:
            try:
                name = node.find('h1', {"class": "ui_header"}).text
                rate = node.find('span', {'class': 'ui_bubble_rating'})['alt'].split(' ')[0]
                ta_place = node.find('span', {'class': 'header_popularity'}).b.span.text.replace('#', '')
                city = node.find('span', {'class': 'header_popularity'}).a.text.split(' ')[-1].lower()
                location = ""
                try:
                    location = node.find('span', {'class': 'restaurants-detail-overview-cards-LocationOverviewCard__detailLinkText--co3ei'}).text
                except:
                    pass
                details = self._get_details(node)
                special_diets = details["special diets"] if "special diets" in details else None
                features = details["features"] if "features" in details else None
                cuisines = details["cuisines"] if "cuisines" in details else None
                meals = details["meals"] if "meals" in details else None
                price = details["price range"] if "price range" in details else None
                restaurant = Restaurant(
                    name=name,
                    ta_place=ta_place,
                    url=url,
                    rate=rate,
                    city=city,
                    address=location,
                    special_diets=special_diets,
                    features=features,
                    cuisines=cuisines,
                    meals=meals,
                    price=price
                )
                return restaurant
            except Exception:
                return None
        return None

    def extract_targets(self, node, article, current_url):
        targets = [urljoin(current_url, tag['href']) for tag in node.findAll(href=re.compile('Restaurant_Review'))]
        targets.extend([urljoin(current_url, tag['href']) for tag in node.findAll(href=re.compile('Restaurants'))])
        return targets
