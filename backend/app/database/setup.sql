DROP TABLE IF EXISTS crawl_data;
DROP TABLE IF EXISTS crawl_history;
DROP TABLE IF EXISTS saved_data_sources;
DROP TABLE IF EXISTS competitor_list;
DROP TABLE IF EXISTS config_items;
DROP TABLE IF EXISTS market_cluster_mapping;

-- Bảng lưu thông tin nguồn data (Excel hoặc Google Sheets)
CREATE TABLE saved_data_sources (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(255) NOT NULL,
  source_type   ENUM('file', 'google_sheets') NOT NULL,
  file_path     TEXT,
  sheets_url    TEXT,
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_source_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE crawl_history (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  crawl_date    DATE NOT NULL,
  crawl_time    TIME NOT NULL,
  crawl_target  TEXT,
  source        VARCHAR(50) DEFAULT 'booking',
  scrape_type   ENUM('info', 'price') NOT NULL DEFAULT 'info',
  market        VARCHAR(100),
  check_in      DATE,
  check_out     DATE,
  total_records INT DEFAULT 0,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_history_crawl_date (crawl_date DESC),
  INDEX idx_history_source (source),
  INDEX idx_history_scrape_type (scrape_type),
  INDEX idx_history_market (market)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE crawl_data (
  id                   BIGINT AUTO_INCREMENT PRIMARY KEY,
  history_id           BIGINT NOT NULL,
  code                 VARCHAR(100),
  hotel_name           TEXT,
  hotel_link           TEXT,
  popular_facilities   TEXT,
  price_after_discount DECIMAL(15,2),
  price_original       DECIMAL(15,2),
  discount_percent     VARCHAR(20),
  review_count         INT,
  review_score         FLOAT,
  room_type            TEXT,
  num_people           INT,
  bed_info             TEXT,
  room_area            VARCHAR(100),
  options              JSON,
  created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (history_id) REFERENCES crawl_history(id) ON DELETE CASCADE,
  INDEX idx_data_history_id (history_id),
  INDEX idx_data_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng config cho các dropdown values
CREATE TABLE config_items (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  category    VARCHAR(100) NOT NULL,
  config_key  VARCHAR(100) NOT NULL,
  config_value VARCHAR(255) NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_category_key (category, config_key),
  INDEX idx_config_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng mapping giữa Code và Market/Cluster
CREATE TABLE market_cluster_mapping (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  code        VARCHAR(100) NOT NULL UNIQUE,
  market      VARCHAR(100) NOT NULL,
  cluster     VARCHAR(100) NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_mapping_code (code),
  INDEX idx_mapping_market (market)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bảng competitor list
CREATE TABLE competitor_list (
  id                   BIGINT AUTO_INCREMENT PRIMARY KEY,
  code                 VARCHAR(100) NOT NULL UNIQUE,
  hotel_name           TEXT,
  hotel_link           TEXT,
  room_type            TEXT,
  num_people           INT,
  bed_info             TEXT,
  room_area            VARCHAR(100),
  room_choices         TEXT,
  popular_facilities   TEXT,
  market               VARCHAR(100),
  cluster              VARCHAR(100),
  competitor_level     VARCHAR(100),
  breakfast_included   VARCHAR(100),
  room_group           VARCHAR(100),
  level                VARCHAR(100),
  created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_competitor_code (code),
  INDEX idx_competitor_market (market)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Database setup completed successfully!' AS message;
