# Update the DB file from the SQL file

echo "Updating database file"
rm ./backend/server/db/sqlite/numail.db
sqlite3 ./backend/server/db/sqlite/numail.db < ./backend/server/db/sqlite/numail.sql
echo "Database file updated"