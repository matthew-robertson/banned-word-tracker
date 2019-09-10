CREATE TABLE `server` (
  server_id Varchar PRIMARY KEY NOT NULL,
  infracted_at Varchar NOT NULL,
  calledout_at Varchar NOT NULL,
  awake Int DEFAULT 1
);
