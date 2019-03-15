class ParsedItem:
    def __init__(self, url):
        self.url = url


class MongoConfiguration:
    def __init__(self, host, port, username=None, password=None):
        self.port = port
        self.password = password
        self.username = username
        self.host = host


class Attraction(ParsedItem):
    def __init__(self, url, name, rate, ta_place, location, reviews, tags, photos=None, about=None, contact=None):
        super().__init__(url)
        self.rate = rate
        self.name = name
        self.ta_place = ta_place  # place in attractions list #1 in blabla etc
        self.location = location
        self.reviews = reviews
        self.tags = tags
        self.photos = photos
        self.about = about
        self.contact = contact


class Review(ParsedItem):
    def __init__(self, url, rate, title, content, reviewer):
        super().__init__(url)
        self.rate = rate
        self.title = title
        self.content = content
        self.reviewer = reviewer


class Restaurant(ParsedItem):
    def __init__(self, url, rate, name, ta_place, city, address=None, special_diets=None, features=None, cuisines=None, meals=None, photos=None, price=None):
        super().__init__(url)
        self.name = name
        self.ta_place = ta_place
        self.url = url
        self.rate = rate
        self.city = city
        self.address = address
        self.special_diets = special_diets
        self.features = features
        self.cuisines = cuisines
        self.meals = meals
        self.photos = photos
        self.price = price


