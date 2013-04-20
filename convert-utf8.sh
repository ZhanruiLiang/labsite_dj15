user=root
db=labsite
mysqldump -u$user -p -c -e --default-character-set=utf8 --single-transaction --skip-set-charset --add-drop-database -B $db > dump.sql
sed 's/DEFAULT CHARACTER SET latin1/DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci/' <dump.sql | sed 's/DEFAULT CHARSET=latin1/DEFAULT CHARSET=utf8/' >dump-fixed.sql
echo 'reload...'
mysql -u$user -p < dump-fixed.sql
