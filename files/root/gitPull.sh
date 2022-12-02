#! /bin/sh

lightingpath="/root/gsSystems_Lighting/"
lightinggit="https://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@github.com/metamericdesign/gsSystems_Lighting.git"

phppath="/srv/www/BaseStationPHP/Php"
phpgit="https://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@github.com/metamericdesign/BaseStationPHP.git"

git -C $lightingpath pull $lightinggit

git -C $phppath pull $phpgit
