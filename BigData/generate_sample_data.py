"""
Synthetic Gaming Customer Data Generator
=========================================
This script generates synthetic gaming customer data that matches the schema
expected by the machine_learning_pipeline.py script.

Use this when testData.data is not available (excluded from git repository).

Usage:
    python generate_sample_data.py --rows 4000 --output testData.data
    python generate_sample_data.py --rows 1000 --output randomsample.data
"""

import random
import argparse
from datetime import datetime, timedelta
import uuid


class GamingDataGenerator:
    """Generate synthetic gaming customer data"""
    
    COUNTRIES = ['USA', 'UK', 'GERMANY', 'FRANCE', 'CANADA', 'SPAIN', 'ITALY']
    FIRST_NAMES = [
        'JOHN', 'EDGAR', 'ROBERT', 'MARY', 'JAMES', 'PATRICIA', 'MICHAEL', 
        'JENNIFER', 'WILLIAM', 'LINDA', 'DAVID', 'ELIZABETH', 'RICHARD', 
        'BARBARA', 'JOSEPH', 'SUSAN', 'THOMAS', 'JESSICA', 'CHARLES', 'SARAH',
        'HERBERT', 'HUGH', 'GEORGE', 'PAUL', 'DONALD', 'MARK', 'STEVEN', 'KEVIN'
    ]
    LAST_NAMES = [
        'SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'GARCIA', 'MILLER',
        'DAVIS', 'RODRIGUEZ', 'MARTINEZ', 'HERNANDEZ', 'LOPEZ', 'GONZALEZ',
        'WILSON', 'ANDERSON', 'THOMAS', 'TAYLOR', 'MOORE', 'JACKSON', 'MARTIN',
        'WASHINGTON', 'HARRIS', 'ROBERTSON', 'LEE', 'WALKER', 'HALL', 'ALLEN'
    ]
    MIDDLE_INITIALS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    def __init__(self, seed=42):
        """Initialize generator with optional seed for reproducibility"""
        random.seed(seed)
    
    def generate_email(self, first_name, last_name):
        """Generate email address"""
        domains = ['@hotmail.com', '@gmail.com', '@privacy.net', '@yahoo.com', '@outlook.com']
        email = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}{random.choice(domains)}"
        return email
    
    def generate_address(self, country):
        """Generate address based on country"""
        if random.random() < 0.3:  # 30% have N/A address
            return 'N/A'
        
        street_num = random.randint(100, 9999)
        street_names = ['Washington Pkwy', 'Highland Trl', 'Highland Ct', 'Main St', 
                       'Oak Ave', 'Maple Dr', 'Park Rd', 'Lake View']
        street_type = ['Ste', 'Apt', 'Fl', 'Unit']
        
        states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 
                 'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI',
                 'CO', 'MN', 'SC', 'AL', 'LA', 'KY', 'OR', 'OK', 'CT', 'IA',
                 'MS', 'AR', 'KS', 'UT', 'NV', 'NM', 'WV', 'NE', 'ID', 'HI',
                 'NH', 'ME', 'MT', 'RI', 'DE', 'SD', 'ND', 'AK', 'VT', 'WY']
        
        if country == 'USA':
            unit = random.randint(100, 999)
            zip_code = random.randint(10000, 99999)
            return f"{street_num} {random.choice(street_names)} {random.choice(street_type)} {unit} {random.choice(states)} {zip_code}"
        else:
            return 'N/A'
    
    def generate_timestamp(self):
        """Generate random timestamp (milliseconds since epoch)"""
        # Generate timestamp between 2012 and 2015
        start_date = datetime(2012, 1, 1)
        end_date = datetime(2015, 12, 31)
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        return int(random_date.timestamp() * 1000)
    
    def generate_customer(self):
        """Generate a single customer record"""
        # Basic info
        session_id = str(uuid.uuid4())
        first_name = random.choice(self.FIRST_NAMES)
        middle_initial = random.choice(self.MIDDLE_INITIALS)
        last_name = random.choice(self.LAST_NAMES)
        cname = f"{first_name} {middle_initial} {last_name}"
        email = self.generate_email(first_name, last_name)
        gender = random.choice(['male', 'female'])
        age = random.randint(18, 30)
        country = random.choice(self.COUNTRIES)
        address = self.generate_address(country)
        register_date = self.generate_timestamp()
        
        # Gaming behavior - use realistic distributions
        # Most users are casual players
        if random.random() < 0.7:  # 70% casual players
            friend_count = random.randint(0, 50)
            lifetime = random.randint(0, 20)
            game1 = random.randint(0, 10)
            game2 = random.randint(0, 10)
            game3 = random.randint(0, 10)
            game4 = random.randint(0, 10)
            revenue = 0
            paid_subscriber = 'no'
        elif random.random() < 0.9:  # 20% moderate players
            friend_count = random.randint(10, 200)
            lifetime = random.randint(10, 50)
            game1 = random.randint(0, 25)
            game2 = random.randint(0, 25)
            game3 = random.randint(0, 25)
            game4 = random.randint(0, 25)
            revenue = random.randint(0, 5) if random.random() < 0.3 else 0
            paid_subscriber = 'yes' if revenue > 0 else 'no'
        else:  # 10% power users
            friend_count = random.randint(100, 417)
            lifetime = random.randint(30, 100)
            game1 = random.randint(5, 30)
            game2 = random.randint(5, 30)
            game3 = random.randint(5, 30)
            game4 = random.randint(10, 60)
            revenue = random.randint(5, 20)
            paid_subscriber = 'yes'
        
        # CSV format matching original data
        row = f"{session_id},{cname},{email},{gender},{age},{address},{country}," \
              f"{register_date},{friend_count},{lifetime},{game1},{game2},{game3}," \
              f"{game4},{revenue},{paid_subscriber}"
        
        return row
    
    def generate_dataset(self, num_rows):
        """Generate complete dataset"""
        print(f"Generating {num_rows} synthetic customer records...")
        rows = []
        for i in range(num_rows):
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1}/{num_rows} rows...")
            rows.append(self.generate_customer())
        print(f"✓ Successfully generated {num_rows} rows")
        return rows
    
    def save_to_file(self, rows, output_file):
        """Save dataset to file"""
        print(f"Saving data to {output_file}...")
        with open(output_file, 'w') as f:
            f.write('\n'.join(rows))
        print(f"✓ Data saved successfully to {output_file}")
        print(f"  File size: {len('\n'.join(rows)) / 1024:.2f} KB")


def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(
        description='Generate synthetic gaming customer data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_sample_data.py --rows 4000 --output testData.data
  python generate_sample_data.py --rows 1000 --output randomsample.data
  python generate_sample_data.py --rows 500 --output randomsample2.data --seed 12345

Dataset Schema:
  session_id, cname, email, gender, age, address, country, register_date,
  friend_count, lifetime, citygame_played, pictionarygame_played,
  scramblegame_played, snipergame_played, revenue, paid_subscriber
        """
    )
    
    parser.add_argument(
        '--rows', '-r',
        type=int,
        default=4000,
        help='Number of customer records to generate (default: 4000)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='testData.data',
        help='Output filename (default: testData.data)'
    )
    
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Generate data
    generator = GamingDataGenerator(seed=args.seed)
    rows = generator.generate_dataset(args.rows)
    generator.save_to_file(rows, args.output)
    
    print(f"\n{'='*60}")
    print("Dataset generation complete!")
    print(f"{'='*60}")
    print(f"Output file: {args.output}")
    print(f"Total rows: {args.rows}")
    print(f"Random seed: {args.seed}")
    print(f"\nYou can now use this file with machine_learning_pipeline.py")


if __name__ == '__main__':
    main()
