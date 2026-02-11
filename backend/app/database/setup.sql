DROP TABLE IF EXISTS crawl_data;
DROP TABLE IF EXISTS crawl_history;

CREATE TABLE crawl_history (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  crawl_date    DATE NOT NULL,
  crawl_target  TEXT,
  source        VARCHAR(50) DEFAULT 'booking',
  total_records INT DEFAULT 0,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_history_crawl_date (crawl_date DESC),
  INDEX idx_history_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE crawl_data (
  id                   BIGINT AUTO_INCREMENT PRIMARY KEY,
  history_id           BIGINT NOT NULL,
  hotel_name           TEXT,
  hotel_link           TEXT,
  price_after_discount DECIMAL(15,2),
  price_original       DECIMAL(15,2),
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
