-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jul 08, 2022 at 12:31 PM
-- Server version: 10.5.15-MariaDB-0+deb11u1
-- PHP Version: 7.4.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `wisebox`
--
CREATE DATABASE IF NOT EXISTS `wisebox` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `wisebox`;

-- --------------------------------------------------------

--
-- Table structure for table `ApiKey`
--

CREATE TABLE `ApiKey` (
  `id` int(11) NOT NULL,
  `key` varchar(32) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Bucket`
--

CREATE TABLE `Bucket` (
  `id` int(11) NOT NULL,
  `start_time` time DEFAULT NULL,
  `interval` int(11) DEFAULT NULL,
  `frequency` int(11) DEFAULT NULL,
  `count` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `BucketMetadata`
--

CREATE TABLE `BucketMetadata` (
  `id` int(11) NOT NULL,
  `name` text DEFAULT NULL,
  `value` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `BucketRssi`
--

CREATE TABLE `BucketRssi` (
  `id` int(11) NOT NULL,
  `rssi` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Device`
-- FIXME: See: https://stackoverflow.com/questions/12504208/what-mysql-data-type-should-be-used-for-latitude-longitude-with-8-decimal-places
-- title is short title and place is an extended description of where the box is...

CREATE TABLE `Device` (
  `id` int(11) NOT NULL,
  `mac` varchar(17) DEFAULT NULL,
  `lat` decimal(8,6) DEFAULT NULL,
  `lng` decimal(9,6) DEFAULT NULL,
  `title` varchar(60) DEFAULT NULL,
  `place` text 
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `Device`
--

INSERT INTO `Device` (`id`, `mac`) VALUES
(3, 'testmac1'),
(4, 'testmac2'),
(5, 'string'),
(6, 'string');

-- --------------------------------------------------------

--
-- Table structure for table `Organisation`
--

CREATE TABLE `Organisation` (
  `id` int(11) NOT NULL,
  `name` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `Timezone`
--

CREATE TABLE `Timezone` (
  `id` int(11) NOT NULL,
  `name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ApiKey`
--
ALTER TABLE `ApiKey`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Bucket`
--
ALTER TABLE `Bucket`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `BucketMetadata`
--
ALTER TABLE `BucketMetadata`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `BucketRssi`
--
ALTER TABLE `BucketRssi`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Device`
--
ALTER TABLE `Device`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id` (`id`);

--
-- Indexes for table `Organisation`
--
ALTER TABLE `Organisation`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `Timezone`
--
ALTER TABLE `Timezone`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ApiKey`
--
ALTER TABLE `ApiKey`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `Bucket`
--
ALTER TABLE `Bucket`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `BucketMetadata`
--
ALTER TABLE `BucketMetadata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `BucketRssi`
--
ALTER TABLE `BucketRssi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Device`
--
ALTER TABLE `Device`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `Organisation`
--
ALTER TABLE `Organisation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Timezone`
--
ALTER TABLE `Timezone`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
