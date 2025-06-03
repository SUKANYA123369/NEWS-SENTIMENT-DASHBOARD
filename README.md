# 📰 News Sentiment Dashboard
## Overview
**News Sentiment Dashboard** is a project that collects news articles from the News API, stores them in AWS S3 and RDS, performs sentiment analysis on the article titles, and visualizes the results using a Streamlit dashboard. The entire application is containerized using Docker and deployed on AWS ECS.
## 🔁 Workflow
1. **Data Ingestion with AWS Lambda**
   - A Lambda function fetches news articles from the News API.
   - The raw data is stored in S3.
   - The same data is also inserted into a PostgreSQL table in Amazon RDS.
   - The RDS table is created programmatically within the Lambda function if it doesn't already exist.
2. **Sentiment Analysis & Dashboard**
   - A Streamlit app connects to the RDS database to read news data.
   - Sentiment analysis is applied to the `title` column using TextBlob.
   - A new `sentiment` column is added to the table with values: **positive**, **negative**, or **neutral**.
   - Each row is color-coded based on sentiment:
     - Positive: Blue
     - Negative: Red
     - Neutral: Green

3. **Deployment**
   - The Streamlit app is containerized using Docker.
   - The Docker image is pushed to Amazon ECR.
   - The image is then pulled and run on Amazon ECS.
   - The dashboard is accessible via the public IP and port `8051` of the ECS task.
