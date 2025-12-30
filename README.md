# sql
# sql command and function with database world and skilla with their problem statment 
# sql project
 Project Title: Local Food Wastage Management System
Name:- Yash solanki
Date: 20/08/2025

Abstract
Food wastage is a growing global challenge, while millions of people still suffer from food insecurity. Restaurants, grocery stores, and households often discard surplus food that could otherwise be redistributed to those in need.
This project, Local Food Wastage Management System, aims to bridge the gap between food providers and receivers using a structured digital platform.
The system is built using Python, SQL, and Streamlit. Four datasets (providers, receivers, food listings, and claims) were cleaned, normalized, and stored in a relational SQLite database. A set of 15 SQL queries were designed to analyze food donation trends, claims distribution, and provider/receiver activity. Insights were supported with EDA visualizations (bar charts, pie charts, and trend graphs). Finally, a Streamlit application was developed to provide CRUD operations, filters, and dashboards for real-time interaction.
The results demonstrate that the platform can effectively reduce food waste, provide transparency in distribution, and empower NGOs and communities to improve food security.

1. Introduction
Food wastage and food insecurity exist simultaneously: while tons of edible food are discarded daily, many individuals and families struggle to meet their dietary needs. Addressing this problem requires efficient redistribution systems.
This project provides a data-driven platform that connects food providers (restaurants, supermarkets, grocery stores) with receivers (NGOs, shelters, individuals). By leveraging SQL for data management and Streamlit for an interactive UI, the system ensures surplus food is tracked, claimed, and distributed efficiently.

2. Datasets
The project uses four main datasets:
Provider Data
Provider_ID, Name, Type, Address, City, Contact
Contains details of restaurants, supermarkets, and other donors.
Receivers Data:-Receiver_ID, Name, Type, City, Contact
Includes NGOs, shelters, and individuals who claim surplus food.
Food Listings Data:-Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type
Tracks available food items with type and expiry details.
Claims Data:-Claim_ID, Food_ID, Receiver_ID, Status, Timestamp
Records claims made by receivers and their statuses (Pending, Completed, Cancelled).

3. Methodology
The project followed a structured pipeline:
Data Cleaning
Fixed inconsistent labels (e.g., “Bread” incorrectly marked as Non-Vegetarian).
Converted dates into standardized formats.
Removed duplicates and standardized city/food names.
Database Creation
Designed SQLite schema with foreign keys and indexes.
Loaded cleaned datasets into tables: provider_data, receivers_data, food_listings_data, claims_data.
SQL Queries (15)
Analyzed provider/receiver distribution, claims performance, and food wastage trends.
EDA (Exploratory Data Analysis)
Bar charts: Providers & Receivers by City, Claims by Status.
Pie chart: Food Type distribution.
Line chart: Claims trend over time.
Streamlit Application
Interactive UI with filtering (city, food type, meal type).
Dashboards for all 15 SQL queries.

4. Streamlit Application
The Streamlit app provided:
Filters for city, provider, food type, meal type.
Dashboards for 15 SQL queries.
Contact details display for collaboration.
Link :- https://foodwastemanagmentupdated.streamlit.app/

