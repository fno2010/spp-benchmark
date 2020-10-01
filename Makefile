
data/20200701.as-rel.txt:
	curl -sSL -o data/20200701.as-rel.txt.bz2 http://data.caida.org/datasets/as-relationships/serial-1/20200701.as-rel.txt.bz2
	bunzip2 data/20200701.as-rel.txt.bz2

data/20200701.as2types.txt:
	curl -sSL -o data/20200701.as2types.txt.gz http://data.caida.org/datasets/as-classification/20200701.as2types.txt.gz
	gunzip data/20200701.as2types.txt.gz

data/as-country.txt:
	curl -sSL http://bgp.potaroo.net/cidr/autnums.html | grep '<a' | sed -E 's/^<a.*>AS([0-9]+).*, ([A-Z]+)$$/\1|\2/' > data/as-country.txt

prepare: data/20200701.as-rel.txt data/20200701.as2types.txt data/as-country.txt

