-- nrs_subscriber_pin.sql
CREATE TABLE IF NOT EXISTS subscriber_pins (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  userID     INT NOT NULL,
  articleID  INT NOT NULL,
  pinned_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_user_article (userID, articleID),
  CONSTRAINT fk_pin_user
    FOREIGN KEY (userID) REFERENCES users(userID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_pin_article
    FOREIGN KEY (articleID) REFERENCES articles(articleID)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
