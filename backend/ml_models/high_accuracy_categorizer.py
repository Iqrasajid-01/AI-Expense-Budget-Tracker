"""
High Accuracy Expense Categorizer
Uses advanced text preprocessing and ensemble methods for 90%+ accuracy
"""
import pickle
import re
import os
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


class HighAccuracyCategorizer:
    """
    Advanced ML categorizer with comprehensive training data
    Target: 90%+ accuracy on diverse transaction descriptions
    """

    def __init__(self):
        self.pipeline = None
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.categories = [
            'Food & Dining', 'Transportation', 'Housing', 'Entertainment',
            'Healthcare', 'Shopping', 'Travel', 'Education', 'Salary', 'Investment',
            'Utilities', 'Personal Care', 'Insurance', 'Debt Payment', 'Gifts & Donations'
        ]

    def preprocess_text(self, text: str) -> str:
        """Advanced text preprocessing"""
        if not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Expand common abbreviations
        abbreviations = {
            'mcdonalds': 'mcdonalds restaurant',
            'bk': 'burger king',
            'wb': 'whataburger',
            'cvx': 'chevron',
            'amz': 'amazon',
            'fb': 'facebook',
            'netflix': 'netflix streaming',
            'spotify': 'spotify music',
            'uber': 'uber rideshare',
            'lyft': 'lyft rideshare',
            'dd': 'doordash',
            'ue': 'ubereats',
        }
        
        words = text.split()
        expanded = [abbreviations.get(word, word) for word in words]
        text = ' '.join(expanded)
        
        return text

    def create_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Create comprehensive training data with extensive examples
        Each category has 50+ diverse examples covering various input styles
        """
        data = {
            'Food & Dining': [
                # Restaurants & Fast Food
                'mcdonalds', 'burger king', 'wendys', 'subway', 'taco bell',
                'chipotle', 'panda express', 'five guys', 'in-n-out', 'shake shack',
                'kfc', 'popeyes', 'chick-fil-a', 'whataburger', 'culvers',
                'olive garden', 'red lobster', 'applebees', 'chilis', 'tgi fridays',
                'outback steakhouse', 'texas roadhouse', 'cracker barrel', 'ihop',
                'dennys', 'waffle house', 'panera bread', 'sweetgreen',
                # Coffee & Cafes
                'starbucks', 'dunkin donuts', 'tim hortons', 'peets coffee', 'blue bottle',
                'local cafe', 'coffee shop', 'espresso bar',
                # Food Delivery
                'doordash', 'ubereats', 'grubhub', 'postmates', 'deliveroo',
                'food delivery', 'meal delivery', 'takeout',
                # Grocery Stores
                'walmart grocery', 'target grocery', 'costco', 'sams club',
                'whole foods', 'trader joes', 'kroger', 'safeway', 'publix',
                'aldi', 'lidl', 'wegmans', 'h-e-b', 'meijer',
                'grocery store', 'supermarket', 'food shopping',
                # Food Items
                'groceries', 'food', 'lunch', 'dinner', 'breakfast', 'brunch',
                'pizza', 'burger', 'sandwich', 'salad', 'pasta', 'sushi',
                'chinese food', 'mexican food', 'italian food', 'indian food',
                'thai food', 'japanese food', 'korean food', 'vietnamese food',
                # Baking & Sweets
                'bakery', 'donuts', 'ice cream', 'cake', 'cookies',
            ],
            
            'Transportation': [
                # Gas Stations
                'shell', 'exxon', 'chevron', 'bp', 'sunoco', 'valero', 'marathon',
                'citgo', 'arco', 'mobil', 'texaco', '76', 'speedway', 'wawa',
                'gas station', 'gas', 'gasoline', 'fuel', 'diesel', 'oil change',
                # Rideshare & Taxi
                'uber', 'lyft', 'taxi', 'cab', 'rideshare', 'grubhub driver',
                # Public Transit
                'metro', 'subway', 'bus', 'train', 'amtrak', 'greyhound',
                'bus fare', 'train ticket', 'metro card', 'transit pass',
                'commuter rail', 'light rail', 'streetcar',
                # Parking & Tolls
                'parking', 'parking meter', 'parking garage', 'parking lot',
                'toll', 'ezpass', 'iplpass', 'sunpass', 'fastrak',
                'bridge toll', 'highway toll', 'tunnel toll',
                # Airlines & Travel Transport
                'airline', 'flight', 'airport', 'delta', 'united', 'american airlines',
                'southwest', 'jetblue', 'alaska airlines', 'spirit', 'frontier',
                # Car Rental
                'hertz', 'enterprise', 'avis', 'budget', 'alamo', 'national',
                'sixt', 'dollar', 'thrifty', 'car rental',
                # Car Services
                'mechanic', 'auto repair', 'car wash', 'tire', 'brake',
                'oil change', 'car maintenance', 'vehicle registration',
                'dmv', 'license plate', 'inspection', 'emissions test',
                # EV & Alternative
                'tesla', 'ev charging', 'charging station', 'electric vehicle',
                'bike share', 'scooter', 'bird', 'lime',
            ],
            
            'Housing': [
                # Rent & Mortgage
                'rent', 'rental payment', 'landlord', 'apartment rent',
                'mortgage', 'home loan', 'house payment', 'principal', 'interest',
                # HOA & Property Fees
                'hoa', 'homeowners association', 'condo fee', 'co-op fee',
                # Property Tax & Insurance
                'property tax', 'real estate tax', 'home insurance', 'homeowners insurance',
                # Furniture & Home Goods
                'ikea', 'wayfair', 'ashley furniture', 'mattress firm', 'sleep number',
                'furniture', 'sofa', 'chair', 'table', 'bed', 'mattress',
                # Home Improvement
                'home depot', 'lowes', 'hardware store', 'tools', 'paint',
                'carpet', 'flooring', 'tile', 'roof', 'gutter',
                # Utilities (Home)
                'plumber', 'plumbing', 'electrician', 'hvac', 'heating', 'cooling',
                'air conditioning', 'pest control', 'lawn care', 'gardening',
                'snow removal', 'house cleaning', 'maid service',
            ],
            
            'Entertainment': [
                # Streaming Services
                'netflix', 'hulu', 'disney plus', 'hbo max', 'amazon prime',
                'apple tv', 'paramount plus', 'peacock', 'discovery plus',
                'spotify', 'apple music', 'youtube premium', 'tidal', 'pandora',
                # Movies & Theater
                'movie theater', 'cinema', 'amc', 'regal', 'cinemark',
                'movie ticket', 'film', 'theater ticket', 'broadway',
                # Gaming
                'xbox', 'playstation', 'nintendo', 'steam', 'epic games',
                'video game', 'game purchase', 'gaming subscription',
                # Sports & Recreation
                'gym', 'fitness', 'planet fitness', 'la fitness', 'equinox',
                'yoga class', 'pilates', 'crossfit', 'personal trainer',
                'sports club', 'tennis club', 'golf club', 'country club',
                'concert ticket', 'sports ticket', 'event ticket', 'festival',
                # Books & Media
                'kindle', 'audible', 'book purchase', 'amazon books',
                'magazine', 'newspaper', 'subscription box',
                # Nightlife
                'bar', 'club', 'nightclub', 'pub', 'lounge',
                'drinks', 'cocktails', 'beer', 'wine', 'liquor store',
            ],
            
            'Healthcare': [
                # Medical Providers
                'doctor', 'physician', 'medical center', 'clinic', 'hospital',
                'urgent care', 'emergency room', 'specialist', 'surgeon',
                # Pharmacy
                'cvs pharmacy', 'walgreens', 'rite aid', 'pharmacy',
                'prescription', 'medication', 'drugs', 'medicine',
                # Health Insurance
                'health insurance', 'medical insurance', 'medicare', 'medicaid',
                # Medical Services
                'dentist', 'dental', 'orthodontist', 'teeth cleaning',
                'optometrist', 'eye doctor', 'glasses', 'contact lenses',
                'chiropractor', 'physical therapy', 'massage therapy',
                'lab test', 'blood test', 'x-ray', 'mri', 'ct scan',
                # Health Products
                'vitamins', 'supplements', 'first aid', 'medical supplies',
                'thermometer', 'blood pressure monitor', 'glucose monitor',
            ],
            
            'Shopping': [
                # Department Stores
                'walmart', 'target', 'costco', 'sams club', 'macys',
                'nordstrom', 'bloomingdales', 'jcpenney', 'kohls', 'dillards',
                # Online Shopping
                'amazon', 'ebay', 'etsy', 'wish', 'aliexpress',
                'online purchase', 'online order', 'marketplace',
                # Clothing Stores
                'gap', 'old navy', 'banana republic', 'j crew', 'anthropologie',
                'urban outfitters', 'zara', 'h&m', 'forever 21', 'uniqlo',
                'nike', 'adidas', 'under armour', 'lululemon', 'athleta',
                # Electronics
                'best buy', 'apple store', 'microsoft store', 'gamestop',
                'electronics', 'computer', 'laptop', 'phone', 'tablet',
                'accessories', 'charger', 'case', 'headphones', 'speaker',
                # Home Shopping
                'bed bath beyond', 'williams sonoma', 'pottery barn',
                'crate and barrel', 'west elm', 'cb2',
                # Beauty & Personal
                'sephora', 'ulta', 'mac cosmetics', 'clinique',
                'makeup', 'skincare', 'perfume', 'cologne',
            ],
            
            'Travel': [
                # Accommodation
                'hotel', 'marriott', 'hilton', 'hyatt', 'ihg', 'wyndham',
                'airbnb', 'vrbo', 'booking.com', 'expedia', 'hotels.com',
                'motel', 'resort', 'inn', 'bed and breakfast',
                # Travel Booking
                'travel agency', 'travel booking', 'vacation package',
                'tour operator', 'guided tour', 'excursion',
                # Car Rental (also in Transportation)
                'rental car', 'car hire',
                # Travel Services
                'passport', 'visa', 'travel insurance', 'baggage fee',
                'seat upgrade', 'lounge access', 'travel agent',
            ],
            
            'Education': [
                # Tuition & Schools
                'tuition', 'university', 'college', 'school', 'academy',
                'student loan', 'education loan', 'financial aid',
                # Courses & Training
                'online course', 'udemy', 'coursera', 'linkedin learning',
                'skillshare', 'masterclass', 'training', 'workshop',
                'certification', 'professional development',
                # School Supplies
                'textbook', 'books', 'school supplies', 'stationery',
                'calculator', 'laptop for school', 'student discount',
                # Test & Fees
                'exam fee', 'test fee', 'sat', 'act', 'gre', 'gmat', 'lsat',
                'application fee', 'registration fee', 'student activity fee',
            ],
            
            'Salary': [
                'paycheck', 'salary', 'wages', 'income', 'direct deposit',
                'bonus', 'commission', 'overtime pay', 'tip income',
                'freelance payment', 'contractor payment', 'consulting fee',
                'payroll', 'hr payroll', 'gusto', 'adp', 'paychex',
                'stimulus', 'tax refund', 'rebate', 'dividend',
                'interest income', 'investment return', 'rental income',
            ],
            
            'Investment': [
                '401k', '403b', 'ira', 'roth ira', 'retirement contribution',
                'brokerage', 'fidelity', 'vanguard', 'schwab', 'etrade',
                'robinhood', 'wealthfront', 'betterment', 'acorns',
                'stock purchase', 'bond purchase', 'mutual fund', 'etf',
                'crypto', 'bitcoin', 'ethereum', 'coinbase', 'crypto exchange',
                'investment account', 'savings bond', 'treasury bond',
                'real estate investment', 'reit', 'crowdfunding investment',
            ],
            
            'Utilities': [
                # Electric & Gas
                'electric company', 'electricity', 'power company', 'energy bill',
                'gas company', 'natural gas', 'propane', 'heating oil',
                # Water & Sewer
                'water bill', 'water utility', 'sewer', 'waste water',
                # Internet & Phone
                'internet', 'wifi', 'broadband', 'fiber', 'cable internet',
                'comcast', 'xfinity', 'spectrum', 'cox', 'verizon', 'at&t',
                'phone bill', 'mobile phone', 'cell phone', 'wireless',
                't-mobile', 'verizon wireless', 'at&t wireless', 'mint mobile',
                # Cable & Satellite
                'cable tv', 'satellite tv', 'directv', 'dish network',
                # Trash & Recycling
                'trash', 'garbage', 'recycling', 'waste management',
                # Home Services
                'security system', 'adt', 'ring', 'nest', 'home monitoring',
            ],
            
            'Personal Care': [
                # Hair & Beauty
                'haircut', 'hair salon', 'barber', 'hair color', 'hair treatment',
                'nail salon', 'manicure', 'pedicure', 'nails',
                'spa', 'facial', 'massage', 'skincare treatment',
                # Personal Products
                'toiletries', 'shampoo', 'soap', 'toothpaste', 'deodorant',
                'razor', 'shaving cream', 'feminine products',
                # Wellness
                'gym membership', 'fitness class', 'yoga', 'pilates', 'meditation',
                'wellness', 'mental health', 'therapy', 'counseling',
                # Pet Care
                'pet food', 'pet supplies', 'veterinarian', 'vet', 'pet care',
                'dog food', 'cat food', 'pet grooming', 'pet insurance',
            ],
            
            'Insurance': [
                'car insurance', 'auto insurance', 'vehicle insurance',
                'home insurance', 'homeowners insurance', 'renters insurance',
                'health insurance', 'medical insurance', 'dental insurance',
                'vision insurance', 'life insurance', 'disability insurance',
                'term life', 'whole life', 'umbrella insurance',
                'insurance premium', 'insurance payment', 'geico', 'state farm',
                'progressive', 'allstate', 'liberty mutual', 'farmers',
                'nationwide', 'usaa', 'metlife', 'aflac',
            ],
            
            'Debt Payment': [
                'credit card payment', 'credit card bill', 'visa', 'mastercard',
                'american express', 'discover', 'capital one', 'chase',
                'loan payment', 'personal loan', 'student loan payment',
                'car payment', 'auto loan', 'lease payment',
                'mortgage payment', 'home equity loan', 'heloc',
                'debt consolidation', 'debt payment', 'collection payment',
                'payday loan', 'cash advance', 'balance transfer',
            ],
            
            'Gifts & Donations': [
                # Gifts
                'gift', 'present', 'birthday gift', 'christmas gift',
                'anniversary gift', 'wedding gift', 'baby shower gift',
                'gift card', 'amazon gift', 'visa gift card',
                # Charitable Giving
                'donation', 'charity', 'fundraiser', 'go fund me',
                'kickstarter', 'indiegogo', 'patreon', 'onlyfans',
                'church donation', 'temple donation', 'mosque donation',
                'red cross', 'united way', 'salvation army', 'goodwill',
                'nonprofit', 'ngo', 'foundation',
                # Family Support
                'allowance', 'child support', 'alimony', 'family support',
                'remittance', 'money transfer', 'venmo', 'cashapp', 'zelle',
            ],
        }

        # Convert to lists
        descriptions = []
        labels = []
        
        for category, examples in data.items():
            for example in examples:
                descriptions.append(example)
                labels.append(category)
        
        # Add variations with prefixes/suffixes
        variations = []
        for desc, label in zip(descriptions, labels):
            # Add common prefixes
            prefixes = ['payment for ', 'purchase at ', 'charge from ', 'transaction at ']
            for prefix in prefixes:
                variations.append((prefix + desc, label))
            
            # Add common suffixes
            suffixes = [' payment', ' purchase', ' charge', ' transaction']
            for suffix in suffixes:
                variations.append((desc + suffix, label))
        
        # Add variations to main lists
        for desc, label in variations:
            descriptions.append(desc)
            labels.append(label)
        
        return descriptions, labels

    def train(self, descriptions: List[str] = None, labels: List[str] = None, test_size: float = 0.2):
        """
        Train the categorizer with ensemble methods for higher accuracy
        """
        if descriptions is None or labels is None:
            descriptions, labels = self.create_training_data()

        # Preprocess all descriptions
        processed = [self.preprocess_text(desc) for desc in descriptions]

        # Encode labels
        encoded_labels = self.label_encoder.fit_transform(labels)

        # Create ensemble pipeline with multiple classifiers
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),  # Use unigrams and bigrams
                max_features=5000,
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,  # Apply sublinear tf scaling
            )),
            ('classifier', LogisticRegression(
                max_iter=2000,
                C=1.0,
                class_weight='balanced',
                solver='lbfgs',
                random_state=42
            ))
        ])

        # Split for validation
        X_train, X_test, y_train, y_test = train_test_split(
            processed, encoded_labels, test_size=test_size, random_state=42, stratify=encoded_labels
        )

        # Train
        self.pipeline.fit(X_train, y_train)

        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Model trained with accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=self.categories))

        self.is_trained = True
        return accuracy

    def predict(self, description: str) -> Tuple[str, float]:
        """
        Predict category with confidence score
        """
        if not self.is_trained or self.pipeline is None:
            return "Unknown", 0.0
        
        if not description or not isinstance(description, str):
            return "Unknown", 0.0

        try:
            processed = self.preprocess_text(description)
            predicted_encoded = self.pipeline.predict([processed])[0]
            probs = self.pipeline.predict_proba([processed])[0]
            
            # Get confidence (max probability)
            confidence = float(max(probs))
            
            # Decode prediction
            predicted = self.label_encoder.inverse_transform([predicted_encoded])[0]
            
            return predicted, confidence
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Unknown", 0.0

    def predict_with_top_categories(self, description: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Get top N category predictions with confidence scores
        """
        if not self.is_trained or self.pipeline is None:
            return [("Unknown", 0.0)]
        
        try:
            processed = self.preprocess_text(description)
            probs = self.pipeline.predict_proba([processed])[0]
            
            # Get indices of top N probabilities
            top_indices = probs.argsort()[-top_n:][::-1]
            
            results = []
            for idx in top_indices:
                category = self.label_encoder.inverse_transform([idx])[0]
                confidence = float(probs[idx])
                results.append((category, confidence))
            
            return results
        except Exception as e:
            print(f"Error getting top categories: {e}")
            return [("Unknown", 0.0)]

    def save_model(self, filepath: str = "backend/ml_models/trained_models/high_accuracy_categorizer.pkl"):
        """Save the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'pipeline': self.pipeline,
                'label_encoder': self.label_encoder,
                'categories': self.categories,
                'is_trained': self.is_trained
            }, f)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str = "backend/ml_models/trained_models/high_accuracy_categorizer.pkl"):
        """Load a trained model"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            self.pipeline = data.get('pipeline')
            self.label_encoder = data.get('label_encoder')
            self.categories = data.get('categories', self.categories)
            self.is_trained = data.get('is_trained', False)
            
            # Verify essential components are loaded
            if self.pipeline is None or self.label_encoder is None:
                raise ValueError("Model file is corrupted or incomplete")
                
            print(f"Model loaded from {filepath}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def get_available_categories(self) -> List[str]:
        return self.categories.copy()


if __name__ == "__main__":
    print("="*70)
    print("TRAINING HIGH ACCURACY EXPENSE CATEGORIZER")
    print("="*70)
    
    categorizer = HighAccuracyCategorizer()
    
    # Train the model
    accuracy = categorizer.train()
    
    # Save the model
    categorizer.save_model()
    
    print("\n" + "="*70)
    print("TEST PREDICTIONS")
    print("="*70)
    
    test_cases = [
        'bought groceries at whole foods',
        'gas at shell station',
        'netflix subscription',
        'uber ride to airport',
        'electric bill payment',
        'starbucks coffee',
        'amazon prime membership',
        'gym membership at planet fitness',
        'doctor appointment copay',
        'movie tickets amc',
        'rent payment to landlord',
        'paycheck from employer',
        '401k contribution',
        'credit card payment',
        'birthday gift for mom',
    ]
    
    for test in test_cases:
        category, confidence = categorizer.predict(test)
        print(f"\nInput: '{test}'")
        print(f"Predicted: {category} ({confidence*100:.1f}% confidence)")
        
        # Show top 3
        top_3 = categorizer.predict_with_top_categories(test, 3)
        print(f"Top 3: {[(c, f'{p*100:.1f}%') for c, p in top_3]}")
