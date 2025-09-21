
-- Retrieve all successful bookings:
SELECT * FROM ola_data WHERE Booking_Status = 'Success';

-- Find the average ride distance for each vehicle type
SELECT Vehicle_Type, AVG(Ride_Distance) AS Avg_Ride_Distance FROM ola_data GROUP BY Vehicle_Type;

-- Get the total number of cancelled rides by customers:
SELECT COUNT(*) AS Total_Cancelled_Rides FROM ola_data WHERE Booking_Status = 'Canceled by Customer';

-- List the top 5 customers who booked the highest number of rides:
SELECT Customer_ID, COUNT(*) AS Ride_Count FROM ola_data GROUP BY Customer_ID ORDER BY Ride_Count DESC LIMIT 5;

-- Get the number of rides cancelled by drivers due to personal and car-related issues:
SELECT COUNT(*) AS Cancelled_Due_To_Personal_Car_Issues FROM ola_data WHERE Booking_Status = 'Canceled by Driver' AND Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- Find the maximum and minimum driver ratings for Prime Sedan bookings:
SELECT MAX(Driver_Ratings) AS Max_Rating, MIN(Driver_Ratings) AS Min_Rating FROM ola_data WHERE Vehicle_Type = 'Prime Sedan';

-- Retrieve all rides where payment was made using UPI:
SELECT * FROM ola_data WHERE Payment_Method = 'UPI';

-- Find the average customer rating per vehicle type:
SELECT Vehicle_Type, AVG(Customer_Rating) AS Avg_Customer_Rating FROM ola_data GROUP BY Vehicle_Type;

-- Calculate the total booking value of rides completed successfully:
SELECT SUM(Booking_Value) AS Total_Booking_Value FROM ola_data WHERE Booking_Status = 'Success';

-- List all incomplete rides along with the reason
SELECT Booking_ID, Incomplete_Rides_Reason FROM ola_data WHERE Incomplete_Rides = 'Yes';
