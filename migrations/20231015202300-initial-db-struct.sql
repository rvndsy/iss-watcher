CREATE TABLE IF NOT EXISTS iss_pass_records (
      id int NOT NULL AUTO_INCREMENT,
      place_name varchar(255) NOT NULL,
      place_lat decimal(30, 6) NOT NULL,
      place_lon decimal(30, 6) NOT NULL,
      start_utc int(10) NOT NULL,
      end_utc int(10) NOT NULL,
      duration int(4) NOT NULL,
      PRIMARY KEY(id)
    )