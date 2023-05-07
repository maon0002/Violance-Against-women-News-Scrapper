# 
<h1 align="center">Hi 👋, I'm Maon</h1>
<h3 align="center">A passionate beginner python developer from Bulgaria</h3>

<h3 align="left">About the 'Violance-Against-women-News-Scrapper'</h3>
<p align="left">The project scope are the news related to vioalance against women
collected from the three main TV website archives in Bulgaria.</p>

<h3 align="left">Project details</h3>
<p align="left">The script can instantiate WebsiteArchive objects with inspected attributes (html classes and tags)
and initialize searching throughout the media archive pages starting from page 1 until matching of existed in the media archive .csv article or until interruption.</p>
<p align="left">Using tuples with predefined keywords related to the project scope, an article can be further inspected or passed.</p>
<p align="left"> - first, the script is looking at the articles in the current page;</p>
<p align="left"> - second, if a word from the first level keywords is in the article's title, the script is looking in a second tuple with keywords for exclusion and if None it continue by getting the article URL;</p>
<p align="left"> - third, the script uses second level of keywords to decide if the data must be kept or passed - this action is about looking for keywords in the article's text accessed by the URL via html class and tag;</p>
<p align="left"> - fourth, if the conditions for the first and second level are met, the script adds the data in a dictionary with columns:</p>
<li>"Title": <i>19-годишен е задържан за убийството на майка си, държал тялото в мазето!</i> (*article's title)</li>
<li>"URL": <i>https://btvnovinite.bg/bulgaria/19-godishen-e-zadarzhan-za-ubijstvoto-na-majka-si-darzhal-tjaloto-v-mazeto.html</i> (*article's link)</li>
<li>"Source": <i>btvnovinite.bg</i> (*article's source/media)</li>
<li>"Type": <i>TV news</i> (*article's source/media type)</li>
<li>"DateTime": <i>2023-05-03 15:48:00</i> (*article's datetime of publishing)</li>
<li>"Article": <i>19-годишен младеж е задържан и обвинен за убийство на майка си, съобщават от Апелативната прокуратура във Велико Търново. По данни на прокуратурата 52-годишната жена живеела на квартира в апартамент в центъра на Ловеч заедно със сина си. На 20 февруари той обявил в районното управление на МВР, че от 13 февруари майка му е напуснала квартирата и оттогава е в неизвестност. След като през април в блока започнала да се носи неприятна миризма, собственикът на жилището бил повикан от София, отключил мазето си и там било открито тялото на жената. 19-годишният ѝ син е установен като извършител на престъплението и задържан на 1 май първоначално за срок от 24 часа, а след това за 72 часа. Предстои да бъде внесено искане за вземане на мярка за неотклонение „задържане под стража“</i>.</li>
<li>"Location": <i>Велико Търново, Ловеч</i> (*article's text)</li>
<li>"Keywords1": <i>майка</i> (*first level keywords found in the article's title)</li>
<li>"Keywords2": <i>уби</i> (*second level keywords found in the article's text)</li>
<p align="left"> - fifth, it passes the dictionary data to dataframes and then export the data in a current file, update the media archive .csv with the new articles and also creates two additional .csv files with word counting columns for the article titles and for the article text</p>

<p align="left">* after the script completion the info.log file can be used to see which articles were successfully added or excluded ('---' prefix for the excluded ones and '+++' for the included ones ('***' prefix is for any cathed interruptions)</p>

<p></p>
<p align="left"> <img src="https://komarev.com/ghpvc/?username=maon0002&label=Profile%20views&color=0e75b6&style=flat" alt="maon0002" /> </p>

- 🌱 I’m currently learning **Python in SoftUni (https://softuni.bg/certificates/details/168179/6b467c9f)**

- 📫 How to reach me **manukov.business@gmail.com**

<h3 align="left">Connect with me:</h3>
<p align="left">
<a href="https://linkedin.com/in/https://www.linkedin.com/in/onik-manukov-7368b6222/" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/linked-in-alt.svg" alt="https://www.linkedin.com/in/onik-manukov-7368b6222/" height="30" width="40" /></a>
</p>

<h3 align="left">Languages and Tools:</h3>
<p align="left"> <a href="https://www.java.com" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/java/java-original.svg" alt="java" width="40" height="40"/> </a> <a href="https://www.mysql.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/mysql/mysql-original-wordmark.svg" alt="mysql" width="40" height="40"/> </a> <a href="https://www.oracle.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/oracle/oracle-original.svg" alt="oracle" width="40" height="40"/> </a> <a href="https://www.python.org" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a> <a href="https://www.sqlite.org/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/sqlite/sqlite-icon.svg" alt="sqlite" width="40" height="40"/> </a> </p>

<p><img align="center" src="https://github-readme-stats.vercel.app/api/top-langs?username=maon0002&show_icons=true&locale=en&layout=compact" alt="maon0002" /></p>



