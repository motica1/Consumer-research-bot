import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium.common.exceptions import TimeoutException

def scrape_google_reviews(product_name):
    # Format the product name for the URL
    formatted_product = product_name.replace(' ', '+')
    url = f"https://www.google.com/search?q={formatted_product}+reviews"

    # Set up Selenium WebDriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()  # Or webdriver.Firefox(), etc.
    driver.get(url)

    # Wait for the reviews to load with a longer timeout and handle potential timeout
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.review-dialog-list"))
        )
    except TimeoutException:
        print("Timed out waiting for reviews to load. Proceeding with available content.")

    # Scroll to load more reviews (adjust the range as needed)
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract reviews
    reviews = []
    review_elements = soup.select('div.review-dialog-list g-review-stars')
    
    # If no reviews found, try alternative selectors
    if not review_elements:
        review_elements = soup.select('div.gws-localreviews__google-review')
    
    # If still no reviews, log the issue
    if not review_elements:
        print("No review elements found. The page structure might have changed.")
        print("Attempting to find any review-like structures...")
        potential_reviews = soup.find_all('div', class_=lambda x: x and 'review' in x.lower())
        if potential_reviews:
            print(f"Found {len(potential_reviews)} potential review elements.")
            review_elements = potential_reviews
        else:
            print("No potential review elements found.")
    else:
        for review in review_elements:
            reviewer_name_elem = review.find_parent().find('div', class_='TSUbDb')
            reviewer_name = reviewer_name_elem.text.strip() if reviewer_name_elem else 'Unknown'
            
            rating_elem = review.select_one('span[aria-label]')
            rating = rating_elem['aria-label'].split()[0] if rating_elem else 'N/A'
            
            review_text_elem = review.find_parent().find('div', class_='Jtu6Td')
            review_text = review_text_elem.text.strip() if review_text_elem else 'No text'
            
            reviews.append({
                'Reviewer': reviewer_name,
                'Rating': rating,
                'Review': review_text
            })

    if not reviews:
        print("No reviews were extracted. Debug information:")
        print(f"Number of review elements found: {len(review_elements)}")
        print("First few elements in the soup:")
        print(soup.find_all(limit=5))

    # Close the browser
    driver.quit()

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(reviews)
    csv_filename = f"{product_name.replace(' ', '_')}_reviews.csv"
    if df.empty:
        print("Warning: No reviews were scraped. The CSV file will be empty.")
    else:
        df.to_csv(csv_filename, index=False)
        print(f"Reviews saved to {csv_filename}")

    return reviews

# Example usage
if __name__ == "__main__":
    product = input("Enter the product name to scrape reviews for: ")
    scrape_google_reviews(product)
