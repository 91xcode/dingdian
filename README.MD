```
顶点小说抓取,数据存入数据库

需要
BeautifulSoup
bs4
python2.7
scrapy
mysqldb


需要创建2张表


DROP TABLE IF EXISTS `dd_name`;
CREATE TABLE `dd_name` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `xs_name` varchar(255) DEFAULT NULL,
  `xs_author` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `name_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;



DROP TABLE IF EXISTS `dd_chaptername`;
CREATE TABLE `dd_chaptername` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `xs_chaptername` varchar(255) DEFAULT NULL,
  `xs_content` text,
  `id_name` int(11) DEFAULT NULL,
  `num_id` int(11) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

执行:
cd dingdian
python start.py
```
