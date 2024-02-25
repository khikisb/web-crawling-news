import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

def get_article_content(article_url):
    response = requests.get(article_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        article_content = soup.find('div', class_='read__content').find_all('p')
        content = ''.join([p.get_text() for p in article_content])
        return content
    return ""

def scrape_news_data(theme, start_date, end_date):
    base_url_dict = {
        "Health": "https://health.kompas.com/search/{}-{}-{}",
        "Travel": "https://travel.kompas.com/search/{}-{}-{}",
        "Sports": "https://www.kompas.com/sports/search/{}-{}-{}",
        "Education": "https://edukasi.kompas.com/search/{}-{}-{}",
        "Technology": "https://tekno.kompas.com/search/{}-{}-{}",
        "Property": "https://properti.kompas.com/search/{}-{}-{}",
        "Food": "https://www.kompas.com/food/search/{}-{}-{}"
    }

    base_url = base_url_dict.get(theme, "")
    if not base_url:
        st.error("Invalid theme selection.")
        return None

    data = []
    current_date = start_date
    while current_date <= end_date:
        url = base_url.format(current_date.year, current_date.month, current_date.day)
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_elements = soup.find_all('h3', class_='article__title article__title--medium')
            
            for element in news_elements:
                title = element.a.text
                article_url = element.a['href']
                
                article_response = requests.get(article_url)
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                date_time_element = article_soup.find('div', class_='read__time')
                date_time = date_time_element.text.strip() if date_time_element else ""
                date_time = date_time.replace('Kompas.com -', '')
                
                article_link_element = article_soup.find('a', class_='article__link')
                article_link = article_link_element['href'] if article_link_element else ""
                
                class_element = article_soup.find('div', class_='article__subtitle article__subtitle--inline')
                class_info = class_element.text.strip() if class_element else ""

                content = get_article_content(article_url)

                data.append({
                    'Date': date_time,
                    'Title': title,
                    'URL': article_link,  
                    'Content': content,
                    'Class': class_info
                })

            current_date += timedelta(days=1)
        else:
            st.error(f"Failed to fetch data for {current_date.strftime('%d-%m-%Y')}")
            return None

    return data

def main():
    st.title("News Crawler App")

    theme_options = ["Health", "Travel", "Sports", "Education", "Technology", "Property", "Food"]
    selected_theme = st.selectbox("Select Theme:", theme_options)

    start_date = st.date_input("Start Date", datetime(2024, 2, 23))
    end_date = st.date_input("End Date", datetime(2024, 2, 24))

    if start_date > end_date:
        st.error("End date must be greater than or equal to start date.")
        return

    if st.button("Scrape News"):
        st.info(f"Scraping news data for {selected_theme} from {start_date} to {end_date}...")

        news_data = scrape_news_data(selected_theme, start_date, end_date)

        if news_data:
            df = pd.DataFrame(news_data)
            st.write(df)
            st.markdown(get_csv_download_link(df), unsafe_allow_html=True)

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="news_data.csv">Download CSV File</a>'
    return href

if __name__ == "__main__":
    main()
