-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 25, 2025 at 10:17 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `django_auctions2`
--

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_category`
--

CREATE TABLE `adminpanel_category` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `deleted_at` datetime(6) DEFAULT NULL,
  `order` int(10) UNSIGNED DEFAULT NULL CHECK (`order` >= 0),
  `parent_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `adminpanel_category`
--

INSERT INTO `adminpanel_category` (`id`, `name`, `image`, `created_at`, `updated_at`, `deleted_at`, `order`, `parent_id`) VALUES
(1, 'Auto Auction', 'category/Auto_Auction_Website_Development_107.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(2, 'Real Estate Auction', 'category/Real_Estate_Auction_Website_Development_102.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(3, 'Art Auction', 'category/Art_Auction_Website_Development_108.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(4, 'Luxury Goods Auction', 'category/Luxury_Goods_Auction_Website_Development_103.webp', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(5, 'Charity Auction', 'category/Charity_Auction_Website_Development_109.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(6, 'Public Sector Auction', 'category/Luxury_Goods_Auction_Website_Development_103.webp', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(7, 'Collectibles & Coins Auction', 'category/Charity_Auction_Website_Development_109.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(8, 'Horses & Livestock Auction', 'category/Horses__Livestock_Auction_Website_Development_105.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(9, 'Marine Auction', 'category/Marine_Auction_Website_Development_111.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(10, 'Plant and Machinery Auction', 'category/Plant_and_Machinery_Auction_Website_Development_106.webp', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(11, 'Agricultural Clearing Sales Auction', 'category/Agricultural_Clearing_Sales_Auction_Website_Development_113.jpg', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(12, 'Sports Trading Cards & Memorabilia Auction', 'category/Sports_Trading_Cards_Memorabilia_Auction_Website_Development_112.avif', '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(13, 'Fine Wine, Whiskey & Spirits Auction', NULL, '2025-06-24 16:45:58.000000', '2025-06-24 16:45:58.000000', NULL, NULL, NULL),
(14, 'New Cars', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(15, 'Used Cars', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(16, 'Salvage Vehicles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(17, 'Classic Cars', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(18, 'Electric Vehicles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(19, 'Motorcycles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(20, 'Trucks & Trailers', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(21, 'RVs & Campers', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(22, 'Auto Parts', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(23, 'Fleet Vehicles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(24, 'Repo Vehicles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 1),
(25, 'Residential Homes', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(26, 'Apartments', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(27, 'Commercial Properties', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(28, 'Land / Plots', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(29, 'Foreclosed Properties', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(30, 'Luxury Real Estate', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(31, 'Investment Properties', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(32, 'Industrial Real Estate', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(33, 'Vacation Homes', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(34, 'Court Auctions', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 2),
(35, 'Paintings', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(36, 'Sculptures', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(37, 'Photographs', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(38, 'Prints & Lithographs', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(39, 'Contemporary Art', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(40, 'Antique Art', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(41, 'Digital Art / NFTs', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(42, 'Installations', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(43, 'Mixed Media', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 3),
(44, 'Watches', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(45, 'Handbags', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(46, 'Jewelry', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(47, 'Fashion & Couture', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(48, 'Footwear', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(49, 'Sunglasses & Accessories', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(50, 'Fine Pens', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(51, 'Limited Editions', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(52, 'Vintage Fashion', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 4),
(53, 'Event Tickets', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(54, 'Celebrity Experiences', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(55, 'Signed Memorabilia', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(56, 'Experiences', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(57, 'Donated Goods', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(58, 'Art for Charity', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(59, 'Gift Baskets', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(60, 'Services', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 5),
(61, 'Govt Vehicles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(62, 'Military Surplus', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(63, 'Seized Assets', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(64, 'Municipal Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(65, 'Office Furniture', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(66, 'IT Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(67, 'School Assets', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(68, 'Public Housing', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 6),
(69, 'Coins', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(70, 'Banknotes', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(71, 'Stamps', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(72, 'Comics', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(73, 'Vintage Toys', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(74, 'Action Figures', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(75, 'Trading Cards', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(76, 'Autographs', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(77, 'Antiques', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(78, 'Model Trains', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 7),
(79, 'Horses', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(80, 'Cattle', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(81, 'Sheep & Goats', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(82, 'Poultry', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(83, 'Pigs', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(84, 'Exotic Animals', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(85, 'Breeding Stock', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(86, 'Livestock Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 8),
(87, 'Sailboats', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(88, 'Jet Skis', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(89, 'Fishing Boats', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(90, 'Commercial Vessels', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(91, 'Outboard Motors', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(92, 'Boat Trailers', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(93, 'Marine Electronics', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(94, 'Marine Accessories', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 9),
(95, 'Construction Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(96, 'Agricultural Machinery', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(97, 'Industrial Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(98, 'Cranes & Lifts', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(99, 'Power Tools', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(100, 'Generators', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(101, 'Welding Machines', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(102, 'Forklifts', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(103, 'Spare Parts', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 10),
(104, 'Tractors', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(105, 'Harvesters', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(106, 'Irrigation Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(107, 'Fencing', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(108, 'Storage Tanks', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(109, 'Workshop Tools', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(110, 'Farm Vehicles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(111, 'Silos', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 11),
(112, 'MLB Cards', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(113, 'NBA Cards', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(114, 'NFL Cards', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(115, 'Soccer Cards', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(116, 'Signed Jerseys', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(117, 'Game Equipment', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(118, 'Sports Photos', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(119, 'Programs & Tickets', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(120, 'Championship Rings', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(121, 'Pins & Medals', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 12),
(122, 'Red Wines', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(123, 'White Wines', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(124, 'Sparkling / Champagne', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(125, 'Scotch', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(126, 'Bourbon', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(127, 'Rum & Vodka', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(128, 'Collector Bottles', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(129, 'Miniatures', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13),
(130, 'Barware', NULL, '2025-06-24 16:47:04.000000', '2025-06-24 16:47:04.000000', NULL, NULL, 13);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `adminpanel_category`
--
ALTER TABLE `adminpanel_category`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `adminpanel_category_name_parent_id_order_662b227f_uniq` (`name`,`parent_id`,`order`),
  ADD KEY `adminpanel_category_parent_id_feb750f1_fk_adminpanel_category_id` (`parent_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `adminpanel_category`
--
ALTER TABLE `adminpanel_category`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=131;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `adminpanel_category`
--
ALTER TABLE `adminpanel_category`
  ADD CONSTRAINT `adminpanel_category_parent_id_feb750f1_fk_adminpanel_category_id` FOREIGN KEY (`parent_id`) REFERENCES `adminpanel_category` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
