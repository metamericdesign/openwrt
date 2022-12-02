#! /bin/sh

lightingpath="/root"
lightinggit="https://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@github.com/metamericdesign/gsSystems_Lighting.git"

phppath="/srv/www" 
phpgit="https://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@github.com/metamericdesign/BaseStationPHP.git"

git -C $lightingpath clone $lightinggit

git -C $phppath clone $phpgit

chmod 777 /srv/www/BaseStationPHP/Php/LightingNodeLog.php




