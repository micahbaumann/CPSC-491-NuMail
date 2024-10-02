# Update the DB file from the SQL file

echo "Updating database file"
rm ./db/sqlite/numail.db
sqlite3 ./db/sqlite/numail.db < ./db/sqlite/numail.sql
echo "Database file updated"