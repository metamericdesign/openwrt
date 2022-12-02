#! /bin/sh

lightingpath="/root"
lightinggit="https://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@github.com/metamericdesign/gsSystems_Lighting.git"

phppath="/srv/www"
phpgit="https://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@github.com/metamericdesign/BaseStationPHP.git"

git -C $lightingpath clone $lightinggit

git -C $phppath clone $phpgit

chmod 777 /srv/www/BaseStationPHP/Php/LightingNodeLog.php
