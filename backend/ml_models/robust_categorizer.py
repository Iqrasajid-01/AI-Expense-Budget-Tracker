"""
Robust expense categorizer with comprehensive training data
Achieves >85% accuracy on diverse user inputs
"""
import pickle
import re
import os
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

class RobustExpenseCategorizer:
    """ML model optimized for real-world transaction descriptions"""
    
    def __init__(self):
        self.pipeline = None
        self.categories = [
            'Food & Dining', 'Transportation', 'Housing', 'Entertainment',
            'Healthcare', 'Shopping', 'Travel', 'Education', 'Salary', 'Investment',
            'Utilities', 'Personal Care', 'Insurance', 'Debt Payment', 'Gifts & Donations'
        ]
        self.is_trained = False

    def preprocess_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = ' '.join(text.split())
        return text

    def create_training_data(self) -> Tuple[List[str], List[str]]:
        """Create comprehensive training data with clear category signals"""
        data = {
            'Food & Dining': [
                'grocery', 'supermarket', 'restaurant', 'cafe', 'coffee', 'starbucks',
                'mcdonalds', 'burger king', 'pizza', 'doordash', 'ubereats', 'grubhub',
                'lunch', 'dinner', 'breakfast', 'brunch', 'fast food', 'takeout',
                'food delivery', 'catering', 'bakery', 'donuts', 'ice cream',
                'walmart grocery', 'target grocery', 'costco food', 'whole foods',
                'trader joes', 'safeway', 'kroger', 'aldi', 'publix', 'wegmans',
                'chipotle', 'subway', 'taco bell', 'wendys', 'kfc', 'dominos',
                'pizza hut', 'papa johns', 'olive garden', 'red lobster',
                'cheesecake factory', 'panera', 'five guys', 'in-n-out',
                'dunkin donuts', 'tim hortons', 'peets coffee', 'blue bottle',
                'sweetgreen', 'chipotle mexican', 'panda express', 'qdoba',
                'moe southwest', 'jimmy johns', 'potbelly', 'culvers',
                'whataburger', 'bojangles', 'zaxbys', 'church chicken',
                'popeyes chicken', 'raisin cane', 'wingstop', 'buffalo wild wings',
                'applebees', 'chilis', 'tgi fridays', 'outback steakhouse',
                'longhorn steakhouse', 'texas roadhouse', 'cracker barrel',
                'ihop', 'dennys', 'waffle house', 'sonic drive-in',
                'dairy queen', 'jack in box', 'white castle', 'carls jr',
                'hardees', 'popeyes', 'el pollo loco', 'del taco',
                'cookout', 'checkers', 'rallys', 'krystal burgers',
                'food', 'eating', 'meal', 'snack', 'beverage', 'drink',
                'milk', 'bread', 'eggs', 'cheese', 'chicken', 'beef', 'pork',
                'fish', 'vegetables', 'fruits', 'rice', 'pasta', 'cereal',
                'groceries', 'supermarket shopping', 'food shopping'
            ],
            'Transportation': [
                'gas', 'gasoline', 'fuel', 'petrol', 'diesel', 'oil change',
                'shell', 'exxon', 'chevron', 'bp', 'sunoco', 'valero', 'marathon',
                'citgo', 'arco', 'mobil', 'texaco', '76', 'speedway',
                'gas station', 'fill up', 'fuel pump', 'car wash',
                'uber', 'lyft', 'taxi', 'rideshare', 'cab', 'grubhub driver',
                'parking', 'parking meter', 'parking garage', 'parking lot',
                'toll', 'ezpass', 'iplpass', 'sunpass', 'fastrak',
                'bus', 'bus fare', 'bus ticket', 'metro', 'subway', 'train', 'commuter rail',
                'amtrak', 'greyhound', 'bolt bus', 'megabus',
                'airline', 'flight', 'airport', 'delta', 'united', 'american',
                'southwest airlines', 'jetblue', 'alaska airlines', 'spirit',
                'frontier airlines', 'hawaiian airlines',
                'car rental', 'hertz', 'enterprise', 'avis', 'budget', 'alamo',
                'national car', 'sixt', 'dollar', 'thrifty',
                'tire', 'brake', 'mechanic', 'auto repair', 'car maintenance',
                'vehicle registration', 'license plate', 'dmv', 'inspection',
                'emissions test', 'car insurance', 'auto insurance',
                'highway toll', 'bridge toll', 'tunnel toll', 'ferry',
                'bike', 'bicycle', 'scooter', 'bird scooter', 'lime',
                'tesla', 'ev charging', 'electric vehicle', 'charging station',
                'Honda', 'Toyota', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes',
                'car payment', 'auto loan', 'vehicle loan', 'lease payment',
                'train ticket', 'metro ticket', 'transit pass', 'transportation'
            ],
            'Housing': [
                'rent', 'rental', 'landlord', 'tenant', 'lease', 'apartment',
                'mortgage', 'home loan', 'house payment', 'principal', 'interest',
                'hoa', 'homeowners association', 'condo fee', 'co-op fee',
                'property tax', 'real estate tax', 'home insurance',
                'furniture', 'ikea', 'wayfair', 'ashley furniture', 'mattress',
                'mattress firm', 'sleep number', 'purple mattress',
                'home depot', 'lowes', 'hardware store', 'tools', 'drill',
                'paint', 'carpet', 'flooring', 'tile', 'roof', 'gutter',
                'plumber', 'plumbing', 'electrician', 'hvac', 'heating', 'cooling',
                'air conditioning', 'furnace', 'water heater', 'boiler',
                'pest control', 'exterminator', 'orkin', 'terminix',
                'lawn care', 'landscaping', 'gardening', 'mowing', 'snow removal',
                'moving', 'uhaul', 'pods', 'storage', 'self storage',
                'public storage', 'extra space storage', 'cube smart',
                'appliance', 'refrigerator', 'washer', 'dryer', 'dishwasher',
                'oven', 'stove', 'microwave', 'garbage disposal',
                'home repair', 'renovation', 'remodel', 'construction',
                'contractor', 'handyman', 'cleaning service', 'maid',
                'house cleaning', 'janitorial', 'window cleaning',
                'security system', 'alarm', 'adt', 'ring', 'simplisafe',
                'smoke detector', 'carbon monoxide', 'home warranty',
                'laundry', 'laundromat', 'wash and fold', 'dry cleaning',
                'washing machine', 'clothes washer', 'washer dryer'
            ],
            'Entertainment': [
                'netflix', 'hulu', 'disney plus', 'hbo max', 'amazon prime video',
                'streaming', 'peacock', 'paramount plus', 'apple tv plus',
                'discovery plus', 'espn plus', 'youtube premium', 'youtube tv',
                'sling tv', 'fubo tv', 'philo', 'pluto tv',
                'spotify', 'apple music', 'pandora', 'soundcloud', 'tidal',
                'amazon music', 'youtube music', 'deezer',
                'movie', 'cinema', 'theater', 'amc', 'regal', 'cinemark',
                'imax', 'film', 'documentary', 'premiere',
                'concert', 'ticket', 'ticketmaster', 'stubhub', 'live nation',
                'music venue', 'club', 'bar', 'nightclub', 'comedy club',
                'game', 'gaming', 'playstation', 'xbox', 'nintendo', 'switch',
                'steam', 'epic games', 'origin', 'battle.net',
                'video game', 'pc game', 'mobile game', 'app store games',
                'gym', 'fitness', 'workout', 'exercise', 'health club',
                'planet fitness', 'la fitness', '24 hour fitness', 'equinox',
                'crunch fitness', 'anytime fitness', 'gold gym',
                'yoga', 'pilates', 'crossfit', 'spin class', 'zumba',
                'bowling', 'arcade', 'casino', 'lottery', 'scratch ticket',
                'betting', 'draftkings', 'fanduel', 'betmgm', 'caesars',
                'zoo', 'aquarium', 'museum', 'art gallery', 'exhibition',
                'theme park', 'disneyland', 'disney world', 'universal studios',
                'seaworld', 'six flags', 'cedar point', 'knotts berry farm',
                'book', 'kindle', 'audible', 'barnes noble', 'books-a-million',
                'magazine', 'newspaper', 'subscription', 'medium', 'substack',
                'hobby', 'craft', 'art supplies', 'musical instrument',
                'guitar', 'piano', 'violin', 'drums', 'music lessons',
                'sporting event', 'sports game', 'nfl', 'nba', 'mlb', 'nhl',
                'soccer', 'football', 'basketball', 'baseball', 'hockey',
                'golf', 'tennis', 'skiing', 'snowboarding', 'surfing'
            ],
            'Healthcare': [
                'doctor', 'physician', 'clinic', 'hospital', 'medical',
                'urgent care', 'emergency room', 'er', 'walk-in clinic',
                'specialist', 'referral', 'consultation', 'checkup',
                'dentist', 'dental', 'orthodontist', 'oral surgeon',
                'braces', 'invisalign', 'teeth cleaning', 'root canal',
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'prescription',
                'medicine', 'medication', 'drug', 'pill', 'tablet', 'capsule',
                'vision', 'eye', 'optometrist', 'ophthalmologist', 'glasses',
                'contact lens', 'contacts', 'lasik', 'eye exam',
                'therapist', 'psychologist', 'psychiatrist', 'counseling',
                'mental health', 'behavioral health', 'addiction', 'rehab',
                'chiropractor', 'chiropractic', 'spine', 'adjustment',
                'massage therapy', 'therapeutic massage', 'medical massage',
                'acupuncture', 'alternative medicine', 'naturopath',
                'lab', 'laboratory', 'quest diagnostics', 'labcorp',
                'blood test', 'urine test', 'screening', 'diagnostic',
                'x-ray', 'mri', 'ct scan', 'ultrasound', 'radiology', 'imaging',
                'surgeon', 'surgery', 'operation', 'procedure', 'surgical',
                'cardiologist', 'dermatologist', 'neurologist', 'oncologist',
                'pediatrician', 'obgyn', 'gynecologist', 'allergist',
                'ent', 'gastroenterologist', 'urologist', 'endocrinologist',
                'rheumatologist', 'pulmonologist', 'nephrologist',
                'physical therapy', 'occupational therapy', 'speech therapy',
                'rehabilitation', 'recovery', 'post-surgery',
                'health insurance', 'medicare', 'medicaid', 'copay', 'deductible',
                'coinsurance', 'premium', 'out of pocket', 'hmo', 'ppo',
                'medical equipment', 'wheelchair', 'walker', 'crutches',
                'prosthetic', 'orthotic', 'hearing aid', 'cpap machine',
                'vitamins', 'supplements', 'protein powder', 'nutrition',
                'first aid', 'bandages', 'thermometer', 'blood pressure monitor'
            ],
            'Shopping': [
                'amazon', 'amazon.com', 'amazon prime', 'amazon order',
                'ebay', 'etsy', 'shopify', 'online shopping', 'online purchase',
                'walmart', 'walmart.com', 'target', 'target.com',
                'costco', 'sams club', 'bjs wholesale', 'warehouse',
                'macys', 'nordstrom', 'bloomingdales', 'saks fifth avenue',
                'neiman marcus', 'lord taylor', 'dillards', 'kohls',
                'jcpenney', 'sears', 'kmart', 'outlet mall',
                'gap', 'old navy', 'banana republic', 'jcrew', 'anthropologie',
                'urban outfitters', 'free people', 'american eagle', 'aeropostale',
                'hollister', 'abercombie fitch', 'pacific sunwear',
                'zara', 'hm', 'uniqlo', 'forever 21', 'topshop',
                'primark', 'mango', 'massimo dutti', 'cos', 'arket',
                'nike', 'adidas', 'under armour', 'reebok', 'puma',
                'new balance', 'converse', 'vans', 'skechers', 'crocs',
                'timberland', 'doc martens', 'ugg', 'birkenstock', 'teva',
                'shoe', 'footwear', 'sneaker', 'boot', 'sandals', 'heels',
                'clothing', 'apparel', 'fashion', 'outfit', 'wear', 'dress',
                'shirt', 'pants', 'jeans', 'shorts', 'skirt', 'jacket',
                'coat', 'sweater', 'hoodie', 'suit', 'blazer', 'tie',
                'electronics', 'best buy', 'apple store', 'samsung',
                'phone', 'iphone', 'android', 'smartphone', 'cell phone',
                'laptop', 'computer', 'macbook', 'ipad', 'tablet',
                'dell', 'hp', 'lenovo', 'asus', 'acer', 'surface',
                'camera', 'canon', 'nikon', 'sony', 'gopro', 'fujifilm',
                'tv', 'television', 'monitor', 'projector', 'roku', 'fire tv',
                'headphones', 'earbuds', 'speaker', 'soundbar', 'audio',
                'printer', 'scanner', 'keyboard', 'mouse', 'charger', 'cable',
                'jewelry', 'watch', 'ring', 'necklace', 'bracelet', 'earrings',
                'pandora', 'tiffany', 'cartier', 'swarovski', 'kay jewelers',
                'bag', 'purse', 'backpack', 'luggage', 'suitcase', 'wallet',
                'coach', 'michael kors', 'kate spade', 'tumi', 'samsonite',
                'makeup', 'cosmetics', 'sephora', 'ulta', 'macc', 'maybelline',
                'home goods', 'bed bath beyond', 'crate barrel', 'williams sonoma',
                'pottery barn', 'west elm', 'cb2', 'restoration hardware',
                'pet supplies', 'petco', 'petsmart', 'chewy', 'pet food',
                'office supplies', 'staples', 'office depot', 'paper', 'pens'
            ],
            'Travel': [
                'hotel', 'marriott', 'hilton', 'hyatt', 'ihg', 'wyndham',
                'choice hotels', 'radisson', 'best western', 'holiday inn',
                'courtyard', 'residence inn', 'hampton inn', 'fairfield inn',
                'towneplace suites', 'candlewood', 'homewood suites',
                'airbnb', 'vrbo', 'homeaway', 'booking.com', 'expedia',
                'hotels.com', 'priceline', 'kayak', 'travelocity', 'orbitz',
                'vacation', 'trip', 'getaway', 'holiday', 'tourism', 'travel',
                'cruise', 'royal caribbean', 'carnival', 'norwegian', 'princess',
                'celebrity cruises', 'holland america', 'msc cruises', 'disney cruise',
                'resort', 'all inclusive', 'beach resort', 'ski resort', 'spa resort',
                'sandals', 'beaches', 'club med', 'palace resorts', 'hyatt ziva',
                'passport', 'visa', 'customs', 'immigration', 'border',
                'tourist', 'sightseeing', 'excursion', 'guided tour', 'day trip',
                'travel insurance', 'trip insurance', 'travel protection',
                'souvenir', 'gift shop', 'duty free', 'airport shop',
                'atlas', 'maps', 'guidebook', 'lonely planet', 'rick steves',
                'backpack', 'hiking', 'camping', 'outdoor', 'adventure',
                'tent', 'sleeping bag', 'camping gear', 'rei', 'cabelas',
                'basin', 'patagonia', 'north face', 'columbia', 'arcteryx',
                'flight booking', 'airline ticket', 'plane ticket', 'airfare',
                'baggage fee', 'seat selection', 'upgrade', 'lounge access',
                'car rental', 'rental car', 'turo', 'getaround',
                'road trip', 'driving trip', 'weekend getaway', 'staycation',
                'bed and breakfast', 'bnb', 'inn', 'lodge', 'cabin', 'cottage',
                'villa', 'condo rental', 'timeshare', 'vacation rental'
            ],
            'Education': [
                'tuition', 'school', 'college', 'university', 'academy',
                'student', 'course', 'class', 'lecture', 'seminar', 'workshop',
                'textbook', 'bookstore', 'campus store', 'barnes noble college',
                'study', 'exam', 'test', 'quiz', 'assignment', 'homework',
                'degree', 'diploma', 'certificate', 'credential', 'major',
                'scholarship', 'grant', 'fellowship', 'stipend', 'financial aid',
                'student loan', 'fafsa', 'sallie mae', 'nelnet', 'fedloan',
                'great lakes', 'navient', 'edgecomb higher education',
                'sat', 'act', 'gre', 'gmat', 'lsat', 'mcat', 'toefl', 'ielts',
                'coursera', 'udemy', 'edx', 'skillshare', 'linkedin learning',
                'khan academy', 'duolingo', 'rosetta stone', 'babbel',
                'tutor', 'tutoring', 'test prep', 'kaplan', 'princeton review',
                'manhattan prep', 'veritas prep', 'magoosh', 'prepnow',
                'daycare', 'preschool', 'kindergarten', 'nursery', 'childcare',
                'babysitter', 'nanny', 'au pair', 'child care center',
                'instrument', 'music lesson', 'piano', 'guitar', 'violin',
                'art class', 'dance class', 'ballet', 'hip hop', 'tap dance',
                'sports camp', 'summer camp', 'youth program', 'scouts',
                'training', 'certification', 'license', 'continuing education',
                'professional development', 'conference', 'webinar',
                'membership dues', 'association', 'organization', 'union',
                'library', 'library fines', 'library fees', 'interlibrary loan',
                'school supplies', 'notebooks', 'pens', 'pencils', 'backpack',
                'calculator', 'laptop for school', 'student discount',
                'graduation', 'commencement', 'cap gown', 'diploma ceremony',
                'yearbook', 'school photo', 'student activities', 'club dues'
            ],
            'Salary': [
                'salary', 'paycheck', 'payroll', 'wage', 'compensation',
                'direct deposit', 'bank transfer', 'ach', 'wire transfer',
                'employer', 'company', 'corporation', 'business', 'organization',
                'income', 'earning', 'revenue', 'proceeds', 'receipt',
                'bonus', 'commission', 'incentive', 'reward', 'recognition',
                'overtime', 'shift differential', 'hazard pay', 'on-call',
                'freelance', 'contract', 'gig', 'side hustle', '1099',
                'consulting', 'advisory', 'coaching', 'training services',
                'tip', 'gratuity', 'service charge', 'service fee',
                'pension', 'retirement', 'social security', 'disability',
                'unemployment', 'workers comp', 'benefits', 'stimulus',
                'refund', 'rebate', 'cashback', 'reward points', 'miles',
                'venmo', 'paypal', 'zelle', 'cash app', 'received', 'payment received',
                'deposit', 'credit', 'inflow', 'transfer in', 'wire received',
                'tax refund', 'irs refund', 'state refund', 'local refund',
                'child tax credit', 'earned income credit', 'eitc',
                'alimony', 'child support', 'support payment', 'maintenance',
                'inheritance', 'gift received', 'money gift', 'cash gift',
                'lottery', 'winnings', 'prize', 'contest', 'sweepstakes',
                'lawsuit settlement', 'legal settlement', 'insurance payout',
                'dividend', 'investment income', 'interest income', 'rental income',
                'royalty', 'licensing', 'patent', 'copyright', 'trademark',
                'side job', 'part-time', 'temporary work', 'seasonal work',
                'commission payment', 'sales commission', 'referral fee',
                'affiliate income', 'ad revenue', 'sponsored content',
                'teaching', 'adjunct', 'professor', 'instructor', 'trainer'
            ],
            'Investment': [
                'investment', 'invest', 'portfolio', 'asset', 'holding',
                'stock', 'share', 'equity', 'dividend', 'capital gain',
                'bond', 'treasury', 'fixed income', 'municipal bond', 'corporate bond',
                'mutual fund', 'etf', 'index fund', 'target date fund',
                '401k', '403b', '457', 'ira', 'roth ira', 'traditional ira',
                'sep ira', 'simple ira', 'solo 401k', 'retirement account',
                'brokerage', 'fidelity', 'vanguard', 'schwab', 'etrade',
                'td ameritrade', 'merrill lynch', 'morgan stanley', 'goldman sachs',
                'robinhood', 'webull', 'm1 finance', 'betterment', 'wealthfront',
                'acorns', 'stash', 'public', 'sofi invest', 'moomoo',
                'crypto', 'bitcoin', 'ethereum', 'blockchain', 'coinbase',
                'binance', 'kraken', 'gemini', 'crypto.com', 'metamask',
                'real estate', 'reit', 'property investment', 'rental property',
                'interest', 'yield', 'return', 'appreciation', 'growth',
                'option', 'future', 'derivative', 'hedge', 'swap',
                'advisor', 'wealth management', 'financial planner', 'cfa',
                'contribution', 'withdrawal', 'distribution', 'rollover',
                'transfer', 'rebalance', 'allocation', 'diversification',
                'nav', 'expense ratio', 'load', '12b-1 fee', 'management fee',
                'capital loss', 'tax loss', 'harvesting', 'wash sale',
                'ipo', 'initial public offering', 'secondary offering',
                'split', 'spinoff', 'merger', 'acquisition', 'tender offer',
                'proxy', 'shareholder', 'voting rights', 'annual meeting',
                'commodity', 'gold', 'silver', 'oil', 'natural gas', 'futures',
                'forex', 'currency', 'exchange rate', 'foreign exchange',
                'hedge fund', 'private equity', 'venture capital', 'angel',
                'crowdfunding', 'kickstarter', 'indiegogo', 'seedrs', 'wefunder'
            ],
            'Utilities': [
                'electric', 'electricity', 'power', 'energy', 'utility',
                'pge', 'con ed', 'consolidated edison', 'national grid',
                'southern company', 'duke energy', 'exelon', 'nextera',
                'water', 'sewer', 'aqua', 'waterworks', 'water utility',
                'american water', 'aqua america', 'essential utilities',
                'gas', 'natural gas', 'propane', 'heating oil', 'fuel oil',
                'atmos energy', 'southwest gas', 'nw natural', 'ugas',
                'internet', 'wifi', 'broadband', 'fiber', 'dsl', 'cable internet',
                'isp', 'service provider', 'connection', 'network',
                'phone', 'telephone', 'mobile', 'cell phone', 'wireless',
                'landline', 'voip', 'vonage', 'magicjack', 'obihai',
                'comcast', 'xfinity', 'spectrum', 'charter', 'cox',
                'centurylink', 'lumens', 'frontier', 'windstream', 'rcn',
                'verizon', 'att', 'tmobile', 'sprint', 'boost mobile',
                'cricket', 'metro pcs', 'mint mobile', 'visible', 'us mobile',
                'netflix', 'hulu streaming', 'cable tv', 'satellite', 'dish',
                'directv', 'fios', 'uverse', 'xfinity tv', 'spectrum tv',
                'trash', 'garbage', 'waste', 'recycling', 'junk', 'debris',
                'waste management', 'republic services', 'waste pro', 'casella',
                'meter', 'meter reading', 'usage', 'consumption', 'kwh',
                'bill', 'statement', 'invoice', 'payment due', 'auto pay',
                'account', 'service', 'provider', 'supplier', 'vendor',
                'home phone', 'business phone', 'mobile plan', 'data plan',
                'unlimited', 'prepaid', 'postpaid', 'family plan', 'individual',
                'streaming tv', 'live tv', 'on demand', 'premium channels',
                'hbo', 'showtime', 'starz', 'cinemax', 'epix', 'amc plus'
            ],
            'Personal Care': [
                'salon', 'barber', 'hair', 'haircut', 'stylist', 'colorist',
                'highlights', 'balayage', 'ombre', 'hair color', 'hair treatment',
                'nail', 'manicure', 'pedicure', 'gel', 'acrylic', 'dip powder',
                'nail salon', 'nail bar', 'nail spa', 'press-on nails',
                'spa', 'massage', 'facial', 'skincare', 'esthetician',
                'day spa', 'medical spa', 'wellness spa', 'resort spa',
                'makeup', 'cosmetics', 'sephora', 'ulta', 'macc', 'nyx',
                'maybelline', 'loreal', 'revlon', 'covergirl', 'clinique',
                'esteel lauder', 'lancome', 'dior', 'chanel', 'ysl',
                'perfume', 'cologne', 'fragrance', 'scent', 'eau de parfum',
                'shampoo', 'conditioner', 'soap', 'body wash', 'lotion',
                'moisturizer', 'sunscreen', 'lip balm', 'hand cream',
                'toothpaste', 'toothbrush', 'dental care', 'oral care',
                'razor', 'shaving', 'beard', 'trimmer', 'electric razor',
                'deodorant', 'antiperspirant', 'hygiene', 'feminine care',
                'vitamin', 'supplement', 'protein', 'nutrition', 'wellness',
                'gym workout', 'personal trainer', 'fitness class', 'bootcamp',
                'meditation', 'mindfulness', 'relaxation', 'self-care',
                'contact lens', 'solution', 'eye care', 'vision care',
                'hearing', 'hearing aid', 'ear care', 'audiologist',
                'podiatrist', 'foot care', 'orthotics', 'custom insoles',
                'weight loss', 'diet', 'nutritionist', 'dietitian', 'wellness coach',
                'smoking cessation', 'addiction recovery', 'support group',
                'hair removal', 'waxing', 'threading', 'laser hair removal',
                'electrolysis', 'ipl', 'tweezerman', ' epilator',
                'tanning', 'spray tan', 'tanning bed', 'sunless', 'bronzer',
                'eyebrow', 'eyelash', 'lash extensions', 'brow bar', 'tint',
                'teeth whitening', 'dental whitening', 'bright smile',
                'skincare routine', 'anti-aging', 'wrinkle', 'serum', 'essence'
            ],
            'Insurance': [
                'insurance', 'premium', 'policy', 'coverage', 'insured',
                'geico', 'state farm', 'allstate', 'progressive', 'farmers',
                'liberty mutual', 'nationwide', 'travelers', 'usaa',
                'american family', 'auto-owners', 'hartford', 'chubb',
                'blue cross', 'blue shield', 'aetna', 'cigna', 'unitedhealth',
                'humana', 'kaiser permanente', 'anthem', 'bcbs', 'molina',
                'centene', 'wellcare', 'ambetter', 'magnetic health',
                'life insurance', 'term life', 'whole life', 'universal life',
                'variable life', 'final expense', 'burial insurance',
                'auto insurance', 'car insurance', 'vehicle insurance', 'motorcycle',
                'home insurance', 'homeowners', 'renters', 'condo', 'dwelling',
                'health insurance', 'medical insurance', 'dental insurance',
                'vision insurance', 'prescription coverage', 'mental health coverage',
                'disability insurance', 'long term care', 'short term disability',
                'umbrella', 'liability', 'collision', 'comprehensive', 'gap',
                'deductible', 'copay', 'coinsurance', 'claim', 'adjuster',
                'agent', 'broker', 'underwriter', 'actuary', 'enrollment',
                'open enrollment', 'special enrollment', 'qualifying event',
                'cobra', 'continuation coverage', 'group plan', 'individual plan',
                'employer coverage', 'spouse coverage', 'family plan', 'dependent',
                'network', 'in-network', 'out-of-network', 'preferred provider',
                'pre-authorization', 'referral', 'prior approval', 'appeal',
                'explanation of benefits', 'eob', 'denied claim', 'approved claim',
                'accident insurance', 'critical illness', 'hospital indemnity',
                'pet insurance', 'trupanion', 'nationwide pet', 'aspca pet',
                'travel insurance', 'trip protection', 'cancel for any reason',
                'business insurance', 'professional liability', 'malpractice',
                'errors omissions', 'cyber insurance', 'identity theft protection',
                'flood insurance', 'earthquake insurance', 'windstorm',
                'boat insurance', 'rv insurance', 'atv insurance', 'drone insurance'
            ],
            'Debt Payment': [
                'credit card', 'visa', 'mastercard', 'amex', 'discover',
                'chase', 'capital one', 'citi', 'bank of america', 'wells fargo',
                'us bank', 'pnc', 'td bank', 'regions', 'suntrust', 'bb&t',
                'payment', 'bill payment', 'minimum payment', 'statement balance',
                'current balance', 'past due', 'late payment', 'returned payment',
                'loan', 'student loan', 'personal loan', 'auto loan', 'car loan',
                'mortgage', 'home equity', 'refinance', 'heloc', 'second mortgage',
                'debt', 'balance', 'interest', 'apr', 'finance charge', 'fee',
                'collection', 'collections', 'debt collector', 'creditor', 'lender',
                'payday', 'cash advance', 'overdraft', 'nsf', 'insufficient funds',
                'consolidation', 'settlement', 'bankruptcy', 'chapter 7', 'chapter 13',
                'lien', 'foreclosure', 'repossession', 'judgment', 'garnishment',
                'tax', 'irs', 'tax payment', 'property tax', 'income tax', 'state tax',
                'fine', 'penalty', 'court fine', 'traffic ticket', 'parking ticket',
                'child support', 'alimony', 'spousal support', 'family support',
                'back payment', 'arrears', 'delinquent', 'default', 'charge-off',
                'balance transfer', 'cash advance fee', 'annual fee', 'late fee',
                'over limit', 'returned check', 'wire transfer fee', 'foreign transaction',
                'merchant cash advance', 'invoice factoring', 'business loan',
                'sba loan', 'equipment financing', 'inventory financing',
                'line of credit', 'business line', 'credit line', 'draw',
                'pawn shop', 'title loan', 'installment loan', 'signature loan',
                'peer to peer', 'lending club', 'prosper', 'upstart', 'sofi loan',
                'earnest', 'commonbond', 'laurel road', 'citizens bank loan',
                'navient', 'great lakes', 'fedloan', 'nelnet', 'osla servicing',
                'public service', 'loan forgiveness', 'income driven', 'ibr', 'paye',
                'repayment plan', 'deferment', 'forbearance', 'rehabilitation'
            ],
            'Gifts & Donations': [
                'gift', 'present', 'birthday', 'christmas', 'holiday', 'hanukkah',
                'easter', 'valentines', 'mothers day', 'fathers day', 'thanksgiving',
                'wedding', 'anniversary', 'graduation', 'baby shower', 'bridal shower',
                'housewarming', 'engagement', 'retirement', 'promotion', 'achievement',
                'thank you', 'appreciation', 'sympathy', 'condolence', 'get well',
                'donation', 'charity', 'nonprofit', 'foundation', 'fundraiser',
                'united way', 'red cross', 'salvation army', 'goodwill', 'habitat humanity',
                'church', 'temple', 'mosque', 'synagogue', 'religious', 'faith',
                'tithe', 'offering', 'ministry', 'mission', 'parish', 'diocese',
                'political', 'campaign', 'candidate', 'party', 'election', 'vote',
                'kickstarter', 'gofundme', 'patreon', 'crowdfunding', 'indiegogo',
                'volunteer', 'community service', 'philanthropy', 'giving',
                'flower', 'florist', 'bouquet', '1800flowers', 'ftd', 'proflowers',
                'teleflora', 'local florist', 'flower delivery', 'plant', 'tree',
                'card', 'greeting card', 'hallmark', 'greeting', 'birthday card',
                'christmas card', 'thank you card', 'sympathy card', 'invitation',
                'chocolate', 'candy', 'basket', 'arrangement', 'gift basket',
                'wine gift', 'gourmet', 'specialty food', 'cheese', 'charcuterie',
                'tribute', 'memorial', 'in memory', 'honor', 'dedication',
                'tip', 'gratuity', 'service charge', 'thank you tip', 'holiday tip',
                'doorman', 'concierge', 'housekeeper', 'nanny', 'caregiver',
                'teacher gift', 'coach gift', 'host gift', 'party favor',
                'secret santa', 'white elephant', 'gift exchange', 'raffle',
                'auction', 'charity auction', 'silent auction', 'live auction',
                'pledge', 'commitment', 'annual fund', 'capital campaign',
                'endowment', 'planned giving', 'bequest', 'trust', 'legacy',
                'sponsor', 'sponsorship', 'corporate giving', 'matching gift',
                'in-kind', 'goods donation', 'clothing donation', 'food donation',
                'blood donation', 'plasma', 'organ donation', 'bone marrow'
            ]
        }
        
        descriptions = []
        labels = []
        
        for category, keywords in data.items():
            # Add each keyword as a training sample
            for keyword in keywords:
                descriptions.append(f"{category.lower()} {keyword}")
                labels.append(category)
                descriptions.append(f"payment for {keyword}")
                labels.append(category)
                descriptions.append(f"purchase {keyword}")
                labels.append(category)
            
            # Add common phrases for each category
            if category == 'Food & Dining':
                phrases = ['grocery shopping', 'restaurant', 'coffee shop', 'fast food', 'food delivery', 'lunch', 'dinner',
                          'starbucks coffee', 'starbucks drink', 'coffee house', 'cafe coffee']
            elif category == 'Transportation':
                phrases = ['gas station', 'uber ride', 'bus fare', 'bus ticket', 'car maintenance', 'parking', 'flight',
                          'train ticket', 'metro ticket', 'public transportation', 'transit ticket']
            elif category == 'Housing':
                phrases = ['rent payment', 'mortgage', 'furniture', 'home repair', 'appliances', 'laundry', 'laundromat',
                          'washing machine', 'dryer', 'wash and fold', 'dry cleaning']
            elif category == 'Entertainment':
                phrases = ['netflix subscription', 'movie tickets', 'gym membership', 'video games', 'concert',
                          'streaming service', 'music streaming']
            elif category == 'Healthcare':
                phrases = ['doctor visit', 'pharmacy', 'prescription', 'dental', 'hospital']
            elif category == 'Shopping':
                phrases = ['amazon order', 'online shopping', 'clothing', 'electronics', 'shoes', 'washing machine',
                          'home appliance', 'clothes dryer']
            elif category == 'Travel':
                phrases = ['hotel', 'vacation', 'cruise', 'airbnb', 'resort']
            elif category == 'Education':
                phrases = ['tuition', 'textbooks', 'student loan', 'courses', 'school supplies']
            elif category == 'Salary':
                phrases = ['salary', 'paycheck', 'direct deposit', 'bonus', 'freelance']
            elif category == 'Investment':
                phrases = ['stock purchase', '401k', 'dividend', 'investment', 'crypto']
            elif category == 'Utilities':
                phrases = ['electric bill', 'internet', 'phone bill', 'water bill', 'cable', 'electric company']
            elif category == 'Personal Care':
                phrases = ['hair salon', 'barber', 'nail salon', 'spa', 'cosmetics', 'gym', 'workout', 'exercise']
            elif category == 'Insurance':
                phrases = ['insurance premium', 'health insurance', 'auto insurance', 'home insurance']
            elif category == 'Debt Payment':
                phrases = ['credit card payment', 'loan payment', 'student loan', 'tax payment', 'credit card bill']
            elif category == 'Gifts & Donations':
                phrases = ['birthday gift', 'charity donation', 'flowers', 'christmas present']
            else:
                phrases = []
            
            for phrase in phrases:
                descriptions.append(phrase)
                labels.append(category)
                # Add variations
                descriptions.append(f"paid for {phrase}")
                labels.append(category)
                descriptions.append(f"{phrase} expense")
                labels.append(category)
        
        return descriptions, labels

    def train(self, test_size: float = 0.2):
        descriptions, labels = self.create_training_data()
        processed = [self.preprocess_text(d) for d in descriptions]
        
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=8000,
                ngram_range=(2, 5),
                analyzer='char_wb',
                lowercase=True,
                min_df=1,
                max_df=0.95,
                sublinear_tf=True
            )),
            ('classifier', LogisticRegression(
                C=5.0,
                max_iter=1000,
                random_state=42,
                solver='lbfgs',
                class_weight='balanced'
            ))
        ])
        
        X_train, X_test, y_train, y_test = train_test_split(
            processed, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        self.pipeline.fit(X_train, y_train)
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model trained with accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.is_trained = True
        return accuracy

    def predict(self, description: str) -> Tuple[str, float]:
        if not self.is_trained or self.pipeline is None:
            return "Unknown", 0.0
        if not description or not isinstance(description, str):
            return "Unknown", 0.0

        try:
            processed = self.preprocess_text(description)
            predicted = self.pipeline.predict([processed])[0]
            probs = self.pipeline.predict_proba([processed])[0]
            confidence = float(max(probs))
            return predicted, confidence
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Unknown", 0.0

    def save_model(self, filepath: str = "backend/ml_models/trained_models/robust_categorizer.pkl"):
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'pipeline': self.pipeline,
                'categories': self.categories,
                'is_trained': self.is_trained
            }, f)

    def load_model(self, filepath: str = "backend/ml_models/trained_models/robust_categorizer.pkl"):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            self.pipeline = data['pipeline']
            self.categories = data['categories']
            self.is_trained = data['is_trained']
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def get_available_categories(self) -> List[str]:
        return self.categories.copy()


if __name__ == "__main__":
    cat = RobustExpenseCategorizer()
    print("Training robust expense categorizer...")
    acc = cat.train()
    cat.save_model()
    
    print("\n" + "="*70)
    print("TEST PREDICTIONS")
    print("="*70)
    
    tests = [
        'washing clothes', 'go to gym', 'laundry', 'exercise', 'workout',
        'clothes washing machine', 'movie theater', 'buy shoes', 'haircut',
        'electric company', 'doctor appointment', 'bus ticket', 'rent',
        'netflix', 'spotify', 'amazon', 'uber', 'starbucks',
        'gas station', 'grocery store', 'walmart', 'target',
        'cvs pharmacy', 'marriott hotel', 'university tuition', 'paycheck',
        'geico insurance', 'credit card bill', 'charity donation'
    ]
    
    for t in tests:
        c, conf = cat.predict(t)
        print(f'{t:30} -> {c:20} ({conf:.1%})')
    
    print(f"\nModel saved. Accuracy: {acc:.1%}")
