DROP TABLE IF EXISTS crawl_data;
DROP TABLE IF EXISTS crawl_history;
DROP TABLE IF EXISTS saved_data_sources;

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
  INDEX idx_data_history_id (history_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Database setup completed successfully!' AS message;
